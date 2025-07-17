from fastapi import FastAPI, Depends, HTTPException, status  # для создания API, обработки зависимостей.
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # стандартный способ реализовать логин по токену.
from sqlalchemy.orm import Session  # для работы с БД через SQLAlchemy

from database import *  # инициализация базы данных
from models import *  # модель пользователя
from auth import *  # функции из auth.py

from pydantic import BaseModel  # базовый класс моделей Pydantic.

from routes import users  # или как у тебя назван файл

app = FastAPI()

app.include_router(users.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Создает подключение к базе и закрывает после запроса 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):  # тело запроса при регистрации
    username: str
    password: str

class Token(BaseModel):  # формат ответа при успешной регистрации или логине
    access_token: str
    token_type: str = 'bearer'

# новый пользоатель регестрируется в системе 
@app.post("/register", response_model=Token)  # FastAPI автоматически сформирует ответ в виде объекта  то есть: {"access_token": ..., "token_type": "bearer"}.
def register(user: UserCreate, db: Session = Depends(get_db)):  # подключаемся к БД, чтобы взаимодействовать с таблицей пользователей.
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail='Пользователь уже существует')

    hashed_password = get_password_hash(user.password)

    # новый пользватель
    new_user = User(username=user.username, hashed_password=hashed_password)  # создаем
    db.add(new_user)  # добавляем
    db.commit()  # сохраняем
    db.refresh(new_user)  # получаем обновленный объект

    token = create_access_token({'user': new_user.username})
    return {'access_token': token, 'token_type': 'bearer'}

# обработчик логина
@app.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):  # вытаскивание пароля автоматиески, подключение в db
    user = db.query(User).filter(User.username == form_data.username).first() 
    if not user or not verify_password(form_data.password, user.hashed_password):  # имя или хеш пароля
        raise HTTPException(status_code=401, detail='неверное имя или пароль')

    token = create_access_token({'user': user.username})
    return {'access_token': token, 'token_type': 'bearer'}

# защищенный маршрут
@app.get("/protected")
def protected_root(token: str = Depends(oauth2_scheme)):  # сюда можно попасть еси только валидный токен (логин и пароль)
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail='Невалидный токен')
    return {'message': f"Привет, {payload['user']}! Это защищенный поток"}
