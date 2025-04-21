import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

load_dotenv()

# Токен бота
TG_TOKEN = os.getenv("TG_TOKEN")
# Ваш OpenAI‑ключ
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Railway предоставляет корректный URL автоматически
RAILWAY_URL = os.getenv("RAILWAY_URL")

# Порт берётся из переменной PORT, Railway подставляет его сам
PORT = int(os.environ.get("PORT", 5000))

# Путь вебхука и полный URL, объединяя Railway URL + токен
WEBHOOK_PATH = f"/hook/{TG_TOKEN}"
WEBHOOK_URL = f"{RAILWAY_URL}{WEBHOOK_PATH}"

# --- Ваши хендлеры ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я готов анализировать состав косметики.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пришли фотографию этикетки, я распознаю ингредиенты.")
    
# Добавьте сюда свой хендлер OCR/анализа
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # … ваш код OCR, OpenAI, ответ пользователю …
    await update.message.reply_text("Обработка завершена!")

def main():
    # Строим приложение
    app = (
        Application
        .builder()
        .token(TG_TOKEN)
        .build()
    )

    # Регистрируем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    # Логгирование
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    # Сбрасываем старый вебхук и устанавливаем новый (без передачи пути!)
    app.bot.delete_webhook(drop_pending_updates=True)
    app.bot.set_webhook(url=WEBHOOK_URL)

    # Запускаем встроенный сервер для приёма POST от Telegram
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
