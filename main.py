import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor, F
from aiogram.filters import Command
from aiogram.types import ContentType

# 1) Настройка логирования
logging.basicConfig(level=logging.INFO)

# 2) Подгружаем переменные окружения из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.error("Не задан BOT_TOKEN в .env")
    exit(1)

# 3) Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 4) Перед стартом long-polling удаляем любой заранее установленный вебхук
async def on_startup(dp: Dispatcher):
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Webhook удалён, бот будет работать через getUpdates (long-polling).")

# 5) Хэндлеры

@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот по безопасности косметики.\n"
        "Отправь мне фото упаковки — я постараюсь помочь."
    )

@dp.message(F.content_type == ContentType.PHOTO)
async def handle_photo(message: types.Message):
    await message.answer("Фото получено, анализирую…")
    # TODO: здесь может быть ваш код распознавания/анализа изображения
    await message.answer("Пока не могу распознать текст — попробуй позже.")

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Я понимаю только команду /start и фото упаковки. Попробуй еще раз.")

# 6) Запуск long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
