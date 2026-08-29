export interface Basket {
  name: string;
  created: number;
}

export interface CapturedRequest {
  id: string;
  method: string;
  fg: string;
  bg: string;
  ts: number;
  path: string;
  query: string;
  headers: [string, string][];
  body: string;
  contentType: string;
}
