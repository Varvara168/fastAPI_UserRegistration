from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Job, JobResponse
from app.job.schemas import JobCreate, JobResponseCreate

async def create_job(db: AsyncSession, job_data: JobCreate, employer_id: int):
    job = Job(**job_data.dict(), employer_id=employer_id)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def get_open_jobs(db: AsyncSession):
    result = await db.execute(select(Job).where(Job.is_open == True))
    return result.scalars().all()

async def create_job_response(db: AsyncSession, response_data: JobResponseCreate, candidate_id: int):
    response = JobResponse(**response_data.dict(), candidate_id=candidate_id)
    db.add(response)
    await db.commit()
    await db.refresh(response)
    return response

async def get_responses_for_job(db: AsyncSession, job_id: int):
    result = await db.execute(select(JobResponse).where(JobResponse.job_id == job_id))
    return result.scalars().all()
