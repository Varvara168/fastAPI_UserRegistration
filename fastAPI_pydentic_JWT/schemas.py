from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserReturn(BaseModel):
    id: int
    username: str
    
    class Config:
        orm_mode = True