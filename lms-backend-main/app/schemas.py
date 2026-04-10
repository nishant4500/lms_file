from pydantic import BaseModel, Field
from typing import Literal

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