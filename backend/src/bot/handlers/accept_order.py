import os
from dotenv import load_dotenv
import json
from aiogram import Router, F, Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

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
    from src.tasks.order_tasks import check_payment_reminder_task
    
    # Инициализируем переменные
    items_summary_text = ""
    order_items_list = []
    calculated_total = 0
    order_text = ""
    try:
        # 1. Получаем данные из Mini App
        data = json.loads(message.web_app_data.data)
        cart_items = data.get("items", {}) # Формат: {"1": 2, "5": 1}

        if not cart_items:
            await message.answer("Корзина пуста.")
            return
        
        # 2. Инициализируем репозитории
        product_repo = ProductRepository(db_session)
        order_repo = OrderRepository(db_session)

        # 2.1 Получаем детали товаров из базы данных
        product_ids = [int(pid) for pid in cart_items.keys()]
        products = await product_repo.get_by_ids(product_ids)

        # Если товаров в базе нет
        if not products:
            await message.answer("🛒 Ваша корзина пуста или товары не найдены.")
            return

        for product in products:
            quantity = cart_items.get(str(product.id))
            # Берем цену первого варианта, как в React
            price = product.variants[0].price if product.variants else 0
            subtotal = price * quantity
            calculated_total += subtotal

            # Формируем схему заказа для сохранения
            order_items_list.append(OrderItemCreate(
                product_id=product.id,
                title=product.title,
                quantity=quantity,
                price=price
            ))
            items_summary_text += f"🔹 <b>{product.title}</b>\n   {quantity} шт. × {price} ₽ = {subtotal} ₽\n"

        # 4. Создаем схему заказа для сохранения
        order_create_data = OrderCreate(
            user_id=message.from_user.id,
            user_name=message.from_user.full_name,
            total_price=calculated_total,
            items=order_items_list
        )
        # 5. Сохраняем заказ в БД
        new_order = await order_repo.create_with_items(order_create_data)

        # 6. Запускаем Celery задачу на напоминание
        check_payment_reminder_task.apply_async(
            args=[message.from_user.id, new_order.id],
            countdown=60. # Через сколько секунд придет напоминание
        )
        # 7. Формируем финальный текст
        order_text = f"<b>📦 ЗАКАЗ №{new_order.id}</b>\n"
        order_text += "--------------------------\n"
        order_text += items_summary_text
        order_text += "--------------------------\n"
        order_text += f"💰 <b>ИТОГО: {calculated_total} ₽</b>"

        # 8. Отправляем ответ пользователю
        await message.answer(f"✅ Ваш заказ принят!\n\n{order_text}\n\n📞 Менеджер свяжется с вами в ближайшее время.", parse_mode="HTML")

        # 9. Формируем сообщение для админа
        if settings.MANAGER_ID:
            admin_report = "<b>🔔 НОВЫЙ ЗАКАЗ!</b>\n\n"
            admin_report += f"👤 Покупатель: @{message.from_user.username or message.from_user.id}\n\n{order_text}"
            # 10. Отправляем админу
            await bot.send_message(chat_id=settings.MANAGER_ID, text=admin_report, parse_mode="HTML")
    
    except Exception as err:
        print(f"❌ Ошибка при обработке заказа: {err}")
        await message.answer("Произошла ошибка при обработке заказа. Попробуйте позже.")

