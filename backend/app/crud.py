from datetime import datetime
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
    
    # Initialize Progress at 0%
    progress = models.Progress(student_id=student_id, course_id=course_id, completion_percentage=0.0)
    db.add(progress)
    db.commit()
    
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
    
    # Trigger progress update to check for certificate eligibility
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if assignment:
        calculate_progress(db, student_id)
        
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

def create_quiz(db: Session, quiz: schemas.QuizCreate):
    db_quiz = models.Quiz(title=quiz.title, course_id=quiz.course_id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    for q in quiz.questions:
        db_question = models.Question(quiz_id=db_quiz.id, text=q.text)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        for opt in q.options:
            db_option = models.Option(question_id=db_question.id, text=opt.text, is_correct=opt.is_correct)
            db.add(db_option)
            db.commit()
            
    return db_quiz

def get_quiz(db: Session, quiz_id: int):
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

def get_quizzes_by_course(db: Session, course_id: int):
    return db.query(models.Quiz).filter(models.Quiz.course_id == course_id).all()

def create_quiz_attempt(db: Session, student_id: int, attempt: schemas.QuizAttemptSubmit):
    # Calculate score
    correct_count = 0
    total_questions = db.query(models.Question).filter(models.Question.quiz_id == attempt.quiz_id).count()
    
    for opt_id in attempt.answers:
        option = db.query(models.Option).filter(models.Option.id == opt_id).first()
        if option and option.is_correct:
            correct_count += 1
            
    score = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    db_attempt = models.QuizAttempt(student_id=student_id, quiz_id=attempt.quiz_id, score=score)
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    # Trigger progress update
    calculate_progress(db, student_id)
        
    return db_attempt

def get_certificates(db: Session, student_id: int):
    # Fetch certificates and attach course titles
    results = db.query(models.Certificate, models.Course.title).join(
        models.Course, models.Certificate.course_id == models.Course.id
    ).filter(models.Certificate.student_id == student_id).all()
    
    certs = []
    for cert, title in results:
        cert.course_title = title
        certs.append(cert)
    return certs

def check_and_generate_certificate(db: Session, student_id: int, course_id: int, progress: float):
    if progress >= 70.0:
        existing = db.query(models.Certificate).filter(
            models.Certificate.student_id == student_id,
            models.Certificate.course_id == course_id
        ).first()
        if not existing:
            cert = models.Certificate(
                student_id=student_id,
                course_id=course_id,
                issue_date=datetime.now().strftime("%Y-%m-%d")
            )
            db.add(cert)
            db.commit()
            db.refresh(cert)
            return cert
    return None

def calculate_progress(db: Session, student_id: int):
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == student_id).all()
    progress_data = []
    
    for enrollment in enrollments:
        # Assignments progress
        assignments = db.query(models.Assignment).filter(models.Assignment.course_id == enrollment.course_id).all()
        assignment_score = 100.0
        if assignments:
            assignment_ids = [a.id for a in assignments]
            submitted = db.query(models.Submission).filter(
                models.Submission.student_id == student_id,
                models.Submission.assignment_id.in_(assignment_ids)
            ).count()
            assignment_score = (submitted / len(assignments)) * 100.0
            
        # Quizzes progress
        quizzes = db.query(models.Quiz).filter(models.Quiz.course_id == enrollment.course_id).all()
        quiz_score = 100.0
        if quizzes:
            quiz_ids = [q.id for q in quizzes]
            attempts = db.query(models.QuizAttempt).filter(
                models.QuizAttempt.student_id == student_id,
                models.QuizAttempt.quiz_id.in_(quiz_ids)
            ).all()
            # Get max score per quiz
            unique_quiz_attempts = {}
            for att in attempts:
                if att.quiz_id not in unique_quiz_attempts or att.score > unique_quiz_attempts[att.quiz_id]:
                    unique_quiz_attempts[att.quiz_id] = att.score
            
            if len(unique_quiz_attempts) == 0:
                quiz_score = 0.0
            else:
                quiz_score = sum(unique_quiz_attempts.values()) / len(quizzes)
        
        # Combined progress (simple average)
        total_percentage = (assignment_score + quiz_score) / 2
            
        progress = db.query(models.Progress).filter(
            models.Progress.student_id == student_id,
            models.Progress.course_id == enrollment.course_id
        ).first()
        
        if not progress:
            progress = models.Progress(student_id=student_id, course_id=enrollment.course_id, completion_percentage=total_percentage)
            db.add(progress)
        else:
            progress.completion_percentage = total_percentage
        db.commit()
        db.refresh(progress)
        
        # Check for certificate (70% threshold)
        check_and_generate_certificate(db, student_id, enrollment.course_id, total_percentage)
        
        progress_data.append({"course_id": enrollment.course_id, "completion_percentage": progress.completion_percentage})
        
    return progress_data