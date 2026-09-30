"""
ExamMentor AI — Streamlit Frontend
Multimodal question solver, PDF-note RAG assistant, and quiz generator
for exam preparation.
"""

import os
import io
import re
import base64
import hashlib
import datetime
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient
import chromadb

# ─── Environment ──────────────────────────────────────────────────────────────
load_dotenv()
hf_token = os.getenv("HF_TOKEN", "").strip()

# ─── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="ExamMentor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Constants ────────────────────────────────────────────────────────────────
APP_TITLE = "ExamMentor AI"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VISION_MODEL = "Qwen/Qwen3-VL-4B-Instruct"

SUBJECTS = [
    "General / Other",
    "Data Structures and Algorithms",
    "Database Management Systems",
    "Computer Networks",
    "Operating Systems",
    "Computer Organization",
    "Theory of Computation",
    "Software Engineering",
    "Mathematics",
]

ANSWER_STYLES = [
    "Step-by-step",
    "Exam answer",
    "Beginner-friendly",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════════════════

def inject_css():
    """Inject the professional blue/indigo theme CSS."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Main title ── */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #2563EB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
        line-height: 1.2;
    }

    /* ── Subtitle ── */
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #64748B;
        margin-top: 0.25rem;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    /* ── Feature cards ── */
    .feature-card {
        background: linear-gradient(
            135deg,
            rgba(79, 70, 229, 0.04) 0%,
            rgba(37, 99, 235, 0.06) 100%
        );
        border: 1px solid rgba(79, 70, 229, 0.15);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.12);
    }
    .feature-card h4 {
        color: #4F46E5;
        margin: 0 0 0.5rem 0;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    .feature-card p {
        color: #475569;
        margin: 0.25rem 0;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    /* ── Source cards ── */
    .source-card {
        background: linear-gradient(
            135deg,
            rgba(16, 185, 129, 0.06) 0%,
            rgba(5, 150, 105, 0.04) 100%
        );
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.5rem;
    }
    .source-card strong {
        color: #059669;
        font-family: 'Inter', sans-serif;
    }
    .source-card span {
        color: #64748B;
        font-size: 0.88rem;
    }

    /* ── Status cards ── */
    .status-card {
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        font-family: 'Inter', sans-serif;
    }
    .status-card.success {
        background: linear-gradient(
            135deg,
            rgba(16, 185, 129, 0.08) 0%,
            rgba(5, 150, 105, 0.05) 100%
        );
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #065F46;
    }
    .status-card.warning {
        background: linear-gradient(
            135deg,
            rgba(245, 158, 11, 0.08) 0%,
            rgba(217, 119, 6, 0.05) 100%
        );
        border: 1px solid rgba(245, 158, 11, 0.25);
        color: #92400E;
    }
    .status-card.info {
        background: linear-gradient(
            135deg,
            rgba(79, 70, 229, 0.08) 0%,
            rgba(37, 99, 235, 0.05) 100%
        );
        border: 1px solid rgba(79, 70, 229, 0.2);
        color: #3730A3;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 100%);
        border-right: 1px solid rgba(79, 70, 229, 0.1);
    }

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }

    /* ── Primary button enhancement ── */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        border: none;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    /* ── Section divider ── */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(79, 70, 229, 0.2) 50%,
            transparent 100%
        );
        margin: 1.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

def init_session_state():
    """Initialize all session-state variables on first run."""
    if "chroma_client" not in st.session_state:
        st.session_state.chroma_client = chromadb.EphemeralClient()
    if "notes_collection" not in st.session_state:
        st.session_state.notes_collection = (
            st.session_state.chroma_client.get_or_create_collection("student_notes")
        )
    defaults = {
        "indexed_files": set(),
        "history": [],
        "last_answer": None,
        "last_sources": None,
        "last_question": None,
        "last_context": None,
        "latest_quiz": None,
        "latest_quiz_sources": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ═══════════════════════════════════════════════════════════════════════════════
#  CACHED MODEL LOADING
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Loading embedding model …")
def load_embedder() -> SentenceTransformer:
    """Load the sentence-transformer model once and cache it."""
    return SentenceTransformer(EMBEDDING_MODEL)


# ═══════════════════════════════════════════════════════════════════════════════
#  TEXT PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def clean_text(text: str) -> str:
    """Normalize whitespace and strip non-printable characters."""
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text(
    text: str, chunk_size: int = 700, overlap: int = 120
) -> list[str]:
    """Split text into overlapping chunks, preferring sentence boundaries."""
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Try to break at the last sentence boundary within the chunk
        if end < len(text):
            last_period = chunk.rfind(". ")
            last_newline = chunk.rfind("\n")
            break_point = max(last_period, last_newline)
            if break_point > chunk_size * 0.3:
                chunk = text[start : start + break_point + 1]
                end = start + break_point + 1
        chunks.append(chunk.strip())
        start = end - overlap if end < len(text) else end
    return [c for c in chunks if c]


def pdf_to_chunks(uploaded_pdf) -> list[dict]:
    """Extract text from a PDF and return chunk dicts with metadata."""
    try:
        reader = PdfReader(uploaded_pdf)
    except Exception as exc:
        st.warning(f"⚠️ Could not read **{uploaded_pdf.name}**: {exc}")
        return []

    all_chunks: list[dict] = []
    for page_idx, page in enumerate(reader.pages, start=1):
        try:
            raw_text = page.extract_text() or ""
        except Exception:
            raw_text = ""

        cleaned = clean_text(raw_text)
        if len(cleaned) < 50:
            continue  # skip pages with very little extractable text

        page_chunks = split_text(cleaned)
        for chunk_idx, chunk_text in enumerate(page_chunks, start=1):
            all_chunks.append({
                "text": chunk_text,
                "source": uploaded_pdf.name,
                "page": page_idx,
                "chunk": chunk_idx,
            })

    return all_chunks


def file_signature(uploaded_file) -> str:
    """Create a unique hash signature to prevent re-indexing the same file."""
    content_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
    return f"{uploaded_file.name}::{content_hash}"


# ═══════════════════════════════════════════════════════════════════════════════
#  RAG — INDEXING & RETRIEVAL
# ═══════════════════════════════════════════════════════════════════════════════

def add_pdfs_to_knowledge_base(
    uploaded_pdfs: list, embedder: SentenceTransformer
) -> int:
    """Index uploaded PDFs into ChromaDB. Returns the number of new chunks."""
    collection = st.session_state.notes_collection
    new_chunks_total = 0

    for pdf_file in uploaded_pdfs:
        sig = file_signature(pdf_file)
        if sig in st.session_state.indexed_files:
            st.info(f"📄 **{pdf_file.name}** is already indexed — skipping.")
            continue

        pdf_file.seek(0)
        chunks = pdf_to_chunks(pdf_file)

        if not chunks:
            st.warning(
                f"⚠️ No usable text found in **{pdf_file.name}**. "
                "Scanned or image-only PDFs may require OCR, which is not "
                "supported in this version."
            )
            continue

        texts = [c["text"] for c in chunks]
        embeddings = embedder.encode(texts, show_progress_bar=False).tolist()
        ids = [f"{sig}__chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {"source": c["source"], "page": c["page"], "chunk": c["chunk"]}
            for c in chunks
        ]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        st.session_state.indexed_files.add(sig)
        new_chunks_total += len(chunks)
        st.success(
            f"✅ **{pdf_file.name}** indexed — {len(chunks)} sections added."
        )

    return new_chunks_total


def search_notes(
    question: str, embedder: SentenceTransformer, top_k: int = 4
) -> tuple[list[str], list[dict], list[float]]:
    """Retrieve the most relevant note chunks for a question."""
    collection = st.session_state.notes_collection
    if collection.count() == 0:
        return [], [], []

    query_embedding = embedder.encode(
        [question], show_progress_bar=False
    ).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    return documents, metadatas, distances


def reset_knowledge_base():
    """Delete and recreate the ChromaDB notes collection."""
    try:
        st.session_state.chroma_client.delete_collection("student_notes")
    except Exception:
        pass
    st.session_state.notes_collection = (
        st.session_state.chroma_client.get_or_create_collection("student_notes")
    )
    st.session_state.indexed_files = set()


# ═══════════════════════════════════════════════════════════════════════════════
#  IMAGE PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def image_to_data_url(uploaded_image) -> str:
    """Convert an uploaded image to a base64 JPEG data URL (max 1600×1600)."""
    img = Image.open(uploaded_image).convert("RGB")

    max_dim = 1600
    if img.width > max_dim or img.height > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


# ═══════════════════════════════════════════════════════════════════════════════
#  PROMPT BUILDING
# ═══════════════════════════════════════════════════════════════════════════════

def build_solver_prompt(
    question: str,
    retrieved_docs: list[str],
    source_metadata: list[dict],
    answer_style: str,
) -> str:
    """Build the structured prompt for the solver model."""
    # Assemble retrieved-note context
    context_block = ""
    if retrieved_docs:
        parts = []
        for doc, meta in zip(retrieved_docs, source_metadata):
            src = meta.get("source", "Unknown")
            pg = meta.get("page", "?")
            parts.append(f"[Source: {src}, Page {pg}]\n{doc}")
        context_block = "\n\n---\n\n".join(parts)

    style_instruction = {
        "Step-by-step": (
            "Explain each step clearly and sequentially, as if teaching."
        ),
        "Exam answer": (
            "Provide a concise, well-structured answer suitable for a "
            "written university or GATE exam."
        ),
        "Beginner-friendly": (
            "Use simple language and analogies. Assume little prior knowledge."
        ),
    }.get(answer_style, "Provide a clear, structured answer.")

    prompt = f"""You are ExamMentor AI, an academic assistant designed for university and GATE-level learners.

INSTRUCTIONS:
- Answer the student's question carefully and accurately.
- {style_instruction}
- Use the retrieved notes below ONLY if they are relevant to the question.
- Never claim the notes say something they do not say.
- If retrieved context is insufficient or absent, provide a best-effort answer using general academic knowledge and clearly state that no matching notes were found.
- If an image is provided, analyze it carefully. If the image is unclear or unreadable, say so explicitly.
- Avoid false certainty when the question is ambiguous.

RETRIEVED NOTES:
{context_block if context_block else "(No notes were retrieved for this question.)"}

STUDENT QUESTION:
{question}

Respond using EXACTLY this Markdown structure:

## Concept
(Brief explanation of the underlying concept)

## Solution
(Detailed solution following the {answer_style} style)

## Key Formula / Key Points
(Relevant formulas, definitions, or key points — use bullet points)

## Final Answer
(One clear, direct final answer)

## Self-check
(One or two questions the student can ask themselves to verify understanding)
"""
    return prompt.strip()


# ═══════════════════════════════════════════════════════════════════════════════
#  HUGGING FACE INFERENCE CALLS
# ═══════════════════════════════════════════════════════════════════════════════

def call_huggingface_model(
    token: str, prompt: str, image_file=None
) -> str:
    """Call the vision-language model for answer generation."""
    client = InferenceClient(api_key=token)

    if image_file is not None:
        data_url = image_to_data_url(image_file)
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]
    else:
        content = prompt

    response = client.chat_completion(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": content}],
        max_tokens=1300,
        temperature=0.25,
    )
    return response.choices[0].message.content


def generate_quiz(token: str, topic: str, context: str) -> str:
    """Generate a 5-question MCQ quiz from a topic and optional note context."""
    client = InferenceClient(api_key=token)

    quiz_prompt = f"""You are ExamMentor AI. Generate exactly 5 multiple-choice questions for exam practice.

TOPIC: {topic}

REFERENCE NOTES:
{context if context else "(No notes available — use general academic knowledge.)"}

RULES:
- Create exactly 5 questions.
- Each question must have choices A, B, C, D.
- After each question, state the correct answer and provide a one-sentence explanation.
- Questions should be suitable for university and GATE-level exams.
- Use clear, unambiguous language.

FORMAT each question exactly like this:

**Q1.** [Question text]
- A) [Choice A]
- B) [Choice B]
- C) [Choice C]
- D) [Choice D]

