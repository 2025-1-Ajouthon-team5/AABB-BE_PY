import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f".env 파일 로드 성공: {ENV_PATH}")
elif Path(".env").exists(): # 혹시 루트에서 직접 실행하는 경우 (uvicorn이 CWD를 루트로 잡는 경우)
    load_dotenv() # 기본 동작으로 루트의 .env 로드 시도
    print(".env 파일 로드 성공 (기본 경로)")
else:
    print(f".env 파일을 찾을 수 없습니다. 시도한 경로: {ENV_PATH}, 또는 기본 경로")

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@host/db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

settings = Settings()

# 로드된 값 확인용 (디버깅 후 제거 가능)
print(f"[config.py] DATABASE_URL: {settings.DATABASE_URL}")
print(f"[config.py] GEMINI_API_KEY: {settings.GEMINI_API_KEY}") 