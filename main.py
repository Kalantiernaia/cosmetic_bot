import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()  # <-- подгружает .env из корня

TG_TOKEN        = os.getenv("TG_TOKEN")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
RAILWAY_URL     = os.getenv("RAILWAY_URL")
PORT            = int(os.getenv("PORT", 80))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот запущен.")

def main():
    app = Application.builder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TG_TOKEN,
        webhook_url=f"{RAILWAY_URL}/hook/{TG_TOKEN}"
    )

if __name__ == "__main__":
    main()
