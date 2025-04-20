import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Логируем, чтобы видеть ошибки при старте
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне фото косметического состава, и я его проанализирую."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"/tmp/{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: здесь сделаем OCR + OpenAI‑анализ
    await update.message.reply_text("Готово, скоро отправлю отчёт по составу.")
    # os.remove(path)


def main():
    # Прочитаем переменные окружения, которые настроены в Railway
    TOKEN = os.environ["TG_TOKEN"]
    RAILWAY_URL = os.environ["RAILWAY_URL"]  # например "https://cosmeticbot-production.up.railway.app"
    PORT = int(os.environ.get("PORT", 5000))

    # Собираем приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # Подключаем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Формируем URL вебхука
    webhook_path = f"/hook/{TOKEN}"
    webhook_url = f"{RAILWAY_URL}{webhook_path}"
    logger.info("Устанавливаем webhook на %s", webhook_url)

    # Этот метод сам выставит setWebhook и запустит HTTP‑сервер
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
