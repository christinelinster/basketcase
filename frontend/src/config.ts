//   - you'll need to set BASKETCASE_URL in the frontend/.env 
//      - include the https in env, so "https://basketcase.com"
//   - Trailing slashes are stripped before the basket name is appended.
//   - When it is not set, links fall back to the origin the app is served
const configured = import.meta.env.BASKETCASE_URL?.trim()
const baseUrl = (configured || 'localhost:8000').replace(/\/+$/, '')

export const BASKETCASE_URL = baseUrl

/** Full absolute collection URL for a basket, e.g. "https://basketcase.com/<name>". */
export function basketUrl(name: string): string {
  return `${BASKETCASE_URL}/${name}`
}
