from app.database.models import async_session, Service, Booking
from sqlalchemy import select, delete

async def get_services():
    async with async_session() as session:
        result = await session.scalars(select(Service))
        return result.all()

async def get_service_by_id(service_id: int):
    async with async_session() as session:
        return await session.scalar(select(Service).where(Service.id == service_id))

async def add_service(title: str, description: str, price: int):
    async with async_session() as session:
        session.add(Service(title=title, description=description, price=price))
        await session.commit()

async def add_booking(user_id: int, name: str, phone: str, service_name: str, booking_date: str):
    async with async_session() as session:
        session.add(Booking(
            user_id=user_id,
            name=name,
            phone=phone,
            service_name=service_name,
            booking_date=booking_date
        ))
        await session.commit()

async def get_all_bookings():
    async with async_session() as session:
        result = await session.scalars(select(Booking))
        return result.all()

async def get_booked_times():
    async with async_session() as session:
        result = await session.scalars(select(Booking.booking_date))
        return result.all()

async def get_user_bookings(user_id: int):
    async with async_session() as session:
        result = await session.scalars(select(Booking).where(Booking.user_id == user_id))
        return result.all()

async def delete_booking_by_id(booking_id: int):
    async with async_session() as session:
        await session.execute(delete(Booking).where(Booking.id == booking_id))
        await session.commit()