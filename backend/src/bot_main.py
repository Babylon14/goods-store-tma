import asyncio
import logging
from aiogram import Bot, Dispatcher

from src.core.config import settings
from src.bot.handlers import catalog


async def main():
    # Включаем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    # Инициализируем бота и диспетчер
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем роутеры
    dp.include_router(catalog.router)

    logging.info("Бот запущен и готов к работе...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

