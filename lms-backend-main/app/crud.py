from sqlalchemy.orm import Session
from app import models, schemas


def create_course(db: Session, course: schemas.CourseCreate, instructor_id: int):
    new_course = models.Course(
        title=course.title,
        description=course.description,
        instructor_id=instructor_id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course



def get_courses(db: Session):
    return db.query(models.Course).all()


def update_course(db: Session, course_id: int, course: schemas.CourseCreate):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    
    if not db_course:
        return None

    db_course.title = course.title
    db_course.description = course.description
    db.commit()
    return db_course


def delete_course(db: Session, course_id: int):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()

    if not db_course:
        return None

    db.delete(db_course)
    db.commit()
    return db_course

def create_module(db: Session, module: schemas.ModuleCreate):
    new_module = models.Module(
        title=module.title,
        content=module.content,
        course_id=module.course_id
    )
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module

def get_modules_by_course(db: Session, course_id: int):
    return db.query(models.Module).filter(models.Module.course_id == course_id).all()


def update_module(db: Session, module_id: int, module: schemas.ModuleCreate):
    db_module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not db_module:
        return None

    db_module.title = module.title
    db_module.content = module.content
    db_module.course_id = module.course_id
    db.commit()
    db.refresh(db_module)
    return db_module


def delete_module(db: Session, module_id: int):
    db_module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not db_module:
        return None

    db.delete(db_module)
    db.commit()
    return db_module

def enroll_student(db: Session, student_id: int, course_id: int):
    enrollment = models.Enrollment(student_id=student_id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def get_enrollment(db: Session, student_id: int, course_id: int):
    return db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student_id,
        models.Enrollment.course_id == course_id
    ).first()

def create_assignment(db: Session, assignment: schemas.AssignmentCreate):
    new_assignment = models.Assignment(
        title=assignment.title,
        description=assignment.description,
        course_id=assignment.course_id
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

def get_assignment(db: Session, assignment_id: int):
    return db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

def create_submission(db: Session, assignment_id: int, student_id: int, content: str):
    new_submission = models.Submission(
        assignment_id=assignment_id,
        student_id=student_id,
        content=content
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    return new_submission


def create_resource(db: Session, resource: schemas.ResourceCreate):
    new_resource = models.Resource(
        title=resource.title,
        url=resource.url,
        resource_type=resource.resource_type,
        module_id=resource.module_id
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource


def get_resources_by_module(db: Session, module_id: int):
    return db.query(models.Resource).filter(models.Resource.module_id == module_id).all()

def calculate_progress(db: Session, student_id: int):
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == student_id).all()
    progress_data = []
    
    for enrollment in enrollments:
        assignments = db.query(models.Assignment).filter(models.Assignment.course_id == enrollment.course_id).all()
        if not assignments:
            percentage = 100.0
        else:
            assignment_ids = [a.id for a in assignments]
            submitted = db.query(models.Submission).filter(
                models.Submission.student_id == student_id,
                models.Submission.assignment_id.in_(assignment_ids)
            ).count()
            percentage = (submitted / len(assignments)) * 100.0
            
        progress = db.query(models.Progress).filter(
            models.Progress.student_id == student_id,
            models.Progress.course_id == enrollment.course_id
        ).first()
        
        if not progress:
            progress = models.Progress(student_id=student_id, course_id=enrollment.course_id, completion_percentage=percentage)
            db.add(progress)
        else:
            progress.completion_percentage = percentage
        db.commit()
        db.refresh(progress)
        progress_data.append({"course_id": enrollment.course_id, "completion_percentage": progress.completion_percentage})
        
    return progress_data