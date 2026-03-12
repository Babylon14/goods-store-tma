import os
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from src.repositories.order_repository import OrderRepository


load_dotenv()
router = Router()
MANAGER_ID = os.getenv("MANAGER_ID")

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


@router.callback_query(F.data.startswith("order_details_"))
async def show_order_details(callback: CallbackQuery, db_session: AsyncSession):
    """Хендлер для отображения деталей заказа."""
    order_id = int(callback.data.split("_")[-1])
    repo = OrderRepository(db_session)

    order = await repo.get_user_orders(callback.from_user.id)
    target_order = next((o for o in order if o.id == order_id), None)

    if not target_order:
        await callback.answer("Заказ не найден", show_alert=True)
        return
    
    details = f"<b>📦 Состав заказа №{order_id}:</b>\n\n"
    for item in target_order.items:
        details += f"🔹 {item.title} — {item.quantity} шт. ({item.price} ₽)\n"
    details += f"\n<b>Итого: {target_order.total_price} ₽</b>"

    # Создаем клавиатуру
    keyboard = InlineKeyboardBuilder()

    # Если нажал админ — добавляем кнопку управления
    if callback.from_user.id == MANAGER_ID:
        keyboard.button(text="🔧 Изменить статус (ADMIN)", callback_data=f"admin_status_{order_id}")
    keyboard.adjust(1)
    
    # Отправляем новым сообщением или меняем текущее
    await callback.message.answer(details, reply_markup=keyboard.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_status_"))
async def admin_choose_status(callback: CallbackQuery):
    """Хендлер АДМИНА для выбора статуса заказа."""
    order_id = int(callback.data.split("_")[-1])

    # Создаем клавиатуру
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="📦 В ожидании", callback_data=f"set_status_{order_id}_В ожидании")
    keyboard.button(text="✅ Оплачен", callback_data=f"set_status_{order_id}_Оплачен")
    keyboard.button(text="🚛 Отправлен", callback_data=f"set_status_{order_id}_Отправлен")
    keyboard.button(text="🚚 Доставлен", callback_data=f"set_status_{order_id}_Доставлен")
    keyboard.button(text="❌ Отменен", callback_data=f"set_status_{order_id}_Отменен")
    keyboard.adjust(2)

    await callback.message.edit_text(
        f"Выберите новый статус для заказа №{order_id}:", reply_markup=keyboard.as_markup()
    )

