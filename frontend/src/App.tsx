import './App.css'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ChatComposer } from './components/ChatComposer'
import { ConversationHistory } from './components/ConversationHistory'
import { BriefPreview } from './components/BriefPreview'
import { UploadsPlaceholder } from './components/UploadsPlaceholder'
import { useBriefWorkflow } from './hooks/useBriefWorkflow'
import type { ConversationTurn } from './types/brief'

const queryClient = new QueryClient()

function AppContent() {
  const {
    conversation,
    documents,
    addDocument,
    appendMessage,
    runWorkflow,
    isLoading,
    data,
    error,
    reset,
  } = useBriefWorkflow()

  const handleSend = (turn: ConversationTurn) => {
    const nextConversation = [...conversation, turn]
    appendMessage(turn)
    runWorkflow({ conversation: nextConversation })
  }

  const handleReset = () => {
    reset()
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <h1>Project Brief Agents</h1>
          <p>Capture project context and generate a Lovable-style brief.</p>
        </div>
        <button type="button" onClick={handleReset} disabled={isLoading}>
          Reset session
        </button>
      </header>

      <section className="layout">
        <div className="panel">
          <ConversationHistory conversation={conversation} />
          <UploadsPlaceholder
            documents={documents}
            onAdd={addDocument}
          />
          <ChatComposer onSend={handleSend} disabled={isLoading} />
          {error && <p className="error">{error.message}</p>}
          {isLoading && <p className="loading">Generating brief...</p>}
        </div>

        <div className="panel">
          {data ? (
            <BriefPreview payload={data} />
          ) : (
            <div className="placeholder">
              Submit project details to generate a structured brief.
            </div>
          )}
        </div>
      </section>
    </main>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}

export default App
