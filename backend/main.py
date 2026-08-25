"""
LearnLens AI - Main FastAPI Application
"""
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models

# Import routers
from routers import auth, student, assessment, practice, ai_assistant, teacher, evaluation

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LearnLens AI",
    description="Adaptive AI Learning & Assessment Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(assessment.router)
app.include_router(practice.router)
app.include_router(ai_assistant.router)
app.include_router(teacher.router)
app.include_router(evaluation.router)


@app.get("/")
def root():
    return {
        "message": "LearnLens AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "demo_mode": os.getenv("DEMO_MODE", "true"),
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "LearnLens AI Backend"}


@app.on_event("startup")
async def startup_event():
    """Auto-seed database on startup if empty."""
    try:
        from seed_data import seed_database
        seed_database()
    except Exception as e:
        print(f"Seed note: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
