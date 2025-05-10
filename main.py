import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import openai

# ——— Настройка логирования ———
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ——— Загрузка переменных окружения из .env ———
load_dotenv()
BOT_TOKEN     = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# ——— Обработчики команд ———
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот по безопасности косметики. Отправь мне фото упаковки, "
        "а я постараюсь дать ответ."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — показать эту подсказку\n\n"
        "Просто отправь фото, и я отвечу."
    )

# ——— Обработчик фото ———
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]  # берём фото наилучшего качества
    file = await photo.get_file()
    img_bytes = await file.download_as_bytearray()

    # Здесь вы можете добавить любую вашу логику,
    # например, отправить изображение в OpenAI Vision или
    # сохранить его и передать в свой ML-модель, и т.д.
    #
    # Ниже просто пример-заглушка:
    #
    await update.message.reply_text("Фото получено, анализирую…")

    # Пример вызова OpenAI (текстовая модель, вместо Vision):
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Что на этом фото?"}],
        )
        text = resp.choices[0].message.content
    except Exception as e:
        logger.exception("OpenAI error:")
        text = "Не смог обработать фото, попробуйте позже."

    await update.message.reply_text(text)

# ——— Точка входа ———
def main():
    if not BOT_TOKEN or not OPENAI_API_KEY:
        logger.error("Не найдены BOT_TOKEN или OPENAI_API_KEY в .env")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    # Запускаем polling
    app.run_polling()

if __name__ == "__main__":
    main()
