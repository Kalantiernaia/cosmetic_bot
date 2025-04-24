import os
from dotenv import load_dotenv
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ---------------------------------------------------------------------------- #
#                              ЗАГРУЗКА .env-ФАЙЛА                            #
# ---------------------------------------------------------------------------- #
load_dotenv()  # прочитает .env из той же папки, где лежит main.py

# ---------------------------------------------------------------------------- #
#                               ПЕРЕМЕННЫЕ СРЕДЫ                              #
# ---------------------------------------------------------------------------- #
TOKEN        = os.environ["TG_TOKEN"]
OPENAI_KEY   = os.environ["OPENAI_API_KEY"]
RAILWAY_URL  = os.environ["RAILWAY_URL"].rstrip("/")  # уберём возможный слеш на конце
PORT         = int(os.environ.get("PORT", 8443))     # Railway сам подставит нужный PORT

# ---------------------------------------------------------------------------- #
#                                ОБРАБОТЧИКИ                                   #
# ---------------------------------------------------------------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start """
    await update.message.reply_text("Привет! Я бот для анализа косметики.")

# сюда можно добавить другие хендлеры, например для распознавания фото и т.п.
# ---------------------------------------------------------------------------- #
#                                Запуск webhook                                #
# ---------------------------------------------------------------------------- #
def main():
    app = Application.builder().token(TOKEN).build()

    # зарегистрируем минимум один хендлер
    app.add_handler(CommandHandler("start", start))

    # путь для webhook — должен совпадать с тем, что передадим в url
    webhook_path = f"/hook/{TOKEN}"

    # запускаем встроенный aiohttp-сервер на 0.0.0.0:PORT
    # он сам установит вебхук в Telegram по адресу RAILWAY_URL + webhook_path
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=f"{RAILWAY_URL}{webhook_path}",
        drop_pending_updates=True,  # удалим старые апдейты при перезапуске
    )

if __name__ == "__main__":
    main()
