import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
from aiogram import F
from aiogram.utils.executor import start_webhook

# 1) Логирование
logging.basicConfig(level=logging.INFO)

# 2) Подгружаем .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

if not TOKEN or not WEBHOOK_URL:
    logging.error("Не заданы BOT_TOKEN или WEBHOOK_URL в окружении")
    exit(1)

# 3) Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 4) Хэндлеры
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот по безопасности косметики.\n"
        "Отправь мне фото упаковки — я постараюсь помочь."
    )

@dp.message(F.content_type == ContentType.PHOTO)
async def handle_photo(message: types.Message):
    await message.answer("Фото получено, анализирую…")
    # TODO: тут твой код анализа
    await message.answer("Пока не умею распознавать — попробуй позже.")

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Я понимаю только /start и фото упаковки.")

# 5) Запуск через webhook
if __name__ == "__main__":
    webhook_path = f"/{TOKEN}"
    full_webhook = f"{WEBHOOK_URL}{webhook_path}"

    async def on_startup():
        await bot.set_webhook(full_webhook)

    async def on_shutdown():
        await bot.delete_webhook()

    start_webhook(
        dispatcher=dp,
        webhook_path=webhook_path,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=PORT,
    )
