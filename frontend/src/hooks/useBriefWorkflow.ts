import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { apiConfig } from '../config/api'
import type {
  BriefPayload,
  BriefRunRequest,
  ConversationTurn,
  DocumentReference,
} from '../types/brief'

const ENDPOINT = `${apiConfig.baseUrl}/briefs/run`

export function useBriefWorkflow() {
  const [conversation, setConversation] = useState<ConversationTurn[]>([])
  const [documents, setDocuments] = useState<DocumentReference[]>([])
  const [threadId, setThreadId] = useState<string | undefined>(undefined)

  const mutation = useMutation<BriefPayload, Error, BriefRunRequest>({
    mutationFn: async (payload) => {
      const requestBody: BriefRunRequest = {
        conversation: payload.conversation ?? conversation,
        documents: payload.documents ?? documents,
        prompt: payload.prompt,
        thread_id: payload.thread_id ?? threadId,
      }

      const response = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      })

      if (!response.ok) {
        throw new Error(`Workflow request failed: ${response.status}`)
      }
      return (await response.json()) as BriefPayload
    },
    onSuccess: (data) => {
      setThreadId(data.thread_id)
      if (data.follow_up_questions.length) {
        const message = `I still need a bit more detail:\n${data.follow_up_questions
          .map((item, index) => `${index + 1}. ${item}`)
          .join('\n')}`
        setConversation((prev) => [
          ...prev,
          { role: 'assistant', content: message },
        ])
      } else {
        setConversation((prev) => [
          ...prev,
          {
            role: 'assistant',
            content:
              'Wonderful! I have enough context to keep refining the brief. Feel free to iterate further or request changes.',
          },
        ])
      }
    },
  })

  const appendMessage = (turn: ConversationTurn) => {
    setConversation((prev) => [...prev, turn])
  }

  const addDocument = (doc: DocumentReference) => {
    setDocuments((prev) => [...prev, doc])
  }

  const reset = () => {
    setConversation([])
    setDocuments([])
    setThreadId(undefined)
    mutation.reset()
  }

  return {
    conversation,
    documents,
    addDocument,
    appendMessage,
    runWorkflow: mutation.mutate,
    isLoading: mutation.isPending,
    data: mutation.data,
    error: mutation.error,
    reset,
    threadId,
  }
}
