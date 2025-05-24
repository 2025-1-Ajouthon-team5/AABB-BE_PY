from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from cryptography.fernet import Fernet

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# # 키는 환경변수나 .env 파일 등 안전한 곳에 저장하세요!
# FERNET_KEY = b'your-generated-fernet-key-here'
# fernet = Fernet(FERNET_KEY)

# def encrypt_text(text: str) -> str:
#     return fernet.encrypt(text.encode()).decode()

# def decrypt_text(token: str) -> str:
#     return fernet.decrypt(token.encode()).decode()

# # Password Hashing
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

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