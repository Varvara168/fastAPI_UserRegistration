#from sqlalchemy.orm import Session -> AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Matchs

# Создаёт новый лайк, если его ещё не было
async def match_user(db: AsyncSession, from_user_id: int, to_user_id: int):
    result = await db.execute(
        select(Matchs).where(Matchs.from_user_id == from_user_id, Matchs.to_user_id == to_user_id)
    )
    existing_like = result.scalar_one_or_none()
    #existing_like = db.query(Matchs).filter_by(from_user_id=from_user_id, to_user_id=to_user_id).first()
    
    if existing_like:
        return None  # Лайк уже есть, не создаём повторно
    
    new_like = Matchs(from_user_id=from_user_id, to_user_id=to_user_id)
    db.add(new_like)
    await db.commit()
    await db.refresh()
    return new_like

# Проверяет, поставил ли to_user взаимный лайк от from_user (взаимность)
async def is_mutual_match(db: AsyncSession, from_user_id: int, to_user_id: int):
    result = await db.execute(
        select(Matchs).where(Matchs.from_user_id == to_user_id, Matchs.to_user_id == from_user_id)
    )
    mutual_like = result.scalar_one_or_none()
    return mutual_like is not None
    #return db.query(Matchs).filter_by(from_user_id=to_user_id, to_user_id=from_user_id).first() is not None