**Correct Answer:** [Letter]
**Explanation:** [One sentence]

---

Now generate the 5 questions.
"""
    response = client.chat_completion(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": quiz_prompt}],
        max_tokens=1300,
        temperature=0.45,
    )
    return response.choices[0].message.content


# ═══════════════════════════════════════════════════════════════════════════════
#  APPLICATION ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

inject_css()
init_session_state()

# Load the embedding model (cached across reruns)
try:
    embedder = load_embedder()
except Exception as exc:
    st.error(
        "❌ Failed to load the embedding model. Ensure `sentence-transformers` "
        "is installed and you have an internet connection for the first download."
    )
    with st.expander("Technical details"):
        st.code(str(exc))
    st.stop()


# ─── Title ────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="main-title">🎓 ExamMentor AI</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">'
    "Multimodal question solver, PDF-note RAG assistant, and quiz "
    "generator for exam preparation."
    "</p>",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # ── Configuration section ──
    st.header("⚙️ Configuration")

    if hf_token:
        st.markdown(
            '<div class="status-card success">'
            "✅ Hugging Face connection configured."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-card warning">'
            "⚠️ <strong>HF_TOKEN is not configured.</strong><br>"
            "Create <code>frontend/.env</code> from "
            "<code>frontend/.env.example</code> and set <code>HF_TOKEN</code> "
            "locally. Never commit <code>.env</code> to GitHub."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(f"**Answer model:** `{VISION_MODEL}`")
    st.markdown(f"**Embedding model:** `{EMBEDDING_MODEL}`")
    st.caption(
        "Tokens belong only in `frontend/.env` and deployment secret settings."
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Upload notes section ──
    st.header("📚 Upload Notes")

    uploaded_pdfs = st.file_uploader(
        "Upload one or more PDF note files",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader",
    )

    col_idx, col_clr = st.columns(2)
    with col_idx:
        index_clicked = st.button(
            "📥 Index PDFs", use_container_width=True
        )
    with col_clr:
        clear_notes_clicked = st.button(
            "🗑️ Clear notes", use_container_width=True
        )

    if index_clicked:
        if not uploaded_pdfs:
            st.warning("Upload at least one PDF first.")
        else:
            with st.spinner("Extracting and indexing PDFs …"):
                count = add_pdfs_to_knowledge_base(uploaded_pdfs, embedder)
            if count > 0:
                st.success(f"Indexed **{count}** new sections total.")

    if clear_notes_clicked:
        reset_knowledge_base()
        st.info("Knowledge base cleared.")

    total_sections = st.session_state.notes_collection.count()
    st.metric("Indexed sections", total_sections)
    st.caption(
        "PDFs are held only in the current app session and are not "
        "permanently stored."
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab_solve, tab_quiz, tab_history, tab_about = st.tabs([
    "🧠 Solve Question",
    "📝 Generate Quiz",
    "📚 History",
    "ℹ️ Project Details",
])


# ─── Tab 1: Solve Question ───────────────────────────────────────────────────
with tab_solve:
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        subject = st.selectbox("Subject area", SUBJECTS)
        answer_style = st.selectbox("Answer style", ANSWER_STYLES)

        student_question = st.text_area(
            "Type your question",
            placeholder=(
                "e.g. Explain the difference between BFS and DFS with "
                "examples."
            ),
            height=130,
        )

        uploaded_image = st.file_uploader(
            "Optionally upload a diagram or image",
            type=["png", "jpg", "jpeg", "webp"],
            key="image_uploader",
        )

        if uploaded_image:
            try:
                st.image(uploaded_image, caption="Uploaded image", width=350)
            except Exception:
                st.warning("Could not preview the uploaded image.")

        solve_clicked = st.button(
            "✨ Solve with AI", type="primary", use_container_width=True
        )

    with right_col:
        st.markdown(
            '<div class="feature-card">'
            "<h4>🔍 How the answer is made</h4>"
            "<p><strong>1. Retrieve</strong> — Your uploaded notes are "
            "semantically searched for the most relevant passages.</p>"
            "<p><strong>2. Understand</strong> — The question, context, and "
            "any image are assembled into a structured prompt.</p>"
            "<p><strong>3. Generate</strong> — A vision-language AI model "
            "produces a detailed, structured answer grounded in your "
            "notes.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="status-card warning">'
            "⚠️ AI-generated responses should always be verified against "
            "your course material, textbooks, and instructor notes."
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Handle solve button ──
    if solve_clicked:
        if not hf_token:
            st.error(
                "❌ Missing Hugging Face configuration. "
                "Create `frontend/.env` from `frontend/.env.example` and "
                "set `HF_TOKEN` locally. Never commit `.env` to GitHub."
            )
        elif not student_question.strip() and not uploaded_image:
            st.warning("Please enter a question or upload an image.")
        else:
            full_question = student_question.strip()
            if subject != "General / Other":
                full_question = f"[Subject: {subject}] {full_question}"

            # Retrieve relevant notes
            retrieved_docs, source_meta, distances = search_notes(
                full_question if full_question else "image question",
                embedder,
            )

            # Build prompt and call model
            solver_prompt = build_solver_prompt(
                full_question or "(See attached image)",
                retrieved_docs,
                source_meta,
                answer_style,
            )

            try:
                with st.spinner("🧠 Thinking …"):
                    if uploaded_image:
                        uploaded_image.seek(0)
                    answer = call_huggingface_model(
                        hf_token,
                        solver_prompt,
                        image_file=uploaded_image,
                    )

                # Persist results in session state
                st.session_state.last_answer = answer
                st.session_state.last_question = full_question
                st.session_state.last_sources = source_meta
                st.session_state.last_context = retrieved_docs

                # Insert into history
                st.session_state.history.insert(0, {
                    "timestamp": datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "subject": subject,
                    "question": full_question or "(Image question)",
                    "answer": answer,
                    "sources": source_meta,
                })

                st.success("✅ Answer generated successfully!")

            except Exception as exc:
                st.error(
                    "❌ The AI model could not generate an answer. This may "
                    "be due to model availability, rate limits, or an "
                    "invalid token."
                )
                with st.expander("Technical details"):
                    st.code(str(exc))

    # ── Display last answer ──
    if st.session_state.last_answer:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.subheader("💡 AI Solution")
        st.markdown(st.session_state.last_answer)

        # Source attribution
        if st.session_state.last_sources:
            with st.expander("📌 Notes retrieved for this answer"):
                for meta in st.session_state.last_sources:
                    st.markdown(
                        f'<div class="source-card">'
                        f'<strong>📄 {meta.get("source", "Unknown")}'
                        f"</strong> — "
                        f'<span>Page {meta.get("page", "?")}, '
                        f'Chunk {meta.get("chunk", "?")}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        # Build download text
        download_text = (
            f"{'=' * 60}\n"
            f"  ExamMentor AI — Generated Answer\n"
            f"{'=' * 60}\n\n"
            f"Question:\n{st.session_state.last_question}\n\n"
            f"{'─' * 40}\n"
            f"Answer:\n{st.session_state.last_answer}\n\n"
            f"{'─' * 40}\n"
            f"Note Sources Used:\n"
        )
        if st.session_state.last_sources:
            for meta in st.session_state.last_sources:
                download_text += (
                    f"  • {meta.get('source', 'Unknown')} — "
                    f"Page {meta.get('page', '?')}, "
                    f"Chunk {meta.get('chunk', '?')}\n"
                )
        else:
            download_text += "  (No uploaded notes were used.)\n"
        download_text += (
            f"\n{'─' * 40}\n"
            "Disclaimer: This answer was generated by an AI model and may "
            "contain errors. Always verify against official course "
            "materials.\n"
        )

        st.download_button(
            "⬇️ Download answer as TXT",
            data=download_text,
            file_name="exammentor_answer.txt",
            mime="text/plain",
        )


# ─── Tab 2: Generate Quiz ────────────────────────────────────────────────────
with tab_quiz:
    st.subheader("📝 Generate a practice quiz from your notes")

    quiz_topic = st.text_input(
        "Enter a topic for the quiz",
        placeholder="e.g. Binary Search Trees, Normalization, OSI Model",
    )

    quiz_clicked = st.button("🎯 Create 5-question quiz", type="primary")

    if quiz_clicked:
        if not hf_token:
            st.error(
                "❌ Missing Hugging Face configuration. "
                "Create `frontend/.env` from `frontend/.env.example` and "
                "set `HF_TOKEN` locally. Never commit `.env` to GitHub."
            )
        elif not quiz_topic.strip():
            st.warning("Please enter a topic for the quiz.")
        else:
            quiz_docs, quiz_meta, _ = search_notes(
                quiz_topic, embedder, top_k=4
            )
            context = "\n\n---\n\n".join(quiz_docs) if quiz_docs else ""

            try:
                with st.spinner("📝 Generating quiz questions …"):
                    quiz_result = generate_quiz(hf_token, quiz_topic, context)

                st.session_state.latest_quiz = quiz_result
                st.session_state.latest_quiz_sources = quiz_meta
                st.success("✅ Quiz generated!")

            except Exception as exc:
                st.error(
                    "❌ Could not generate the quiz. This may be due to "
                    "model availability or rate limits."
                )
                with st.expander("Technical details"):
                    st.code(str(exc))

    # Persist quiz display across reruns
    if st.session_state.latest_quiz:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown(st.session_state.latest_quiz)

        if st.session_state.latest_quiz_sources:
            with st.expander("📌 Notes used for quiz generation"):
                for meta in st.session_state.latest_quiz_sources:
                    st.markdown(
                        f'<div class="source-card">'
                        f'<strong>📄 {meta.get("source", "Unknown")}'
                        f"</strong> — "
                        f'<span>Page {meta.get("page", "?")}, '
                        f'Chunk {meta.get("chunk", "?")}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )


# ─── Tab 3: History ──────────────────────────────────────────────────────────
with tab_history:
    st.subheader("📚 Session question history")

    if not st.session_state.history:
        st.info(
            "No questions have been solved yet. Use the "
            "**🧠 Solve Question** tab to get started."
        )
    else:
        for idx, item in enumerate(st.session_state.history):
            q_preview = item["question"][:80]
            if len(item["question"]) > 80:
                q_preview += "…"
            with st.expander(
                f"**{item['subject']}** — {item['timestamp']}  |  "
                f"{q_preview}"
            ):
                st.markdown(f"**Subject:** {item['subject']}")
                st.markdown(f"**Time:** {item['timestamp']}")
                st.markdown(f"**Question:** {item['question']}")
                st.markdown("---")
                st.markdown(item["answer"])

                if item.get("sources"):
                    st.markdown("**Note sources used:**")
                    for meta in item["sources"]:
                        st.markdown(
                            f"- 📄 {meta.get('source', 'Unknown')} — "
                            f"Page {meta.get('page', '?')}, "
                            f"Chunk {meta.get('chunk', '?')}"
                        )

        if st.button("🗑️ Clear session history"):
            st.session_state.history = []
            st.session_state.last_answer = None
            st.session_state.last_sources = None
            st.session_state.last_question = None
            st.session_state.last_context = None
            st.rerun()


# ─── Tab 4: Project Details ──────────────────────────────────────────────────
with tab_about:
    st.subheader("ℹ️ Project Details — ExamMentor AI")

    st.markdown("""
