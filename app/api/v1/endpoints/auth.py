from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app import crud, schemas, models
from app.database import get_db
from app.services.AnnService import get_coursist
from app.services.chatbot_service import analyze_announcement

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
        school_password=user_in.password,
        student_number=None  # student_number를 명시적으로 None으로 설정
    )
    created_user = crud.create_user(db=db, user=user_create_data)

    # 2. Ann Service 로직 호출 (동기 함수이므로 run_in_threadpool 사용)
    try:
        print(f"[Register API] AnnService.get_coursist 호출 시작: user_id={user_in.id}")
        # get_coursist는 리스트를 반환합니다. [{title, detail, type, course_id}, ...]
        announcement_dtos: List[Dict[str, Any]] = await run_in_threadpool(get_coursist, user_id=user_in.id, user_pw=user_in.password)
        
        print(f"[Register API] AnnService.get_coursist 호출 완료. {len(announcement_dtos) if announcement_dtos else 0}개의 공지 DTO 수신.")
        
        return announcement_dtos

        if announcement_dtos:
            unique_courses = {}
            for dto in announcement_dtos:
                # 과목 정보 저장 (중복 방지)
                course_id_from_ann = dto.get("course_id")
                
                if course_id_from_ann and course_id_from_ann not in unique_courses:
                    # course_name을 어떻게 가져올지 정의 필요. 여기서는 course_id를 임시 사용
                    existing_class = db.query(models.ClassList).filter(
                        models.ClassList.user_school_id == created_user.school_id,
                        models.ClassList.course_id == course_id_from_ann
                    ).first()
                    if not existing_class:
                        class_list_create = schemas.ClassListCreate(
                            course_name=f"과목_{course_id_from_ann}", # 실제 과목명 필요
                            course_id=course_id_from_ann
                        )
                        crud.create_user_class_list_item(db=db, item=class_list_create, user_school_id=created_user.school_id)
                    unique_courses[course_id_from_ann] = True

                # 공지사항 분석 및 Task 저장
                announcement_detail = dto.get("detail")
                announcement_title = dto.get("title", "(제목 없음)")
                if announcement_detail:
                    print(f"[Register API] ChatbotService.analyze_announcement 호출 시작: title={announcement_title}")
                    # analyze_announcement는 dict 또는 list를 반환
                    analysis_result: Any = await analyze_announcement(announcement_detail)
                    print(f"[Register API] ChatbotService.analyze_announcement 호출 완료.")

                    tasks_to_create = []
                    if isinstance(analysis_result, list):
                        tasks_to_create = analysis_result
                    elif isinstance(analysis_result, dict) and analysis_result.get("is_announcement_valid"):
                        # 단일 객체 결과도 리스트로 감싸서 일관되게 처리
                        tasks_to_create = [analysis_result]
                    
                    for task_data in tasks_to_create:
                        if isinstance(task_data, dict) and task_data.get("is_announcement_valid"):
                            # date 필드 형식 변환 (YYYY-MM-DD HH:MM:SS -> datetime 객체 or None)
                            due_date_str = task_data.get("date")
                            due_date_obj = None
                            if due_date_str:
                                try:
                                    due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    print(f"[Register API] 날짜 형식 오류: {due_date_str}. Null로 처리합니다.")
                                    pass # 날짜 형식이 맞지 않으면 None으로 유지
                            
                            task_create_data = schemas.TaskCreate(
                                title=task_data.get("title", announcement_title), # Gemini가 title 안주면 공지 제목 사용
                                detail=task_data.get("detail"),
                                type=task_data.get("type", "일반"), # 기본값을 일반으로
                                due_date=due_date_obj,
                                source_description=announcement_detail # 원본 공지 내용 저장
                            )
                            crud.create_user_task(db=db, task=task_create_data, user_school_id=created_user.school_id)
                            print(f"[Register API] Task 저장 완료: {task_create_data.title}")
        else:
            print(f"[Register API] AnnService로부터 받은 공지사항 DTO가 없습니다.")

    except Exception as e:
        print(f"[Register API] AnnService 또는 ChatbotService 처리 중 오류 발생: {e}")

    return created_user