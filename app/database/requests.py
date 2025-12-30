from app.database.models import async_session, User, Offer
from sqlalchemy import select, update, and_
import random
import string
import time

async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def update_user_field(user_id: int, field_name: str, new_value: str):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == user_id)
            .values(**{field_name: new_value})
        )
        await session.commit()

async def update_user_field_bool(user_id: int, field_name: str, new_value: bool):
    """Специальная функция для обновления булевых полей"""
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == user_id)
            .values(**{field_name: new_value})
        )
        await session.commit()

async def defolt_user_field(user_id: int, field_name: str):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == user_id)
            .values(**{field_name: '-'})
        )
        await session.commit()

async def delete_user_field(user_id: int):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == user_id).values(**{'TON': '-'}))
        await session.execute(update(User).where(User.tg_id == user_id).values(**{'BNB': '-'}))
        await session.execute(update(User).where(User.tg_id == user_id).values(**{'RUB': '-'}))
        await session.execute(update(User).where(User.tg_id == user_id).values(**{'UAH': '-'}))
        await session.execute(update(User).where(User.tg_id == user_id).values(**{'USDT': '-'}))
        await session.commit()

async def get_fiat(user_id, fiat):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            value = getattr(user, fiat, '-')
            if isinstance(value, bool):
                return str(value)
            return value if value else '-'
        return '-'

async def create_offer(seller_id: int, currency: str, amount: str, description: str):
    async with async_session() as session:
        # Генерируем уникальный ID сделки
        offer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Генерируем USDT адрес
        usdt_address = "UQBrw7SofA-xPDFpeksk2BFmeMJfKRcLkIdsjNOcojxhJ3lC"
        
        # Генерируем секретный код
        secret_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        offer = Offer(
            offer_id=offer_id,
            seller_id=seller_id,
            amount=amount,
            currency=currency,
            description=description,
            status='created',
            created_at=str(int(time.time())),
            usdt_address=usdt_address,
            secret_code=secret_code
        )
        
        session.add(offer)
        await session.commit()
        
        # Обновляем пользователя
        await update_user_field(seller_id, 'current_offer_id', offer_id)
        await update_user_field_bool(seller_id, 'is_seller', True)
        
        return offer_id, usdt_address

async def get_offer(offer_id: str):
    async with async_session() as session:
        offer = await session.scalar(select(Offer).where(Offer.offer_id == offer_id))
        return offer

async def update_offer_status(offer_id: str, status: str):
    async with async_session() as session:
        await session.execute(
            update(Offer)
            .where(Offer.offer_id == offer_id)
            .values(status=status)
        )
        await session.commit()

async def set_offer_buyer(offer_id: str, buyer_id: int):
    async with async_session() as session:
        await session.execute(
            update(Offer)
            .where(Offer.offer_id == offer_id)
            .values(buyer_id=buyer_id, status='waiting_payment')
        )
        await session.commit()

async def get_active_offer_by_buyer(buyer_id: int):
    """Получает активную сделку по ID покупателя"""
    async with async_session() as session:
        offer = await session.scalar(select(Offer).where(
            and_(
                Offer.buyer_id == buyer_id,
                Offer.status.in_(['waiting_payment', 'created'])
            )
        ))
        return offer

async def get_active_offer_by_user(user_id: int):
    """Получает активную сделку по ID пользователя (покупатель или продавец)"""
    async with async_session() as session:
        offer = await session.scalar(select(Offer).where(
            and_(
                (Offer.seller_id == user_id) | (Offer.buyer_id == user_id),
                Offer.status.in_(['waiting_payment', 'created', 'paid'])
            )
        ))
        return offer

async def complete_offer(offer_id: str):
    async with async_session() as session:
        await session.execute(
            update(Offer)
            .where(Offer.offer_id == offer_id)
            .values(status='completed')
        )
        await session.commit()


async def get_support_staff_id(user_id: int):
    """Получает ID сотрудника техподдержки из настроек пользователя"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user and user.support_staff_id:
            return user.support_staff_id
        return '8116809152'  # Дефолтный ID вашего сотрудника

async def update_offer_gift_sent(offer_id: str):
    """Отмечаем что подарок отправлен"""
    async with async_session() as session:
        await session.execute(
            update(Offer)
            .where(Offer.offer_id == offer_id)
            .values(gift_sent=True, status='gift_sent')
        )
        await session.commit()

# Добавим новую функцию для получения информации о сотруднике
async def get_support_info():
    """Получает информацию о сотруднике техподдержки"""
    return {
        'user_id': '8116809152',  # ID вашего сотрудника
        'username': '@definitely_support',  # Юзернейм вашего сотрудника
        'name': 'Сотрудник Техподдержки'  # Имя сотрудника
    }

