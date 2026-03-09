from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal as PyDecimal
from typing import List, Optional
from datetime import datetime
from enum import Enum


# --- СХЕМЫ ДЛЯ ПОЗИЦИЙ ЗАКАЗА (OrderItem) ---
class OrderItemBase(BaseModel):
    product_id: int
    title: str
    quantity: int = Field(..., gt=0) # Количество всегда больше 0
    price: PyDecimal


class OrderItemCreate(OrderItemBase):
    """Используется при создании позиции в БД"""
    pass


class OrderItemRead(OrderItemBase):
    """Схема для отображения позиции (с ID)"""
    id: int
    order_id: int

    model_config = ConfigDict(from_attributes=True)


# --- СХЕМЫ ДЛЯ САМОГО ЗАКАЗА (Order) ---
class OrderBase(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    total_price: PyDecimal
    status: str = "в ожидании"


class OrderCreate(OrderBase):
    """Список позиций, используется для создания вместе с заказом"""
    items: List[OrderItemCreate]


class OrderRead(OrderBase):
    """Полная схема заказа для API (например, для истории заказов)"""
    id: int
    created_at: datetime
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)


class OrderStatus(str, Enum):
    """Статусы заказа"""
    PENDING = "В ожидании"
    PAID = "Оплачен"
    SHIPPED = "Отправлен"
    DELIVERED = "Доставлен"
    CANCELLED = "Отменен"


class OrderUpdateStatus(BaseModel):
    """Для смены статуса заказа (например, из группы админа)"""
    status: OrderStatus

    