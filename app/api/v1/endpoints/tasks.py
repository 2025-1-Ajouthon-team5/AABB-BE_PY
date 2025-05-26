from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/users/{school_id}/tasks", response_model=List[schemas.Task], status_code=status.HTTP_200_OK)
async def read_user_tasks(
    school_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 사용자의 모든 Task(일정) 목록을 반환합니다.

    - **school_id**: Task를 조회할 사용자의 학교 ID
    """
    # 사용자 존재 여부 확인 (선택 사항, crud.get_tasks_by_user가 빈 리스트를 반환하므로 굳이 필요 없을 수 있음)
    # db_user = crud.get_user(db, school_id=school_id)
    # if not db_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"{school_id}에 해당하는 사용자를 찾을 수 없습니다."
    #     )
    
    tasks = crud.get_tasks_by_user(db=db, user_school_id=school_id)
    if not tasks:
        # Task가 없는 경우 빈 리스트를 반환하는 것이 일반적이지만,
        # 명시적으로 404를 반환하고 싶다면 아래 주석을 해제할 수 있습니다.
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail=f"{school_id} 사용자의 Task를 찾을 수 없습니다."
        # )
        return [] # Task가 없으면 빈 리스트 반환
    return tasks 