import type { ConversationTurn } from '../types/brief'

interface ConversationHistoryProps {
  conversation: ConversationTurn[]
}

export function ConversationHistory({ conversation }: ConversationHistoryProps) {
  if (!conversation.length) {
    return (
      <div className="conversation-empty">
        Share your project notes and questions will appear here.
      </div>
    )
  }

  return (
    <ul className="conversation-history">
      {conversation.map((turn, index) => (
        <li key={index} data-role={turn.role}>
          <span className="role">{turn.role === 'user' ? 'You' : 'Assistant'}</span>
          <p>{turn.content}</p>
        </li>
      ))}
    </ul>
  )
}
