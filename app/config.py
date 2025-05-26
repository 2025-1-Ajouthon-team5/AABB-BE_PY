from pydantic_settings import BaseSettings
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = "a_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

settings = Settings()

# 로드된 값 확인용 (디버깅 후 제거 가능)
print(f"[config.py] DATABASE_URL: {settings.DATABASE_URL}")
print(f"[config.py] GEMINI_API_KEY: {settings.GEMINI_API_KEY}") 