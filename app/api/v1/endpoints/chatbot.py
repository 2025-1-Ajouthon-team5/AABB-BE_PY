from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Any

from app import schemas, models
from app.database import get_db
from app.services import chatbot_service
from app import crud

router = APIRouter()

@router.post("/analyze_announcement", response_model=schemas.AnnouncementAnalysisResponse)
async def analyze_text(
    request_data: schemas.AnnouncementAnalysisRequest,
):
    """
    텍스트를 받아 Gemini를 통해 분석하고, 분석된 아이템 리스트 또는 오류를 반환합니다.
    """
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Not authenticated"
    #     )
    
    # 서비스 함수 호출 시 await 사용
    analysis_result = await chatbot_service.analyze_announcement(request_data.text)

    # 결과가 딕셔너리 형태이고 'error' 키를 포함하는지 확인
    if isinstance(analysis_result, dict) and 'error' in analysis_result:
        # Gemini 응답 파싱 실패 시 original_response를 포함하여 반환
        if 'original_response' in analysis_result:
            return schemas.AnnouncementAnalysisResponse(
                error=analysis_result.get('error'), 
                original_response=analysis_result.get('original_response')
            )
        return schemas.AnnouncementAnalysisResponse(error=analysis_result.get('error'))

    return schemas.AnnouncementAnalysisResponse(analysis_result=analysis_result)

@router.post("/chat") # 반환 타입을 명시 (예: str 또는 적절한 Pydantic 모델)
async def handle_chat_request(
    request_data: schemas.ChatRequest, # 요청 본문을 ChatRequest 스키마로 받음
    db: Session = Depends(get_db)
):
    """
    사용자 토큰과 메시지를 받아, 해당 사용자의 과제 정보를 포함한 프롬프트를 생성하여
    Gemini 모델에 질의하고 응답을 반환합니다.
    """
    user = crud.get_user_by_token(db=db, token=request_data.token)
    
    print(f"user.school_id: {user.school_id}")
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다."
        )
        
    # 사용자의 모든 과제 정보 가져오기
    user_tasks = crud.get_tasks_by_user(db=db, user_school_id=user.school_id, limit=20) # limit는 적절히 조절
    
    print(f"user_tasks: {user_tasks}")
    
    # 과제 정보를 문자열로 조합 (컨텍스트 생성)
    tasks_context_parts = []
    if user_tasks:
        for task in user_tasks:
            task_info = f"- 과제명: {task.title}"
            if task.detail:
                task_info += f", 설명: {task.detail}"
            if task.due_date:
                task_info += f", 마감일: {task.due_date.strftime('%Y-%m-%d %H:%M')}"
            if task.course:
                task_info += f", 과목: {task.course}"
            tasks_context_parts.append(task_info)
    
    user_tasks_context = "\n".join(tasks_context_parts) if tasks_context_parts else "현재 등록된 과제가 없습니다."

    # chatbot_service의 chat 함수 호출
    # chat 함수는 (user_query: str, user_tasks_context: str)를 인자로 받음
    bot_response = await chatbot_service.chat(user_query=request_data.message, user_tasks_context=user_tasks_context)
    
    # 모델의 텍스트 응답을 그대로 반환 (또는 JSON 형태로 감싸서 반환)
    return {"response": bot_response} 