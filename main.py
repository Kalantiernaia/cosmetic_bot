import os
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ————————————————
# Настройка логирования
# ————————————————
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ————————————————
# Чтение настроек из окружения
# ————————————————
TOKEN       = os.getenv("TG_TOKEN")
RAILWAY_URL = os.getenv("RAILWAY_URL")       # например https://<your-service>.up.railway.app
PORT        = int(os.getenv("PORT", "8443"))
HOOK_PATH   = f"/hook/{TOKEN}"

if not TOKEN or not RAILWAY_URL:
    logger.error("Не заданы переменные окружения TG_TOKEN и/или RAILWAY_URL.")
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
        "Чтобы начать, отправьте команду /start.\n"
        "Больше команд пока нет."
    )


def main() -> None:
    # 1) Создаём приложение
    app = Application.builder().token(TOKEN).build()

    # 2) Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # 3) Сначала удаляем старый webhook и ставим новый
    #    (бот-объект внутри приложения доступен через app.bot)
    logger.info("Deleting old webhook (if any)…")
    app.bot.delete_webhook(drop_pending_updates=True)

    new_url = RAILWAY_URL + HOOK_PATH
    logger.info(f"Setting new webhook to {new_url}")
    app.bot.set_webhook(new_url)

    # 4) Запускаем встроенный HTTP-сервер для приёма Telegram-вебхуков
    logger.info(f"Starting webhook listener on 0.0.0.0:{PORT}{HOOK_PATH}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_path=HOOK_PATH,
    )


if __name__ == "__main__":
    main()