### Problem Statement

University and competitive-exam students frequently deal with large volumes of
study material spread across multiple PDF notes, textbooks, and handwritten
documents. Extracting relevant answers, verifying conceptual understanding, and
generating practice questions from this material is time-consuming and
error-prone.

### Proposed Solution

**ExamMentor AI** is a multimodal, RAG-powered academic assistant that enables
students to:

1. Upload their own PDF study notes.
2. Ask questions — via text, image, or both — and receive structured,
   exam-ready answers grounded in their uploaded material.
3. Generate practice quizzes on specific topics using retrieved note context.
4. Review their question history and download answers for offline study.

### Architecture — Multimodal RAG Pipeline

```
PDF Upload
   ↓
Text Extraction (pypdf)
   ↓
Chunking (700 chars, 120 overlap)
   ↓
Embedding Generation (all-MiniLM-L6-v2)
   ↓
Vector Storage (ChromaDB — ephemeral, in-session)
   ↓
Semantic Retrieval (top-k relevant chunks)
   ↓
Prompt Assembly (question + context + style + image)
   ↓
Vision-Language Model (Qwen3-VL via Hugging Face Inference API)
   ↓
Structured Answer Display + Source Attribution
   ↓
Quiz Generation / History / TXT Download
```

### Technologies Used

