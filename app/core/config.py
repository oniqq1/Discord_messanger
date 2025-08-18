from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    APP_NAME: str = "Messenger API"
    DEBUG: bool = True

    DB_NAME: str = "data.db"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data.db'}"

    SECRET_KEY: str = "sekret_Key_vadim_lox"
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30

    class Config:
        env_file = ".env"

settings = Settings()