from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app import crud, schemas, models
from app.database import get_db
from app.services.chatbot_service import analyze_announcement

router = APIRouter()

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: schemas.UserRegistrationRequest, 
    db: Session = Depends(get_db)
):
    """
    새로운 사용자를 등록하고, Blackboard 정보를 크롤링 및 분석하여 초기 데이터를 저장합니다. 성공 시 토큰을 반환합니다. 

    - **id**: 학교 ID (중복 불가)
    - **password**: 비밀번호
    """
    db_user = crud.get_user(db, school_id=user_in.id)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 학교 ID입니다."
        )
    
    # 1. User Database 생성 
    user_create_data = schemas.UserCreate(
        school_id=user_in.id,
        school_password=user_in.password
    )
    created_user = crud.create_user(db=db, user=user_create_data)
    
    # # 2. Ann Service와 assgin_service 로직 호출 (간단한 호출 예시)
    # try:
    #     print(f"[Register API] AnnService.get_coursist 호출 시작: user_id={created_user.school_id}")
    #     # get_coursist는 동기 함수일 수 있으므로 run_in_threadpool 사용 고려
    #     announcements = await run_in_threadpool(get_coursist, user_id=created_user.school_id, user_pw=user_in.password)
    #     print(f"[Register API] AnnService.get_coursist 호출 완료. {len(announcements) if announcements else 0}개의 공지 수신.")

    #     print(f"[Register API] assgin_service.get_assignments 호출 시작: user_id={created_user.school_id}")
    #     # get_assignments도 동기 함수일 수 있으므로 run_in_threadpool 사용 고려
    #     assignments = await run_in_threadpool(get_assignments, user_id=created_user.school_id, user_pw=user_in.password)
    #     print(f"[Register API] assgin_service.get_assignments 호출 완료. {len(assignments) if assignments else 0}개의 과제 수신.")

    #     # 여기에서 announcements와 assignments를 사용하여 추가 작업 수행 가능
    #     # 예를 들어, DB에 저장하거나, 분석하거나 등등

    # except Exception as e:
    #     # 실제 프로덕션에서는 더 구체적인 예외 처리 및 로깅 필요
    #     print(f"[Register API] 서비스 호출 중 오류 발생: {e}")
    #     # 오류 발생 시 사용자 생성은 성공했으므로 created_user를 반환하거나,
    #     # 혹은 상황에 따라 사용자 생성을 롤백하는 등의 처리를 고려할 수 있습니다.
    #     # 여기서는 우선 오류를 출력하고 사용자 정보를 반환합니다.

    return created_user