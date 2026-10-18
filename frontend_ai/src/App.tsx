import { C1Chat, ThemeProvider } from '@thesysai/genui-sdk'
import '@crayonai/react-ui/styles/index.css'

import './App.css'

function App() {
  return (
    <div className="app-container">
      <ThemeProvider mode="dark">
        <header className="app-header">
          <div>
            <p className="eyebrow">AI MARKET INTELLIGENCE</p>
            <h1>Stock Analysis Assistant</h1>
          </div>
          <span className="status-pill">
            <span className="status-dot" />
            Live data tools
          </span>
        </header>
        <main className="chat-shell">
          <C1Chat apiUrl="/api/chat" />
        </main>
      </ThemeProvider>
    </div>
  )
}

export default App
