from fastapi import APIRouter

# 삭제된 엔드포인트 임포트 주석 처리
from app.api.v1.endpoints import chatbot, auth, crawler, tasks # tasks 임포트 추가

api_router = APIRouter()

api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"]) # analysis 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["auth"]) # auth 라우터 등록
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"]) # crawler 라우터 등록
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"]) # tasks 라우터 등록