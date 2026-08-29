import { useEffect, useState } from 'react'
import './App.css'

type HelloResponse = { message: string }
type BasketResponse = {
  name: string
  webhook_url: string
  token: string
  expires_at: string
}
type StoredBasket = Pick<BasketResponse, 'name' | 'token'>

const BASKETS_PATH = '/baskets'
const DEFAULT_BASKET_NAME = 'newbasket'
const TOKEN_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

function loadStoredBaskets(): StoredBasket[] {
  const baskets: StoredBasket[] = []

  for (let index = 0; index < window.localStorage.length; index += 1) {
    const name = window.localStorage.key(index)
    const token = name ? window.localStorage.getItem(name) : null

    if (!name || name.trim().length === 0 || !token || !TOKEN_PATTERN.test(token)) {
      continue
    }

    baskets.push({ name, token })
  }

  return baskets
}

function BasketsPage({ baskets }: { baskets: StoredBasket[] }) {
  return (
    <>
      <h1>Basketcase</h1>
      <main>
        <h2>Saved baskets</h2>
        {baskets.length > 0 ? (
          <ul>
            {baskets.map((basket) => (
              <li key={basket.name}>{basket.name}</li>
            ))}
          </ul>
        ) : (
          <p>No saved baskets.</p>
        )}
      </main>
    </>
  )
}

function App() {
  const isBasketsRoute = window.location.pathname === BASKETS_PATH
  const [count, setCount] = useState(0)
  const [backendMessage, setBackendMessage] = useState('Loading...')
  const [basketName, setBasketName] = useState(DEFAULT_BASKET_NAME)
  const [createdBasket, setCreatedBasket] = useState<BasketResponse | null>(null)
  const [storedBaskets, setStoredBaskets] = useState<StoredBasket[]>(loadStoredBaskets)
  const [createError, setCreateError] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    if (isBasketsRoute) return

    fetch('/api/baskets/hello')
      .then((response) => {
        if (!response.ok) throw new Error(`Backend returned ${response.status}`)
        return response.json() as Promise<HelloResponse>
      })
      .then(({ message }) => setBackendMessage(message))
      .catch(() => setBackendMessage('Backend unavailable'))
  }, [isBasketsRoute])

  const handleCreate = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setCreateError(null)
    setIsCreating(true)

    try {
      const response = await fetch('/api/baskets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: basketName }),
      })
      const result = (await response.json()) as BasketResponse & { detail?: string }

      if (!response.ok) {
        throw new Error(result.detail ?? `Backend returned ${response.status}`)
      }

      setCreatedBasket(result)
      window.localStorage.setItem(result.name, result.token)
      const nextBaskets = [
        { name: result.name, token: result.token },
        ...storedBaskets.filter((basket) => basket.name !== result.name),
      ]
      setStoredBaskets(nextBaskets)
    } catch (error) {
      setCreateError(error instanceof Error ? error.message : 'Unable to create basket')
    } finally {
      setIsCreating(false)
    }
  }

  if (isBasketsRoute) {
    return <BasketsPage baskets={storedBaskets} />
  }

  return (
    <>
      <h1>Basketcase</h1>
      <p>{backendMessage}</p>
      <main>
        <h2>Create a basket</h2>
        <form onSubmit={handleCreate}>
          <label htmlFor="basket-name">Basket name</label>
          <input
            id="basket-name"
            value={basketName}
            onChange={(event) =>
              setBasketName(event.target.value.replace(/[^a-zA-Z0-9]/g, '').slice(0, 50))
            }
            required
            maxLength={50}
          />
          <button type="submit" disabled={isCreating}>
            {isCreating ? 'Creating...' : 'Create basket'}
          </button>
        </form>
        {createError && <p role="alert">{createError}</p>}
        {createdBasket && (
          <section aria-label="Created basket">
            <h2>Basket created</h2>
            <p>
              Webhook URL: <code>{createdBasket.webhook_url}</code>
            </p>
            <p>Expires: {createdBasket.expires_at}</p>
          </section>
        )}
        {storedBaskets.length > 0 && (
          <section aria-label="Saved baskets">
            <h2>Saved baskets</h2>
            <ul>
              {storedBaskets.map((basket) => (
                <li key={basket.name}>{basket.name}</li>
              ))}
            </ul>
          </section>
        )}
      </main>
      <button onClick={() => setCount((current) => current + 1)}>
        count is {count}
      </button>
    </>
  )
}

export default App
