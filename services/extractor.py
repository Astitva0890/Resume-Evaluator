"""
extractor.py
Reads a resume file (PDF or DOCX) and returns its raw text content.
"""

from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_text(file_path: str) -> str:
    """
    Extracts raw text from a resume file.
    Supports .pdf and .docx formats.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.suffix.lower()

    if extension == ".pdf":
        return _extract_from_pdf(path)
    elif extension == ".docx":
        return _extract_from_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {extension}. Use .pdf or .docx")


def _extract_from_pdf(path: Path) -> str:
    reader = PdfReader(path)
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    full_text = "\n".join(text_parts)

    if not full_text.strip():
        raise ValueError(
            "No text could be extracted. This PDF might be a scanned image "
            "rather than actual text — try a text-based PDF instead."
        )

    return full_text


def _extract_from_docx(path: Path) -> str:
    doc = Document(path)
    text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
    full_text = "\n".join(text_parts)

    if not full_text.strip():
        raise ValueError("No text could be extracted from this DOCX file.")

    return full_text


# Quick manual test — run this file directly to check extraction works
if __name__ == "__main__":
    test_file = "tests/sample_resume.pdf"  # change this to your actual file name

    try:
        text = extract_text(test_file)
        print("Extraction successful!\n")
        print("First 500 characters:\n")
        print(text[:500])
        print(f"\n\nTotal characters extracted: {len(text)}")
    except Exception as e:
        print(f"Error: {e}")