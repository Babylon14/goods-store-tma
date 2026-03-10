from src.bot_main import bot
from src.schemas.order_schema import OrderStatus

# Тексты для уведомлений
STATUS_NAMES = {
    OrderStatus.PENDING: "⏳ В ожидании",
    OrderStatus.PAID: "✅ Оплачен",
    OrderStatus.SHIPPED: "🚚 Отправлен",
    OrderStatus.DELIVERED: "🎁 Доставлен",
    OrderStatus.CANCELLED: "❌ Отменен"
}

async def notify_order_status_change(user_id: int, order_id: int, new_status: str):
    """Отправляет уведомление пользователю о смене статуса заказа."""
    status_text = STATUS_NAMES.get(new_status)
    message = (
        f"🔔 **Обновление заказа №{order_id}**\n\n"
        f"Статус вашего заказа изменен на: **{status_text}**"
    )
    try:
        await bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
    except Exception as err:
        print(f"Ошибка при отправке уведомления: {err}")

        