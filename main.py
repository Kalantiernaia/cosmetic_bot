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

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Читаем переменные окружения
TOKEN = os.environ["TG_TOKEN"]
OPENAI_KEY = os.environ["OPENAI_API_KEY"]  # если не нужен — можно убрать
RAILWAY_URL = os.environ["RAILWAY_URL"]
PORT = int(os.environ.get("PORT", "8443"))

# Путь вебхука (будь уверен, что совпадает с тем, что ты прописал в переменных Railway)
HOOK_PATH = f"/hook/{TOKEN}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ответ на /start."""
    await update.message.reply_text(
        "Привет! Я бот по анализу косметики. "
        "Отправь мне фото — и я попробую помочь."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ответ на /help."""
    await update.message.reply_text(
        "/start — запустить бота\n"
        "/help  — инструкция по использованию"
    )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик фото."""
    # Тут ты получаешь файл и делаешь свой анализ
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = await file.download_to_drive()

    # Здесь вставляй свой код обработки картинки,
    # например с OpenAI или PIL, и отправляй результат:
    await update.message.reply_text("Фото получено, анализирую…")
    # …твой анализ…
    await update.message.reply_text("Готово!")

def main() -> None:
    """Точка входа — собираем апп и запускаем вебхук."""
    app = Application.builder().token(TOKEN).build()

    # Регистрируем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    # Запускаем вебхук
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=HOOK_PATH,
        webhook_url=RAILWAY_URL + HOOK_PATH,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
