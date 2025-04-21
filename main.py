import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ========= Настройка логирования (необязательно) =========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ========= Загрузка переменных окружения =========
load_dotenv()  # если есть .env-файл локально
TG_TOKEN    = os.environ["TG_TOKEN"]
RAILWAY_URL = os.environ["RAILWAY_URL"]   # что-то вроде https://your-app.up.railway.app
PORT        = int(os.environ.get("PORT", 5000))


# ========= Обработчики команд и сообщений =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Привет! Отправь мне фото или текст состава косметики — я его проанализирую."
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # TODO: сюда ваш код OCR / анализа состава
    # Например, вы могли сделать:
    #   text = ocr_recognize(update.message.photo[-1].file_id)
    #   result = analyze_ingredients(text)
    #   await update.message.reply_text(result)
    #
    # А пока просто отзовёмся эхо:
    incoming = ""
    if update.message.photo:
        incoming = "📷 получил фото, но OCR пока не реализован."
    else:
        incoming = update.message.text or "🤔 пустое сообщение"
    await update.message.reply_text(f"Результат анализа: «{incoming}»")


# ========= Основная функция =========
def main() -> None:
    application = Application.builder().token(TG_TOKEN).build()

    # регистрируем все хендлеры
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.PHOTO | filters.TEXT, analyze)
    )

    # ========== Настройка Webhook =========
    # Удаляем старый webhook (если был)
    application.bot.delete_webhook(drop_pending_updates=True)

    # Путь, на который Telegram будет слать POST‑запросы
    webhook_path = f"/hook/{TG_TOKEN}"

    # Устанавливаем новый webhook
    application.bot.set_webhook(f"{RAILWAY_URL}{webhook_path}")

    # Запускаем встроенный веб‑сервер на всех интерфейсах
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_path=webhook_path,
        url_path=webhook_path,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
