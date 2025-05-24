from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas, models # Updated import
from app.database import get_db # Updated import
from app.core.security import get_current_active_user # Updated import

router = APIRouter()

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@router.get("/{user_id}/tasks", response_model=List[schemas.Task])
def read_user_tasks(
    user_id: str, 
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.school_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")
    tasks = crud.get_tasks_by_user(db, user_school_id=user_id, skip=skip, limit=limit)
    return tasks

@router.post("/{user_id}/sync") # PRD 내용대로 응답 모델은 일단 제외
def sync_user_data(
    user_id: str, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.school_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to sync this user's data")
    # TODO: Implement Blackboard crawling and AI analysis logic here
    # 1. Trigger crawling for the user (user_id)
    # 2. Get text data from crawler
    # 3. Analyze with Gemini & LangChain (using prompt from PRD)
    # 4. If is_announcement_valid is true, save to Task table using crud.create_user_task
    # 5. Potentially save ClassList info using crud.create_user_class_list_item
    
    # Placeholder response
    return {"message": "Sync process initiated for user " + user_id + ". Implementation pending."}

@router.get("/{user_id}/courses", response_model=List[schemas.ClassList])
def read_user_courses(
    user_id: str, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.school_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's courses")
    courses = crud.get_class_list_by_user(db, user_school_id=user_id)
    return courses 