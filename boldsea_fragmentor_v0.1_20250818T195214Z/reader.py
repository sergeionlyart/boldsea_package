from __future__ import annotations
from typing import List, Tuple
import os

def read_text_file(path: str) -> List[Tuple[int, str]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    return [(1, txt)]

def read_pdf(path: str) -> List[Tuple[int, str]]:
    pages: List[Tuple[int, str]] = []
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(path)
        for i, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            pages.append((i, text))
        return pages
    except Exception:
        pass
    try:
        from pdfminer.high_level import extract_text
        txt = extract_text(path) or ""
        return [(1, txt)]
    except Exception:
        pass
    return [(1, "")]

def read_any(path: str) -> List[Tuple[int, str]]:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".rst"):
        return read_text_file(path)
    if ext == ".pdf":
        return read_pdf(path)
    return read_text_file(path)
