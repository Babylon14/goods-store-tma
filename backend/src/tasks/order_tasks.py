import asyncio
from celery import shared_task

from src.bot_main import bot
from src.schemas.order_schema import OrderStatus
from src.services.notification_service import STATUS_NAMES


@shared_task(name="send_order_notification")
def send_order_notification(user_id: int, order_id: int, new_status: str):
    """Фоновая задача на отправку сообщения"""
    status_text = STATUS_NAMES.get(new_status, new_status)
    message = (
        f"🔔 **Обновление заказа №{order_id}**\n\n"
        f"Статус Вашего заказа изменен на: **{status_text}**"
    )
    # Трюк: запускаем асинхронную отправку внутри синхронного Celery
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
    )


    