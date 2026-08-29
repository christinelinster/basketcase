import axios from 'axios'

const API_BASKETS_PATH = '/api/baskets'

class BasketService {
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
