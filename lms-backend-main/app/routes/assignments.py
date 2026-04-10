from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.deps import get_db, get_current_user

router = APIRouter(tags=["assignments"])

@router.post("/assignments")
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_course = db.query(models.Course).filter(models.Course.id == assignment.course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if db_course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this course")
        
    return crud.create_assignment(db, assignment)

@router.post("/assignments/{id}/submit")
def submit_assignment(id: int, submission: schemas.SubmissionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit")
        
    assignment = crud.get_assignment(db, id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    enrollment = crud.get_enrollment(db, current_user.id, assignment.course_id)
    if not enrollment:
        raise HTTPException(status_code=403, detail="Must be enrolled to submit")
        
    updated = crud.create_submission(db, id, current_user.id, submission.content)
    return {"msg": "Assignment submitted successfully"}
