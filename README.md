# AI Telegram Assistant — Центр Красок #1

MVP Telegram-бот с AI-ассистентом, который отвечает на вопросы о компании **«Центр Красок #1»** (Казахстан) на основе собранной базы знаний.

## Возможности

- Обычный чат **без команд и меню**
- Ответы на основе файла `data/company_knowledge.md` (RAG через system prompt)
- **Контекст диалога** — последние N сообщений на пользователя
- **Защита от галлюцинаций**: низкая temperature, строгий system prompt, отказ от off-topic
- Подсказка связаться с менеджером, если данных нет в базе

## Структура проекта

```
telegrambot2/
├── data/
│   └── company_knowledge.md   # структурированная информация о компании
├── src/
│   ├── bot.py                 # Telegram handlers
│   ├── ai_service.py          # Groq API + промпт
│   ├── conversation.py        # история диалога
│   ├── knowledge.py           # загрузка базы
│   └── config.py
├── main.py
├── requirements.txt
└── .env.example
```

## Быстрый старт

### 1. Python 3.11+

```bash
cd d:\telegrambot2
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка

```bash
copy .env.example .env
```

Заполните в `.env`:

| Переменная | Описание |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | Токен от [@BotFather](https://t.me/BotFather) |
| `GROQ_API_KEY` | Ключ [Groq Console](https://console.groq.com/) (префикс `gsk_`) |
| `GROQ_MODEL` | Например `llama-3.3-70b-versatile`, `llama-3.1-8b-instant` |

### 3. Запуск

```bash
python main.py
```

Напишите боту в Telegram, например:

- «Чем занимается компания?»
- «Где салон в Алматы?»
- «Какие бренды продаёте?»
- «Есть доставка?»

## Источники данных

Информация собрана с:

- https://centr-krasok.kz/
- https://centr-krasok.kz/about/
- https://centr-krasok.kz/about/contacts/
- https://center-krasok.kz/ (landing ABIS)
- Instagram: @centr_krasok

## Технологии

- Python 3.11+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Groq API](https://console.groq.com/docs/quickstart)

## Для проверяющего (задание)

| Требование | Реализация |
|------------|------------|
| Сбор и структурирование информации | `data/company_knowledge.md` |
| Бот без команд | только `MessageHandler` на текст |
| AI API | Groq chat completions (OpenAI-совместимый) |
| Ограничение галлюцинаций | база в system prompt + temperature 0.3 + правила |
| Контекст диалога | `ConversationStore` |
| Защита от некорректных ответов | off-topic filter + fallback при ошибках |
