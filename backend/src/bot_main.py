import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from src.core.config import settings


# Включаем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Инициализируем бота и диспетчер
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Добро пожаловать в наш магазин.")


async def main():
    logging.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

