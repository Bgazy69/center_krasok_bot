import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.ai_service import AIService
from src.config import Settings
from src.conversation import ConversationStore

logger = logging.getLogger(__name__)

WELCOME = (
    "Здравствуйте! Я AI-ассистент «Центр Красок #1» 🎨\n\n"
    "Спросите меня о компании: услуги, адреса салонов в Алматы и Астане, "
    "бренды, колеровку, доставку и ассортимент.\n\n"
    "Просто напишите вопрос — команды не нужны."
)

THINKING = "Секунду, ищу информацию…"


def build_application(settings: Settings) -> Application:
    ai = AIService(settings)
    conversations = ConversationStore(max_messages=settings.max_history_messages)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_user or not update.message:
            return

        await update.message.reply_text(WELCOME)
        conversations.add(update.effective_user.id, "assistant", WELCOME)

    async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_user or not update.message:
            return

        user = update.effective_user
        text = (update.message.text or "").strip()

        if not text:
            await update.message.reply_text(
                "Напишите текстовый вопрос о «Центре Красок #1»."
            )
            return

        user_id = user.id
        history = conversations.get_history(user_id)

        # Первое сообщение — короткое приветствие + ответ
        if not history and text.lower() in {"привет", "здравствуйте", "hello", "hi", "start"}:
            await update.message.reply_text(WELCOME)
            conversations.add(user_id, "assistant", WELCOME)
            return

        status = await update.message.reply_text(THINKING)
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

        try:
            reply = await ai.generate_reply(text, history)
        except Exception:
            logger.exception("AI request failed for user %s", user_id)
            reply = (
                "Сейчас не могу обработать запрос. "
                "Попробуйте позже или позвоните: +7 778 061 50 00."
            )

        conversations.add(user_id, "user", text)
        conversations.add(user_id, "assistant", reply)

        try:
            await status.edit_text(reply)
        except Exception:
            await update.message.reply_text(reply)

    app = (
        Application.builder()
        .token(settings.telegram_token)
        .build()
    )

    app.bot_data["ai"] = ai
    app.bot_data["conversations"] = conversations
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    return app
