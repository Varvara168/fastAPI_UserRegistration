from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import router as user_router
from fastapi.security import OAuth2PasswordBearer
from app.routes import router, validation_exception_handler
from fastapi.exceptions import RequestValidationError

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(router)


'''
@app.get("/")
async def root():
    return {"message": "FastAPI is working"}
'''
