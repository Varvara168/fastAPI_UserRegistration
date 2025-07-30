from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import *
from app.schemas import UserCreate, UserUpdate, PostCreate, Post

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password  # предполагаем, что уже хэширован
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: int, data: dict):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    for key, value in data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user

async def soft_delete_user(session: AsyncSession, user: User):
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    
    # Помечаем все посты пользователя как мягко удалённые, если они не удалены
    for post in user.posts:
        if not post.is_deleted:
            post.is_deleted = True
            post.deleted_at = datetime.utcnow()
    await session.commit()
async def add_tag_to_post(db: AsyncSession, post_id: int, tag_id: int):
    post = await db.get(Post, post_id)
    tag = await db.get(Tag, tag_id)
    post.tags.append(tag)
    await db.commit()
    await db.refresh(post)
    return post

# ✅ Создание нового поста
async def create_post(db: AsyncSession, post: PostCreate, author_id: int):
    db_post = Post(
        title=post.title,
        content=post.content,
        author_id=author_id
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

# ✅ Получение всех активных (не удалённых) постов с пагинацией и фильтрацией
async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 10, search: str = ""):
    stmt = (
        select(Post)
        .where(Post.is_deleted == False)
        .filter(Post.title.ilike(f"%{search}%"))
        .order_by(Post.id.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

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
