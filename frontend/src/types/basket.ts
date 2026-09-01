export interface BasketRequest {
  id: number;
  method: string;
  path: string;
  headers: Record<string, string>;
  query_params: Record<string, string>;
  body: string | null;
  received_at: string;
}

export interface Basket {
  name: string;
  capacity: number;
  expires_at: string;
  requests: BasketRequest[];
}