| Component | Technology |
|---|---|
| Frontend & UI | Streamlit |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Database | ChromaDB (ephemeral client) |
| PDF Processing | pypdf |
| Image Processing | Pillow |
| LLM Inference | Hugging Face Inference API |
| Answer Model | `Qwen/Qwen3-VL-4B-Instruct` |
| Environment Config | python-dotenv |

### Key Novelty / Contribution

- **Multimodal input**: Students can ask questions using text, images (diagrams,
  handwritten problems), or both.
- **Personalized retrieval**: Answers are grounded in the student's own uploaded
  notes via semantic search, not generic internet results.
- **Structured exam-ready output**: Every answer follows a consistent academic
  format (Concept → Solution → Key Points → Final Answer → Self-check).
- **Quiz generation from notes**: Practice MCQs are generated using the
  student's own study material as context.

### Limitations

- **Text-based PDFs work best.** Scanned or image-only PDFs require OCR
  preprocessing, which is not included in this version.
- **AI answers can be incorrect.** All generated responses should be verified
  against official course materials and textbooks.
- **Uploaded data is session-only.** Notes and history are not persisted across
  sessions; they exist only while the app is running.
- **Model availability and cost** depend on the Hugging Face provider and
  account tier. Rate limits may apply.
- **Image analysis quality** depends on image resolution and clarity.
    """)
