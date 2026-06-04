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
    gemini_api_key: str
    gemini_model: str
    max_history_messages: int
    max_reply_chars: int


def get_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не задан в .env")

    return Settings(
        telegram_token=token,
        gemini_api_key=api_key,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
        max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "10")),
        max_reply_chars=int(os.getenv("MAX_REPLY_CHARS", "3500")),
    )
