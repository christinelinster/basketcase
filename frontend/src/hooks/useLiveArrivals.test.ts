import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import useLiveArrivals from './useLiveArrivals'
import type { BasketRequest } from '../types/basket'

function makeRequests(...ids: string[]): BasketRequest[] {
  return ids.map((id) => ({
    id,
    method: 'GET',
    path: '/',
    headers: {},
    query_params: {},
    body: null,
    received_at: '2026-09-01T12:00:00Z',
  }))
}

describe('useLiveArrivals', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  test('highlights nothing for the first population', () => {
    const { result } = renderHook(() => useLiveArrivals('demo'))

    act(() => result.current.setBaseline(makeRequests('a', 'b')))
    expect(result.current.highlighted.size).toBe(0)

    // A refresh that arrives before any load also only sets the baseline.
    const { result: raced } = renderHook(() => useLiveArrivals('demo'))
    act(() => raced.current.recordRefresh(makeRequests('a', 'b')))
    expect(raced.current.highlighted.size).toBe(0)
  })

  test('highlights a new id and clears it after 3 seconds', () => {
    const { result } = renderHook(() => useLiveArrivals('demo'))
    act(() => result.current.setBaseline(makeRequests('a')))

    act(() => result.current.recordRefresh(makeRequests('b', 'a')))
    expect([...result.current.highlighted]).toEqual(['b'])

    act(() => vi.advanceTimersByTime(2999))
    expect(result.current.highlighted.has('b')).toBe(true)

    act(() => vi.advanceTimersByTime(1))
    expect(result.current.highlighted.size).toBe(0)
  })

  test('clears staggered arrivals on their own timers', () => {
    const { result } = renderHook(() => useLiveArrivals('demo'))
    act(() => result.current.setBaseline(makeRequests('a')))

    act(() => result.current.recordRefresh(makeRequests('b', 'a')))
    act(() => vi.advanceTimersByTime(1000))
    act(() => result.current.recordRefresh(makeRequests('c', 'b', 'a')))
    expect(result.current.highlighted).toEqual(new Set(['b', 'c']))

    act(() => vi.advanceTimersByTime(2000))
    expect(result.current.highlighted).toEqual(new Set(['c']))

    act(() => vi.advanceTimersByTime(1000))
    expect(result.current.highlighted.size).toBe(0)
  })

  test('counts arrivals while scrolled away and re-tints them on return', () => {
    const { result } = renderHook(() => useLiveArrivals('demo'))
    act(() => result.current.setBaseline(makeRequests('a')))

    // Arrivals while the top is visible don't touch the pill.
    act(() => result.current.recordRefresh(makeRequests('b', 'a')))
    expect(result.current.pillCount).toBe(0)

    act(() => result.current.setScrolledAway(true))
    act(() => result.current.recordRefresh(makeRequests('c', 'b', 'a')))
    act(() => result.current.recordRefresh(makeRequests('d', 'c', 'b', 'a')))
    expect(result.current.pillCount).toBe(2)

    // Both tints fade while the user is still scrolled down.
    act(() => vi.advanceTimersByTime(3000))
    expect(result.current.highlighted.size).toBe(0)

    act(() => result.current.setScrolledAway(false))
    expect(result.current.pillCount).toBe(0)
    expect(result.current.highlighted).toEqual(new Set(['c', 'd']))

    act(() => vi.advanceTimersByTime(3000))
    expect(result.current.highlighted.size).toBe(0)
  })

  test('resets everything when the basket changes', () => {
    const { result, rerender } = renderHook(({ name }) => useLiveArrivals(name), {
      initialProps: { name: 'first' },
    })
    act(() => result.current.setBaseline(makeRequests('a')))
    act(() => result.current.setScrolledAway(true))
    act(() => result.current.recordRefresh(makeRequests('b', 'a')))
    expect(result.current.highlighted.has('b')).toBe(true)
    expect(result.current.pillCount).toBe(1)

    rerender({ name: 'second' })
    expect(result.current.highlighted.size).toBe(0)
    expect(result.current.pillCount).toBe(0)
    expect(vi.getTimerCount()).toBe(0) // the old basket's timer was cancelled

    // The new basket's first response is a fresh baseline, not a burst of arrivals.
    act(() => result.current.recordRefresh(makeRequests('x', 'y')))
    expect(result.current.highlighted.size).toBe(0)

    act(() => result.current.recordRefresh(makeRequests('z', 'x', 'y')))
    expect([...result.current.highlighted]).toEqual(['z'])
  })
})
