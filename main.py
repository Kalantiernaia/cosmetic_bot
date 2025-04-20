import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ExtBot,
    CommandHandler,
    MessageHandler,
    filters,
)

# --- 1. Берём токен и URL из переменных окружения Railway ---
TOKEN      = os.environ["TG_TOKEN"]
RAILWAY_URL = os.environ["RAILWAY_URL"]  # без слеша на конце

# --- 2. Создаём Flask-приложение и Telegram-бота ---
app     = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# --- 3. Команда /start ---
async def start(update: Update, context):
    await update.message.reply_text("Привет! Пришлите мне фото состава косметики.")
bot_app.add_handler(CommandHandler("start", start))

# --- 4. Обработчик фото ---
async def handle_photo(update: Update, context):
    photo = update.message.photo[-1]
    file  = await photo.get_file()
    path  = f"tmp_{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: OCR + анализ через OpenAI
    await update.message.reply_text("Готово, скоро пришлю вам отчёт по составу.")
    os.remove(path)
bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# --- 5. Маршрут для Webhook ---
@app.route(f"/hook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK"

# --- 6. Главная точка входа ---
if __name__ == "__main__":
    # Собираем URL для установки webhook
    webhook_url = f"{RAILWAY_URL}/hook/{TOKEN}"

    # Устанавливаем webhook асинхронно перед стартом Flask
    asyncio.run(bot_app.bot.set_webhook(webhook_url))

    # Запускаем Flask, порт берем из среды Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
