import os
import logging
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Включаем логирование, чтобы видеть ошибки
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем настройки из окружения
TOKEN       = os.environ["TG_TOKEN"]
RAILWAY_URL = os.environ["RAILWAY_URL"].rstrip("/")  # https://...up.railway.app
PORT        = int(os.environ.get("PORT", 5000))
HOOK_PATH   = f"/hook/{TOKEN}"                     # путь вебхука

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    text = (
        "Привет! Я бот по безопасности косметики.\n\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — инструкции по использованию\n\n"
        "Чтобы проверить безопасность средства, просто отправьте мне фото флакончика или состава."
    )
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    text = (
        "Инструкции по использованию:\n"
        "1) Отправьте фото состава или упаковки косметического средства\n"
        "2) Я проанализирую его и отвечу, безопасно ли это средство\n"
        "3) Задавайте вопросы по результатам"
    )
    await update.message.reply_text(text)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик поступившего фото."""
    # Берём фотографию пользователя (последний элемент в list)
    photo = update.message.photo[-1]
    bio = BytesIO()
    await photo.get_file().download(out=bio)
    bio.seek(0)
    # Открываем через PIL (можете здесь вставить свой анализ)
    image = Image.open(bio)
    # Пока просто подтверждаем приём
    await update.message.reply_text("Фото получено, начинаю анализ…")
    # TODO: здесь "image" можно передать в OpenAI Vision или другой модуль анализа
    # После анализа отправьте пользователю результат:
    # await update.message.reply_text("Результат анализа: ...")

def main() -> None:
    """Главная функция — создаёт приложение и запускает вебхук."""
    app = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    # Фильтр на любые фото-сообщения
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    # Запускаем вебхук-сервер
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url_path=HOOK_PATH,        # НОВЫЙ параметр
        webhook_url=RAILWAY_URL + HOOK_PATH,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
