import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Включим простой логгер, чтобы видеть, что происходит
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = os.getenv("TG_TOKEN")
# Публичный URL вашего Railway-приложения, например "https://cosmeticbot-production.up.railway.app"
RAILWAY_URL = os.getenv("RAILWAY_URL")
# Порт, на котором Railway ожидает HTTP-сервер
PORT = int(os.getenv("PORT", "8443"))

# Путь для приёма вебхуков (должен совпадать в set_webhook и в run_webhook)
HOOK_PATH = f"/hook/{TOKEN}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text(
        "Привет! Я бот по безопасности косметики.\n\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — инструкции по использованию\n\n"
        "Чтобы использовать бота, просто отправьте /start."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text(
        "Этот бот ничего не умеет, кроме демонстрации работы вебхуков.\n"
        "Просто отправьте ему /start."
    )


def main() -> None:
    """Главная функция: настраиваем и запускаем вебхук-сервер."""
    # 1) Собираем приложение
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # 2) Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_command))

    # 3) Сброс старого вебхука и установка нового
    #    Без этого Telegram может продолжать слать на старый URL
    logger.info("Deleting old webhook (if any)…")
    app.bot.delete_webhook().result()

    full_hook_url = RAILWAY_URL + HOOK_PATH
    logger.info(f"Setting webhook to {full_hook_url} …")
    app.bot.set_webhook(url=full_hook_url).result()

    # 4) Запуск сервера для приёма вебхуков от Telegram
    #    Telegram будет слать POST-запросы на этот путь
    logger.info(
        f"Starting webhook listener on 0.0.0.0:{PORT}{HOOK_PATH}"
    )
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=HOOK_PATH,
        webhook_url=full_hook_url,
    )


if __name__ == "__main__":
    main()
