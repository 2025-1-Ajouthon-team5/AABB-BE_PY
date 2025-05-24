from fastapi import APIRouter, HTTPException, status
from typing import Any

from app import schemas
from app.services.chatbot_service import analyze_announcement

router = APIRouter()

@router.post("/analyze", response_model=Any) # 응답 모델을 Any로 하여 유연하게 처리
async def analyze_text_announcement_no_auth(
    request_data: schemas.AnnouncementAnalysisRequest
):
    """
    공지사항 텍스트를 분석하여 구조화된 정보를 반환합니다. (인증 불필요)

    - **text**: 분석할 공지사항 텍스트입니다.
    """
    analysis_result = await analyze_announcement(request_data.text)

    if isinstance(analysis_result, dict) and "error" in analysis_result:
        # 서비스 내부 오류 또는 Gemini API 오류
        if "original_response" in analysis_result:
             # Gemini 응답이 JSON이 아닌 경우
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, 
                detail=f"Gemini API response parsing failed: {analysis_result['error']}. Original: {analysis_result['original_response']}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=analysis_result["error"]
        )
    
    return analysis_result 