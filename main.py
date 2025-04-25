import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import openai

# ——— Логирование —————————————————————————————————————
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ——— Обработчик команды /start —————————————————————————
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот для анализа косметики. Пришли описание продукта, и я дам оценку."
    )


# ——— Обработчик любых текстовых сообщений —————————————
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    openai.api_key = os.environ["OPENAI_API_KEY"]
    try:
        resp = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Дай экспертный анализ косметического продукта: «{user_text}»",
            max_tokens=200,
        )
        answer = resp.choices[0].text.strip()
    except Exception as e:
        logger.error("OpenAI error: %s", e)
        answer = "Извини, не смог связаться с OpenAI."
    await update.message.reply_text(answer)


# ——— Точка входа —————————————————————————————————————
def main() -> None:
    token = os.environ["TG_TOKEN"]
    app = ApplicationBuilder().token(token).build()

    # Регистрируем хэндлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))

    # Параметры вебхука
    port = int(os.environ.get("PORT", "8443"))
    railway_url = os.environ["RAILWAY_URL"]

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=f"hook/{token}",
        webhook_url=f"{railway_url}/hook/{token}",
    )


if __name__ == "__main__":
    main()
