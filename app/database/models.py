from sqlalchemy import BigInteger, String, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime

# Используйте свою базу данных
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), default='-')
    first_name: Mapped[str] = mapped_column(String(100), default='-')
    last_name: Mapped[str] = mapped_column(String(100), default='-')
    
    # Реквизиты
    TON: Mapped[str] = mapped_column(String(100), default='-')
    BNB: Mapped[str] = mapped_column(String(100), default='-')
    RUB: Mapped[str] = mapped_column(String(100), default='-')
    UAH: Mapped[str] = mapped_column(String(100), default='-')
    USDT: Mapped[str] = mapped_column(String(100), default='-')
    
    # Данные сделки
    offer_fiat: Mapped[str] = mapped_column(String(20), default='-')
    discripton_fiat: Mapped[str] = mapped_column(String(500), default='-')
    sum_fiat: Mapped[str] = mapped_column(String(50), default='-')
    
    # Статистика
    successful_deals: Mapped[int] = mapped_column(Integer, default=0)
    failed_deals: Mapped[int] = mapped_column(Integer, default=0)
    total_deals: Mapped[int] = mapped_column(Integer, default=0)
    
    # Даты
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_active: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"User(id={self.id}, tg_id={self.tg_id}, username={self.username})"

class Offer(Base):
    __tablename__ = 'offers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    seller_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    buyer_id: Mapped[int] = mapped_column(BigInteger, default=0)
    currency: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(500), default='')
    status: Mapped[str] = mapped_column(String(20), default='pending')  # pending, active, completed, cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"Offer(id={self.id}, offer_id={self.offer_id}, status={self.status})"

async def async_main():
    """Создает таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных успешно инициализирована")