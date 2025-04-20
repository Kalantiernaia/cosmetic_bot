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

# читаем из окружения
TOKEN       = os.environ["TG_TOKEN"]
RAILWAY_URL = os.environ["RAILWAY_URL"]  # например https://cosmeticbot-production.up.railway.app
# если PORT не задан вручную, возьмётся 5000
PORT = int(os.environ.get("PORT", 5000))

# включаем логирование
logging.basicConfig(
    format="%(asctime)s ‑ %(name)s ‑ %(levelname)s ‑ %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# создаём приложение
app = ApplicationBuilder().token(TOKEN).build()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот, который анализирует состав косметики. Пришли фото состава."
    )

# обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file  = await photo.get_file()
    path  = f"tmp/{photo.file_id}.jpg"
    await file.download_to_drive(path)
    await update.message.reply_text("Фото получено, скоро отчёт будет готов.")
    # тут вставишь OCR + OpenAI‑анализ

# регистрируем хендлеры
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    # формируем путь и полный URL
    hook_path   = f"/hook/{TOKEN}"
    webhook_url = RAILWAY_URL + hook_path
    logger.info(f"Запускаем на {PORT}, url_path={hook_path}, webhook_url={webhook_url}")

    # запускаем встроенный веб‑сервер PTB
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=hook_path,
        webhook_url=webhook_url,
    )
