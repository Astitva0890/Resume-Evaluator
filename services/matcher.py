"""
matcher.py
Compares parsed resume data against HR requirements using Groq (LLM-based
semantic matching) and returns a match percentage + breakdown.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


class MatchResult(BaseModel):
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    match_percentage: int = Field(ge=0, le=100)
    reasoning: str


MATCH_PROMPT = """You are an HR recruiter evaluating a candidate's resume against job requirements.

Candidate's resume data:
{resume_data}

Job requirements:
{hr_requirements}

Compare the candidate's skills, experience, and projects against the requirements.
Consider a requirement "matched" if the candidate's skills OR their project descriptions
demonstrate that capability, even if worded differently (e.g. "built a REST API" counts
towards a "REST APIs" requirement).

Return ONLY valid JSON in this exact structure, no preamble, no markdown fences:

{{
  "matched_skills": ["..."],
  "missing_skills": ["..."],
  "match_percentage": <integer 0-100>,
  "reasoning": "<2-3 sentence explanation of the score>"
}}
"""


def match_resume(resume_data: dict, hr_requirements: dict) -> dict:
    """
    Sends resume data + HR requirements to Groq, returns match result as a dict.
    """
    prompt = MATCH_PROMPT.format(
        resume_data=json.dumps(resume_data, indent=2),
        hr_requirements=json.dumps(hr_requirements, indent=2),
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw_output = response.choices[0].message.content.strip()
    cleaned = raw_output.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(cleaned)
        validated = MatchResult(**data)
        return validated.model_dump()
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
    from services.extractor import extract_text
    from services.parser import parse_resume
    from data.hr_requirements import hr_requirements

    test_file = "tests/sample_resume.pdf"  # update if needed

    resume_text = extract_text(test_file)
    resume_data = parse_resume(resume_text)

    print("Matching against HR requirements...\n")
    result = match_resume(resume_data, hr_requirements)

    print("Match result:\n")
    print(json.dumps(result, indent=2))