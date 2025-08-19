from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.interests.schemas import *
from app.interests.crud import *
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import UserOut


from typing import List

router = APIRouter()

@router.post("/interests/", response_model=InterestRead)
async def add_interest(interest: InterestCreate, db: AsyncSession = Depends(get_db)):
    return await create_interest(db, interest)

@router.get("/interests/", response_model=List[InterestRead])
async def list_interests(db: AsyncSession = Depends(get_db)):
    return await get_interests(db)


@router.put("/me/interests", response_model=UserOut)
async def update_my_interests(
    interests_update: UserUpdateInterests,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await update_user_interests(db, current_user, interests_update)