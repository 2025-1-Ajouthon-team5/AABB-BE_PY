from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class User(Base):
    __tablename__ = "User"

    school_id = Column(String(255), primary_key=True, index=True)
    school_password = Column(String(255), nullable=False)  
    token = Column(String(255), nullable=True) 
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    tasks = relationship("Task", back_populates="owner")
    class_lists = relationship("ClassList", back_populates="user")

class ClassList(Base):
    __tablename__ = "ClassList"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_school_id = Column(String(255), ForeignKey("User.school_id", ondelete="CASCADE"), nullable=False)
    course_name = Column(String(255), nullable=False)
    course_id = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="class_lists")

class TaskType(str, enum.Enum):
    quiz = "퀴즈"
    assignment = "과제"
    exam = "시험"
    general = "일반"

class Task(Base):
    __tablename__ = "Task"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_school_id = Column(String(255), ForeignKey("User.school_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    detail = Column(Text, nullable=True)
    type = Column(Enum(TaskType), nullable=False)
    course = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(Boolean, default=False, nullable=False)
    source_description = Column(Text, nullable=True)  # Gemini 분석 전 원본 공지 내용
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="tasks") 