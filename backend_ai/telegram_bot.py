from dotenv import load_dotenv

import logging
import os

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from llm import create_model
from stock_tools import TOOLS, SYSTEM_PROMPT

load_dotenv()

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.INFO)
# httpx logs every Telegram request URL, which contains the bot token
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger('telegram_bot')

telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not telegram_token:
    raise RuntimeError(
        'Missing TELEGRAM_BOT_TOKEN. Get one from @BotFather and add it to backend_ai/.env.'
    )

model = create_model()

agent = create_agent(
    model = model,
    checkpointer = InMemorySaver(),
    tools = TOOLS,
    system_prompt = SYSTEM_PROMPT + ' Reply in plain text without Markdown tables, since the answer is shown in Telegram.',
)

TELEGRAM_MESSAGE_LIMIT = 4096


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Hi! I am a stock analysis assistant. Ask me about a ticker, e.g. "How is NVDA doing?"'
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(ChatAction.TYPING)
    # One conversation memory per Telegram chat
    config = {'configurable': {'thread_id': str(update.effective_chat.id)}}

    try:
        result = await agent.ainvoke(
            {'messages': [HumanMessage(content=update.message.text)]},
            config=config,
        )
        answer = result['messages'][-1].text or 'Sorry, I could not produce an answer.'
    except Exception as e:
        logger.error('Agent request failed: %r', e)
        answer = f'Error from the AI model: {getattr(e, "message", None) or e}'

    for i in range(0, len(answer), TELEGRAM_MESSAGE_LIMIT):
        await update.message.reply_text(answer[i:i + TELEGRAM_MESSAGE_LIMIT])


if __name__ == '__main__':
    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    logger.info('Telegram bot is polling for messages')
    application.run_polling()
