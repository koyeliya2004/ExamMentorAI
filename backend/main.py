from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import app as exammentor_app

app = FastAPI(
    title="ExamMentorAI Backend",
    description="ExamMentorAI API service is running.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["status"])
def root():
    return {
        "status": "ok",
        "service": "ExamMentorAI Backend",
        "message": "Backend is live. Use /docs for API documentation and /health for a health check.",
    }

@app.get("/health", tags=["status"])
def health():
    return {"status": "healthy"}

app.mount("/api", exammentor_app)
