import type { FormEvent } from 'react'
import { useState } from 'react'
import type { ConversationTurn } from '../types/brief'

interface ChatComposerProps {
  onSend: (turn: ConversationTurn) => void
  disabled?: boolean
}

export function ChatComposer({ onSend, disabled }: ChatComposerProps) {
  const [value, setValue] = useState('')

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (!value.trim()) return
    onSend({ role: 'user', content: value.trim() })
    setValue('')
  }

  return (
    <form className="chat-composer" onSubmit={handleSubmit}>
      <textarea
        placeholder="Describe your project goals, constraints, and success metrics..."
        value={value}
        onChange={(event) => setValue(event.target.value)}
        rows={4}
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  )
}
