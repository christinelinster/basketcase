export interface BasketRequest {
  id: string;
  method: string;
  path: string;
  headers: Record<string, string | string[]>;
  query_params: Record<string, string | string[]>;
  body: string | null;
  received_at: string;
}

export interface Basket {
  name: string;
  capacity: number;
  expires_at: string;
  requests: BasketRequest[];
}

export interface CreatedBasket {
  name: string;
  webhook_url: string;
  token: string;
  expires_at: string;
}
