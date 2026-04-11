from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas, crud, models
from app.deps import get_db, get_current_user

router = APIRouter(tags=["courses"])


# CREATE
@router.post("/courses")
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not course.title:
        raise HTTPException(status_code=400, detail="Title required")
    if current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Only instructors/admin can create courses")
    return crud.create_course(db, course, current_user.id)


# READ
@router.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db)


# UPDATE
@router.put("/courses/{course_id}")
def update_course(course_id: int, course: schemas.CourseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Only instructors/admin can update courses")
    
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and db_course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this course")

    updated_course = crud.update_course(db, course_id, course)
    return {"msg": "Course updated"}


# DELETE
@router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Only instructors/admin can delete courses")
    
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and db_course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this course")

    deleted_course = crud.delete_course(db, course_id)
    return {"msg": "Course deleted"}