from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal as PyDecimal
from typing import List, Optional


# --- Схемы для Вариантов (Объемов) Товара ---
class ProductVariantBase(BaseModel):
    size_name: str = Field(..., examples="XL")
    price: PyDecimal = Field(..., gt=0, examples="1500.00")
    stock: int = Field(default=0, ge=0)


class ProductVariantCreate(ProductVariantBase):
    """Схема для создания варианта (используется внутри ProductCreate)"""
    pass


class ProductVariantRead(ProductVariantBase):
    """Схема для отображения варианта (с ID)"""
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Схемы для Самого Товара ---
class ProductBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    """Схема для создания товара вместе с его вариантами"""
    variants: List[ProductVariantCreate]


class ProductRead(ProductBase):
    """Схема для отдачи данных клиенту"""
    id: int
    variants: List[ProductVariantRead] = []

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    """Схема для частичного обновления товара"""
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


    