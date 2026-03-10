from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.order_schema import OrderRead, OrderUpdateStatus
from src.repositories.order_repository import OrderRepository
from src.api.dependencies import get_order_repo
from src.services.notification_service import notify_order_status_change
from src.tasks.order_tasks import send_status_notification_task


router = APIRouter()

@router.get("/", response_model=List[OrderRead])
async def get_orders(
    skip: int = 0, 
    limit: int = 100,
    order_repo: OrderRepository = Depends(get_order_repo)
):
    """Получить список всех заказов с вложенными вариантами. (пагинация)."""
    orders = await order_repo.get_all_with_items(skip=skip, limit=limit)
    return orders


@router.get("/{order_id}", response_model=OrderRead)
async def get_order_by_id(
    order_id: int,
    order_repo: OrderRepository = Depends(get_order_repo)
):
    """Получить конкретный заказ со всеми его позициями по ID."""
    order = await order_repo.get_with_items(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return order


@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    order_id: int,
    status_data: OrderUpdateStatus,
    order_repo: OrderRepository = Depends(get_order_repo)
):
    """Смена статуса (из админки/Swagger) с уведомлением через Celery"""
    # 1. Получаем текущий заказ, чтобы узнать user_id
    db_order = await order_repo.get(order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    
    # Обновляем статус в БД
    updated_order = await order_repo.update_status(order_id, status_data.status)

    # 2. Отправляем уведомление в Celery (задача улетает в Redis)
    send_status_notification_task.delay(
        user_id=db_order.user_id, 
        order_id=order_id, 
        new_status=status_data.status
    )
    # 3. Возвращаем ответ в Swagger/Админку
    return await order_repo.get_with_items(updated_order.id)


