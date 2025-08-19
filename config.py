from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ADMIN_SECRET_WORD: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ADMIN_SECRET_PASSWORD: str

    class Config:
        env_file = ".env"
        extra = "allow"  # разрешает дополнительные переменные

settings = Settings()