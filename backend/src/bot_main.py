import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from src.core.config import settings
from src.bot.handlers.catalog import router as catalog_router
from src.bot.handlers.accept_order import router as web_app_router
from src.bot.keyboards.keyboadrs import get_main_menu
from src.bot.middlewares.db import DbSessionMiddleware
from src.db.session import async_session


load_dotenv()

WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

async def main():
    # Включаем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    # Инициализируем бота и диспетчер
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем middleware
    dp.message.middleware(DbSessionMiddleware(session_pool=async_session))

    # Регистрируем роутеры
    dp.include_router(catalog_router)
    dp.include_router(web_app_router)

    @dp.message(Command("start"))
    async def send_welcome(message: Message):
        await message.answer(
            f"Привет, {message.from_user.first_name}! 👋\n"
            "Добро пожаловать в наш новый магазин.",
            reply_markup=get_main_menu(WEBAPP_URL)
        )

    logging.info("Бот запущен и готов к работе...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



