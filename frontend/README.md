# ExamMentor AI — Frontend

Multimodal question solver, PDF-note RAG assistant, and quiz generator for exam preparation.

## Features

- **PDF Note Upload** — Upload one or more text-based PDF study notes.
- **Semantic Retrieval (RAG)** — Notes are chunked, embedded, and stored in an in-session ChromaDB vector store for retrieval.
- **Text Questions** — Ask any academic question and receive a structured, exam-ready answer.
- **Image / Diagram Questions** — Upload an image (diagram, handwritten problem) alongside your question for multimodal analysis.
- **Structured Answers** — Every answer follows: Concept → Solution → Key Points → Final Answer → Self-check.
- **Source Attribution** — See exactly which uploaded note pages were used to generate the answer.
- **Quiz Generation** — Generate 5 MCQs on any topic, grounded in your uploaded notes.
- **Answer History** — Review all questions solved during the session.
- **TXT Download** — Download any generated answer as a `.txt` file for offline study.
- **No Permanent Storage** — All data exists only in the current app session.

## Architecture Summary

```
PDF Upload → Text Extraction (pypdf) → Chunking → Embeddings (all-MiniLM-L6-v2)
   → ChromaDB (ephemeral) → Semantic Retrieval → Prompt Assembly
   → Qwen3-VL (Hugging Face Inference API) → Structured Answer + Sources
```

## Local Setup (Windows PowerShell)

```powershell
# 1. Navigate to the frontend directory
cd frontend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\Activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create your environment file from the template
copy .env.example .env

# 6. Open .env and replace the placeholder with your real Hugging Face token
#    HF_TOKEN=hf_your_actual_token_here

# 7. Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Security Warning

> **Never commit `.env` or your `HF_TOKEN` to version control.**
>
> The `.gitignore` in this directory already excludes `.env` files. Your token
> should exist only in your local `.env` file or in your deployment platform's
> secret/environment settings.

## Limitations & Disclaimer

- **Text-based PDFs work best.** Scanned or image-only PDFs require OCR, which is not included.
- **AI answers can be incorrect.** Always verify against official course materials and textbooks.
- **Session-only storage.** Uploaded notes and history are not saved between sessions.
- **Model availability** depends on your Hugging Face account tier; rate limits may apply.
- This tool is an academic aid, not a replacement for studying.
