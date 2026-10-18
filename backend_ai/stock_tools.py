from langchain.tools import tool

import yfinance as yf


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


TOOLS = [get_stock_price, get_historical_stock_price, get_balance_sheet, get_stock_news]

SYSTEM_PROMPT = 'You are a stock analysis assistant. Use the available tools to answer with current prices, historical prices, balance sheet data, and recent news. Clearly distinguish retrieved facts from your interpretation.'
