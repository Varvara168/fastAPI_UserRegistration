from fastapi import APIRouter, Depends, Query, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.hash_password(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


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
    post: schemas.PostCreate,
    session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_post = models.Post(**post.dict(), author_id=current_user.id)
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post

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
