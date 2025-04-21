import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# 1) Загрузка .env
load_dotenv()
TG_TOKEN       = os.environ["TG_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]   # если нужен
RAILWAY_URL    = os.environ["RAILWAY_URL"]

# 2) Порт и путь берём из окружения с дефолтами
PORT     = int(os.environ.get("PORT", 5000))
URL_PATH = f"/hook/{TG_TOKEN}"
WEBHOOK_URL = f"{RAILWAY_URL}{URL_PATH}"

# 3) Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# 4) Пример хендлера
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я бот для анализа косметики.")

# 5) Точка входа
def main():
    # 5.1) Создаём Application
    app = ApplicationBuilder().token(TG_TOKEN).build()

    # 5.2) Регистрируем хендлеры
    app.add_handler(CommandHandler("start", start))
    # TODO: тут ваши OCR/анализ‑хендлеры

    # 5.3) Запускаем вебхук
    #
    # Важно: используем url_path, а не webhook_path,
    # и передаём полный публичный webhook_url.
    #
    # drop_pending_updates=True сбросит накопившиеся апдейты
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=URL_PATH,         # путь в контейнере
        webhook_url=WEBHOOK_URL,   # полный URL, куда Telegram будет шлать
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
