import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ————————————————
# Логирование (для дебага)
# ————————————————
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger()

# ————————————————
# Переменные окружения
# ————————————————
TOKEN       = os.getenv("TG_TOKEN")       # новый токен из BotFather
RAILWAY_URL = os.getenv("RAILWAY_URL")    # https://<your-app>.up.railway.app
PORT        = int(os.getenv("PORT", "8443"))
HOOK_PATH   = f"/hook/{TOKEN}"

# Проверим, что токен и URL есть
if not TOKEN or not RAILWAY_URL:
    logger.error("Необходимо задать TG_TOKEN и RAILWAY_URL в ENV")
    exit(1)

# ————————————————
# Хэндлеры
# ————————————————
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот по безопасности косметики.\n\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help  — показать эту подсказку"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Чтобы начать, просто отправьте /start."
    )

def main():
    # Создаём приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Сбрасываем старый вебхук и ставим новый
    logger.info("Deleting old webhook…")
    app.bot.delete_webhook(drop_pending_updates=True)
    new_url = RAILWAY_URL + HOOK_PATH
    logger.info(f"Setting webhook to {new_url}")
    app.bot.set_webhook(new_url)

    # Запускаем HTTP-сервер для вебхука
    logger.info(f"Starting webhook listener on 0.0.0.0:{PORT}{HOOK_PATH}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=HOOK_PATH,
    )

if __name__ == "__main__":
    main()
