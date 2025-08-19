from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Interest, User
from app.interests.schemas import *

async def create_interest(db: AsyncSession, interest: InterestCreate):
    new_interest = Interest(name=interest.name)
    db.add(new_interest)
    await db.commit()
    await db.refresh(new_interest)
    return new_interest

async def get_interests(db: AsyncSession):
    result = await db.execute(select(Interest))
    return result.scalars().all()

async def update_user_interests(
    db: AsyncSession,
    user: User,
    interests_update: UserUpdateInterests
):
    # Получаем интересы по ID
    stmt = select(Interest).where(Interest.id.in_(interests_update.interests))
    result = await db.execute(stmt)
    interests = result.scalars().all()

    # Привязываем интересы к пользователю
    user.interests = interests
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user