import os
import logging
from aiohttp import web
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 1) Настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2) Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "8080"))

# 3) Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот по безопасности косметики.\n" 
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — инструкции по использованию\n\n"
        "Чтобы отправить фото, просто перешлите его сюда."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Инструкция:\n"
        "1. /start — запустить бота\n"
        "2. Отправьте любое фото — я его обработаю и верну результат."
    )

# 4) Обработчик фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]
    file = await photo.get_file()
    # временно сохраняем в /tmp
    local_path = "/tmp/input.jpg"
    await file.download_to_drive(local_path)
    # TODO: здесь ваша логика анализа изображения
    # например:
    # result = my_cosmetics_analyzer(local_path)
    result = "⚠️ Ваше фото получено, но анализ ещё не реализован."
    await update.message.reply_text(result)

# 5) Точка входа и запуск вебхука
async def on_startup(app: web.Application) -> None:
    logger.info("Deleting old webhook (if any)…")
    await app.bot.delete_webhook(drop_pending_updates=True)
    new_url = f"{WEBHOOK_URL}/hook/{TOKEN}"
    logger.info("Setting new webhook to %s", new_url)
    await app.bot.set_webhook(new_url)

def build_app() -> web.Application:
    application = ApplicationBuilder()\
        .token(TOKEN)\
        .webhook(host="0.0.0.0", port=PORT, path=f"/hook/{TOKEN}")\
        .build()

    # регистрируем хэндлеры
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # при старте aiohttp-сервера вызываем on_startup
    application.post_init(on_startup)

    return application

def main() -> None:
    app = build_app()
    # запускаем aiohttp и телеграм вместе
    app.run_webhook()

if __name__ == "__main__":
    main()
