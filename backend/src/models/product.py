from sqlalchemy import String, Text, ForeignKey, Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from decimal import Decimal as PyDecimal

from src.db.base_class import Base


class Product(Base):
    """
    Основная модель Товар.
    Содержит общие данные: название, описание, изображения.
    """
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)

    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product")


class ProductVariant(Base):
    """
    Вариант Товара (объемы/емкости)
    Здесь хранятся цена и остатки.
    """
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"))

    size_name: Mapped[str] = mapped_column(String(50)) # "100 мл", "500 мл", "1 л"
    price: Mapped[PyDecimal] = mapped_column(Decimal(10, 2))
    stock: Mapped[int] = mapped_column(default=0)  # Количество в наличии

    product: Mapped["Product"] = relationship("Product", back_populates="variants")

