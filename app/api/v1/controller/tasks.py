from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas, models # Updated import
from app.database import get_db # Updated import
from app.core.security import get_current_active_user # Updated import

router = APIRouter()

class TaskStatusUpdate(schemas.BaseModel):
    status: bool

@router.put("/{task_id}/status", response_model=schemas.Task)
def update_task_status_endpoint(
    task_id: int, 
    task_update_status: TaskStatusUpdate, # Request body로 status를 받음
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # 현재 로그인한 사용자가 해당 과제의 소유자인지 확인
    if db_task.user_school_id != current_user.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this task")
        
    updated_task = crud.update_task_status(db=db, task_id=task_id, status=task_update_status.status)
    if updated_task is None:
        # crud 함수 내에서 task_id로 못찾는 경우는 이미 위에서 처리되었으므로, 여기는 다른 이유로 실패한 경우.
        # 하지만 현재 crud.update_task_status는 task를 못찾으면 None을 반환하게 되어있음.
        # 일관성을 위해 crud 함수가 못찾으면 예외를 발생시키거나, 여기서 다시 체크.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or could not be updated")
    return updated_task 