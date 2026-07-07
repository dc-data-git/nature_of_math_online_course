"""Parse section manifest and locate PDF files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "contemporary-mathematics_section-level"
MANIFEST = PDF_DIR / "split_manifest.txt"

SECTION_RE = re.compile(r"^(\d+\.\d+)_")


@dataclass
class SectionInfo:
    section_id: str
    title: str
    page_start: int
    page_end: int
    pdf_path: Path
    chapter: int

    @property
    def chapter_prefix(self) -> str:
        return f"ch{self.chapter:02d}"


def load_sections() -> list[SectionInfo]:
    sections: list[SectionInfo] = []
    if not MANIFEST.exists():
        return sections
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        filename, title, page_range = parts[0], parts[1], parts[2]
        m = SECTION_RE.match(filename)
        if not m:
            continue
        section_id = m.group(1)
        chapter = int(section_id.split(".")[0])
        start_s, end_s = page_range.split("-")
        pdf_path = PDF_DIR / filename
        if not pdf_path.exists():
            continue
        sections.append(
            SectionInfo(
                section_id=section_id,
                title=title,
                page_start=int(start_s),
                page_end=int(end_s),
                pdf_path=pdf_path,
                chapter=chapter,
            )
        )
    return sections


def section_by_id(section_id: str) -> SectionInfo | None:
    for s in load_sections():
        if s.section_id == section_id:
            return s
    return None
