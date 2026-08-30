import { afterEach, expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App.tsx'

afterEach(() => {
  vi.unstubAllGlobals()
  window.history.replaceState({}, '', '/')
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

test('creates a basket and stores its name and token in local storage', async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'hello world' }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        name: 'demo123',
        webhook_url: 'http://testserver/demo123',
        token: '12345678-1234-5678-1234-567812345678',
        expires_at: '2026-09-01T12:00:00Z',
      }),
    })
  vi.stubGlobal('fetch', fetchMock)

  render(<App />)

  await screen.findByText('hello world')
  const user = userEvent.setup()
  const input = screen.getByLabelText('Basket name')
  await user.clear(input)
  await user.type(input, 'demo123')
  await user.click(screen.getByRole('button', { name: 'Create basket' }))

  expect(await screen.findByText('http://testserver/demo123')).toBeDefined()
  expect(fetchMock).toHaveBeenNthCalledWith(2, '/api/baskets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: 'demo123' }),
  })
  expect(window.localStorage.getItem('demo123')).toBe(
    '12345678-1234-5678-1234-567812345678',
  )
  expect(window.localStorage.getItem('basketcase.baskets')).toBeNull()
})

test('lists saved basket names at /baskets without calling the API', () => {
  window.history.replaceState({}, '', '/baskets')
  window.localStorage.setItem('firstbasket', '11111111-1111-4111-8111-111111111111')
  window.localStorage.setItem('secondbasket', '22222222-2222-4222-8222-222222222222')
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ message: 'should not be fetched' }),
  })
  vi.stubGlobal('fetch', fetchMock)

  render(<App />)

  expect(screen.getByRole('heading', { name: 'Saved baskets' })).toBeDefined()
  expect(screen.getByText('firstbasket')).toBeDefined()
  expect(screen.getByText('secondbasket')).toBeDefined()
  expect(fetchMock).not.toHaveBeenCalled()
})

test('does not show saved baskets with invalid local storage tokens', () => {
  window.history.replaceState({}, '', '/baskets')
  window.localStorage.setItem('namedbasket', '33333333-3333-4333-8333-333333333333')
  window.localStorage.setItem('emptytoken', '')
  window.localStorage.setItem('invalidtoken', 'token-3')
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'should not be fetched' }),
    }),
  )

  render(<App />)

  expect(screen.getByText('namedbasket')).toBeDefined()
  expect(screen.getAllByRole('listitem')).toHaveLength(1)
})
