import os
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ————————————————
# Логирование
# ————————————————
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ————————————————
# Переменные окружения
# ————————————————
TOKEN = os.getenv("TG_TOKEN")
RAILWAY_URL = os.getenv("RAILWAY_URL")  # без слеша в конце
PORT = int(os.getenv("PORT", "8443"))
HOOK_PATH = f"/hook/{TOKEN}"

if not TOKEN or not RAILWAY_URL:
    logger.error("Необходимо задать TG_TOKEN и RAILWAY_URL")
    exit(1)


# ————————————————
# Обработчики команд
# ————————————————
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот по безопасности косметики.\n\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — инструкции по использованию"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Чтобы начать, отправьте /start.\n"
        "Больше команд пока нет."
    )


def main() -> None:
    # 1) Создаём приложение
    app = Application.builder().token(TOKEN).build()

    # 2) Регистрируем командные хэндлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # 3) Сбрасываем старый вебхук и устанавливаем новый
    logger.info("Deleting old webhook (if any)…")
    app.run_sync(app.bot.delete_webhook, drop_pending_updates=True)

    new_url = RAILWAY_URL + HOOK_PATH
    logger.info(f"Setting new webhook to {new_url}")
    app.run_sync(app.bot.set_webhook, new_url)

    # 4) Запускаем HTTP-сервер для приёма вебхуков
    logger.info(f"Starting webhook listener on 0.0.0.0:{PORT}{HOOK_PATH}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=HOOK_PATH,     # <-- здесь именно url_path
    )


if __name__ == "__main__":
    main()
