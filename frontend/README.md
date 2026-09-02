# Basketcase frontend

The frontend is a React, TypeScript, and Vite application for creating local
webhook baskets and inspecting their captured requests. See the
[root setup guide](../README.md) for database initialization and the complete
local workflow.

## Install and start

From `frontend`:

```bash
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

The backend must be running at `http://127.0.0.1:8000`. During development,
Vite proxies frontend `/api` requests to that address. If the backend uses a
different port, update the proxy target in `vite.config.ts`.

## Local basket workflow

1. Enter an alphanumeric name in the New Basket form.
2. Select **Create**.
3. Use **Copy URL** to copy the webhook URL returned by the backend.
4. Send an HTTP request to that URL.
5. Select the basket under My Baskets and refresh it to inspect the request.

The frontend stores each created basket name and ownership token in browser
local storage. It uses the token when deleting that basket. Baskets created in
another browser do not appear in the local My Baskets list.

## Commands

```bash
npm test
npm run lint
npm run build
```

- `npm test` runs the Vitest test suite.
- `npm run lint` runs ESLint.
- `npm run build` type-checks and creates the production bundle.
