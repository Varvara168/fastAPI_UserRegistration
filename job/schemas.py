from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    description: str

class JobCreate(JobBase):
    pass

class JobResponseCreate(BaseModel):
    job_id: int
    message: Optional[str] = None

class JobResponseOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    message: Optional[str]
    created_at: datetime
    is_accepted: bool

    class Config:
        orm_mode = True

class JobOut(JobBase):
    id: int
    employer_id: int
    is_open: bool
    created_at: datetime

    class Config:
        orm_mode = True
