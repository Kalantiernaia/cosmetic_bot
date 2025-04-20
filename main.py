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

# забираем всё из окружения
TOKEN       = os.environ["TG_TOKEN"]
RAILWAY_URL = os.environ["RAILWAY_URL"]  # например https://cosmeticbot-production.up.railway.app
PORT        = int(os.environ.get("PORT", 5000))

# включаем логирование, чтобы видеть что происходит
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# создаём приложение
app = ApplicationBuilder().token(TOKEN).build()

# обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот, который анализирует состав косметики. Пришли фото состава."
    )

# обработчик фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file  = await photo.get_file()
    path  = f"tmp/{photo.file_id}.jpg"
    await file.download_to_drive(path)
    await update.message.reply_text("Фото получено, скоро пришлю отчёт…")
    # тут можно подключить OCR + OpenAI

# регистрируем их
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    # удаляем старый вебхук (на случай деплоя повторно)
    app.bot.delete_webhook()

    # формируем URL нашего хука
    hook_path   = f"/hook/{TOKEN}"
    webhook_url = RAILWAY_URL + hook_path

    # вешаем вебхук
    app.bot.set_webhook(webhook_url)
    logging.info(f"Webhook установлен на {webhook_url}")

    # запускаем встроенный сервер
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_path=hook_path,
        # таймауты и опции можно не трогать
    )
