import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ================
#  Настройка логгирования
# ================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================
#  Переменные окружения
# ================
TOKEN      = os.getenv("TG_TOKEN")        # ваш Bot Token
RAILWAY_URL = os.getenv("RAILWAY_URL")    # например https://cosmeticbot-production.up.railway.app
PORT       = int(os.getenv("PORT", "8443"))  # порт, который слушает Railway
HOOK_PATH  = f"/hook/{TOKEN}"             # путь должен совпадать с тем, что укажем в set_webhook


# ================
#  Обработчики команд
# ================
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
        "Просто отправьте /start, и бот ответит."
    )


# ================
#  Функция, которая выполнится при старте приложения
# ================
async def on_startup(app):
    # 1) Удаляем старый вебхук (если есть)
    logger.info("Deleting old webhook (if any)…")
    await app.bot.delete_webhook()

    # 2) Ставим новый вебхук на наш публичный URL
    full_webhook = RAILWAY_URL + HOOK_PATH
    logger.info(f"Setting webhook to {full_webhook}")
    await app.bot.set_webhook(url=full_webhook)


def main() -> None:
    # 1) Строим приложение
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # 2) Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # 3) Регистрируем функцию on_startup
    app.post_init(on_startup)

    # 4) Запускаем HTTP-сервер для приёма вебхуков
    logger.info(f"Starting webhook listener on 0.0.0.0:{PORT}{HOOK_PATH}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=HOOK_PATH,
        webhook_url=RAILWAY_URL + HOOK_PATH,
    )


if __name__ == "__main__":
    main()
