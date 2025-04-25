import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Включаем логирование (полезно при отладке)
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text("Привет! Бот запущен и работает через webhook.")


def main() -> None:
    # Загружаем обязательные переменные окружения
    TOKEN = os.environ["TG_TOKEN"]
    RAILWAY_URL = os.environ.get("RAILWAY_URL")  # будет None при локальном запуске
    PORT = int(os.environ.get("PORT", "8000"))

    # Строим приложение
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # Регистрируем хендлеры
    app.add_handler(CommandHandler("start", start))

    if RAILWAY_URL:
        # --- ПРОДАКШЕН НА RAILWAY: запускаем webhook ---
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_path=f"/hook/{TOKEN}",
            webhook_url=f"{RAILWAY_URL}/hook/{TOKEN}",
        )
    else:
        # --- ЛОКАЛЬНАЯ ОТЛАДКА: запускаем long-polling ---
        app.run_polling()


if __name__ == "__main__":
    main()
