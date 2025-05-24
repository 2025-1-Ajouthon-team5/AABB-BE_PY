from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import TaskType # Enum import

# User Schemas
class UserBase(BaseModel):
    school_id: str = Field(..., max_length=255)

class UserCreate(UserBase):
    school_password: str = Field(..., max_length=255)

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

# 현재 chatbot_service.analyze_announcement는 dict를 반환하므로
# 응답 스키마는 유연하게 Dict 또는 좀 더 구체적인 필드를 정의할 수 있습니다.
# PRD에 명시된 JSON 구조를 기반으로 응답 스키마를 정의해볼 수 있습니다.
class AnalyzedItem(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None # Gemini가 YYYY-MM-DD HH:MM:SS 또는 null로 반환 예정
    detail: Optional[str] = None
    is_announcement_valid: Optional[bool] = None

class AnnouncementAnalysisResponse(BaseModel):
    # chatbot_service가 단일 객체 또는 객체의 배열을 반환할 수 있음
    # 여기서는 일반성을 위해 최상위 키를 두고 그 안에 결과를 넣거나, 직접 리스트를 반환할 수 있도록 함
    # 단순화를 위해, 서비스가 반환하는 dict/list를 그대로 반환하도록 하고, 여기서는 에러 메시지 구조만 정의
    # 또는, 성공 시 List[AnalyzedItem] 또는 AnalyzedItem을 반환하도록 구체화할 수 있습니다.
    # 지금은 서비스의 반환값을 그대로 활용하는 방향으로 가겠습니다.
    # 실제 사용 시에는 여기서 더 명확한 스키마를 정의하는 것이 좋습니다.
    # 모델 객체를 직접 반환할 경우 필요할 수 있음
    analysis_result: Optional[List[AnalyzedItem]] = None
    raw_result: Optional[dict] = None # 또는 List[dict]
    error: Optional[str] = None
    original_response: Optional[str] = None # Gemini가 JSON 파싱 실패 시 원본 응답

    class Config:
        orm_mode = True 