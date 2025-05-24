from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import TaskType # Enum import

# User Schemas
class UserBase(BaseModel):
    school_id: str = Field(..., max_length=255)

class UserCreate(UserBase):
    school_password: str = Field(..., max_length=255)
    token: str = Field(..., max_length=255)

class User(UserBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# User Registration Request Schema (as per user's new requirement)
class UserRegistrationRequest(BaseModel):
    id: str = Field(..., description="학교 ID")
    password: str = Field(..., description="비밀번호")

# ClassList Schemas
class ClassListBase(BaseModel):
    course_name: str = Field(..., max_length=255)
    course_id: str = Field(..., max_length=100)

class ClassListCreate(ClassListBase):
    pass

class ClassList(ClassListBase):
    id: int
    user_school_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    detail: Optional[str] = None
    type: TaskType
    due_date: Optional[datetime] = None
    source_description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    detail: Optional[str] = None
    type: Optional[TaskType] = None
    due_date: Optional[datetime] = None
    status: Optional[bool] = None
    source_description: Optional[str] = None

class Task(TaskBase):
    id: int
    user_school_id: str
    status: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Token Schemas for Authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    school_id: Optional[str] = None

# Schemas for Chatbot Analysis
class AnnouncementAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="분석할 공지사항 텍스트")
    
class AnalyzedItem(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None # Gemini가 YYYY-MM-DD HH:MM:SS 또는 null로 반환 예정
    detail: Optional[str] = None
    is_announcement_valid: Optional[bool] = None

class AnnouncementAnalysisResponse(BaseModel):
    analysis_result: Optional[List[AnalyzedItem]] = None
    raw_result: Optional[dict] = None # 또는 List[dict]
    error: Optional[str] = None
    original_response: Optional[str] = None # Gemini가 JSON 파싱 실패 시 원본 응답

    class Config:
        orm_mode = True 