import './App.css'
import { apiConfig } from './config/api'

function App() {
  return (
    <main className="app-shell">
      <section className="intro">
        <h1>Project Brief Agents</h1>
        <p>
          This placeholder UI will be replaced by the dedicated frontend team. Until then,
          it demonstrates where the conversational intake and brief preview experiences
          will live.
        </p>
      </section>

      <section className="status">
        <h2>API Target</h2>
        <p>
          Requests will be routed to <code>{apiConfig.baseUrl}</code>.
        </p>
        <p>
          Ensure the backend service is reachable and update <code>VITE_API_BASE_URL</code>{' '}
          in <code>.env</code> as needed.
        </p>
      </section>
    </main>
  )
}

export default App
