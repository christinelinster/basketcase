import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import BasketService from '../services/BasketService'
import BasketPage from './BasketPage'

vi.mock('../services/BasketService', () => ({
  default: {
    loadBasketDetails: vi.fn(),
  },
}))

const mockedBasketService = vi.mocked(BasketService)

describe('BasketPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('refreshes requests through the basket-detail endpoint', async () => {
    mockedBasketService.loadBasketDetails
      .mockResolvedValueOnce({
        name: 'demo123',
        capacity: 200,
        expires_at: '2026-09-01T12:00:00Z',
        requests: [],
      })
      .mockResolvedValueOnce({
        name: 'demo123',
        capacity: 200,
        expires_at: '2026-09-01T12:00:00Z',
        requests: [
          {
            id: '12345678-1234-5678-1234-567812345678',
            method: 'POST',
            path: '/events',
            headers: { 'content-type': 'application/json' },
            query_params: { source: ['stripe', 'retry'] },
            body: '{"ok":true}',
            received_at: '2026-08-29T20:00:00Z',
          },
        ],
      })
    const user = userEvent.setup()

    render(
      <MemoryRouter initialEntries={['/baskets/demo123']}>
        <Routes>
          <Route path="/baskets/:name" element={<BasketPage onDelete={vi.fn()} />} />
        </Routes>
      </MemoryRouter>,
    )

    expect(await screen.findByText('Requests: 0')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Refresh' }))

    expect(await screen.findByText('/events?source=stripe&source=retry')).toBeInTheDocument()
    expect(screen.getByText('Requests: 1')).toBeInTheDocument()
  })
})
