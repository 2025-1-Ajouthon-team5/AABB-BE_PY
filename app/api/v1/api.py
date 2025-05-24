from fastapi import APIRouter

# 삭제된 엔드포인트 임포트 주석 처리
from app.api.v1.endpoints import chatbot, auth, crawler # crawler 임포트 추가

api_router = APIRouter()

api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"]) # analysis 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["auth"]) # auth 라우터 등록
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"]) # crawler 라우터 등록

# 현재는 빈 라우터입니다. 필요시 엔드포인트를 추가하고 아래 주석을 해제하세요. 

# 삭제되었거나 아직 구현되지 않은 다른 라우터들은 주석 처리 유지
# from app.api.v1.endpoints import users, tasks 
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"]) 