import { afterEach, expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App.tsx'

afterEach(() => {
  vi.unstubAllGlobals()
})

test('increments the counter', async () => {
  render(<App />)

  const user = userEvent.setup()
  const button = screen.getByRole('button', { name: 'count is 0' })

  await user.click(button)

  expect(screen.getByRole('button', { name: 'count is 1' })).toBeDefined()
})

test('displays the hello response from the backend', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ message: 'hello world' }),
  })
  vi.stubGlobal('fetch', fetchMock)

  render(<App />)

  expect(await screen.findByText('hello world')).toBeDefined()
  expect(fetchMock).toHaveBeenCalledWith('/api/baskets/hello')
})
