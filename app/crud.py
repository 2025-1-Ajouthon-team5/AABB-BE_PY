from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password Hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# User CRUD
def get_user(db: Session, school_id: str):
    return db.query(models.User).filter(models.User.school_id == school_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.school_password)
    db_user = models.User(school_id=user.school_id, student_number=user.student_number, school_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Task CRUD
def get_tasks_by_user(db: Session, user_school_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.user_school_id == user_school_id).offset(skip).limit(limit).all()

def create_user_task(db: Session, task: schemas.TaskCreate, user_school_id: str):
    db_task = models.Task(**task.dict(), user_school_id=user_school_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

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