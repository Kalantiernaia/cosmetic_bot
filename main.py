import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes
)

# Читать токен и URL из окружения
TOKEN       = os.environ["TG_TOKEN"]
RAILWAY_URL = os.environ["RAILWAY_URL"].rstrip("/")
PORT        = int(os.environ.get("PORT", 5000))

# Пути для вебхука
WEBHOOK_PATH = f"hook/{TOKEN}"
WEBHOOK_URL  = f"{RAILWAY_URL}/{WEBHOOK_PATH}"

# Простейший handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и готов к анализу!")

async def main():
    # Строим асинхронное приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем команду
    application.add_handler(CommandHandler("start", start))

    # 1) Сбросить старый вебхук
    await application.bot.delete_webhook(drop_pending_updates=True)

    # 2) Установить новый
    await application.bot.set_webhook(url=WEBHOOK_URL)

    # 3) Запустить встроенный веб-сервер
    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    asyncio.run(main())
