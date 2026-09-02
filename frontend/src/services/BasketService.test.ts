import axios from 'axios'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import BasketService from './BasketService'

vi.mock('axios', () => ({
  default: {
    delete: vi.fn(),
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockedAxios = vi.mocked(axios)

describe('BasketService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('creates a basket with the API response contract', async () => {
    const createdBasket = {
      name: 'demo123',
      webhook_url: 'http://127.0.0.1:8000/demo123',
      token: '12345678-1234-5678-1234-567812345678',
      expires_at: '2026-09-01T12:00:00Z',
    }
    mockedAxios.post.mockResolvedValue({ data: createdBasket })

    const result = await BasketService.createBasket('demo123')

    expect(mockedAxios.post).toHaveBeenCalledWith('/api/baskets', { name: 'demo123' })
    expect(result).toEqual(createdBasket)
  })

  test('loads encoded basket details and all associated requests', async () => {
    const basket = {
      name: 'demo 123',
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
    }
    mockedAxios.get.mockResolvedValue({ data: basket })

    const result = await BasketService.loadBasketDetails('demo 123')

    expect(mockedAxios.get).toHaveBeenCalledWith('/api/baskets/demo%20123')
    expect(result).toEqual(basket)
  })

  test('deletes a basket using its ownership token', async () => {
    mockedAxios.delete.mockResolvedValue({ status: 204 })

    await BasketService.deleteBasket('demo 123', 'basket-token')

    expect(mockedAxios.delete).toHaveBeenCalledWith('/api/baskets/demo%20123', {
      headers: { 'X-Basket-Token': 'basket-token' },
    })
  })

  test('propagates API failures without returning fake data', async () => {
    const apiError = new Error('Network unavailable')
    mockedAxios.get.mockRejectedValue(apiError)

    await expect(BasketService.loadBasketDetails('demo123')).rejects.toBe(apiError)
  })
})
