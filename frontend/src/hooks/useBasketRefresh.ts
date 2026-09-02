import useWebSocket, { ReadyState } from 'react-use-websocket'

// How App.tsx stores basket ownership: localStorage { basket_<name>: <token> }
const LS_BASKET_PREFIX = 'basket_'

/**
 * Keep a WebSocket open to /ws/{name} and call `onRefresh` whenever the server
 * says that basket changed.
 *
 * The server's message is only a signal - it carries no request data - so the
 * page reacts by re-fetching through the normal API, exactly as the Refresh
 * button does.
 *
 * Does nothing when the basket has no token stored locally, which is the case
 * for someone opening a shared link.
 *
 * Returns the connection state so the page can show whether updates are live.
 * There is no automatic reconnect: once the socket drops it stays dropped, and
 * the user reloads the page to start a new one.
 */
export default function useBasketRefresh(
  name: string | undefined,
  onRefresh: () => void,
): ReadyState {
  const token =
    name === undefined ? null : window.localStorage.getItem(`${LS_BASKET_PREFIX}${name}`)

  // Built from the page's own origin, so it works in dev through the Vite proxy
  // and in production without changes. The token goes in the query string
  // because a browser cannot set headers on a WebSocket connection.
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const url =
    name !== undefined && token !== null
      ? `${protocol}//${window.location.host}/ws/${name}?token=${token}`
      : null

  const { readyState } = useWebSocket(
    url,
    {
      onMessage: (event: MessageEvent) => {
        if (JSON.parse(event.data).event === 'refresh') onRefresh()
      },
    },
    url !== null,
  )

  return readyState
}
