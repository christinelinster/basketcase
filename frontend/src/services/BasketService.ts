import axios from 'axios'
import type { Basket, BasketRequest } from '../types/basket'

const API_BASKETS_PATH = '/api/baskets'

// CURRENTLY STUBBED 
class BasketService {
  static async loadBasketDetails(name: string): Promise<Basket> {
    return {
      name: 'testbasket',
      capacity: 200,
      expires_at: '2026-09-01T20:28:29.564579Z',
      requests: [
        {
          id: 2,
          method: 'POST',
          path: '/webhooks/stripe',
          headers: {
            'Host': 'basketcase.com',
            'User-Agent': 'Stripe/1.0 (+https://stripe.com/docs/webhooks)',
            'Content-Type': 'application/json',
            'Content-Length': '176',
          },
          query_params: {},
          body: '{"id":"evt_1P9dQz2eZvKYlo2C","type":"payment_intent.succeeded","amount":4200}',
          received_at: '2026-08-29T20:26:04.000Z',
        },
        {
          id: 1,
          method: 'GET',
          path: '/v1/events',
          headers: {
            'Host': 'basketcase.com',
            'User-Agent': 'curl/8.4.0',
            'Accept': '*/*',
          },
          query_params: { page: '2', per_page: '50' },
          body: null,
          received_at: '2026-08-29T20:20:11.000Z',
        },
      ],
    }
    // const response = await axios.get(`${API_BASKETS_PATH}/${name}`)
    // return response.data.data // Data returned as { data: { ... } }
  }

  static async loadBasketRequests(name: string): Promise<BasketRequest[]> {
    return [
      {
        id: 2,
        method: 'POST',
        path: '/webhooks/stripe',
        headers: {
          'Host': 'basketcase.com',
          'User-Agent': 'Stripe/1.0 (+https://stripe.com/docs/webhooks)',
          'Content-Type': 'application/json',
          'Content-Length': '176',
        },
        query_params: {},
        body: '{"id":"evt_1P9dQz2eZvKYlo2C","type":"payment_intent.succeeded","amount":4200}',
        received_at: '2026-08-29T20:26:04.000Z',
      },
      {
        id: 1,
        method: 'GET',
        path: '/v1/events',
        headers: {
          'Host': 'basketcase.com',
          'User-Agent': 'curl/8.4.0',
          'Accept': '*/*',
        },
        query_params: { page: '2', per_page: '50' },
        body: null,
        received_at: '2026-08-29T20:20:11.000Z',
      },
    ]
  }
  
  static async createBasket(name: string) {
    return { 
      name: 'testbasket', 
      token: 'testtoken', 
      capacity: 200,
      expires_at: new Date('2026-09-01 16:28:29.564579-04')
    }
    // const response = await axios.post(API_BASKETS_PATH, name)
    // return response.data.data // Data returned as { data: { ... } }
  }

  static async deleteBasket(name: string) {
    // get basket token from local storage
    // const response = await axios.delete(`${API_BASKETS_PATH}/${name}`, {
    //   headers: { 'X-Basket-Token': basketToken }
    // })
    
    // return response.status === 204 
    return true
  }
}

export default BasketService
