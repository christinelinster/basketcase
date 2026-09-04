import { useEffect, useState } from 'react'

const LS_BASKET_PREFIX = 'basket_'

function socketUrl(name: string): string | null {
  const token = window.localStorage.getItem(`${LS_BASKET_PREFIX}${name}`)
  if (token === null) return null

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

  return `${protocol}//${window.location.host}/ws/${name}?token=${token}`
}

export default function useBasketRefresh(
  name: string | undefined,
  onRefresh: (name: string) => void,
): boolean | null {
  const [isLive, setIsLive] = useState<boolean | null>(null)

  useEffect(() => {
    setIsLive(null)

    if (name === undefined) return

    const url = socketUrl(name)
    if (url === null) return

    const socket = new WebSocket(url)

    socket.onopen = () => setIsLive(true)
    socket.onclose = () => setIsLive(false)

    socket.onmessage = (event: MessageEvent) => {
      let message: { event?: string }

      try {
        message = JSON.parse(event.data)
      } catch {
        return
      }

      if (message.event === 'refresh') onRefresh(name)
    }

    return () => {
      socket.onopen = null
      socket.onclose = null
      socket.onmessage = null
      socket.close()
    }
  }, [name])

  return isLive
}
