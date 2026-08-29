import { test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App.tsx'

test('increments the counter', async () => {
  render(<App />)

  const user = userEvent.setup()
  const button = screen.getByRole('button', { name: 'count is 0' })

  await user.click(button)

  expect(screen.getByRole('button', { name: 'count is 1' })).toBeDefined()
})
