from app.database.models import async_session, User
from sqlalchemy import select, update
from sqlalchemy.orm import sessionmaker

async def set_user(tg_id: int) -> None:
    """Создает пользователя в БД если его нет"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            # Создаем нового пользователя с именем
            from aiogram.types import User as TgUser
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()
            print(f"Создан новый пользователь с ID: {tg_id}")

async def update_user_field(user_id: int, field_name: str, new_value: str):
    """Обновляет поле пользователя"""
    async with async_session() as session:
        stmt = update(User).where(User.tg_id == user_id).values(**{field_name: new_value})
        await session.execute(stmt)
        await session.commit()

async def defolt_user_field(user_id: int, field_name: str):
    """Удаляет реквизит пользователя"""
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == user_id)
            .values(**{field_name: '-'})
        )
        await session.commit()

async def delete_user_field(user_id: int):
    """Удаляет все реквизиты пользователя"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            user.TON = '-'
            user.BNB = '-'
            user.RUB = '-'
            user.UAH = '-'
            user.USDT = '-'
            await session.commit()

async def get_fiat(user_id: int, fiat: str) -> str:
    """Получает реквизит пользователя"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            value = getattr(user, fiat, '-')
            return value if value else '-'
        return '-'

async def get_successful_deals(user_id: int) -> int:
    """Получает количество успешных сделок"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user and hasattr(user, 'successful_deals'):
            return user.successful_deals
        return 0

async def create_offer(user_id: int, currency: str, amount: float, description: str) -> int:
    """Создает новую сделку и возвращает ее ID"""
    async with async_session() as session:
        # Здесь должна быть логика создания сделки
        # Пока возвращаем временный ID
        from datetime import datetime
        import random
        offer_id = int(datetime.now().timestamp() * 1000) + random.randint(100, 999)
        return offer_id

async def get_user_by_id(user_id: int):
    """Получает пользователя по ID"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        return user