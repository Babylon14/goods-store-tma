import asyncio
import logging

from src.core.celery_app import celery_app
from src.services.notification_service import STATUS_NAMES


logger = logging.getLogger(__name__)

def run_async(coro):
    """Вспомогательная функция для запуска асинхронного кода в Celery."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@celery_app.task(
    name="send_status_notification",
    bind=True,              # Дает доступ к объекту self (самой задаче)
    default_retry_delay=60, # Повторная попытка через 1 минуту
    max_retries=5           # Максимум 5 попыток
)
def send_status_notification_task(self, user_id: int, order_id: int, new_status: str):
    """Фоновая задача на отправку сообщения."""
    from src.bot_main import bot
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


@celery_app.task(name="check_payment_reminder")
def check_payment_reminder_task(user_id: int, order_id: int):
    """Фоновая задача на отправку напоминания о неоплате."""
    from src.db.session import async_session
    from src.repositories.order_repository import OrderRepository
    from src.bot_main import bot

    async def run_check():
        async with async_session() as session:
            order_repo = OrderRepository(session)
            order = await order_repo.get(order_id)

            logger.info(f"DEBUG: Заказ {order_id} найден? {bool(order)}. Статус в БД: '{order.status if order else 'N/A'}'")
            if order and order.status.lower() == "в ожидании":
                text = (
                    f"⚠️ **Ваш заказ №{order_id} ожидает оплаты**\n\n"
                    f"Вы не завершили оформление. Если возникли трудности, "
                    f"нажмите на кнопку О нас. Там вы найдете наши контакты.\n\n"
                    f"Мы придержали товары для вас! 📦"
                )
                await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
                logger.info(f"Напоминание отправлено для заказа {order_id}")
            else:
                status = order.status if order else "None"
                logger.info(f"Напоминание для {order_id} пропущено (статус: {status})")
    run_async(run_check())



