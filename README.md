# ExamMentor AI

## Problem Statement

Students often struggle to efficiently review and understand large volumes of exam material. ExamMentor AI is an AI-powered exam preparation assistant that allows students to upload PDF documents (textbooks, past papers, notes) and ask questions. The system uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware answers grounded in the uploaded material.

## Planned Architecture

```
┌──────────────────┐       ┌──────────────────┐
│   Next.js        │  HTTP │   FastAPI         │
│   Frontend       │◄─────►│   Backend         │
│   (React)        │       │                   │
└──────────────────┘       └────────┬──────────┘
                                    │
                        ┌───────────┼───────────┐
                        │           │           │
                   PDF Service  RAG Service  AI Service
                   (pypdf)     (ChromaDB +   (HuggingFace
                               sentence-     Inference API)
                               transformers)
```

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Frontend | Next.js 14, React 18                    |
| Backend  | FastAPI, Uvicorn                        |
| AI/ML    | Hugging Face Inference API, Sentence Transformers |
| Vector DB| ChromaDB                                |
| PDF      | pypdf, Pillow                           |
| Deploy   | Docker                                  |

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- Git

### Backend

```bash
cd backend
# TODO: Create and activate virtual environment
# pip install -r requirements.txt
# cp .env.example .env   (fill in your keys)
# uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
# npm install
# cp .env.example .env.local
# npm run dev
```

### Verify

- Backend health check: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`

## License

<!-- TODO: Add license -->
