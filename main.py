"""
main.py
FastAPI entry point for the Resume Evaluator.
Accepts a resume upload, runs it through extract -> parse -> match,
and returns the evaluation result as JSON.
"""

import os
import shutil
import json
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException

from services.extractor import extract_text
from services.parser import parse_resume
from services.matcher import match_resume
from data.hr_requirements import hr_requirements

app = FastAPI(
    title="Resume Evaluator",
    description="Extracts structured data from a resume and matches it against HR requirements.",
    version="1.0.0",
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@app.get("/")
def root():
    return {"message": "Resume Evaluator API is running. POST a resume to /evaluate-resume"}


@app.post("/evaluate-resume")
async def evaluate_resume(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Only .pdf and .docx are allowed."
        )

    temp_path = UPLOAD_DIR / file.filename

    try:
        # Save uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run the pipeline
        resume_text = extract_text(str(temp_path))
        resume_data = parse_resume(resume_text)
        result = match_resume(resume_data, hr_requirements)

        return {
            "filename": file.filename,
            "resume_data": resume_data,
            "match_result": result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temp file regardless of success/failure
        if temp_path.exists():
            os.remove(temp_path)