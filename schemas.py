from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field
from fastapi import Form
from typing import Optional, List
from datetime import datetime

from app.models import GenderEnum, User

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    city: Optional[str] = None
    age: Optional[int] = None
    gender: GenderEnum = Field(..., description="Choose gender: male or female")

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
class PostCreate(BaseModel):
    title: str
    content: str
    tag_ids: List[int] = []
    
    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        content: str = Form(...)
    ):
        return cls(title=title, content=content)
    
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tag_ids: Optional[list[int]] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminPasswordCheck(BaseModel):
    admin_password: str
    
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int
    name: str

    class Config:
        orm_mode = True

# Модель для вывода поста (включает ID)
class PostOut(BaseModel):
    title: str
    content: str
    #tags: list[TagOut] = []
    #file_path: Optional[str] = None
    file_url: Optional[str] = None

    model_config = {
        "from_attributes": True  
    }

class UserOutDel(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    city: Optional[str]
    age: Optional[int]
    gender: Optional[str] = None
    posts: List[PostOut] = []

    model_config = {
        "from_attributes": True  
    }

    @classmethod
    def from_orm_with_interests(cls, user: User):
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            city=user.city,
            age=user.age,
            gender=user.gender.value if user.gender else None,
            relationship_goal=user.relationship_goal,
            interests=[interest.name for interest in user.interests] if user.interests else [],
            posts=[PostOut.from_orm(post) for post in user.posts] if user.posts else [],
        )
    
class UserRestore(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

