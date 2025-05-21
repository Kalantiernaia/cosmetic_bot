import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import ContentType

# ========== 1) Настраиваем логирование ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ========== 2) Подгружаем переменные окружения ==========
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.error("❌ Не найден BOT_TOKEN в окружении")
    exit(1)

# ========== 3) Инициализируем бота и диспетчер ==========
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========== 4) Хэндлеры ==========
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот по анализу косметики.\n"
        "Пришли фото упаковки – постараюсь помочь."
    )

@dp.message(F.content_type == ContentType.PHOTO)
async def handle_photo(message: types.Message):
    await message.answer("🖼️ Фото получено, анализирую…")
    # TODO: вставьте здесь свой код OCR / анализа
    await message.answer("Пока не умею распознавать — попробуй позже.")

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Я понимаю только /start и фотографии упаковки.")

# ========== 5) Запуск долгого опроса (long polling) ==========
if __name__ == "__main__":
    # dp.run_polling автоматически вызывает bot.delete_webhook(), skip_updates=True сбрасывает старые сообщения
    dp.run_polling(bot, skip_updates=True)
