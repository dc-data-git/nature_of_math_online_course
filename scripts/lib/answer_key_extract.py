"""Parse OpenStax answer key PDF into per-section exercise answers."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
ANSWER_KEY_PDF = ROOT / "contemporary-mathematics_sections" / "17_Answer Key.pdf"

SECTION_MARKER = re.compile(r"^(\d+\.\d+)\s*$", re.M)
ANSWER_LINE = re.compile(r"^(\d+)\s*\.\s*(.*)$", re.M)
SKIP_LINE = re.compile(
    r"^Answer Key\s+\d+|^Access for free|^Chapter \d+|^Your Turn|^Check Your Understanding",
    re.I,
)


@lru_cache(maxsize=1)
def _load_full_text() -> str:
    doc = fitz.open(str(ANSWER_KEY_PDF))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


@lru_cache(maxsize=1)
def _section_spans() -> list[tuple[str, int, int]]:
    text = _load_full_text()
    markers = [(m.group(1), m.start(), m.end()) for m in SECTION_MARKER.finditer(text)]
    spans: list[tuple[str, int, int]] = []
    for i, (sid, _start, end) in enumerate(markers):
        next_start = markers[i + 1][1] if i + 1 < len(markers) else len(text)
        spans.append((sid, end, next_start))
    return spans


@lru_cache(maxsize=1)
def _parse_all_sections() -> dict[str, dict[int, str]]:
    text = _load_full_text()
    sections: dict[str, dict[int, str]] = {}
    for sid, start, end in _section_spans():
        body = text[start:end]
        answers: dict[int, str] = {}
        for line in body.splitlines():
            if SKIP_LINE.match(line.strip()):
                continue
            m = ANSWER_LINE.match(line.strip())
            if not m:
                continue
            num = int(m.group(1))
            ans = m.group(2).strip()
            if num > 200:
                continue
            if ans:
                answers[num] = ans
            elif num not in answers:
                answers[num] = ""
        if answers:
            sections[sid] = answers
    return sections


def get_section_answers(section_id: str) -> dict[int, str]:
    return dict(_parse_all_sections().get(section_id, {}))


def infer_exercise_count(section_id: str, pdf_count: int) -> int:
    ak = get_section_answers(section_id)
    if ak:
        return max(max(ak.keys()), pdf_count)
    return pdf_count
