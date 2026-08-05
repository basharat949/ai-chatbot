from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


@lru_cache
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )