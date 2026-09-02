import axios from 'axios'
import type { Basket, CreatedBasket } from '../types/basket'

const API_BASKETS_PATH = '/api/baskets'

class BasketService {
  static async loadBasketDetails(name: string): Promise<Basket> {
    const response = await axios.get<Basket>(`${API_BASKETS_PATH}/${encodeURIComponent(name)}`)
    return response.data
  }

  static async createBasket(name: string): Promise<CreatedBasket> {
    const response = await axios.post<CreatedBasket>(API_BASKETS_PATH, { name })
    return response.data
  }

  static async deleteBasket(name: string, token: string): Promise<void> {
    await axios.delete(`${API_BASKETS_PATH}/${encodeURIComponent(name)}`, {
      headers: { 'X-Basket-Token': token },
    })
  }
}

export default BasketService
