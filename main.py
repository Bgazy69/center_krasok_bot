import logging
import sys

from src.bot import build_application
from src.config import get_settings


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    try:
        settings = get_settings()
    except ValueError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        print("Скопируйте .env.example в .env и заполните переменные.", file=sys.stderr)
        sys.exit(1)

    app = build_application(settings)
    print("Бот «Центр Красок #1» запущен. Остановка: Ctrl+C")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
