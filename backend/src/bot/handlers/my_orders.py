from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.order_repository import OrderRepository


router = Router()

@router.message(F.text =="📦 Мои заказы")
async def show_my_orders(message: Message, db_session: AsyncSession):
    """Хендлер для отображения всех заказов пользователя."""

    repo = OrderRepository(db_session)
    orders = await repo.get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("У вас пока нет заказов. 😔")
        return

    # Показываем последние 5 заказов
    await message.answer("<b>📜 История ваших заказов:</b>", parse_mode="HTML")
    
    for order in orders[:5]:
        # Определяем статус и эмодзи
        status_lower = order.status.lower()
        if "ожидании" in status_lower:
            emoji = "⏳"
        elif "оплачен" in status_lower:
            emoji = "✅"
        elif "отправлен" in status_lower:
            emoji = "🚛"
        elif "доставлен" in status_lower:
            emoji = "🎉"
        elif "отменен" in status_lower:
            emoji = "❌"
        
        text = (
            f"{emoji} <b>Заказ №{order.id}</b>\n"
            f"💰 Сумма: {order.total_price} ₽\n"
            f"📅 Статус: <i>{order.status}</i>"
        )
        # Кнопка для просмотра состава заказа
        view_order_button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔍 Детали заказа", 
                callback_data=f"order_details_{order.id}"
            )]
        ])

        await message.answer(text=text, reply_markup=view_order_button, parse_mode="HTML")