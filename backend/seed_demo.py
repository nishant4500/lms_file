from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
import datetime

def seed():
    db = SessionLocal()
    try:
        # 1. Get or Create an Instructor
        instructor = db.query(models.User).filter(models.User.email == "inst_test@gmail.com").first()
        if not instructor:
            instructor = models.User(name="Expert Instructor", email="inst_test@gmail.com", password="1234", role="instructor")
            db.add(instructor)
            db.commit()
            db.refresh(instructor)

        # 2. Create the Demo Course
        course = models.Course(
            title="Next.js 15 Mastery: From Zero to Hero",
            description="Master the latest features of Next.js 15, including Server Components, App Router, and Turbopack.",
            instructor_id=instructor.id
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        # 3. Add a Module
        module = models.Module(
            title="Module 1: React Server Components (RSC)",
            content="In this module, we explore how Server Components work and why they are the future of React.",
            course_id=course.id
        )
        db.add(module)
        db.commit()
        db.refresh(module)

        # 4. Add a Resource
        resource = models.Resource(
            title="Intro to Next.js 15 RSC (Video)",
            url="https://nextjs.org/docs/app/building-your-application/rendering/server-components",
            resource_type="video",
            module_id=module.id
        )
        db.add(resource)

        # 5. Add an Assignment
        assignment = models.Assignment(
            title="Final Project: Portfolio Site",
            description="Create a 3-page portfolio site using Next.js 15 and Tailwind CSS.",
            course_id=course.id
        )
        db.add(assignment)

        # 6. Create a Quiz (US-07)
        quiz = models.Quiz(
            title="Next.js 15 Knowledge Check",
            course_id=course.id
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

        # 7. Add Questions to the Quiz
        q1 = models.Question(quiz_id=quiz.id, text="What is the default component type in Next.js 15?")
        db.add(q1)
        db.commit()
        db.refresh(q1)
        
        db.add_all([
            models.Option(question_id=q1.id, text="Client Component", is_correct=False),
            models.Option(question_id=q1.id, text="Server Component", is_correct=True),
            models.Option(question_id=q1.id, text="Hybrid Component", is_correct=False)
        ])

        q2 = models.Question(quiz_id=quiz.id, text="Which file is used for layouts in the App Router?")
        db.add(q2)
        db.commit()
        db.refresh(q2)
        
        db.add_all([
            models.Option(question_id=q2.id, text="page.tsx", is_correct=False),
            models.Option(question_id=q2.id, text="layout.tsx", is_correct=True),
            models.Option(question_id=q2.id, text="_app.tsx", is_correct=False)
        ])

        db.commit()
        print(f"Demo Course Created: {course.title}")
        print("Instructor Login: inst_test@gmail.com / 1234")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
