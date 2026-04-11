from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from fastapi import HTTPException

router = APIRouter(tags=["auth"])

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if not user.email:
        raise HTTPException(status_code=400, detail="Email required")

    if not user.password:
        raise HTTPException(status_code=400, detail="Password required")

    if not user.name:
        raise HTTPException(status_code=400, detail="Name required")

    if not user.role:
        raise HTTPException(status_code=400, detail="Role required")
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"msg": "User registered"}


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    if not user.email:
        raise HTTPException(status_code=400, detail="Email required")

    if not user.password:
        raise HTTPException(status_code=400, detail="Password required")
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "user_id": db_user.id,
            "role": db_user.role
        }, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": db_user.id,
        "role": db_user.role,
        "name": db_user.name
    }