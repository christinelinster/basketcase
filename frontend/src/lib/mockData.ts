import type { Basket, CapturedRequest } from '../types/basket';

const ALPHA = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const STORAGE_KEY = 'basketcase.baskets';

export function makeToken(rand?: () => number): string {
  let s = '';
  for (let i = 0; i < 7; i++) s += ALPHA[Math.floor((rand ? rand() : Math.random()) * ALPHA.length)];
  return s;
}

function seeded(name: string): () => number {
  let h = 2166136261;
  for (let i = 0; i < name.length; i++) {
    h ^= name.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return () => {
    h ^= h << 13;
    h ^= h >>> 17;
    h ^= h << 5;
    return ((h >>> 0) % 100000) / 100000;
  };
}

const METHODS = [
  { m: 'GET', fg: '#8fd0bd', bg: 'rgba(143,208,189,0.14)', w: 5 },
  { m: 'POST', fg: '#95b4e6', bg: 'rgba(149,180,230,0.15)', w: 4 },
  { m: 'PUT', fg: '#b5abfc', bg: 'rgba(181,171,252,0.15)', w: 2 },
  { m: 'PATCH', fg: '#cfd3e5', bg: 'rgba(207,211,229,0.12)', w: 1 },
  { m: 'DELETE', fg: '#d99a9a', bg: 'rgba(217,154,154,0.14)', w: 1 },
];
const PATHS = ['/', '/webhooks/stripe', '/hooks/github/push', '/v1/events', '/callback', '/notify/slack', '/ingest', '/v2/orders/8841'];
const QUERIES = ['', '', 'signature=8f2c1a&ts=1724910233', 'page=2&per_page=50', 'token=live_9d1&verify=true', 'source=cli'];
const AGENTS = ['Stripe/1.0 (+https://stripe.com/docs/webhooks)', 'GitHub-Hookshot/2c9a1f3', 'curl/8.4.0', 'python-requests/2.31.0', 'PostmanRuntime/7.36.1', 'Go-http-client/2.0'];
const BODIES = [
  '{"id":"evt_1P9dQz2eZvKYlo2C","type":"payment_intent.succeeded","created":1724910233,"data":{"object":{"id":"pi_3P9dQz","amount":4200,"currency":"usd","status":"succeeded","customer":"cus_QK1x9Zt"}},"livemode":false}',
  '{"ref":"refs/heads/main","before":"a1b2c3d","after":"9f8e7d6","pusher":{"name":"avery","email":"avery@example.com"},"commits":[{"id":"9f8e7d6","message":"fix: retry webhook delivery","distinct":true}]}',
  '{"order_id":8841,"status":"shipped","items":[{"sku":"BC-102","qty":2},{"sku":"BC-770","qty":1}],"total":"89.40"}',
  'name=avery&plan=pro&notify=1',
];

export function makeRequest(rand: () => number, ts: number, i: number): CapturedRequest {
  const pool = METHODS.flatMap((m) => Array(m.w).fill(m));
  const meth = pool[Math.floor(rand() * pool.length)];
  const hasBody = meth.m !== 'GET' && meth.m !== 'DELETE';
  const body = hasBody ? BODIES[Math.floor(rand() * BODIES.length)] : '';
  const form = body.indexOf('{') !== 0;
  const headers: [string, string][] = [
    ['Host', 'basketcase.com'],
    ['User-Agent', AGENTS[Math.floor(rand() * AGENTS.length)]],
    ['Accept', '*/*'],
    ['X-Request-Id', Math.floor(rand() * 1e9).toString(16).padStart(8, '0')],
    ['X-Forwarded-For', '18.' + Math.floor(rand() * 250) + '.' + Math.floor(rand() * 250) + '.' + Math.floor(rand() * 250)],
  ];
  if (hasBody) {
    headers.push(['Content-Type', form ? 'application/x-www-form-urlencoded' : 'application/json']);
    headers.push(['Content-Length', String(body.length)]);
  }
  return {
    id: 'r' + ts + '-' + i,
    method: meth.m,
    fg: meth.fg,
    bg: meth.bg,
    ts,
    path: PATHS[Math.floor(rand() * PATHS.length)],
    query: QUERIES[Math.floor(rand() * QUERIES.length)],
    headers,
    body,
    contentType: hasBody ? (form ? 'application/x-www-form-urlencoded' : 'application/json') : 'none',
  };
}

export function seedRequests(name: string, limit: number): { list: CapturedRequest[]; total: number } {
  if (name === 'a3Nw8jH') return { list: [], total: 0 };
  const rand = seeded(name);
  const total = 20 + Math.floor(rand() * 40);
  const list: CapturedRequest[] = [];
  let t = Date.now() - 1000 * 60 * 3;
  for (let i = 0; i < limit; i++) {
    list.push(makeRequest(rand, t, i));
    t -= Math.floor(1000 * (40 + rand() * 900));
  }
  return { list, total };
}

export function loadBaskets(): Basket[] {
  let baskets: Basket[] = [];
  try {
    baskets = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch {
    baskets = [];
  }
  if (!baskets.length) {
    baskets = [
      { name: 'q7Rm2vD', created: Date.now() - 86400000 * 2 },
      { name: 'kP9xz4T', created: Date.now() - 86400000 * 5 },
      { name: 'a3Nw8jH', created: Date.now() - 86400000 * 11 },
    ];
    saveBaskets(baskets);
  }
  return baskets;
}

export function saveBaskets(baskets: Basket[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(baskets));
  } catch {
    // localStorage unavailable; nothing to persist
  }
}

export function fmtTime(ts: number): string {
  const d = new Date(ts);
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

export function ago(ts: number): string {
  const s = Math.max(1, Math.round((Date.now() - ts) / 1000));
  if (s < 60) return s + 's ago';
  if (s < 3600) return Math.round(s / 60) + 'm ago';
  if (s < 86400) return Math.round(s / 3600) + 'h ago';
  return Math.round(s / 86400) + 'd ago';
}
