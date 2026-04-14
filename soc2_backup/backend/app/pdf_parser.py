import PyPDF2
from typing import List, Tuple

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")
    return text

def get_text_snippet(text: str, keyword: str, window: int = 300) -> str:
    """Return a snippet around the first occurrence of keyword."""
    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return ""
    start = max(0, idx - window//2)
    end = min(len(text), idx + len(keyword) + window//2)
    snippet = text[start:end].strip()
    # add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet