# LTiDS

## Stock analysis assistant

The stock assistant uses a Vite/React chat frontend and a FastAPI/LangChain
backend. The agent can retrieve current prices, historical prices, balance
sheets, and recent news through `yfinance`.

1. Copy `backend_ai/.env.example` to `backend_ai/.env` and add your API key.
2. Start the backend:

   ```powershell
   cd backend_ai
   uv run aiagent.py
   ```

3. In a second terminal, start the frontend:

   ```powershell
   cd frontend_ai
   npm run dev
   ```

Open `http://localhost:3000`. The Vite proxy forwards `/api` requests to the
FastAPI server on port `8888`.