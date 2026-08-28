import { test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App.tsx'

test('renders content', async () => {
  render(<App />)


  const user = userEvent.setup()
  const button = screen.getByText('Count is 0')
  await user.click(button)
  
  expect(screen.getByText('Count is 1')).toBeDefined()
})