from celery import Celery
import os

# Берем URL из переменной окружения, которую ты добавил в .env
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "shop_tasks",
    broker=redis_url,
    backend=redis_url
)

@celery_app.task
def send_order_notification(order_id: int):
    # Здесь будет логика отправки сообщения менеджеру через бота
    print(f"Отправка уведомления по заказу №{order_id}")
    return True

