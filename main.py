import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.handlers import router
from app.database.models import async_main, async_session, Service
from sqlalchemy import select

async def seed_initial_services():
    async with async_session() as session:
        result = await session.scalars(select(Service))
        services = result.all()
        
        if not services:
            initial_services = [
                Service(
                    title="Стрижка + Укладка", 
                    description="Классическая или трендовая стрижка", 
                    price=5000
                ),
                Service(
                    title="Оформление бороды", 
                    description="Моделирование, контуры и уход", 
                    price=3000
                ),
                Service(
                    title="Комплекс (Стрижка + Борода)", 
                    description="Полный уход по спеццене", 
                    price=7000
                )
            ]
            session.add_all(initial_services)
            await session.commit()

async def main():
    await async_main()
    await seed_initial_services()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("Booking Bot успешно запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")