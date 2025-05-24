from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app import crud, schemas, models
from app.database import get_db
from app.services.AnnService import get_coursist
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

    return created_user