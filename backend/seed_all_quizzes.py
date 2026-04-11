from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

def seed_all_quizzes():
    db = SessionLocal()
    try:
        courses = db.query(models.Course).all()
        for course in courses:
            # Check if course already has a quiz
            existing_quiz = db.query(models.Quiz).filter(models.Quiz.course_id == course.id).first()
            if not existing_quiz:
                print(f"Adding quiz to course: {course.title}")
                quiz = models.Quiz(title=f"Final Assessment: {course.title}", course_id=course.id)
                db.add(quiz)
                db.commit()
                db.refresh(quiz)
                
                # Add 2 sample questions
                q1 = models.Question(quiz_id=quiz.id, text=f"Which of the following describes {course.title} best?")
                db.add(q1)
                db.commit()
                db.refresh(q1)
                db.add_all([
                    models.Option(question_id=q1.id, text="The correct answer", is_correct=True),
                    models.Option(question_id=q1.id, text="The wrong answer", is_correct=False)
                ])
                
                q2 = models.Question(quiz_id=quiz.id, text="Is this course useful for beginners?")
                db.add(q2)
                db.commit()
                db.refresh(q2)
                db.add_all([
                    models.Option(question_id=q2.id, text="Yes, definitely", is_correct=True),
                    models.Option(question_id=q2.id, text="No, not at all", is_correct=False)
                ])
                db.commit()
        print("Done: All courses now have at least one quiz.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_all_quizzes()
