import os

from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Загружаем секреты из переменных окружения
TOKEN = os.getenv("TG_TOKEN")
RAILWAY_URL = os.getenv("RAILWAY_URL")
PORT = int(os.environ.get("PORT", 5000))

if TOKEN is None or RAILWAY_URL is None:
    raise RuntimeError("Не найдены TG_TOKEN или RAILWAY_URL в окружении")

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()


# ——— Пример простых хэндлеров ——————————————————

async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Я бот по анализу косметики. Пришли фото состава, и я распознаю текст."
    )

bot_app.add_handler(CommandHandler("start", start))


async def handle_photo(update: Update, context):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"tmp_{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: здесь OCR + отправка в OpenAI, ждите…
    await update.message.reply_text("Готово, скоро отчёт отправлю.")
    os.remove(path)

bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))


# ——— Эндпоинт для вебхука —————————————————————

@app.route(f"/hook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK"


# ——— Стартуем Flask + регистрируем вебхук ——————————

if __name__ == "__main__":
    # Регистрируем вебхук на Railway-домен
    webhook_url = f"https://{RAILWAY_URL}/hook/{TOKEN}"
    bot_app.bot.set_webhook(webhook_url)
    # Запускаем встроенный сервер Flask
    app.run(host="0.0.0.0", port=PORT)
