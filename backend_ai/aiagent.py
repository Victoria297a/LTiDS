from dotenv import load_dotenv
from pydantic import BaseModel

from html import escape

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from llm import create_model
from stock_tools import TOOLS, SYSTEM_PROMPT

load_dotenv()

logger = logging.getLogger('uvicorn.error')

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

model = create_model()

checkpointer = InMemorySaver()


agent = create_agent(
    model = model,
    checkpointer = checkpointer,
    tools = TOOLS,
    system_prompt = SYSTEM_PROMPT,
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
        # C1Chat parses an XML-like stream; <custommarkdown> renders plain Markdown,
        # so text from a regular (non-C1) model is wrapped in it and HTML-escaped.
        yield '<custommarkdown>'
        try:
            for token, _ in agent.stream(
                {'messages': [HumanMessage(content=request.prompt.content)]},
                stream_mode='messages',
                config=config,
            ):
                # Skip tool results; only stream the model's own answer
                if isinstance(token, AIMessage) and token.text:
                    yield escape(token.text, quote=False)
        except Exception as e:
            # Surface model errors (bad key, rate limit) in the chat instead of an empty reply
            logger.error('Model request failed: %r', e)
            yield escape(f'Error from the AI model: {getattr(e, "message", None) or e}', quote=False)
        yield '</custommarkdown>'

    return StreamingResponse(generate(), media_type='text/event-stream',
                             headers={
                                 'Cache-Control': 'no-cache, no-transform',
                                 'Connection': 'keep-alive',
                             })

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)