from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.repositories.product_repository import ProductRepository
from src.repositories.order_repository import OrderRepository


async def get_product_repo(session: AsyncSession = Depends(get_async_session)) -> ProductRepository:
    """Dependency для получения репозитория товаров."""
    return ProductRepository(session)


async def get_order_repo(session: AsyncSession = Depends(get_async_session)) -> OrderRepository:
    """Dependency для получения репозитория заказов."""
    return OrderRepository(session)

