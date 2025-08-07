from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import RequestValidationError
import os

from app import models
from app.database import engine
from app.routes import router, validation_exception_handler
from app.interests.router import router as interest_router
from app.matching.router import router as match_router
from app.job.router import router as job_router

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(router)
app.include_router(interest_router, prefix="/interests", tags=["Interests"])
app.include_router(match_router, prefix="/matches", tags=["Matches"])
app.include_router(job_router, prefix="/job", tags=["Job"])


# Монтируем статику (для раздачи файлов из папки static/)
static_path = os.path.join(os.path.dirname(__file__), "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    return {"message": "FastAPI is working"}

