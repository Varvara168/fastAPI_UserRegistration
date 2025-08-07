from fastapi import APIRouter, Depends, Query, HTTPException, Header, Request, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import os

from app.dependencies import get_current_user
from app import models, schemas, auth, crud
from app.database import get_db
from app.dependencies import get_current_user

from app.config import settings


settings.ADMIN_SECRET_PASSWORD

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
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Хеширование пароля и создание пользователя
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)  # Обновить, чтобы получить db_user.id

    # Повторно загружаем пользователя с постами
    stmt = select(models.User).options(selectinload(models.User.posts)).where(models.User.id == db_user.id)
    result = await db.execute(stmt)
    full_user = result.scalar_one()

    # Возвращаем Pydantic-схему
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
async def update_existing_user(user_id: int, user_update: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud.update_user(db, user_id, user_update.dict(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}", response_model=schemas.UserOut)
async def delete_existing_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#получение постов юзера любой даже не авторизованный
@router.get("/user_posts", response_model=schemas.UserOut)
async def get_user_posts(
    user_param: str = Query(..., description="ID или username пользователя"),
    session: AsyncSession = Depends(get_db),
):
    """
    Получить пользователя и его посты, по ID или username — автоматически определяется.
    """
    query = select(models.User).options(selectinload(models.User.posts))

    # Попробуем интерпретировать параметр как ID
    try:
        user_id = int(user_param)
        query = query.where(models.User.id == user_id)
    except ValueError:
        # Если это не число — считаем, что это username
        query = query.where(models.User.username == user_param)

    # Выполняем запрос
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user

#Получение текущего пользователя 
@router.get("/me", response_model=schemas.UserOut)
async def get_current_user_data(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


# Получить всех пользователей (для авторизованных)
@router.get("/users/all", response_model=list[schemas.UserOut])
async def get_users(
    username: str | None = None,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = select(models.User)

    if username:
        query = query.where(models.User.username.ilike(f"%{username}%"))
    if email:
        query = query.where(models.User.email.ilike(f"%{email}%"))

    result = await db.execute(query)
    users = result.scalars().all()
    return users
 
#получение по id
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
    post: schemas.PostCreate = Depends(schemas.PostCreate.as_form),
    uploaded_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Формируем безопасное имя файла
    safe_filename = uploaded_file.filename.replace(" ", "_")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(BASE_DIR, "static", "app")
    os.makedirs(static_dir, exist_ok=True)
    file_path = os.path.join(static_dir, f"1_{safe_filename}")

    try:
        content = await uploaded_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {e}")

    # Создаём пост
    new_post = models.Post(
        **post.dict(exclude={"tag_ids"}),
        author_id=current_user.id
        # file_path=file_path,  # добавь, если есть поле в модели
    )

    # 🔥 Загружаем теги из базы и добавляем к посту
    if post.tag_ids:
        stmt = select(models.Tag).where(models.Tag.id.in_(post.tag_ids))
        result = await session.execute(stmt)
        tags = result.scalars().all()
        new_post.tags.extend(tags)

    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)

    # Явно загружаем связанные теги
    stmt = select(models.Post).options(selectinload(models.Post.tags)).where(models.Post.id == new_post.id)
    result = await session.execute(stmt)
    post_with_tags = result.scalars().first()

    return post_with_tags

# Только для админа  alembic upgrade head
@router.get("/admin/dashboard")
async def admin_dashboard(
    current_user: models.User = Depends(get_current_user),
    x_admin_password: str = Header(alias="X-Admin-Password")
):
    if current_user.username != "admin" or x_admin_password != settings.ADMIN_SECRET_PASSWORD:
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")
    return {
        "message": "Welcome to the admin dashboard",
        "admin_user": current_user.username
    }
