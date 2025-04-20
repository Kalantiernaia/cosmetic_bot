# main.py
import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

# 1) Загрузка переменных окружения из .env (локально)
load_dotenv()

# 2) Читаем токен и URL из переменных окружения
TOKEN       = os.getenv("TG_TOKEN")       # твой телеграм‑токен
RAILWAY_URL = os.getenv("RAILWAY_URL")    # https://…up.railway.app
PORT        = int(os.getenv("PORT", 5000))

if not TOKEN or not RAILWAY_URL:
    raise RuntimeError("TG_TOKEN или RAILWAY_URL не заданы в окружении!")

# 3) Настраиваем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 4) Создаём Flask‑приложение
app = Flask(__name__)

# 5) Создаём Telegram‑бот
application = ApplicationBuilder().token(TOKEN).build()

# 6) Определяем хэндлеры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне фото состава косметики, " 
        "и я попробую его проанализировать."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Берём самое крупное фото из сообщения
    photo = update.message.photo[-1]
    # Скачиваем его во временный файл
    file = await context.bot.get_file(photo.file_id)
    path = f"/tmp/{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: здесь можно вызвать OCR и OpenAI для анализа
    await update.message.reply_text("Готово! Скоро пришлю отчёт по составу.")
    try:
        os.remove(path)
    except OSError:
        pass

# 7) Регистрируем хэндлеры в приложении
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# 8) Маршрут Webhook-а, куда Telegram будет слать апдейты
@app.route(f"/hook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put(update)
    return "OK"

# 9) Точка входа
if __name__ == "__main__":
    # Ставим вебхук в Telegram
    webhook_url = f"{RAILWAY_URL}/hook/{TOKEN}"
    application.bot.set_webhook(webhook_url)
    # Запускаем встроенный Flask‑сервер
    app.run(host="0.0.0.0", port=PORT)
