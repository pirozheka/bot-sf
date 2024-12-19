from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.future import select
from datetime import datetime

# Создаем асинхронный движок для подключения к базе данных PostgreSQL
DATABASE_URL = 'postgresql+asyncpg://user:userpassword@localhost:5433/bulletjournal'
engine = create_async_engine(DATABASE_URL, echo=True)


# Создаем базовый класс для моделей - это наследование обязательно
class Base(DeclarativeBase):
    pass


# Определяем модель для пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, unique=True, nullable=False)  # ID чата, уникальное поле

# Создаем асинхронную сессию
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Асинхронное создание таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Логика создания пользователя 
async def create_user(chat_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.chat_id == chat_id)
        )
        existing_user = result.scalar_one_or_none()
        # Проверка на существование пользователя
        if existing_user:
            return existing_user.id

        new_user = User(chat_id=chat_id)
        session.add(new_user)
        await session.commit()
        return new_user.id  # Возвращаем ID нового пользователя