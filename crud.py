from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models import *
from app.schemas import UserCreate, UserUpdate, PostCreate
import os

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: UserCreate):
    
    db_user = User(
    username=user.username,
    email=user.email,
    hashed_password=user.hashed_password,
    name=user.name,
    city=user.city,
    age=user.age,
    gender=user.gender)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_post_with_tags(db: AsyncSession, post_data: PostCreate, user_id: int):
    db_post = Post(
        title=post_data.title,
        content=post_data.content,
        user_id=user_id,
        created_at=datetime.utcnow()
    )

    # 🔍 Загружаем все теги по переданным id
    if post_data.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(post_data.tag_ids)))
        tags = result.scalars().all()
        db_post.tags = tags

    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

async def update_user(db: AsyncSession, user_id: int, data: UserUpdate):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user
    
async def soft_delete_user(user: User, db: AsyncSession):
    # Софт-делит самого пользователя
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    db.add(user)

    # Софт-делит все посты
    for post in user.posts:
        post.is_deleted = True
        post.deleted_at = datetime.utcnow()
        db.add(post)

    # Софт-делит все интересы
    for interest in user.interests:
        interest.is_deleted = True
        interest.deleted_at = datetime.utcnow()
        db.add(interest)

    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise Exception("User not found")
    for post in user.posts:
        if post.file_path:
            try:
                os.remove(post.file_path)
            except FileNotFoundError:
                pass
        await db.delete(post)
                
    await db.delete(user)
    await db.commit()
    return user

# ✅ Получение всех активных (не удалённых) постов с пагинацией и фильтрацией
async def get_posts(db: AsyncSession, post_id: int):
    result = await db.execute(select(Post).options(selectinload(Post.tags)).where(Post.id == post_id))
    return result.scalar_one_or_none()

# ✅ Мягкое удаление поста
async def soft_delete_post(db: AsyncSession, post_id: int):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        return None

    post.is_deleted = True
    post.deleted_at = datetime.utcnow()
    await db.commit()
    return post

# ✅ Восстановление поста (если прошло меньше 6 месяцев)
async def restore_post(db: AsyncSession, post_id: int):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post or not post.is_deleted:
        return None

    if datetime.utcnow() - post.deleted_at > timedelta(days=180):
        return None  # слишком поздно

    post.is_deleted = False
    post.deleted_at = None
    await db.commit()
    return post
