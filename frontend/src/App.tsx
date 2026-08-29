import { useEffect, useState } from 'react'
import './App.css'

type HelloResponse = { message: string }

function App() {
  const [count, setCount] = useState(0)
  const [backendMessage, setBackendMessage] = useState('Loading...')

  useEffect(() => {
    fetch('/api/baskets/hello')
      .then((response) => {
        if (!response.ok) throw new Error(`Backend returned ${response.status}`)
        return response.json() as Promise<HelloResponse>
      })
      .then(({ message }) => setBackendMessage(message))
      .catch(() => setBackendMessage('Backend unavailable'))
  }, [])

  return (
    <>
      <h1>Vite + React</h1>
      <p>{backendMessage}</p>
      <button onClick={() => setCount((current) => current + 1)}>
        count is {count}
      </button>
    </>
  )
}

export default App
