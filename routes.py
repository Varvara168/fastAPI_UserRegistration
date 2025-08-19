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

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err['loc'])
        msg = err['msg']
        errors.append({'field': loc, 'error': msg})
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации данных",
            "errors": errors
        },
    )

@router.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверка существующего пользователя
    result = await db.execute(select(models.User).where(
        (models.User.email == user.email) | (models.User.username == user.username)
    ))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    hashed_password = auth.hash_password(user.password)

    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        city=user.city,
        age=user.age,
        gender=user.gender,
    )
    
    db.add(db_user)
    await db.commit()          # сохраняем в базу
    await db.refresh(db_user)  # получаем id и связанные поля

    # Теперь можно загрузить пользователя с постами и интересами
    stmt = select(models.User).options(
        selectinload(models.User.posts),
        selectinload(models.User.interests)
    ).where(models.User.id == db_user.id)

    result = await db.execute(stmt)
    full_user = result.scalars().first()  # scalars().first() безопаснее

    return schemas.UserOut.model_validate(full_user, from_attributes=True)

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.username == form_data.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/users/rename", response_model=schemas.UserOut)
async def update_existing_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Обновляем пользователя
    user = await crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Повторно получаем пользователя с нужными связями
    stmt = (
        select(models.User)
        .options(
            selectinload(models.User.posts).selectinload(models.Post.tags),
            selectinload(models.User.interests)
        )
        .where(models.User.id == user_id)
    )
    result = await db.execute(stmt)
    full_user = result.scalar_one()

    # Возвращаем готовую Pydantic-схему
    return schemas.UserOut.model_validate(full_user, from_attributes=True)

@router.post("/users/restore", response_model=schemas.UserOut)
async def restore_user_account(
    restore_data: schemas.UserRestore,  # схема с username/email и password
    db: AsyncSession = Depends(get_db)
):

    stmt = (
        select(models.User)
        .options(
            selectinload(models.User.posts).selectinload(models.Post.tags),
            selectinload(models.User.interests)
        )
        .where(
            (models.User.email == restore_data.email) |
            (models.User.username == restore_data.username)
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, что аккаунт удалён
    if not user.is_deleted:
        raise HTTPException(status_code=400, detail="User account is already active")

    # Проверяем пароль
    if not auth.verify_password(restore_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # Восстанавливаем
    user.is_deleted = False
    user.deleted_at = None
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return schemas.UserOut.model_validate(user, from_attributes=True)
#получение постов юзера любой даже не авторизованный

@router.get("/user_posts", response_model=schemas.UserOut)
async def get_user_posts(
    request: Request,
    username: str = Query(..., description="Имя пользователя"),
    session: AsyncSession = Depends(get_db),
):
    query = (
        select(models.User)
        .options(
            selectinload(models.User.posts).selectinload(models.Post.tags),
            selectinload(models.User.interests),
        )
        .where(models.User.username == username)
    )

    result = await session.execute(query)
    user = result.scalars().unique().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    base_url = str(request.base_url).rstrip("/")
    for post in user.posts:
        if post.file_path:
            post.file_url = f"{base_url}/{post.file_path}"
        else:
            post.file_url = None

    return schemas.UserOut.from_orm(user)
    
@router.get("/me", response_model=schemas.UserOut)
async def get_current_user_data(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Загружаем пользователя из БД с posts и interests
    stmt = (
        select(models.User)
        .options(
            selectinload(models.User.posts).selectinload(models.Post.tags),
            selectinload(models.User.interests)
        )
        .where(models.User.id == current_user.id)
    )
    result = await db.execute(stmt)
    user_full = result.scalar_one()

    # Возвращаем Pydantic-схему
    return schemas.UserOut.model_validate(user_full, from_attributes=True)

# Получить всех пользователей (для авторизованных)
'''@router.get("/users/all")
async def get_users(
    username: str | None = None,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Базовый запрос — все пользователи, которые НЕ удалены
    base_query = select(models.User).where(models.User.is_deleted == False)

    # Если есть фильтр по username
    if username:
        base_query = base_query.where(models.User.username.ilike(f"%{username}%"))

    # Если есть фильтр по email
    if email:
        base_query = base_query.where(models.User.email.ilike(f"%{email}%"))

    if current_user.username == "admin":
        # Для админа загружаем все связи (посты, интересы)
        stmt = base_query.options(
            selectinload(models.User.posts).selectinload(models.Post.tags),
            selectinload(models.User.interests)
        )
        result = await db.execute(stmt)
        users_full = result.scalars().all()
        # Возвращаем список полных данных пользователей
        return [schemas.UserOut.model_validate(u, from_attributes=True) for u in users_full]

    else:
        # Для обычных пользователей возвращаем список ВСЕХ username (НЕ только себя!)
        result = await db.execute(base_query)
        users = result.scalars().all()
        return [user.username for user in users]

'''

@router.get("/users/{user_id}", response_model=schemas.UserOut)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#Написание поста
@router.post("/posts", response_model=schemas.PostOut)
async def create_post(
    request: Request,
    post: schemas.PostCreate = Depends(schemas.PostCreate.as_form),
    uploaded_file: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    relative_path = None
    if uploaded_file:
        safe_filename = uploaded_file.filename.replace(" ", "_")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(BASE_DIR, "static", "app")
        os.makedirs(static_dir, exist_ok=True)

        relative_path = f"static/app/{safe_filename}"
        file_path = os.path.join(static_dir, safe_filename)

        content = await uploaded_file.read()
        with open(file_path, "wb") as f:
            f.write(content)

    new_post = models.Post(
        **post.dict(exclude={"tag_ids"}),
        author_id=current_user.id,
        file_path=relative_path
    )

    if post.tag_ids:
        stmt = select(models.Tag).where(models.Tag.id.in_(post.tag_ids))
        result = await session.execute(stmt)
        #tags = result.scalars().all()
        #new_post.tags.extend(tags)

    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)

    stmt = select(models.Post).options(selectinload(models.Post.tags)).where(models.Post.id == new_post.id)
    result = await session.execute(stmt)
    post_with_tags = result.scalars().first()

    base_url = str(request.base_url).rstrip("/")
    if post_with_tags.file_path:
        post_with_tags.file_url = f"{base_url}/{post_with_tags.file_path}"
    else:
        post_with_tags.file_url = None

    return post_with_tags

@router.delete("/users/me", response_model=schemas.UserOut)
async def delete_me(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.is_deleted:
        raise HTTPException(status_code=400, detail="User already deleted")

    # Софт-делит
    current_user.is_deleted = True
    current_user.deleted_at = datetime.utcnow()
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    # Возвращаем только базовые атрибуты (без posts, interests)
    return schemas.UserOutDel.model_validate(current_user, from_attributes=True)
