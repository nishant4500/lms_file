from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.deps import get_db, get_current_user

router = APIRouter(tags=["enrollments"])

@router.post("/courses/{id}/enroll")
def enroll_in_course(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can enroll")
    
    course = db.query(models.Course).filter(models.Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    existing = crud.get_enrollment(db, current_user.id, id)
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")
        
    enrollment = crud.enroll_student(db, current_user.id, id)
    return {"msg": "Successfully enrolled", "enrollment_id": enrollment.id}


@router.get("/me/enrollments")
def my_enrollments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view enrollments")

    enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == current_user.id).all()
    course_ids = [en.course_id for en in enrollments]
    if not course_ids:
        return []

    courses = db.query(models.Course).filter(models.Course.id.in_(course_ids)).all()
    return courses


@router.get("/courses/{course_id}/content")
def course_content(course_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    is_owner_instructor = current_user.role == "instructor" and course.instructor_id == current_user.id
    is_admin = current_user.role == "admin"
    is_enrolled_student = False
    if current_user.role == "student":
        is_enrolled_student = crud.get_enrollment(db, current_user.id, course_id) is not None

    if not (is_owner_instructor or is_admin or is_enrolled_student):
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    modules = db.query(models.Module).filter(models.Module.course_id == course_id).all()
    module_ids = [module.id for module in modules]
    resources = []
    if module_ids:
        resources = db.query(models.Resource).filter(models.Resource.module_id.in_(module_ids)).all()

    return {
        "course": course,
        "modules": modules,
        "resources": resources
    }
