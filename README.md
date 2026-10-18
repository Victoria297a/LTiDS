# LTiDS

## Stock analysis assistant

The stock assistant uses a Vite/React chat frontend and a FastAPI/LangChain
backend. The agent can retrieve current prices, historical prices, balance
sheets, and recent news through `yfinance`.

The model is Google Gemini on the free tier of Google AI Studio (default
`gemini-3.8-flash`, override with `GEMINI_MODEL`). No billing account is
needed; free-tier requests are rate limited and Google may use them to improve
its products.

1. Create a free key at https://aistudio.google.com/apikey, copy
   `backend_ai/.env.example` to `backend_ai/.env`, and set `GEMINI_API_KEY`.
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
## Telegram bot

`backend_ai/telegram_bot.py` exposes the same agent and tools as a Telegram
bot, using the same free Gemini model.

1. In Telegram, message [@BotFather](https://t.me/BotFather), send `/newbot`,
   and copy the token it gives you.
2. In `backend_ai/.env`, set `TELEGRAM_BOT_TOKEN` to that token (and
   `GEMINI_API_KEY` as above).
3. Start the bot (it runs independently of the web backend):

   ```powershell
   cd backend_ai
   uv run telegram_bot.py
   ```

Open your bot in Telegram, send `/start`, then ask about a ticker. Each chat
keeps its own conversation memory until the bot restarts.
