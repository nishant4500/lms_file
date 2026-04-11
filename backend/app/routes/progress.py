from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.deps import get_db, get_current_user

router = APIRouter(tags=["progress"])

@router.get("/progress/{student_id}")
def get_student_progress(student_id: int, db: Session = Depends(get_db)):
    progress_data = crud.calculate_progress(db, student_id)
    return {"student_id": student_id, "progress": progress_data}
