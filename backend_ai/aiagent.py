from dotenv import load_dotenv
from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

import yfinance as yf

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ],
    allow_credentials=True,
    allow_methods=['POST'],
    allow_headers=['*'],
)

model = ChatOpenAI(
    model='c1/openai/gpt-5/v-20250930',
    base_url='https://api.thesys.dev/v1/embed/',
)

checkpointer = InMemorySaver()


@tool('get_stock_price', description='A function that returns the current stock price based on a ticker symbol.')
def get_stock_price(ticker: str):
    stock = yf.Ticker(ticker)
    history = stock.history(period='5d')
    if history.empty:
        return f'No price data found for {ticker.upper()}.'
    return {'ticker': ticker.upper(), 'close': float(history['Close'].iloc[-1])}


@tool('get_historical_stock_price', description='A function that returns the current stock price over time based on a ticker symbol and a start and end date.')
def get_historical_stock_price(ticker: str, start_date: str, end_date: str):
    stock = yf.Ticker(ticker)
    history = stock.history(start=start_date, end=end_date)
    if history.empty:
        return f'No historical price data found for {ticker.upper()} in that date range.'
    return history[['Open', 'High', 'Low', 'Close', 'Volume']].round(2).to_json(date_format='iso')


@tool('get_balance_sheet', description='A function that returns the balance sheet based on a ticker symbol.')
def get_balance_sheet(ticker: str):
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet
    if balance_sheet.empty:
        return f'No balance sheet data found for {ticker.upper()}.'
    return balance_sheet.to_json(date_format='iso')


@tool('get_stock_news', description='A function that returns news based on a ticker symbol.')
def get_stock_news(ticker: str):
    stock = yf.Ticker(ticker)
    news = stock.news
    if not news:
        return f'No recent news found for {ticker.upper()}.'
    return news



agent = create_agent(
    model = model,
    checkpointer = checkpointer,
    tools = [get_stock_price, get_historical_stock_price, get_balance_sheet, get_stock_news]
)


class PromptObject(BaseModel):
    content: str
    id: str
    role: str


class RequestObject(BaseModel):
    prompt: PromptObject
    threadId: str
    responseId: str


@app.post('/api/chat')
async def chat(request: RequestObject):
    config = {'configurable': {'thread_id': request.threadId}}

    def generate():
        for token, _ in agent.stream(
            {'messages': [
                SystemMessage(content='You are a stock analysis assistant. Use the available tools to answer with current prices, historical prices, balance sheet data, and recent news. Clearly distinguish retrieved facts from your interpretation.'),
                HumanMessage(content=request.prompt.content),
            ]},
            stream_mode='messages',
            config=config,
        ):
            content = token.content
            if isinstance(content, str):
                yield content
            elif content:
                yield ''.join(
                    block.get('text', '')
                    for block in content
                    if isinstance(block, dict)
                )

    return StreamingResponse(generate(), media_type='text/event-stream',
                             headers={
                                 'Cache-Control': 'no-cache, no-transform',
                                 'Connection': 'keep-alive',
                             })

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)