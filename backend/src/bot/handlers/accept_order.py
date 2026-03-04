import json
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.product import Product


router = Router()

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message, db_session: AsyncSession):
    """
    Хендлер для приема заказа.
    Принимает JSON из Mini App, запрашивает детали товаров в БД
    и формирует итоговый чек.
    """
    try:
        # 1. Получаем данные из Mini App
        data = json.loads(message.web_app_data.data)
        cart_items = data.get("items", {}) # Формат: {"1": 2, "5": 1}
        total_price_app = data.get("totalPrice", 0)

        if not cart_items:
            await message.answer("Корзина пуста.")
            return 

        # Превращаем ключи (ID) в числа
        product_ids = [int(pid) for pid in cart_items.keys()]

        # 2. Запрос в БД для получения НАЗВАНИЙ и АКТУАЛЬНЫХ ЦЕН
        query = (
            select(Product)
            .where(Product.id.in_(product_ids))
            .options(selectinload(Product.variants))
        )
        result = await db_session.execute(query)
        products = result.scalars().all()

        # 3. Формируем текст заказа
        order_text = "<b>🔔 НОВЫЙ ЗАКАЗ!</b>\n\n"
        order_text += f"👤 Покупатель: {message.from_user.full_name}\n"
        order_text += "--------------------------\n"

        calculated_total = 0
        for product in products:
            quantity = cart_items.get(str(product.id))
            # Берем цену первого варианта, как в React
            price = product.variants[0].price if product.variants else 0
            subtotal = price * quantity
            calculated_total += subtotal

            order_text += f"🔹 <b>{product.title}</b>\n"
            order_text += f"   {quantity} шт. × {price} ₽ = {subtotal} ₽\n"
        order_text += "--------------------------\n"
        order_text += f"💰 <b>ИТОГО К ОПЛАТЕ: {calculated_total} ₽</b>"

        # 4. Отправляем ответ пользователю
        await message.answer(order_text, parse_mode="HTML")
    
    except Exception as e:
        print(f"Ошибка при обработке заказа: {e}")
        await message.answer("Произошла ошибка при обработке заказа. Попробуйте позже.")


