from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

class Service(Base):
    __tablename__ = 'services'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column()

class Booking(Base):
    __tablename__ = 'bookings'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    service_name: Mapped[str] = mapped_column(String(100))
    booking_date: Mapped[str] = mapped_column(String(50))

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)