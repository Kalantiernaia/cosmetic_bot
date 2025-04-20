import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришлите мне фото состава косметики, и я его проанализирую."
    )

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"tmp_{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: здесь вставьте ваш OCR + анализ через OpenAI
    await update.message.reply_text("Готово, скоро пришлю вам отчёт по составу.")
    os.remove(path)

def main():
    # Читаем из переменных окружения
    TOKEN = os.environ["TG_TOKEN"]
    APP_URL = os.environ["RAILWAY_URL"]  # например "https://cosmeticbot-production.up.railway.app"
    PORT = int(os.environ.get("PORT", "5000"))

    # Собираем приложение
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # Регистрируем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Запускаем webhook‑сервер
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{APP_URL}/hook/{TOKEN}",
    )

if __name__ == "__main__":
    main()
