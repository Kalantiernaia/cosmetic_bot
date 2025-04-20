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
TG_TOKEN        = os.environ["TG_TOKEN"]
RAILWAY_URL     = os.environ["RAILWAY_URL"].rstrip("/")  # без завершающего /
OPENAI_API_KEY  = os.environ["OPENAI_API_KEY"]
openai.api_key  = OPENAI_API_KEY

PORT            = int(os.environ.get("PORT", 5000))
HOOK_PATH       = f"/hook/{TG_TOKEN}"
WEBHOOK_URL     = f"{RAILWAY_URL}{HOOK_PATH}"

# ——————————————————————————————————————————————————————————————
# /start
async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Пришли мне фото этикетки с ингредиентами — "
        "я распознаю текст, отмечу опасные и предложу аналоги."
    )

# ——————————————————————————————————————————————————————————————
# Обработка фото
async def handle_photo(update: Update, context):
    # 1) скачиваем файл
    photo = update.message.photo[-1]
    file  = await photo.get_file()
    path  = f"tmp/{photo.file_id}.jpg"
    os.makedirs("tmp", exist_ok=True)
    await file.download_to_drive(path)

    try:
        # 2) OCR
        img_text = pytesseract.image_to_string(
            Image.open(path),
            lang="rus+eng"
        ).strip()
        if not img_text:
            await update.message.reply_text(
                "Не удалось распознать текст. Попробуйте фото получше."
            )
            return

        # 3) Анализ через OpenAI
        prompt = (
            "Перед тобой список ингредиентов косметики:\n"
            f"{img_text}\n\n"
            "Разбери его, отметь опасные/раздражающие компоненты, "
            "и предложи натуральные альтернативы."
        )
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        result = resp.choices[0].message.content.strip()

        # 4) Отправляем ответ
        await update.message.reply_text(result)

    except Exception as e:
        logger.exception("Ошибка при анализе фото")
        await update.message.reply_text(
            "Что‑то пошло не так при анализе. Попробуйте позже."
        )

    finally:
        # 5) очищаем
        try:
            os.remove(path)
        except OSError:
            pass

# ——————————————————————————————————————————————————————————————
def main():
    app = (
        ApplicationBuilder()
        .token(TG_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Сбрасываем старый вебхук
    app.delete_webhook(drop_pending_updates=True)
    # Устанавливаем новый по адресу RAILWAY_URL/hook/TG_TOKEN
    app.set_webhook(WEBHOOK_URL)

    logger.info(
        f"Запускаем на порту={PORT}, path={HOOK_PATH}, webhook={WEBHOOK_URL}"
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        path=HOOK_PATH,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
