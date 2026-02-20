from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repositories.base_repository import BaseRepository
from src.models.product import Product, ProductVariant


class ProductRepository(BaseRepository[Product]):
    async def get_with_variants(self, product_id: int) -> Optional[Product]:
        """
        Получить товар со всеми его вариантами (объемами).
        selectinload для решения проблемы N+1.
        """ 
        query = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.variants))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    

    async def get_multi_with_variants(self, skip: int = 0, limit: int = 100):
        """Получить список товаров вместе с вариантами"""
        query = (
            select(Product)
            .options(selectinload(Product.variants))
            .offset(skip)
            .limit(limit)     
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    
