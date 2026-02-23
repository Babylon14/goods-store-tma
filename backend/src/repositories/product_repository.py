from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repositories.base_repository import BaseRepository
from src.models.product import Product, ProductVariant
from src.services.file_service import delete_file


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
        variants_data = obj_in_data.pop("variants", [])

        # Создание объекта товара
        db_obj = self.model(**obj_in_data)

        # Создание объектов вариантов и привязывание их к товару
        for var_data in variants_data:
            variant = ProductVariant(**var_data)
            db_obj.variants.append(variant)

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    
    async def delete(self, id: int) -> bool:
        """Удаляет товар и его изображение"""

        # 1. Находим товар перед удалением
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        # Запоминаем URL картинки
        image_to_delete = db_obj.image_url

        # 2. Удаляем запись из БД (вызываем базовый метод или делаем вручную)
        await self.session.delete(db_obj)
        await self.session.commit()

        # 3. Если в базе всё удалено — чистим диск
        if image_to_delete:
            delete_file(image_to_delete)
        return True


