from dotenv import load_dotenv

import os

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def create_model():
    """Gemini via Google AI Studio's free tier (no billing account needed)."""
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        raise RuntimeError(
            'Missing GEMINI_API_KEY. Create a free key at https://aistudio.google.com/apikey '
            'and add it to backend_ai/.env.'
        )
    return ChatGoogleGenerativeAI(
        model=os.getenv('GEMINI_MODEL', 'gemini-3.8-flash'),
        google_api_key=gemini_api_key,
    )
