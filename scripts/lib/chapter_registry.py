"""Map chapters to consolidated PDF files for reliable exercise extraction."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAPTER_DIR = ROOT / "contemporary-mathematics_sections"

CHAPTER_PDFS: dict[int, Path] = {
    1: CHAPTER_DIR / "03_Chapter 1 Sets.pdf",
    2: CHAPTER_DIR / "04_Chapter 2 Logic.pdf",
    3: CHAPTER_DIR / "05_Chapter 3 Real Number Systems and Number Theory.pdf",
    4: CHAPTER_DIR / "06_Chapter 4 Number Representation and Calculation.pdf",
    5: CHAPTER_DIR / "07_Chapter 5 Algebra.pdf",
    6: CHAPTER_DIR / "08_Chapter 6 Money Management.pdf",
    7: CHAPTER_DIR / "09_Chapter 7 Probability.pdf",
    8: CHAPTER_DIR / "10_Chapter 8 Statistics.pdf",
    9: CHAPTER_DIR / "11_Chapter 9 Metric Measurement.pdf",
    10: CHAPTER_DIR / "12_Chapter 10 Geometry.pdf",
    11: CHAPTER_DIR / "13_Chapter 11 Voting and Apportionment.pdf",
    12: CHAPTER_DIR / "14_Chapter 12 Graph Theory.pdf",
    13: CHAPTER_DIR / "15_Chapter 13 Math and___.pdf",
}


def chapter_pdf(chapter: int) -> Path | None:
    p = CHAPTER_PDFS.get(chapter)
    return p if p and p.exists() else None
