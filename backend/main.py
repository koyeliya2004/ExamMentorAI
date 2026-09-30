# backend/main.py
# FastAPI entry point for ExamMentor AI backend

from fastapi import FastAPI

app = FastAPI(
    title="ExamMentor AI API",
    description="Backend API for the ExamMentor AI exam preparation assistant",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# TODO: Add routes for /upload, /ask, /documents
