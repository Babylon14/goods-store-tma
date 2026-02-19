from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    От него будут наследоваться все модели в папке src/models/
    """
    # 1. id будет у всех таблиц автоматически
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 2. Даты создания и обновления (автоматические)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__.lower()
    
