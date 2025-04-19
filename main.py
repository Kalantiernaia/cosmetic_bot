import os
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")

app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Пришли мне фото состава косметики, и я проанализирую каждый ингредиент."
    )

bot_app.add_handler(CommandHandler("start", start))

async def handle_photo(update: Update, context):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"tmp_{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: OCR и анализ через OpenAI
    await update.message.reply_text("Готово, скоро пришлю вам отчёт по составу.")
    # os.remove(path)

bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

@app.route(f"/hook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK"

if __name__ == "__main__":
    bot_app.bot.set_webhook(f"https://<YOUR_RAILWAY_URL>/hook/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
