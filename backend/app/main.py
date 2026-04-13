from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from app.database import engine
from app import models
from app.routes import auth
from app.routes import courses


# CREATE TABLES
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://ambitious-glacier-0d2d4010f.7.azurestaticapps.net",  # ✅ your Azure frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": f"Database integrity error: {str(exc.orig)}"}
    )


@app.get("/")
def root():
    return {"message": "LMS running"}

from app.routes import modules, enrollments, assignments, progress, resources, quizzes, certificates

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(modules.router)
app.include_router(enrollments.router)
app.include_router(assignments.router)
app.include_router(progress.router)
app.include_router(resources.router)
app.include_router(quizzes.router)
app.include_router(certificates.router)

frontend_dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(frontend_dist_dir), html=True), name="ui")
