"use client";

import { useMemo, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

const subjects = [
  "General / Other",
  "Data Structures and Algorithms",
  "Database Management Systems",
  "Computer Networks",
  "Operating Systems",
  "Computer Organization",
  "Theory of Computation",
  "Software Engineering",
  "Mathematics",
];

const answerStyles = [
  "Step-by-step",
  "Exam answer",
  "Beginner-friendly",
];

function formatMarkdownText(text) {
  return text.split("\n").map((line, index) => {
    if (line.startsWith("## ")) {
      return <h3 key={`${line}-${index}`}>{line.replace("## ", "")}</h3>;
    }

    if (line.startsWith("- ")) {
      return <p className="answer-bullet" key={`${line}-${index}`}>• {line.slice(2)}</p>;
    }

    if (/^\d+\.\s/.test(line)) {
      return <p className="answer-number" key={`${line}-${index}`}>{line}</p>;
    }

    return <p key={`${line}-${index}`}>{line || "\u00A0"}</p>;
  });
}

function makeDownloadText(question, answer, subject, notes) {
  const noteNames = notes.length
    ? notes.map((note) => `- ${note.name}`).join("\n")
    : "- No PDF notes were used.";

  return [
    "EXAMMENTOR AI - GENERATED STUDY RESPONSE",
    "=".repeat(54),
    "",
    "SUBJECT",
    subject,
    "",
    "QUESTION",
    question || "Question supplied through an uploaded image.",
    "",
    "ANSWER",
    answer,
    "",
    "PDF NOTES PROVIDED",
    noteNames,
    "",
    "DISCLAIMER",
    "This response is AI-generated for learning support. Verify calculations, definitions, and facts with official course materials.",
  ].join("\n");
}

export default function HomePage() {
  const [activeTab, setActiveTab] = useState("solve");
  const [subject, setSubject] = useState(subjects[0]);
  const [answerStyle, setAnswerStyle] = useState(answerStyles[0]);
  const [question, setQuestion] = useState("");
  const [questionImage, setQuestionImage] = useState(null);
  const [notes, setNotes] = useState([]);
  const [answer, setAnswer] = useState("");
  const [quiz, setQuiz] = useState("");
  const [quizTopic, setQuizTopic] = useState("");
  const [history, setHistory] = useState([]);
  const [isSolving, setIsSolving] = useState(false);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);
  const [error, setError] = useState("");
  const [quizError, setQuizError] = useState("");

  const notesContext = useMemo(() => {
    if (!notes.length) {
      return "";
    }

    return notes
      .map(
        (note, index) =>
          `[Uploaded PDF ${index + 1}: ${note.name}]\n${note.text.slice(0, 6000)}`
      )
      .join("\n\n");
  }, [notes]);

  async function readPdfFiles(files) {
    const selectedFiles = Array.from(files || []);

    if (!selectedFiles.length) {
      return;
    }

    const loadedNotes = await Promise.all(
      selectedFiles.map(async (file) => {
        const text = await file.text().catch(() => "");

        return {
          name: file.name,
          size: file.size,
          text:
            text ||
            "PDF text could not be extracted in the browser. The file name is still provided as study context.",
        };
      })
    );

    setNotes(loadedNotes);
  }

  async function solveQuestion(event) {
    event.preventDefault();
    setError("");
    setAnswer("");

    if (!question.trim() && !questionImage) {
      setError("Type a question, upload a question image, or do both.");
      return;
    }

    setIsSolving(true);

    try {
      const formData = new FormData();

      formData.append("question", question);
      formData.append("subject", subject);
      formData.append("answer_style", answerStyle);
      formData.append("notes_context", notesContext);

      if (questionImage) {
        formData.append("image", questionImage);
      }

      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "The backend could not solve this question.");
      }

      const generatedAnswer = data.answer || "No answer was returned by the AI model.";

      setAnswer(generatedAnswer);

      setHistory((currentHistory) => [
        {
          id: `${Date.now()}-${Math.random()}`,
          time: new Date().toLocaleString(),
          subject,
          question: question || "Question supplied through an uploaded image.",
          answer: generatedAnswer,
          noteNames: notes.map((note) => note.name),
        },
        ...currentHistory,
      ]);
    } catch (requestError) {
      setError(
        requestError.message ||
        "Could not contact the backend. Ensure the FastAPI server is running on port 8000."
      );
    } finally {
      setIsSolving(false);
    }
  }

  async function createQuiz() {
    setQuizError("");
    setQuiz("");

    if (!quizTopic.trim()) {
      setQuizError("Enter a topic before generating a quiz.");
      return;
    }

    setIsGeneratingQuiz(true);

    try {
      const response = await fetch(`${API_BASE_URL}/quiz`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: quizTopic,
          notes_context: notesContext,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "The backend could not generate a quiz.");
      }

      setQuiz(data.quiz || "The AI model did not return a quiz.");
    } catch (requestError) {
      setQuizError(
        requestError.message ||
        "Could not contact the backend. Ensure FastAPI is running on port 8000."
      );
    } finally {
      setIsGeneratingQuiz(false);
    }
  }

  function clearNotes() {
    setNotes([]);
  }

  function clearHistory() {
    setHistory([]);
  }

  function downloadAnswer() {
    const downloadText = makeDownloadText(question, answer, subject, notes);
    const blob = new Blob([downloadText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "exammentor_solution.txt";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI-POWERED EXAM PREPARATION</p>
          <h1>ExamMentor AI</h1>
          <p className="subtitle">
            Multimodal question solver, PDF-note assistant, and quiz generator
            for university and GATE-style preparation.
          </p>
        </div>

        <div className="status-pill">
          <span className="status-dot" />
          AI Ready
        </div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div className="sidebar-section">
            <p className="section-label">Study workspace</p>
            <h2>Your notes</h2>
            <p className="muted">
              Upload PDF notes. Their temporary text context is sent only with
              your current question or quiz request.
            </p>

            <label className="upload-box">
              <span className="upload-icon">↑</span>
              <span>Choose PDF notes</span>
              <small>Multiple PDF files supported</small>
              <input
                type="file"
                accept=".pdf,application/pdf"
                multiple
                onChange={(event) => readPdfFiles(event.target.files)}
              />
            </label>

            <div className="note-count">
              <span>Uploaded files</span>
              <strong>{notes.length}</strong>
            </div>

            {notes.length > 0 && (
              <div className="uploaded-note-list">
                {notes.map((note) => (
                  <p key={note.name} title={note.name}>
                    📄 {note.name}
                  </p>
                ))}
              </div>
            )}

            <button
              className="secondary-button full-width"
              onClick={clearNotes}
              type="button"
            >
              Clear notes
            </button>
          </div>

          <div className="sidebar-divider" />

          <div className="sidebar-section">
            <p className="section-label">How it works</p>

            <div className="step-row">
              <span className="step-number">1</span>
              <div>
                <strong>Retrieve</strong>
                <p>Use your uploaded notes as relevant study context.</p>
              </div>
            </div>

            <div className="step-row">
              <span className="step-number">2</span>
              <div>
                <strong>Understand</strong>
                <p>Analyze question text, diagrams, images, and formulas.</p>
              </div>
            </div>

            <div className="step-row">
              <span className="step-number">3</span>
              <div>
                <strong>Generate</strong>
                <p>Create a structured learning-focused answer or quiz.</p>
              </div>
            </div>
          </div>

          <div className="privacy-note">
            <span>🔒</span>
            <p>
              PDFs are used only as temporary request context in this prototype.
              Do not upload private or sensitive documents.
            </p>
          </div>
        </aside>

        <section className="content-area">
          <nav className="tabs" aria-label="Application sections">
            <button
              className={activeTab === "solve" ? "tab active" : "tab"}
              onClick={() => setActiveTab("solve")}
              type="button"
            >
              <span>✦</span> Solve Question
            </button>

            <button
              className={activeTab === "quiz" ? "tab active" : "tab"}
              onClick={() => setActiveTab("quiz")}
              type="button"
            >
              <span>▣</span> Generate Quiz
            </button>

            <button
              className={activeTab === "history" ? "tab active" : "tab"}
              onClick={() => setActiveTab("history")}
              type="button"
            >
              <span>◷</span> History
            </button>

            <button
              className={activeTab === "details" ? "tab active" : "tab"}
              onClick={() => setActiveTab("details")}
              type="button"
            >
              <span>ⓘ</span> Project Details
            </button>
          </nav>

          {activeTab === "solve" && (
            <section className="panel">
              <div className="panel-heading">
                <p className="section-label">Study assistant</p>
                <h2>Solve a question</h2>
                <p className="muted">
                  Ask about theory, algorithms, formulas, diagrams, circuits,
                  graphs, or technical exam problems.
                </p>
              </div>

              <form onSubmit={solveQuestion}>
                <div className="form-grid">
                  <label>
                    <span>Subject area</span>
                    <select
                      value={subject}
                      onChange={(event) => setSubject(event.target.value)}
                    >
                      {subjects.map((item) => (
                        <option key={item} value={item}>
                          {item}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    <span>Answer style</span>
                    <select
                      value={answerStyle}
                      onChange={(event) => setAnswerStyle(event.target.value)}
                    >
                      {answerStyles.map((item) => (
                        <option key={item} value={item}>
                          {item}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <label className="question-label">
                  <span>Your question</span>
                  <textarea
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="Example: Explain database normalization with a simple example."
                    rows={7}
                  />
                </label>

                <label className="image-upload">
                  <span className="image-upload-title">
                    <span>▧</span> Question image <small>(optional)</small>
                  </span>
                  <span className="image-upload-subtitle">
                    Upload a diagram, handwritten question, graph, circuit, table,
                    or formula.
                  </span>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    onChange={(event) =>
                      setQuestionImage(event.target.files?.[0] || null)
                    }
                  />
                  {questionImage && (
                    <span className="selected-file">
                      Selected: {questionImage.name}
                    </span>
                  )}
                </label>

                {error && <div className="error-message">{error}</div>}

                <button
                  className="primary-button"
                  disabled={isSolving}
                  type="submit"
                >
                  {isSolving ? "Solving..." : "✦ Solve with AI"}
                </button>
              </form>

              {answer && (
                <article className="answer-card">
                  <div className="answer-card-header">
                    <div>
                      <p className="section-label">Generated response</p>
                      <h3>AI Solution</h3>
                    </div>

                    <button
                      className="secondary-button"
                      onClick={downloadAnswer}
                      type="button"
                    >
                      Download TXT
                    </button>
                  </div>

                  <div className="answer-content">
                    {formatMarkdownText(answer)}
                  </div>

                  {notes.length > 0 && (
                    <div className="source-box">
                      <strong>📌 PDF notes provided for this answer</strong>
                      {notes.map((note) => (
                        <span key={note.name}>• {note.name}</span>
                      ))}
                    </div>
                  )}
                </article>
              )}
            </section>
          )}

          {activeTab === "quiz" && (
            <section className="panel">
              <div className="panel-heading">
                <p className="section-label">Practice mode</p>
                <h2>Generate a five-question quiz</h2>
                <p className="muted">
                  Enter a topic. Your uploaded PDF-note context will be included
                  when available.
                </p>
              </div>

              <div className="quiz-controls">
                <input
                  className="topic-input"
                  value={quizTopic}
                  onChange={(event) => setQuizTopic(event.target.value)}
                  placeholder="Example: DBMS normalization, TCP/IP, stack and queue"
                />

                <button
                  className="primary-button"
                  onClick={createQuiz}
                  disabled={isGeneratingQuiz}
                  type="button"
                >
                  {isGeneratingQuiz
                    ? "Generating quiz..."
                    : "Create 5-question quiz"}
                </button>
              </div>

              {quizError && <div className="error-message">{quizError}</div>}

              {quiz && (
                <article className="answer-card quiz-card">
                  <div className="answer-card-header">
                    <div>
                      <p className="section-label">Practice questions</p>
                      <h3>Quiz: {quizTopic}</h3>
                    </div>
                    <span className="answer-badge">5 MCQs</span>
                  </div>

                  <div className="answer-content">{formatMarkdownText(quiz)}</div>

                  {notes.length > 0 && (
                    <div className="source-box">
                      <strong>📌 PDF notes provided for this quiz</strong>
                      {notes.map((note) => (
                        <span key={note.name}>• {note.name}</span>
                      ))}
                    </div>
                  )}
                </article>
              )}
            </section>
          )}

          {activeTab === "history" && (
            <section className="panel">
              <div className="panel-heading row-between">
                <div>
                  <p className="section-label">Your activity</p>
                  <h2>Question history</h2>
                </div>

                {history.length > 0 && (
                  <button
                    className="secondary-button"
                    onClick={clearHistory}
                    type="button"
                  >
                    Clear history
                  </button>
                )}
              </div>

              {history.length === 0 ? (
                <div className="empty-state">
                  <div className="large-icon">◷</div>
                  <h3>No questions solved yet</h3>
                  <p className="muted">
                    Answers generated in this browser session appear here.
                  </p>
                </div>
              ) : (
                <div className="history-list">
                  {history.map((item) => (
                    <article className="history-card" key={item.id}>
                      <div className="row-between">
                        <strong>{item.subject}</strong>
                        <small>{item.time}</small>
                      </div>

                      <p className="history-question">{item.question}</p>
                      <p>{item.answer}</p>

                      {item.noteNames.length > 0 && (
                        <small className="history-notes">
                          Notes: {item.noteNames.join(", ")}
                        </small>
                      )}
                    </article>
                  ))}
                </div>
              )}
            </section>
          )}

          {activeTab === "details" && (
            <section className="panel details-panel">
              <p className="section-label">About the final-year project</p>
              <h2>ExamMentor AI</h2>

              <h3>Problem statement</h3>
              <p>
                Students often struggle with technical questions involving
                diagrams, algorithms, circuits, formulae, graphs, and dense theory.
                Standard chatbots may not use a student&apos;s own study material
                or provide a structured revision workflow.
              </p>

              <h3>Proposed solution</h3>
              <p>
                ExamMentor AI is a multimodal academic assistant. Students can
                upload PDF notes, submit a typed question or image question, and
                receive a structured explanation that can use the note context.
              </p>

              <h3>Project pipeline</h3>
              <p>
                PDF notes → temporary text context → question/image understanding →
                Hugging Face multimodal AI → structured answer → quiz generation →
                session history.
              </p>

              <h3>Technologies</h3>
              <p>
                Next.js, React, FastAPI, Hugging Face Inference API, Qwen3-VL,
                Python, PDF processing, and planned semantic retrieval using
                sentence-transformer embeddings.
              </p>

              <h3>Important limitation</h3>
              <p>
                This prototype is for learning support, not an official answer key.
                AI output can be inaccurate. Always verify calculations,
                definitions, and facts against official course materials.
              </p>
            </section>
          )}
        </section>
      </div>
    </main>
  );
}