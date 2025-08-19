from pydantic import BaseModel
from typing import List
class InterestCreate(BaseModel):
    name: str

class InterestRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# Новая схема для обновления интересов
class UserUpdateInterests(BaseModel):
    interests: List[int]
    