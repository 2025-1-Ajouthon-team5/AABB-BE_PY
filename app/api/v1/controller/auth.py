from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app import crud, schemas, models # Updated import
from app.database import get_db # Updated import
from app.config import settings # Updated import
from app.core.security import create_access_token, get_current_user # Placeholder for security functions

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, school_id=user.school_id)
    if db_user:
        raise HTTPException(status_code=400, detail="School ID already registered")
    return crud.create_user(db=db, user=user)

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user(db, school_id=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.school_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect school_id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.school_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 