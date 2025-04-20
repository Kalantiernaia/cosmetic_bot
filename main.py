import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

# Читаем токен, URL и API‑ключ из переменных окружения
TG_TOKEN      = os.environ["TG_TOKEN"]
OPENAI_API_KEY= os.environ["OPENAI_API_KEY"]
RAILWAY_URL   = os.environ["RAILWAY_URL"]  # например "https://cosmeticbot-production.up.railway.app"

WEBHOOK_PATH = f"/hook/{TG_TOKEN}"
WEBHOOK_URL  = f"{RAILWAY_URL}{WEBHOOK_PATH}"

app = Flask(__name__)

# 1) Сборка асинхронного приложения-бота
application = ApplicationBuilder().token(TG_TOKEN).build()

# 2) Регистрируем хендлеры
async def start(update: Update, context):
    await update.message.reply_text("Привет! Пришлите, пожалуйста, фото состава косметики.")

async def handle_photo(update: Update, context):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    tmp_path = f"tmp_{photo.file_id}.jpg"
    await file.download_to_drive(tmp_path)

    # TODO: здесь вызываете OpenAI для анализа состава
    await update.message.reply_text("Готово, скоро пришлю отчёт.")
    os.remove(tmp_path)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))


# 3) Маршрут Flask для приема вебхуков
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    # Передаём апдейт в очередь PTB
    application.create_task(application.process_update(update))
    return "OK"


def main():
    # Устанавливаем вебхук перед запуском Flask
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL))
    # Запускаем Flask‑сервера на порту из окружения (Railway задаёт PORT сам)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
