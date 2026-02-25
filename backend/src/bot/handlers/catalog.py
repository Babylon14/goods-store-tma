import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from src.bot.services.api_client import shop_api


router = Router()

@router.message(Command("catalog"))
async def show_catalog(message: Message):
    # Используем logging вместо print для надежности
    import logging
    logging.info("--- ХЕНДЛЕР КАТАЛОГА ВЫЗВАН ---")
    
    products = await shop_api.get_products()
    logging.info(f"ДАННЫЕ ИЗ API: {products}")

    if not products:
        await message.answer("Каталог пока пуст.")
        return

    for prod in products:
        caption = f"<b>{prod['title']}</b>\n\n{prod.get('description') or ''}\n"
        
        if prod.get("variants"):
            for v in prod["variants"]:
                caption += f"\n💰 {v['size_name']}: {v['price']} руб."

        image_url = prod.get("image_url")
        if image_url:
            # Превращаем /static/products/file.jpg в /app/backend/uploads/products/file.jpg
            # Путь должен быть абсолютным внутри контейнера!
            file_path = os.path.join("/app/backend", image_url.lstrip("/").replace("static", "uploads", 1))
            
            if os.path.exists(file_path):
                await message.answer_photo(
                    photo=FSInputFile(file_path),
                    caption=caption,
                    parse_mode="HTML"
                )
                continue # Переходим к следующему товару

        # Если фото нет или путь неверный - шлем текст
        await message.answer(caption, parse_mode="HTML")


        