from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, deps
from typing import List

router = APIRouter(prefix="/quizzes", tags=["quizzes"])

@router.post("/", response_model=schemas.QuizResponse)
def create_quiz(quiz: schemas.QuizCreate, db: Session = Depends(deps.get_db), current_user = Depends(deps.get_current_user)):
    if current_user.role not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Only instructors or admins can create quizzes")
    return crud.create_quiz(db, quiz)

@router.get("/{quiz_id}", response_model=schemas.QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(deps.get_db), current_user = Depends(deps.get_current_user)):
    db_quiz = crud.get_quiz(db, quiz_id)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return db_quiz

@router.get("/course/{course_id}", response_model=List[schemas.QuizResponse])
def get_course_quizzes(course_id: int, db: Session = Depends(deps.get_db), current_user = Depends(deps.get_current_user)):
    return crud.get_quizzes_by_course(db, course_id)

@router.post("/{quiz_id}/attempt", response_model=schemas.QuizAttemptResponse)
def attempt_quiz(quiz_id: int, attempt: schemas.QuizAttemptSubmit, db: Session = Depends(deps.get_db), current_user = Depends(deps.get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can attempt quizzes")
    if attempt.quiz_id != quiz_id:
        raise HTTPException(status_code=400, detail="Quiz ID mismatch")
    return crud.create_quiz_attempt(db, current_user.id, attempt)
