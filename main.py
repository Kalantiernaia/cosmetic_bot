import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# Включаем логгирование, чтобы можно было видеть HTTP‑запросы и ошибки
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне фото косметического состава, я его проанализирую."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"/tmp/{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: здесь ваш OCR + анализ через OpenAI
    await update.message.reply_text("Готово, скоро пришлю отчёт по составу.")
    # os.remove(path)


async def main():
    # Telegram‑токен и URL вашего Railway‑сервиса читаем из переменных окружения
    TOKEN = os.environ["TG_TOKEN"]
    RAILWAY_URL = os.environ["RAILWAY_URL"]  # без конца «/»
    PORT = int(os.environ.get("PORT", 5000))

    # Создаём приложение и регистрируем хендлеры
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Устанавливаем webhook в Telegram
    webhook_url = f"{RAILWAY_URL}/hook/{TOKEN}"
    await app.bot.set_webhook(webhook_url)
    logger.info("Webhook set to %s", webhook_url)

    # Запускаем встроенный HTTP‑сервер, который будет принимать POST запросы от Telegram
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_path=f"/hook/{TOKEN}",
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
