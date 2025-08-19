from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from datetime import datetime

from app.models import Chat, Message, Matchs
from app.chat.schemas import MessageCreate

async def get_chat_by_users_and_type(db: AsyncSession, user1_id: int, user2_id: int, chat_type: str):
    result = await db.execute(
        select(Chat).where(
            and_(
                or_(
                    and_(Chat.user1_id == user1_id, Chat.user2_id == user2_id),
                    and_(Chat.user1_id == user2_id, Chat.user2_id == user1_id)
                ),
                Chat.chat_type == chat_type
            )
        )
    )
    return result.scalars().first()

async def create_chat(db: AsyncSession, user1_id: int, user2_id: int, chat_type: str):
    chat = Chat(user1_id=user1_id, user2_id=user2_id, chat_type=chat_type)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat

async def get_or_create_chat(db: AsyncSession, user1_id: int, user2_id: int, chat_type: str, is_mutual_like_check: bool = False):
    chat = await get_chat_by_users_and_type(db, user1_id, user2_id, chat_type)
    if chat:
        return chat
    
    if chat_type == "tinder" and is_mutual_like_check:
        # Проверяем взаимный лайк
        mutual_like_result = await db.execute(
            select(Matchs).where(
                and_(
                    Matchs.from_user_id == user2_id,
                    Matchs.to_user_id == user1_id
                )
            )
        )
        mutual_like = mutual_like_result.scalars().first()
        if not mutual_like:
            # Взаимного лайка нет — чат не создаём
            return None
    
    return await create_chat(db, user1_id, user2_id, chat_type)

async def send_message(db: AsyncSession, chat_id: int, sender_id: int, message_data: MessageCreate) -> Message:
    new_message = Message(
        chat_id=chat_id,
        sender_id=sender_id,
        content=message_data.content,
        timestamp=datetime.utcnow()
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

async def get_messages(db: AsyncSession, chat_id: int) -> list[Message]:
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.timestamp)
    )
    return result.scalars().all()