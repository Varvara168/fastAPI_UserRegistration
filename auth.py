from datetime import datetime, timedelta  # для работы с временем (истечение срока действия токена)
from typing import Optional  # чтобы указать, что параметр может быть None

from jose import JWTError, jwt  # библиотека для создания и проверки JWT
from passlib.context import CryptContext  # для безопасного хеширования паролей

#секретный ключ хранится в .env файле
SECRET_KEY = 'total secret'

#Алгоритм шифрования токена
ALGORITHM = 'HS256'  
#Время действия токена - по умолчанию 30
TOKEN_EXPIRE_MINUTES = 30

#контекстт для работы с хешами 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#хеширование пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

#проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#Создание JWT токена, в котором данные (имя пользвателя, ...)
#можно задат срок жизни токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()  # ← переименовано с uncopy для читаемости, но смысл тот же
    #срок жихзни или стандартный
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # ← исправлено ALGORITM → ALGORITHM
    # кодируем токен и возвращаем строку
    return encoded_jwt

#расшифровка токена
#если просрочен или неверный вернет None
def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
