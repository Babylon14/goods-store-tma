from typing import Generic, Type, TypeVar, List, Optional, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base_class import Base


ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session


    async def get(self, id: Any) -> Optional[ModelType]:
        """Получить одну запись по ID"""
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить список записей с пагинацией"""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    

    async def create(self, obj_in_data: dict) -> ModelType:
        """Создать новую запись"""
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        await self.session.flush()  # Получаем ID без коммита всей транзакции
        return db_obj


    async def update(self, db_obj: ModelType, obj_in_data: dict | Any) -> ModelType:
        """
        Обновить запись в базе.
        db_obj: объект из базы, который мы уже получили через get()
        obj_in_data: либо словарь с новыми данными, либо Pydantic-схема
        """
        # Если пришла Pydantic-схема, превращаем её в словарь, исключая неустановленные поля
        if isinstance(obj_in_data, dict):
            update_data = obj_in_data
        else:
            update_data = obj_in_data.model_dump(exclude_unset=True)

        # Обновляем атрибуты объекта
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        self.session.add(db_obj)
        await self.session.flush() # Сохраняем изменения в текущей транзакции
        await self.session.refresh(db_obj) # Обновляем объект данными из базы
        return db_obj


    async def delete(self, id: Any) -> bool:
        """Удалить запись по ID"""
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.rowcount > 0 

