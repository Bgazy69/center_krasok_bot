import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_PATH = ROOT_DIR / "data" / "company_knowledge.md"


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    groq_api_key: str
    groq_model: str
    max_history_messages: int
    max_reply_chars: int


def get_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    api_key = (
        os.getenv("GROQ_API_KEY", "").strip()
        or os.getenv("GROK_API_KEY", "").strip()
    )

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")
    if not api_key:
        raise ValueError("GROQ_API_KEY не задан в .env")

    model = (
        os.getenv("GROQ_MODEL", "").strip()
        or os.getenv("GROK_MODEL", "").strip()
        or "llama-3.3-70b-versatile"
    )

    return Settings(
        telegram_token=token,
        groq_api_key=api_key,
        groq_model=model,
        max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "10")),
        max_reply_chars=int(os.getenv("MAX_REPLY_CHARS", "3500")),
    )
