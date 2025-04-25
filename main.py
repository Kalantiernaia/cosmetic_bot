import os
from dotenv import load_dotenv
import openai

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# 1) Подгружаем переменные из .env
load_dotenv()
TG_TOKEN       = os.environ["TG_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
RAILWAY_URL    = os.environ.get("RAILWAY_URL")       # будет определён на Railway
PORT           = int(os.environ.get("PORT", 8000))   # Railway сам пробросит PORT

# 2) Настраиваем OpenAI
openai.api_key = OPENAI_API_KEY

# 3) Простейший handler для /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Привет! Я бот для анализа косметики. Пришли мне описание продукта — расскажу, как он работает."
    )

def main() -> None:
    # 4) Строим приложение
    app = ApplicationBuilder().token(TG_TOKEN).build()

    # 5) Регистрируем handlers
    app.add_handler(CommandHandler("start", start))

    # 6) Если запущено на Railway — работаем через webhook
    if RAILWAY_URL:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=f"/hook/{TG_TOKEN}",                 # <-- url_path, не path и не webhook_path
            webhook_url=f"{RAILWAY_URL}/hook/{TG_TOKEN}",  # полный URL на ваш Railway-хук
        )
    else:
        # 7) Иначе в локале — polling
        app.run_polling()

if __name__ == "__main__":
    main()
