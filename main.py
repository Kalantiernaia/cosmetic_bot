import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Бот запущен и работает через webhook.")

def main() -> None:
    TOKEN = os.environ["TG_TOKEN"]
    RAILWAY_URL = os.environ.get("RAILWAY_URL")
    PORT = int(os.environ.get("PORT", 8000))

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    if RAILWAY_URL:
        # В продакшене (Railway) — webhook
        app.run_webhook(
            listen="0.0.0.0",          # или host="0.0.0.0"
            port=PORT,
            path=f"/hook/{TOKEN}",    # здесь важен именно этот параметр
            webhook_url=f"{RAILWAY_URL}/hook/{TOKEN}",
        )
    else:
        # Локально — polling
        app.run_polling()

if __name__ == "__main__":
    main()
