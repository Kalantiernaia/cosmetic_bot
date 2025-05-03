import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Включаем логирование, чтобы было видно, что происходит внутри
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text(
        "Привет! Я бот по безопасности косметики.\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — инструкции по использованию"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text(
        "Чтобы использовать бота, просто отправьте ему /start."
    )


def main() -> None:
    """Точка входа — создаём приложение и запускаем polling."""
    token = os.getenv("TG_TOKEN")
    if not token:
        logger.error("Переменная TG_TOKEN не задана в окружении!")
        return

    app = (
        ApplicationBuilder()
        .token(token)
        .build()
    )

    # Регистрируем командные обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Запускаем бота в режиме polling
    logger.info("Запускаем бота в режиме polling…")
    app.run_polling()


if __name__ == "__main__":
    main()
