import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models import Base  # импортируй Base из своего файла с моделями

# Твой URL к базе данных PostgreSQL с asyncpg
DATABASE_URL = 'postgresql+asyncpg://user:password@localhost/dbname'

async_engine = create_async_engine(DATABASE_URL, echo=True)

async def create_tables():
    async with async_engine.begin() as conn:
        # Асинхронно запускаем синхронный метод создания таблиц
        await conn.run_sync(Base.metadata.create_all)
    await async_engine.dispose()  # Закрываем движок после создания

if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Таблицы созданы")
