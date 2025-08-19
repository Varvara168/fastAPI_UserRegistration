from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.chat.crud import *

from app.chat.schemas import MessageCreate, MessageOut
from app.models import User

router = APIRouter()

@router.post("/chat/{chat_type}/{user_id}/message", response_model=MessageOut)
async def send_message_to_user(
    chat_type: str,
    user_id: int,
    msg_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя писать себе")

    # Проверка типа чата
    allowed_types = ["tinder", "family", "language", "work"]
    if chat_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Неверный тип чата")

    # Для Tinder — проверяем взаимный лайк перед созданием чата
    is_mutual_like_check = chat_type == "tinder"

    chat = await get_or_create_chat(db, current_user.id, user_id, chat_type, is_mutual_like_check)
    if chat is None:
        raise HTTPException(status_code=403, detail="Чат доступен только после взаимного лайка")

    message = await send_message(db, chat.id, current_user.id, msg_data.content)
    return message


@router.get("/chat/{chat_type}/{user_id}/messages", response_model=list[MessageOut])
async def get_chat_messages(
    chat_type: str,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_types = ["tinder", "family", "language", "work"]
    if chat_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Неверный тип чата")

    chat = await get_chat_by_users_and_type(db, current_user.id, user_id, chat_type)
    if chat is None:
        raise HTTPException(status_code=404, detail="Чат не найден")

    return await get_messages(db, chat.id)