from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., max_length=120)
    password: str = Field(..., min_length=4, max_length=128)
    role: Literal["student", "instructor", "admin"]


class UserLogin(BaseModel):
    email: str = Field(..., max_length=120)
    password: str


class CourseCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., min_length=3, max_length=1000)

class ModuleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=1)
    course_id: int = Field(..., gt=0)


class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    url: str = Field(..., min_length=5, max_length=500)
    resource_type: Literal["video", "file", "link"]
    module_id: int = Field(..., gt=0)

class EnrollmentCreate(BaseModel):
    course_id: int = Field(..., gt=0)

class AssignmentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=1)
    course_id: int = Field(..., gt=0)

class SubmissionCreate(BaseModel):
    content: str = Field(..., min_length=1)

class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: str
    course_id: int
    class Config:
        orm_mode = True

class OptionCreate(BaseModel):
    text: str
    is_correct: bool

class OptionResponse(BaseModel):
    id: int
    text: str
    is_correct: bool
    class Config:
        orm_mode = True

class QuestionCreate(BaseModel):
    text: str
    options: List[OptionCreate]

class QuestionResponse(BaseModel):
    id: int
    text: str
    options: List[OptionResponse]
    class Config:
        orm_mode = True

class QuizCreate(BaseModel):
    title: str
    course_id: int
    questions: List[QuestionCreate]

class QuizResponse(BaseModel):
    id: int
    title: str
    course_id: int
    questions: List[QuestionResponse]
    class Config:
        orm_mode = True

class QuizAttemptSubmit(BaseModel):
    quiz_id: int
    answers: List[int]  # List of selected option IDs

class QuizAttemptResponse(BaseModel):
    id: int
    score: float
    class Config:
        orm_mode = True

class CertificateResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    course_title: Optional[str] = None
    issue_date: str
    class Config:
        orm_mode = True