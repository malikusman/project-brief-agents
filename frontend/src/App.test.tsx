import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders placeholder content', () => {
    render(<App />)
    expect(screen.getByText(/Project Brief Agents/i)).toBeInTheDocument()
  })
})


