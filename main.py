from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import RequestValidationError
import os

from app.models import *
from app.database import engine
from app.routes import router, validation_exception_handler
from app.interests.router import router as interest_router
from app.matching.router import router as match_router
from app.job.router import router as job_router
from app.routes_admin import router as admin_router

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
 
app.include_router(router)
app.include_router(interest_router, prefix="/interests", tags=["Interests"])
app.include_router(match_router, prefix="/matches", tags=["Matches"])
app.include_router(job_router, prefix="/job", tags=["Job"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


# Монтируем статику (для раздачи файлов из папки static/)
static_path = os.path.join(os.path.dirname(__file__), "static")

@app.get("/")
async def root():
    return {"message": "FastAPI is working"}

