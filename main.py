import os
import logging
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ContentType, Message

# 1) Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# 2) Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.error("Не задан BOT_TOKEN в .env")
    exit(1)

# 3) Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 4) Хэндлеры

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот по безопасности косметики.\n"
        "Отправь мне фото упаковки — я постараюсь помочь."
    )

@dp.message(F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message):
    await message.answer("Фото получено, анализирую…")
    # TODO: сюда ваш код распознавания/анализа
    await message.answer("Пока не могу распознать текст — попробуй позже.")

@dp.message()
async def fallback(message: Message):
    await message.answer("Я понимаю только команду /start и фото упаковки. Попробуй ещё раз.")

# 5) Запуск long-polling
async def main():
    # Если ранее был установлен вебхук, то удалим его, чтобы использовать getUpdates
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Webhook удалён (если был). Работаем через getUpdates.")
    except Exception:
        pass

    logging.info("Бот запущен. Ожидаю сообщений…")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
