import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import App from './App'
import BasketService from './services/BasketService'

vi.mock('./services/BasketService', () => ({
  default: {
    createBasket: vi.fn(),
    deleteBasket: vi.fn(),
    loadBasketDetails: vi.fn(),
  },
}))

const mockedBasketService = vi.mocked(BasketService)

const createdBasket = {
  name: 'demo123',
  webhook_url: 'http://127.0.0.1:8000/demo123',
  token: '12345678-1234-5678-1234-567812345678',
  expires_at: '2026-09-01T12:00:00Z',
}

function renderApp(initialEntry = '/baskets') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <App />
    </MemoryRouter>,
  )
}

describe('App basket ownership flows', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('shows the returned webhook URL and stores the returned basket ownership data', async () => {
    mockedBasketService.createBasket.mockResolvedValue(createdBasket)
    const user = userEvent.setup()
    renderApp()

    const nameInput = screen.getByRole('textbox')
    await user.clear(nameInput)
    await user.type(nameInput, 'requestedName')
    await user.click(screen.getByRole('button', { name: 'Create' }))

    expect(await screen.findByText(createdBasket.webhook_url)).toBeInTheDocument()
    expect(localStorage.getItem('basket_demo123')).toBe(createdBasket.token)
    expect(screen.getByRole('link', { name: 'demo123' })).toBeInTheDocument()
  })

  test('copies the exact webhook URL returned by the backend', async () => {
    mockedBasketService.createBasket.mockResolvedValue(createdBasket)
    const user = userEvent.setup()
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText },
    })
    renderApp()

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'demo123' } })
    await user.click(screen.getByRole('button', { name: 'Create' }))
    await user.click(await screen.findByRole('button', { name: 'Copy webhook URL' }))

    expect(writeText).toHaveBeenCalledWith(createdBasket.webhook_url)
    expect(screen.getByText('Copied')).toBeInTheDocument()
  })

  test('passes the stored token when deleting and removes ownership only after success', async () => {
    localStorage.setItem('basket_demo123', createdBasket.token)
    mockedBasketService.loadBasketDetails.mockResolvedValue({
      name: 'demo123',
      capacity: 200,
      expires_at: createdBasket.expires_at,
      requests: [],
    })
    mockedBasketService.deleteBasket.mockResolvedValue()
    const user = userEvent.setup()
    renderApp('/baskets/demo123')

    await user.click(await screen.findByRole('button', { name: 'Delete basket' }))

    await waitFor(() => {
      expect(mockedBasketService.deleteBasket).toHaveBeenCalledWith('demo123', createdBasket.token)
    })
    expect(localStorage.getItem('basket_demo123')).toBeNull()
  })

  test('keeps ownership data when deletion fails', async () => {
    localStorage.setItem('basket_demo123', createdBasket.token)
    mockedBasketService.loadBasketDetails.mockResolvedValue({
      name: 'demo123',
      capacity: 200,
      expires_at: createdBasket.expires_at,
      requests: [],
    })
    mockedBasketService.deleteBasket.mockRejectedValue(new Error('Network unavailable'))
    const user = userEvent.setup()
    renderApp('/baskets/demo123')

    await user.click(await screen.findByRole('button', { name: 'Delete basket' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Unable to delete basket demo123.')
    expect(localStorage.getItem('basket_demo123')).toBe(createdBasket.token)
  })
})
