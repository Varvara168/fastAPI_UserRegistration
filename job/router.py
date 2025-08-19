from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.job.schemas import JobCreate, JobOut, JobResponseCreate, JobResponseOut
from app.job.crud import *
from app.models import User

router = APIRouter()

@router.post("/", response_model=JobOut)
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await create_job(db, job, current_user.id)

@router.get("/", response_model=list[JobOut])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    return await get_open_jobs(db)

@router.post("/responses/", response_model=JobResponseOut)
async def respond_to_job(response: JobResponseCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await create_job_response(db, response, current_user.id)

@router.get("/{job_id}/responses/", response_model=list[JobResponseOut])
async def get_responses(job_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Добавь проверку прав доступа, если хочешь
    return await get_responses_for_job(db, job_id)
