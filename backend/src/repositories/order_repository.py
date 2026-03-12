from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repository import BaseRepository
from src.models.order import Order, OrderItem
from src.schemas.order_schema import OrderCreate


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    
    async def create_with_items(self, order_in_data: OrderCreate) -> Order:
        """Создает заказ вместе с его позициями в одной транзакции."""

        # 1. Подготавка данных самого заказа (без вложенных items)
        order_data = order_in_data.model_dump(exclude={"items"})
        db_order = Order(**order_data)

        self.session.add(db_order)
        await self.session.flush()

        # 2. Создаем позиции заказа (OrderItems)
        for item_data in order_in_data.items:
            db_item = OrderItem(
                order_id=db_order.id,
                **item_data.model_dump()
            )
            self.session.add(db_item)
        
        # 3. Фиксируем транзакцию
        await self.session.commit()
        await self.session.refresh(db_order)

        return await self.get_with_items(db_order.id)
    

    async def get_with_items(self, order_id: int) -> Optional[Order]:
        """Получает заказ вместе со всеми его позициями (eager loading)."""
        query = (
            select(self.model)
            .where(self.model.id == order_id)
            .options(selectinload(self.model.items))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        

    async def get_user_orders(self, user_id: int) -> List[Order]:
        """Получить историю всех заказов пользователя, отсортированные по дате (новые сверху)."""
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(selectinload(self.model.items))
            .order_by(self.model.id.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


    async def get_all_with_items(self, skip: int = 0, limit: int = 50) -> List[Order]:
        """Получить список всех заказов с вложенными вариантами. (пагинация)."""
        query = (
            select(self.model)
            .options(selectinload(self.model.items))
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id.desc()) # Сначала новые
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


    async def update_status(self, order_id: int, new_status: str) -> Order:
        """Обновляет статус заказа и возвращает обновленный объект."""
        query = (
            update(self.model)
            .where(self.model.id == order_id)
            .values(status=new_status)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()





