import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Если у вас есть собственная функция анализа – импортируйте её:
# from cosmetics_analyzer import analyze_cosmetics

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TG_TOKEN")  # теперь это ваш новый токен из Railway

# ---- ХЕНДЛЕРЫ ----

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот по безопасности косметики.\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — инструкции по использованию\n\n"
        "Чтобы проанализировать состав, просто пришлите мне текст или фото упаковки."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Чтобы проанализировать косметику:\n"
        "• Отправьте мне текст ингредиентов\n"
        "• Или фото этикетки\n"
        "Я верну вам оценку безопасности состава."
    )

async def analyse_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    # Здесь вызываем вашу логику анализа:
    # result = analyze_cosmetics(text)
    # Для примера просто эхо-ответ:
    result = f"🔍 Анализирую текст:\n{text[:100]}…\n(здесь будет результат вашего анализа)"
    await update.message.reply_text(result)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Ошибка при обработке запроса:", exc_info=context.error)
    # Сообщаем пользователю об ошибке без паники
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Упс, что-то пошло не так. Попробуйте ещё раз или напишите /help."
        )

# ---- ТОЧКА ВХОДА ----

def main() -> None:
    app = Application.builder().token(TOKEN).build()

    # Регистрация хендлеров
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Все текстовые сообщения пойдут в analyse_text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyse_text))
    # (позже можно добавить фильтр для фотографий и фотохендлер)

    # Глобальный error handler
    app.add_error_handler(error_handler)

    # Запуск
    app.run_webhook()  # или .run_polling() локально для теста

if __name__ == "__main__":
    main()
