from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.database import engine
from app import models

# 데이터베이스 테이블 생성 (개발용)
# 프로덕션 환경에서는 Alembic과 같은 마이그레이션 도구를 사용하는 것이 좋습니다.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blackboard 과제 관리 및 알림 서버", version="1.0")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Blackboard Assignment Management API"}

# CORS 설정
origins = [
    "*" # 모든 출처 허용 (개발용) 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # 쿠키 등의 자격 증명을 허용할 경우 True
    allow_methods=["*"],    # 모든 HTTP 메소드 허용
    allow_headers=["*"],    # 모든 HTTP 헤더 허용
) 