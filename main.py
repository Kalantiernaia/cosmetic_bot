import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ==============  
#  Настройка  
# ==============
load_dotenv()  # для локальной разработки; на Railway считывает из переменных сервиса
TG_TOKEN    = os.environ["TG_TOKEN"]
OPENAI_KEY  = os.environ["OPENAI_API_KEY"]
RAILWAY_URL = os.environ["RAILWAY_URL"].rstrip("/")  # например https://cosmeticbot-production.up.railway.app
PORT        = int(os.environ.get("PORT", 5000))

# Путь, куда Telegram будет присылать вебхуки
URL_PATH   = f"/hook/{TG_TOKEN}"
WEBHOOK_URL = f"{RAILWAY_URL}{URL_PATH}"

# ==============
#  Логирование  
# ==============
logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ====================
#  Обработчики команд  
# ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я бот по анализу состава косметики. Пришли мне фото или текст состава.")

# ================
#  Основная логика  
# ================
def main() -> None:
    # 1) Создаём приложение
    app = ApplicationBuilder()\
        .token(TG_TOKEN)\
        .build()

    # 2) Регистрируем все хендлеры
    app.add_handler(CommandHandler("start", start))
    # ... сюда добавьте остальные CommandHandler / MessageHandler для OCR и OpenAI ...

    # 3) Сбрасываем старые вебхуки и ставим новый
    #    drop_pending_updates=True — удалит старые неотправленные апдейты
    app.bot.delete_webhook(drop_pending_updates=True)
    app.bot.set_webhook(url=WEBHOOK_URL, path=URL_PATH)

    # 4) Запускаем встроенный HTTP‑сервер PTB
    #    listen="0.0.0.0" чтобы принимать извне, порт берём из PORT
    #    url_path = URL_PATH чтобы совпадало с тем, что мы передали в set_webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=URL_PATH,
    )

if __name__ == "__main__":
    main()
