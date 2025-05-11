import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.types import ContentType
from aiogram.utils.executor import start_webhook

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TG_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

if not TOKEN or not WEBHOOK_URL:
    logging.error("Не заданы переменные TG_TOKEN или WEBHOOK_URL")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот по безопасности косметики. Отправь мне фото упаковки, я постараюсь помочь.")

@dp.message_handler(ContentType.PHOTO)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    await message.answer("Фото получено, анализирую…")
    # Здесь вставь свой код распознавания/анализа
    # Для теста просто отвечаем:
    await message.answer("Пока не могу обработать фото, попробуй позже.")

@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Я понимаю только команды /start и фото.")

async def on_startup(dp):
    logging.info("Deleting old webhook (if any)…")
    await bot.delete_webhook(drop_pending_updates=True)
    webhook_path = f"/hook/{TOKEN}"
    webhook_full = f"{WEBHOOK_URL}{webhook_path}"
    logging.info(f"Setting new webhook to {webhook_full}")
    await bot.set_webhook(webhook_full)

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=f"/hook/{TOKEN}",
        on_startup=on_startup,
        host="0.0.0.0",
        port=PORT,
    )
