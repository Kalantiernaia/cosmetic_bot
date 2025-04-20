import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from PIL import Image
import pytesseract
import openai

# ——————————————————————————————————————————————————————————————
# Логирование
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ——————————————————————————————————————————————————————————————
# Переменные окружения
TG_TOKEN       = os.environ["TG_TOKEN"]
RAILWAY_URL    = os.environ["RAILWAY_URL"].rstrip("/")   # без завершающего /
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

PORT      = int(os.environ.get("PORT", 5000))
URL_PATH  = f"/hook/{TG_TOKEN}"
WEBHOOK   = f"{RAILWAY_URL}{URL_PATH}"

# ——————————————————————————————————————————————————————————————
async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Пришли мне фото этикетки с ингредиентами — "
        "распознаю текст, отмечу опасные компоненты и предложу натуральные аналоги."
    )

# ——————————————————————————————————————————————————————————————
async def handle_photo(update: Update, context):
    photo = update.message.photo[-1]
    file  = await photo.get_file()
    tmpf  = f"tmp/{photo.file_id}.jpg"
    os.makedirs("tmp", exist_ok=True)
    await file.download_to_drive(tmpf)

    try:
        text = pytesseract.image_to_string(
            Image.open(tmpf), lang="rus+eng"
        ).strip()
        if not text:
            await update.message.reply_text("Не смог распознать текст. Попробуй другое фото.")
            return

        prompt = (
            "Перед тобой список ингредиентов косметики:\n"
            f"{text}\n\n"
            "Отметь опасные/раздражающие вещества и предложи натуральные альтернативы."
        )
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        result = resp.choices[0].message.content.strip()
        await update.message.reply_text(result)

    except Exception:
        logger.exception("Ошибка обработки фото")
        await update.message.reply_text("Что‑то пошло не так. Попробуй позже.")

    finally:
        try:
            os.remove(tmpf)
        except OSError:
            pass

# ——————————————————————————————————————————————————————————————
def main():
    app = ApplicationBuilder().token(TG_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info(f"Запускаем webhook: порт={PORT}, path={URL_PATH}, url={WEBHOOK}")

    # Здесь автоматически удалится старый вебхук и поставится новый
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=URL_PATH,
        webhook_url=WEBHOOK,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
