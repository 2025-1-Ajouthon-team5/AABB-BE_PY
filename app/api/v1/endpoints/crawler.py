from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import crawler_service # 수정: crawler_service 모듈 전체를 임포트

from app import crud

router = APIRouter()

@router.get("/crawl/{token}", status_code=status.HTTP_200_OK)
async def crawl_user_data(
    token: str,
    db: Session = Depends(get_db)
):
    """
    지정된 사용자의 공지사항 및 과제 정보를 크롤링하고 데이터베이스에 저장합니다.
    - **id**: 학교 ID
    - **password**: 비밀번호
    """
    #token 
    user_in = crud.get_user_by_token(db, token=token)
    
    school_id = user_in.school_id
    password = user_in.school_password
    
    print("school_id : ", school_id)
    print("password : ", password)
    
    # password 복호화 
    # plain_password = crud.decrypt_text(password)
    # print("plain_password : ", plain_password)
    
    try:
        result = await crawler_service.process_crawled_data_for_user(
            school_id=school_id,
            password=password,
            db=db
        )
        return result
    
    except Exception as e:
        # 서비스 레벨에서 처리되지 않은 예외가 발생할 경우
        print(f"[Crawl Endpoint] 최종 예외 처리: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"크롤링 및 데이터 처리 중 예상치 못한 오류 발생: {e}"
        ) 
        
        

@router.get("/crawl2/{token}", status_code=status.HTTP_200_OK)
async def crawl_user_data2(
    token: str,
    db: Session = Depends(get_db)
):
    """
    지정된 사용자의 공지사항 및 과제 정보를 크롤링하고 데이터베이스에 저장합니다.
    - **id**: 학교 ID
    - **password**: 비밀번호
    """
    #token 
    user_in = crud.get_user_by_token(db, token=token)
    
    print("user_in : ", user_in)
    
    if(user_in is None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다."
        )
    
    school_id = user_in.school_id
    password = user_in.school_password
    
    print("school_id : ", school_id)
    print("password : ", password)
    
    try:
        result = await crawler_service.process_crawled_data_for_user2(
            school_id=school_id,
            password=password,
            db=db
        )
        return result
    
    except Exception as e:
        # 서비스 레벨에서 처리되지 않은 예외가 발생할 경우
        print(f"[Crawl Endpoint] 최종 예외 처리: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"크롤링 및 데이터 처리 중 예상치 못한 오류 발생: {e}"
        ) 