import os
import asyncio

from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# Берём все секреты и URL из переменных окружения
TG_TOKEN = os.environ["TG_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
RAILWAY_URL = os.environ["RAILWAY_URL"]
PORT = int(os.environ.get("PORT", 5000))

# Строим сам бот и Flask‑приложение
bot_app = ApplicationBuilder().token(TG_TOKEN).build()
app = Flask(__name__)


# === Обработчики команд и сообщений ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне фотографию косметики — я попробую проанализировать состав.")


bot_app.add_handler(CommandHandler("start", start))


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"tmp_{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: отправить в OpenAI, распарсить состав
    await update.message.reply_text("Готово, скоро пришлю вам отчёт по составу.")
    os.remove(path)


bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))


# === Webhook для Telegram ===
@app.route(f"/hook/{TG_TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK"


# Небольшая «лазига»: чтобы Railway «увидел» приложение как HTTP‑сервис,
# добавим простую корневую страницу
@app.route("/")
def index():
    return "Bot is running!"


if __name__ == "__main__":
    # Устанавливаем webhook у Telegram
    webhook_url = f"{RAILWAY_URL}/hook/{TG_TOKEN}"
    asyncio.run(bot_app.bot.set_webhook(webhook_url))

    # Запускаем Flask
    app.run(host="0.0.0.0", port=PORT)
