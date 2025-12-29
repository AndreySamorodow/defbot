from sqlalchemy import BigInteger, String, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
import random
import string

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    TON: Mapped[str] = mapped_column(default='-')
    BNB: Mapped[str] = mapped_column(default='-')
    RUB: Mapped[str] = mapped_column(default='-')
    UAH: Mapped[str] = mapped_column(default='-')
    USDT: Mapped[str] = mapped_column(default='-')
    offer_fiat: Mapped[str] = mapped_column(default='-')
    discripton_fiat: Mapped[str] = mapped_column(default='-')
    sum_fiat: Mapped[str] = mapped_column(default='-')
    user_name_buyer: Mapped[str] = mapped_column(default='-')
    
    # Новые поля для сделок
    current_offer_id: Mapped[str] = mapped_column(default='-')
    is_seller: Mapped[bool] = mapped_column(Boolean, default=False)
    current_buyer_id: Mapped[str] = mapped_column(default='-')
    
    # Поле для сотрудника техподдержки
    support_staff_id: Mapped[str] = mapped_column(default='123456789')  # ID вашего сотрудника

class Offer(Base):
    __tablename__ = 'offers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[str] = mapped_column(unique=True)
    seller_id: Mapped[int] = mapped_column(BigInteger)
    buyer_id: Mapped[int] = mapped_column(BigInteger, default=0)
    amount: Mapped[str] = mapped_column()
    currency: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(default='')
    status: Mapped[str] = mapped_column(default='created')  # created, waiting_payment, paid, gift_sent, completed
    created_at: Mapped[str] = mapped_column(default='')
    usdt_address: Mapped[str] = mapped_column(default='')
    secret_code: Mapped[str] = mapped_column(default='')
    gift_sent: Mapped[bool] = mapped_column(Boolean, default=False)  # Подарок отправлен
    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)