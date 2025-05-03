import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# 1) Логгирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2) Переменные окружения
TOKEN       = os.getenv("TG_TOKEN")
RAILWAY_URL = os.getenv("RAILWAY_URL")      # без слеша в конце!
PORT        = int(os.getenv("PORT", "8443"))
HOOK_PATH   = f"/hook/{TOKEN}"

# 3) Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот по безопасности косметики.\n\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — инструкции по использованию"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Инструкции по использованию:\n"
        "Отправьте /start, и бот скажет «привет»."
    )

# 4) Функция-хук, выполняемая при старте HTTP-сервера
async def on_startup() -> None:
    app = ApplicationBuilder().token(TOKEN).build()
    # (мы не используем app внутри — просто логируем)
    logger.info("Deleting old webhook (if any)…")
    # NOTE: app.bot — бот-объект, но нам нужно получить его из глобального Application:
    from telegram.ext import applications
    running_app = applications.get_current_application()
    await running_app.bot.delete_webhook()

    new_webhook = RAILWAY_URL + HOOK_PATH
    logger.info(f"Setting webhook to {new_webhook}")
    await running_app.bot.set_webhook(url=new_webhook)

def main() -> None:
    # Собираем приложение
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Запускаем webhook-сервер
    logger.info(f"Starting webhook listener on 0.0.0.0:{PORT}{HOOK_PATH}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=HOOK_PATH,
        webhook_url=RAILWAY_URL + HOOK_PATH,
        on_startup=on_startup,       # <--- сюда
    )

if __name__ == "__main__":
    main()
