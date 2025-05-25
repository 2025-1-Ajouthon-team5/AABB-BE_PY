from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from cryptography.fernet import Fernet

# User CRUD
def get_user(db: Session, school_id: str):
    return db.query(models.User).filter(models.User.school_id == school_id).first()

def get_user_by_token(db: Session, token: str):
    return db.query(models.User).filter(models.User.token == token).first()

def create_user(db: Session, user: schemas.UserCreate):
    
    db_user = models.User(school_id=user.school_id, school_password=user.school_password, token=user.token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, school_id: str):
    db_user = get_user(db, school_id=school_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

# Task CRUD
def get_tasks_by_user(db: Session, user_school_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.user_school_id == user_school_id).offset(skip).limit(limit).all()

# 중복 검증 : 기존 Task에서 type, course, date, user가 완전히 겹치는게 있는지 체크하기 
def check_duplicate_task(db: Session, task: schemas.TaskCreate, user_school_id: str):
    return db.query(models.Task).filter(
        models.Task.user_school_id == user_school_id,
        models.Task.type == task.type,
        models.Task.course == task.course,
        models.Task.due_date == task.due_date,
    ).first()
    
def create_user_task(db: Session, task: schemas.TaskCreate, user_school_id: str):
    
    db_task = models.Task(**task.dict(), user_school_id=user_school_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_user_token(db: Session, school_id: str, token: str):
    db_user = get_user(db, school_id=school_id)
    if db_user:
        db_user.token = token
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def get_task_by_title_and_type(db: Session, user_school_id: str, title: str, task_type: models.TaskType):
    """
    주어진 사용자의 특정 제목과 타입을 가진 Task가 있는지 확인합니다.
    """
    return db.query(models.Task).filter(
        models.Task.user_school_id == user_school_id,
        models.Task.title == title,
        models.Task.type == task_type
    ).first()

def update_task_status(db: Session, task_id: int, status: bool):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.status = status
        db.commit()
        db.refresh(db_task)
    return db_task

# ClassList CRUD (기본)
def create_user_class_list_item(db: Session, item: schemas.ClassListCreate, user_school_id: str):
    db_item = models.ClassList(**item.dict(), user_school_id=user_school_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_class_list_by_user(db: Session, user_school_id: str):
    return db.query(models.ClassList).filter(models.ClassList.user_school_id == user_school_id).all() 