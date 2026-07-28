# Resume Evaluator

An AI-powered tool that extracts structured information from a resume (skills, experience, projects) and evaluates how well it matches a given set of job requirements — returning a match percentage with reasoning.

Built as a mini-project to explore practical LLM application design: structured extraction, output validation, and semantic (not just keyword) matching.

## What it does

1. Takes a resume in PDF or DOCX format
2. Extracts skills, experience, and projects using an LLM (Groq / Llama 3.3)
3. Compares the extracted data against a set of job requirements
4. Returns a match percentage, matched/missing skills, and a short reasoning explanation

## Why this isn't just keyword matching

A naive resume screener does string matching — "Python" in resume, "Python" in job requirement, match. That misses candidates who demonstrate a skill without listing it verbatim (e.g. someone who "built a REST API with FastAPI" but never wrote the words "REST APIs" as a bullet point).

This project uses the LLM for two distinct jobs instead:

- **Extraction is kept strict.** The prompt explicitly instructs the model to only extract skills that are *explicitly stated* in a skills/technologies section — not inferred from project descriptions. This avoids the model "hallucinating" skills a candidate didn't actually claim.
- **Matching is kept semantic.** The matching step, by contrast, is explicitly allowed to reason about whether a project description demonstrates a required capability, even if the exact keyword isn't present. This mirrors how a human recruiter actually reads a resume — they read what you *built*, not just what you *listed*.

Keeping these two steps separate (rather than one big "just do it all" prompt) also made the output far more consistent and easier to validate.

## Tech stack

- **Python** — core language
- **Groq API (Llama 3.3 70B)** — structured extraction and semantic matching
- **Pydantic** — validates LLM output against a strict schema, catching malformed responses before they break downstream logic
- **FastAPI** — backend API serving the evaluation pipeline
- **Streamlit** — simple frontend for uploading a resume and viewing results
- **pypdf / python-docx** — resume text extraction from PDF and DOCX

## Architecture
Resume (PDF/DOCX)
│
▼
extractor.py → raw text extraction
│
▼
parser.py → LLM call → structured JSON (skills, experience, projects)
→ validated against a Pydantic schema
│
▼
matcher.py → LLM call → compares resume data vs HR requirements
→ returns match %, matched/missing skills, reasoning
│
▼
FastAPI (main.py) → exposes /evaluate-resume endpoint
│
▼
Streamlit (app_ui.py) → upload UI + results display

## Running it locally

**1. Clone and install dependencies**
```bash
git clone <your-repo-url>
cd resume-evaluator
uv sync
```

**2. Add your Groq API key**

Create a `.env` file in the project root:

**3. Start the backend**
```bash
uv run uvicorn main:app --reload
```

**4. Start the frontend** (in a second terminal)
```bash
uv run streamlit run app_ui.py
```

**5. Open the app**

Streamlit will open automatically at `http://localhost:8501`. Upload a resume (PDF or DOCX) and click "Evaluate Resume."

## Known limitations / future improvements

- HR requirements are currently hardcoded; a future version could accept a job description as free text and have the LLM structure it automatically
- No persistence layer yet — each evaluation is stateless
- Could add batch processing for evaluating multiple resumes against the same job posting