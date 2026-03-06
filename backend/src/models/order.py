from decimal import Decimal as PyDecimal
from sqlalchemy import Integer, String, ForeignKey, Numeric, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from src.db.base_class import Base 


class Order(Base):
    """Модель заказа"""

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=True)
    total_price: Mapped[PyDecimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="в ожидании") 
   
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """Модель позиции в заказе"""

    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False) # Текущее название на момент покупки
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[PyDecimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")



