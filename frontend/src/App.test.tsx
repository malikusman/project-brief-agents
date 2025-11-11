import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders chat and brief panels', () => {
    render(<App />)
    expect(screen.getByText(/Project Brief Agents/i)).toBeInTheDocument()
    expect(
      screen.getByText(/Submit project details to generate a structured brief/i)
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Reset session/i })).toBeInTheDocument()
  })
})
