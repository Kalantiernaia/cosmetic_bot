# main.py
import os
import logging
from io import BytesIO

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from PIL import Image
import pytesseract
import openai

# 1) Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2) Загрузить .env
load_dotenv()
TG_TOKEN = os.getenv("TG_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RAILWAY_URL = os.getenv("RAILWAY_URL")  # https://yourapp.up.railway.app

if not TG_TOKEN or not OPENAI_API_KEY:
    logger.error("Не задан TG_TOKEN или OPENAI_API_KEY в .env")
    exit(1)

openai.api_key = OPENAI_API_KEY


# 3) Функция анализа текста через OpenAI
async def analyze_cosmetics(text: str) -> str:
    """
    Отправляем запрос в OpenAI, возвращаем ответ.
    Подставьте здесь свой prompt / параметры модели.
    """
    try:
        resp = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты эксперт по косметике."},
                {"role": "user", "content": f"Проанализируй состав: {text}"},
            ],
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("OpenAI error:")
        return "Ошибка анализа состава."


# 4) Обработчики команд
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот по анализу косметики.\n"
        "Отправьте мне текст (названия ингредиентов) или фото состава."
    )


async def help_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — запустить бота\n"
        "/help — показать эти инструкции\n\n"
        "Просто отправьте мне текст или фото."
    )


# 5) Обработка текста (списка ингредиентов)
async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("Идёт анализ, подождите…")
    result = await analyze_cosmetics(user_text)
    await update.message.reply_text(result)


# 6) Обработка фото (OCR → анализ текста)
async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скачиваю фото и распознаю текст…")
    photo_file = await update.message.photo[-1].get_file()
    bio = BytesIO()
    await photo_file.download_to_memory(out=bio)
    bio.seek(0)

    try:
        img = Image.open(bio)
        ocr_text = pytesseract.image_to_string(img, lang="eng+rus")
        if not ocr_text.strip():
            raise ValueError("Текст не найден")
    except Exception as e:
        logger.exception("OCR error:")
        await update.message.reply_text("Не удалось распознать текст на фото.")
        return

    await update.message.reply_text("Найденный текст:\n" + ocr_text[:200] + "…\nАнализирую…")
    result = await analyze_cosmetics(ocr_text)
    await update.message.reply_text(result)


def main():
    # 7) Создаём приложение
    app = ApplicationBuilder().token(TG_TOKEN).build()

    # 8) Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # 9) Запуск polling или webhook
    if RAILWAY_URL:
        # webhook на Railway
        webhook_path = f"/hook/{TG_TOKEN}"
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", "8080")),
            webhook_url=RAILWAY_URL + webhook_path,
            webhook_path=webhook_path,
        )
    else:
        # локально
        app.run_polling()


if __name__ == "__main__":
    main()
