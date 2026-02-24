from aiogram import Router, F
from aiogram.types import Message, URLInputFile
from aiogram.filters import Command

from src.bot.services.api_client import shop_api


router = Router()

@router.message(Command("/catalog"))
async def show_catalog(message: Message):
    """ Показать каталог товаров """
    product = await shop_api.get_products()

    if not product:
        await message.answer("Каталог пуст")
        return
    
    for prod in product:
        caption = f"<b>{prod['title']}</b>\n\n{prod.get('description', '')}\n"

        # Добавляем варианты (цены)
        if prod.get("variants"):
            for variant in prod["variants"]:
                caption += f"\n💰 {variant['size_name']}: {variant['price']} руб."

        # Если есть картинка, отправляем фото, если нет - только текст
        if prod.get("image_url"):
            # Внутри Docker-сети обращаемся к backend:8000
            image_url = f"http://backend:8000{prod['image_url']}"
            try:
                await message.answer_photo(
                    photo=URLInputFile(image_url),
                    caption=caption,
                    parse_mode="HTML"
                )
            except Exception as err:
                # Если фото не загрузилось, отправим хотя бы текст
                await message.answer(f"{caption}\n\n<i>(Ошибка загрузки фото)</i>", parse_mode="HTML")
        else:
            await message.answer(caption, parse_mode="HTML")

            
