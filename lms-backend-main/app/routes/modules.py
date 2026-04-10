from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.deps import get_db, get_current_user

router = APIRouter(tags=["modules"])

@router.post("/modules")
def create_module(module: schemas.ModuleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    # Verify instructor owns course
    db_course = db.query(models.Course).filter(models.Course.id == module.course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and db_course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this course")
        
    return crud.create_module(db, module)

@router.get("/modules/{course_id}")
def get_modules(course_id: int, db: Session = Depends(get_db)):
    return crud.get_modules_by_course(db, course_id)


@router.put("/modules/{module_id}")
def update_module(module_id: int, module: schemas.ModuleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    db_course = db.query(models.Course).filter(models.Course.id == module.course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and db_course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    updated = crud.update_module(db, module_id, module)
    if not updated:
        raise HTTPException(status_code=404, detail="Module not found")
    return updated


@router.delete("/modules/{module_id}")
def delete_module(module_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    db_module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")

    db_course = db.query(models.Course).filter(models.Course.id == db_module.course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and db_course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    crud.delete_module(db, module_id)
    return {"msg": "Module deleted"}
