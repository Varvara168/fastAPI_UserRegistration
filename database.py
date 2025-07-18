import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()
# обязательно должно быть

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
