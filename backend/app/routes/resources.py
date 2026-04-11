from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.deps import get_current_user, get_db

router = APIRouter(tags=["resources"])


@router.post("/resources")
def create_resource(
    resource: schemas.ResourceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    db_module = db.query(models.Module).filter(models.Module.id == resource.module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")

    db_course = db.query(models.Course).filter(models.Course.id == db_module.course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role != "admin" and db_course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    return crud.create_resource(db, resource)


@router.get("/modules/{module_id}/resources")
def list_module_resources(module_id: int, db: Session = Depends(get_db)):
    db_module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    return crud.get_resources_by_module(db, module_id)
