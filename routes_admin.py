from fastapi import APIRouter, Depends, Query, HTTPException, Header, Request, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import os
from datetime import datetime

from app.dependencies import get_current_user
from app import models, schemas, auth, crud
from app.database import get_db
from app.dependencies import get_current_user

from app.config import settings


settings.ADMIN_SECRET_WORD
router = APIRouter()

@router.delete("/admin/delete_user", response_model=schemas.UserOut)
async def delete_existing_user(
    current_user: models.User = Depends(get_current_user),   
    x_admin_password: str = Header(alias="X-Admin-Password"),
    user_id: int = Query(..., description="id пользователя"),   
    db: AsyncSession = Depends(get_db)
):

    if current_user.username != "admin" or x_admin_password != settings.ADMIN_SECRET_WORD:
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    stmt = select(models.User).options(
        selectinload(models.User.posts), 
        selectinload(models.User.interests)
    ).where(models.User.id == user_id)

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")   
    
    await crud.delete_user(db, user_id)
    return user

# Только для админа 
@router.get("/admin/dashboard")
async def admin_dashboard(
    current_user: models.User = Depends(get_current_user),
    x_admin_password: str = Header(alias="X-Admin-Password")
):
    if current_user.username != "admin" or x_admin_password != settings.ADMIN_SECRET_WORD:
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")
    return {
        "message": "Welcome to the admin dashboard",
        "admin_user": current_user.username
    }
