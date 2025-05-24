from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

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

@router.delete("/users/{school_id}", response_model=schemas.User, status_code=status.HTTP_200_OK)
async def delete_user_endpoint(
    school_id: str,
    db: Session = Depends(get_db)
):
    """
    지정된 school_id를 가진 사용자를 삭제합니다.

    - **school_id**: 삭제할 사용자의 학교 ID
    """
    deleted_user = crud.delete_user(db=db, school_id=school_id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{school_id}에 해당하는 사용자를 찾을 수 없습니다."
        )
    # 성공적으로 삭제된 경우, 삭제된 사용자 정보를 반환합니다.
    # 혹은 간단한 성공 메시지를 반환할 수도 있습니다. 예: return {"message": "User deleted successfully"}
    return deleted_user