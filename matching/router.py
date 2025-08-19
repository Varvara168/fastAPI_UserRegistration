from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
#from sqlalchemy.orm import Session -> AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.matching.crud import *
from app.models import User

router = APIRouter()

# Эндпоинт: текущий пользователь лайкает пользователя с id=user_id
@router.post("/match/{user_id}")
async def match_users(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя лайкнуть себя")
    
    # Пытаемся поставить лайк
    # ... match_user() -> await match_user()
    like = await match_user(db, current_user.id, user_id)
    if like is None:
        return {"message": "Вы уже лайкали этого пользователя"}

    # Проверяем, есть ли взаимный лайк
    mutual_like = await is_mutual_match(db, current_user.id, user_id)
    if mutual_like:
        return {"message": "Взаимный лайк! Вы теперь совпали 🥰"}

    return {"message": "Лайк отправлен"}
