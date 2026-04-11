from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, deps
from typing import List

router = APIRouter(prefix="/certificates", tags=["certificates"])

@router.get("/me", response_model=List[schemas.CertificateResponse])
def get_my_certificates(db: Session = Depends(deps.get_db), current_user = Depends(deps.get_current_user)):
    return crud.get_certificates(db, current_user.id)
