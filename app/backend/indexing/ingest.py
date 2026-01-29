from __future__ import annotations

from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
import pdfplumber


def _read_pdf(path: Path) -> str:
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
    return "\n".join(text)


def _read_html(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ", strip=True)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def ingest_pack(pack_dir: Path) -> List[dict]:
    docs: List[dict] = []
    for path in pack_dir.rglob("*"):
        if path.is_dir():
            continue
        ext = path.suffix.lower()
        if ext in {".pdf"}:
            content = _read_pdf(path)
        elif ext in {".html", ".htm"}:
            content = _read_html(path)
        elif ext in {".txt", ".md"}:
            content = _read_text(path)
        else:
            continue
        docs.append({"path": path, "content": content})
    return docs
