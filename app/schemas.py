from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен быть минимум 6 символов')
        if ' ' in v:
            raise ValueError('Пароль не должен содержать пробелов')
        return v
    
    @model_validator(mode='after')
    @classmethod
    def password_not_email_part(cls, values):
        email = values.email
        password = values.password
        username = values.username

        local_part = email.split('@')[0].lower()
        if password.lower() == local_part:
            raise ValueError('Пароль не должен совпадать с частью email до @')
        if password.lower() == username.lower():
            raise ValueError('Пароль не должен совпадать с именем пользователя')
        return values

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен быть минимум 6 символов')
        if ' ' in v:
            raise ValueError('Пароль не должен содержать пробелов')
        
        return v

    @model_validator(mode='after')
    @classmethod
    def password_not_email_part(cls, values):
        email = values.email
        password = values.password
        username = values.username

        local_part = email.split('@')[0].lower()
        if password.lower() == local_part:
            raise ValueError('Пароль не должен совпадать с частью email до @')
        if password.lower() == username.lower():
            raise ValueError('Пароль не должен совпадать с именем пользователя')
        return values

# Базовая модель поста (используется при создании и отображении)
class PostBase(BaseModel):
    title: str
    content: str

# Модель для создания поста
class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tag_ids: Optional[list[int]] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminPasswordCheck(BaseModel):
    admin_password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int
    class Config:
        orm_mode = True

# Модель для вывода поста (включает ID)
class PostOut(BaseModel):
    id: int
    title: str
    content: str
    tags: list[TagOut] = []

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    posts: List[PostOut] = []

    class Config:
        orm_mode = True
