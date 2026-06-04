import logging

import httpx

from src.config import Settings
from src.conversation import ChatMessage
from src.knowledge import load_knowledge

logger = logging.getLogger(__name__)

# Groq: OpenAI-совместимый API (ключи начинаются с gsk_)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT_TEMPLATE = """Ты — дружелюбный AI-ассистент компании «Центр Красок #1» (Казахстан, centr-krasok.kz).
Ты отвечаешь в Telegram в формате обычного чата: кратко, по делу, на русском языке.

СТРОГИЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе блока «БАЗА ЗНАНИЙ» ниже. Не придумывай факты, цены, адреса, вакансии и контакты.
2. Если в базе нет ответа — скажи честно: «В моих данных этой информации нет» и предложи позвонить +7 778 061 50 00 или написать info@centr-krasok.kz.
3. Не путай компанию с российским «Центр Красок» (centerkrasok.ru) — это другая организация.
4. На вопросы не о компании (погода, программирование, политика и т.д.) — вежливо откажи и предложи спросить о «Центре Красок #1».
5. Не давай медицинских, юридических и опасных советов по ЛКМ — только общую информацию из базы; по техническим деталям — к специалистам салона.
6. Не выдумывай точные цены товаров — направляй на сайт centr-krasok.kz или к менеджеру.
7. Используй эмодзи умеренно (0–2 на ответ).

БАЗА ЗНАНИЙ:
{knowledge}
"""


OFF_TOPIC_HINTS = (
    "погод",
    "рецепт",
    "код ",
    "python",
    "javascript",
    "политик",
    "крипт",
    "ставк",
    "футбол",
)


def _build_system_prompt() -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(knowledge=load_knowledge())


def looks_off_topic(text: str) -> bool:
    lower = text.lower().strip()
    if len(lower) < 3:
        return False
    company_hints = (
        "краск",
        "центр",
        "dulux",
        "marshall",
        "алмат",
        "астан",
        "достав",
        "колер",
        "магазин",
        "салон",
        "бренд",
        "лак",
        "грунт",
        "штукатур",
        "офис",
        "адрес",
        "телефон",
        "ваканс",
        "работ",
        "компани",
        "услуг",
        "продукт",
        "клиент",
        "технолог",
        "abis",
        "armada",
        "привет",
        "здравств",
        "спасиб",
        "помог",
    )
    if any(h in lower for h in company_hints):
        return False
    return any(h in lower for h in OFF_TOPIC_HINTS)


class AIService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._system_prompt = _build_system_prompt()
        self._client = httpx.AsyncClient(timeout=60.0)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def generate_reply(
        self,
        user_message: str,
        history: list[ChatMessage],
    ) -> str:
        if looks_off_topic(user_message):
            return (
                "Я помогаю только с вопросами о «Центре Красок #1»: "
                "услуги, адреса, бренды, доставка, колеровка и т.д. "
                "Спросите, например: «Где салон в Алматы?» или «Какие бренды есть?»"
            )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": self._system_prompt},
        ]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self._settings.groq_model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 800,
        }

        response = await self._client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {self._settings.groq_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if response.is_error:
            logger.error(
                "Groq API error %s: %s",
                response.status_code,
                response.text[:500],
            )
            response.raise_for_status()

        data = response.json()

        text = _extract_text(data)
        if not text:
            return (
                "Не удалось сформировать ответ. "
                "Позвоните менеджеру: +7 778 061 50 00."
            )

        if len(text) > self._settings.max_reply_chars:
            text = text[: self._settings.max_reply_chars - 3] + "..."

        return text


def _extract_text(data: dict) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""

    message = choices[0].get("message") or {}
    return (message.get("content") or "").strip()
