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

# Логирование HTTP‑запросов и внутренних ошибок
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне фото косметического состава, я сделаю анализ."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"/tmp/{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: здесь OCR + OpenAI‑анализ
    await update.message.reply_text("Готово, скоро вышлю отчёт по составу.")
    # os.remove(path)


def main():
    TOKEN = os.environ["TG_TOKEN"]
    RAILWAY_URL = os.environ["RAILWAY_URL"]  # пример: https://cosmeticbot-production.up.railway.app
    PORT = int(os.environ.get("PORT", 5000))

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # Регистрируем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Устанавливаем webhook в Telegram
    webhook_url = f"{RAILWAY_URL}/hook/{TOKEN}"
    app.bot.set_webhook(webhook_url)
    logger.info("Webhook установлен на %s", webhook_url)

    # Запускаем HTTP‑сервер, который будет принимать POST от Telegram
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=f"/hook/{TOKEN}",     # <-- здесь раньше было webhook_path — теперь url_path
        drop_pending_updates=True,      # опционально, чтобы не накапливались старые апдейты
    )


if __name__ == "__main__":
    main()
