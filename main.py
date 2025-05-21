import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
from aiogram.utils.executor import start_polling

# 1) Логирование
logging.basicConfig(level=logging.INFO)

# 2) Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.error("Не задан BOT_TOKEN в .env")
    exit(1)

# 3) Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 4) Регистрируем хэндлеры

@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот по безопасности косметики.\n"
        "Отправь мне фото упаковки — я постараюсь помочь."
    )

@dp.message(lambda msg: msg.content_type == ContentType.PHOTO)
async def handle_photo(message: types.Message):
    await message.answer("Фото получено, анализирую…")
    # TODO: сюда ваш код распознавания/анализа
    await message.answer("Пока не могу распознать текст — попробуй позже.")

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Я понимаю только команду /start и фото упаковки.")

# 5) Стартуем long-polling
if __name__ == "__main__":
    start_polling(dp, skip_updates=True)
