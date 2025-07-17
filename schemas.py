from pydantic import BaseModel, EmailStr


class TokenData(BaseModel):
    sub: str | None = None
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
