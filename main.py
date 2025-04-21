import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

# 1) подгружаем .env (локально) или переменные окружения в Railway
load_dotenv()

# 2) достаём нужные переменные
TOKEN       = os.environ["TG_TOKEN"]
RAILWAY_URL = os.environ["RAILWAY_URL"].rstrip("/")  # без завершающего /
PORT        = int(os.environ.get("PORT", 5000))

# 3) логирование
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 4) хендлеры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот для анализа состава косметики. Пришли мне фото состава — отвечу отчётом."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"/tmp/{photo.file_id}.jpg"
    await file.download_to_drive(path)
    # TODO: тут ваш OCR и анализ через OpenAI
    await update.message.reply_text("Фото получено, анализирую…")
    # os.remove(path)

# 5) точка входа
def main() -> None:
    # 5.1 создаём приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # 5.2 навешиваем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # 5.3 настраиваем вебхук
    url_path   = f"/hook/{TOKEN}"
    webhook_url = f"{RAILWAY_URL}{url_path}"
    logger.info(
        "Запускаем webhook: port=%s, path=%s, url=%s",
        PORT, url_path, webhook_url
    )

    # 5.4 запускаем
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=url_path,
        drop_pending_updates=True,
        webhook_url=webhook_url,
    )

if __name__ == "__main__":
    main()
