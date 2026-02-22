from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repositories.base_repository import BaseRepository
from src.models.product import Product, ProductVariant


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(Product, session)

    async def get_with_variants(self, product_id: int) -> Optional[Product]:
        """
        Получить один товар со всеми его вариантами по ID.
        selectinload для решения проблемы N+1.
        """ 
        query = (
            select(self.model)
            .where(self.model.id == product_id)
            .options(selectinload(self.model.variants))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    

    async def get_multi_with_variants(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Получить список товаров с подгруженными вариантами (пагинация)."""
        query = (
            select(self.model)
            .options(selectinload(self.model.variants))
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id)     
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create_with_variants(self, obj_in_data: dict) -> Product:
        """
        Специальный метод создания, который умеет сразу добавлять варианты.
        Ожидает, что в словаре obj_in_data есть ключ 'variants' со списком словарей.
        """
        variants_data = obj_in_data.pip("variants", [])

        # Создание объекта товара
        db_obj = self.model(**obj_in_data)

        # Создание объектов вариантов и привязывание их к товару
        for var_data in variants_data:
            variant = ProductVariant(**var_data)
            db_obj.variants.append(variant)

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    
