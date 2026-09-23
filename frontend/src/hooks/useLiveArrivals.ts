import { useEffect, useRef, useState } from 'react'
import type { BasketRequest } from '../types/basket'

const HIGHLIGHT_MS = 3000

export default function useLiveArrivals(name: string | undefined) {
  const knownIds = useRef<Set<string> | null>(null)
  const timers = useRef(new Map<string, number>())
  const [highlighted, setHighlighted] = useState<Set<string>>(new Set())

  // Arrivals the user scrolled past; the page shows them as "N new requests".
  const scrolledAway = useRef(false)
  const pillIds = useRef<string[]>([])
  const [pillCount, setPillCount] = useState(0)

  // Start over on basket switch; also clears pending timers on unmount.
  useEffect(() => {
    const pending = timers.current
    return () => {
      knownIds.current = null
      for (const timer of pending.values()) clearTimeout(timer)
      pending.clear()
      setHighlighted(new Set())
      pillIds.current = []
      setPillCount(0)
    }
  }, [name])

  // Whichever response lands first (initial load or a socket refresh) is the baseline.
  const setBaseline = (requests: BasketRequest[]) => {
    if (knownIds.current !== null) return
    knownIds.current = new Set(requests.map((req) => req.id))
  }

  const highlight = (ids: string[]) => {
    setHighlighted((prev) => new Set([...prev, ...ids]))

    for (const id of ids) {
      clearTimeout(timers.current.get(id))
      timers.current.set(id, setTimeout(() => {
        timers.current.delete(id)
        setHighlighted((prev) => {
          const next = new Set(prev)
          next.delete(id)
          return next
        })
      }, HIGHLIGHT_MS))
    }
  }

  const recordRefresh = (requests: BasketRequest[]) => {
    const known = knownIds.current
    if (known === null) return setBaseline(requests)

    const arrivals = requests.map((req) => req.id).filter((id) => !known.has(id))
    for (const id of arrivals) known.add(id)
    if (arrivals.length === 0) return

    highlight(arrivals)
    if (scrolledAway.current) {
      pillIds.current.push(...arrivals)
      setPillCount(pillIds.current.length)
    }
  }

  // Coming back to the top clears the pill and re-tints what it was counting,
  // since their first tint most likely faded while off-screen.
  const setScrolledAway = (away: boolean) => {
    if (away === scrolledAway.current) return
    scrolledAway.current = away
    if (away || pillIds.current.length === 0) return

    highlight(pillIds.current)
    pillIds.current = []
    setPillCount(0)
  }

  return { highlighted, pillCount, setBaseline, recordRefresh, setScrolledAway }
}
