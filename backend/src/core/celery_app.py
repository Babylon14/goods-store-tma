from celery import Celery
import os


# Берем URL из переменной окружения, которую ты добавил в .env
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
print(f"DEBUG: Celery подключился к Redis: {redis_url}") # Увидишь в логах Docker

celery_app = Celery(
    "shop_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["src.tasks.order_tasks"]
)

# Настройки для стабильности
celery_app.conf.update(
    task_track_started=True,                # Отслеживание статуса задач
    broker_connection_retry_on_startup=True, # Повторная попытка подключения к брокеру
    timezone="UTC",                         # Временная зона
    enable_utc=True,                        # Включение UTC
)


