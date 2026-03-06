import os
from dotenv import load_dotenv
import json
from aiogram import Router, F, Bot, types
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.product import Product
from src.repositories.order_repository import OrderRepository
from src.repositories.product_repository import ProductRepository
from src.schemas.order_schema import OrderCreate, OrderItemCreate
from src.core.config import settings


load_dotenv()
MANAGER_ID = os.getenv("MANAGER_ID")

router = Router()

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message, db_session: AsyncSession, bot: Bot):
    """
    Хендлер для приема заказа.
    Принимает JSON из Mini App, запрашивает детали товаров в БД
    и формирует итоговый чек.
    """
    order_text = ""
    try:
        # 1. Получаем данные из Mini App
        data = json.loads(message.web_app_data.data)
        cart_items = data.get("items", {}) # Формат: {"1": 2, "5": 1}

        if not cart_items:
            await message.answer("Корзина пуста.")
            return
        
        # Превращаем ключи (ID) в числа
        product_ids = [int(pid) for pid in cart_items.keys()]

        # 3. Запрос в БД для получения НАЗВАНИЙ и АКТУАЛЬНЫХ ЦЕН
        query = (
            select(Product)
            .where(Product.id.in_(product_ids))
            .options(selectinload(Product.variants))
        )
        result = await db_session.execute(query)
        products = result.scalars().all()

        # 3. Формируем текст заказа
        items_details = ""
        calculated_total = 0

        for product in products:
            quantity = cart_items.get(str(product.id))
            # Берем цену первого варианта, как в React
            price = product.variants[0].price if product.variants else 0
            subtotal = price * quantity
            calculated_total += subtotal

        # Собираем итоговый текст заказа
        order_text = "<b>📦 СОСТАВ ЗАКАЗА:</b>\n"
        order_text += items_details
        order_text += "--------------------------\n"
        order_text += f"💰 <b>ИТОГО: {calculated_total} ₽</b>"

        # 3. Отправляем ответ пользователю
        await message.answer(f"✅ Ваш заказ принят!\n\n{order_text}\n\n📞 Менеджер свяжется с вами в ближайшее время.", parse_mode="HTML")

        # 4. Формируем сообщение для админа
        if MANAGER_ID:
            admin_report = "<b>🔔 НОВЫЙ ЗАКАЗ!</b>\n\n"
            admin_report += f"👤 Покупатель: @{message.from_user.username or 'без username'}\n"
            admin_report += f"🆔 ID: <code>{message.from_user.id}</code>\n"
            admin_report += "--------------------------\n"
            admin_report += order_text # Добавляем состав заказа из твоего кода

        # 5. Отправляем админу
        await bot.send_message(chat_id=MANAGER_ID, text=admin_report, parse_mode="HTML")
    
    except Exception as e:
        print(f"❌ Ошибка при обработке заказа: {e}")
        await message.answer("Произошла ошибка при обработке заказа. Попробуйте позже.")

