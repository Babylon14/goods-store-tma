import asyncio

from src.core.celery_app import celery_app
from src.bot_main import bot
from src.services.notification_service import STATUS_NAMES


@celery_app.task(
    name="send_status_notification",
    bind=True,              # Дает доступ к объекту self (самой задаче)
    default_retry_delay=60, # Повторная попытка через 1 минуту
    max_retries=5           # Максимум 5 попыток
)
def send_status_notification_task(self, user_id: int, order_id: int, new_status: str):
    """Фоновая задача на отправку сообщения"""
    try:
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
    except Exception as exc:
        raise self.retry(exc=exc)

