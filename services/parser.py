"""
parser.py
Sends raw resume text to Groq and gets back structured data:
skills, experience, projects — as clean JSON.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

load_dotenv()  # reads .env and loads GROQ_API_KEY into environment

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

from pydantic import BaseModel, Field

class ResumeData(BaseModel):
    skills: list[str] = Field(min_length=1, description="List of technical skills")
    experience: list[str] = Field(default_factory=list, description="Work experience entries")
    projects: list[str] = Field(min_length=1, description="Personal or academic projects")

    
EXTRACTION_PROMPT = """You are a resume parser. Extract the following information from the resume text below.

Return ONLY valid JSON in this exact structure, with no preamble, no explanation, no markdown code fences:

{{
  "skills": ["skill1", "skill2", ...],
  "experience": ["experience item 1", "experience item 2", ...],
  "projects": ["project 1", "project 2", ...]
}}

Rules:
- skills: technical skills, tools, languages, frameworks mentioned anywhere in the resume
- experience: internships, jobs, or work experience entries (short summary each)
- projects: personal/academic projects mentioned, with a short description of what it does
- Only extract skills that are explicitly listed in a Skills/Technologies section. Do NOT infer skills from project descriptions unless they are also explicitly mentioned elsewhere.
Resume text:
{resume_text}
"""


def parse_resume(resume_text: str) -> dict:
    """
    Sends resume text to Groq and returns structured data as a dict.
    """
    prompt = EXTRACTION_PROMPT.format(resume_text=resume_text)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw_output = response.choices[0].message.content.strip()

    # Safety net: sometimes the model wraps output in ```json ... ``` anyway
    cleaned = raw_output.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(cleaned)
        validated = ResumeData(**data)  # validates structure/types
        return validated.model_dump()   # returns plain dict, same as before
    except json.JSONDecodeError as e:
        print("Failed to parse JSON. Raw model output was:\n")
        print(raw_output)
        raise e
    except Exception as e:
        print("Groq's output didn't match expected structure:\n")
        print(cleaned)
        raise e


# Quick manual test — run this file directly
if __name__ == "__main__":
    from services.extractor import extract_text # only works if run from services/ folder context

    test_file = "tests/sample_resume.pdf"  # update if needed

    resume_text = extract_text(test_file)
    print("Text extracted, sending to Groq...\n")

    parsed_data = parse_resume(resume_text)

    print("Parsed resume data:\n")
    print(json.dumps(parsed_data, indent=2))