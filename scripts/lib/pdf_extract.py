"""Extract exercise structure and stems from chapter PDFs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

import fitz

from scripts.lib.answer_key_extract import infer_exercise_count
from scripts.lib.chapter_registry import chapter_pdf

SECTION_HEADER = re.compile(r"SECTION\s+(\d+\.\d+)\s+EXERCISES", re.I)
GROUP_HEADER = re.compile(r"For the following exercises,[^\n]+", re.I)
EX_LINE = re.compile(r"^(\d+)\s*\.\s*(.*)$", re.M)


@dataclass
class ExerciseSpec:
    number: int
    group_hint: str = ""
    stem_text: str = ""
    has_figure: bool = False


@dataclass
class SectionExercises:
    section_id: str
    exercises: list[ExerciseSpec] = field(default_factory=list)

    @property
    def exercise_numbers(self) -> list[int]:
        return [e.number for e in self.exercises]

    @property
    def total_count(self) -> int:
        return max(self.exercise_numbers) if self.exercises else 0


@lru_cache(maxsize=16)
def _chapter_text(chapter: int) -> str:
    path = chapter_pdf(chapter)
    if not path:
        return ""
    doc = fitz.open(str(path))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def _section_bounds(text: str, section_id: str) -> tuple[int, int] | None:
    headers = [(m.group(1), m.start()) for m in SECTION_HEADER.finditer(text)]
    for i, (sid, pos) in enumerate(headers):
        if sid == section_id:
            end = headers[i + 1][1] if i + 1 < len(headers) else len(text)
            return pos, end
    return None


def extract_section_exercises(pdf_path: str, section_id: str) -> SectionExercises:
    """Extract exercises using chapter PDF (falls back to section pdf_path)."""
    result = SectionExercises(section_id=section_id)
    chapter = int(section_id.split(".")[0])
    text = _chapter_text(chapter)
    if not text:
        return _extract_from_file(pdf_path, section_id)

    bounds = _section_bounds(text, section_id)
    if not bounds:
        return _extract_from_file(pdf_path, section_id)

    exercise_text = text[bounds[0] : bounds[1]]
    result.exercises = _parse_exercise_block(exercise_text)
    return result


def _extract_from_file(pdf_path: str, section_id: str) -> SectionExercises:
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    m = SECTION_HEADER.search(text)
    if not m:
        return SectionExercises(section_id=section_id)
    exercise_text = text[m.start() :]
    return SectionExercises(section_id=section_id, exercises=_parse_exercise_block(exercise_text))


CYU_STOP = re.compile(r"Check Your Understanding", re.I)
FOOTER_LINE = re.compile(r"Access for free at openstax\.org.*", re.I)


def _parse_exercise_block(exercise_text: str) -> list[ExerciseSpec]:
    # Remove footer lines without truncating the whole section (footers repeat mid-chapter)
    exercise_text = FOOTER_LINE.sub("", exercise_text)

    stop = CYU_STOP.search(exercise_text)
    if stop:
        exercise_text = exercise_text[: stop.start()]

    parts = re.split(r"(For the following exercises,[^\n]+)", exercise_text, flags=re.I)
    current_group = "general"
    ordered: list[ExerciseSpec] = []

    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if part.lower().startswith("for the following exercises"):
            current_group = part
            i += 1
            continue
        for m in EX_LINE.finditer(part):
            num = int(m.group(1))
            if num > 120:
                continue
            stem = m.group(2).strip()
            has_fig = bool(
                re.search(r"figure|graph|diagram|venn|sketch|plot", stem + current_group, re.I)
            )
            ordered.append(
                ExerciseSpec(
                    number=num,
                    group_hint=current_group,
                    stem_text=stem,
                    has_figure=has_fig,
                )
            )
        i += 1

    if not ordered:
        return []

    # Keep first run starting at 1; stop when numbering restarts after a gap (next section bleed)
    by_num: dict[int, ExerciseSpec] = {}
    prev = 0
    for spec in ordered:
        if spec.number > 120:
            continue
        if spec.number == 1 and prev > 5:
            break
        if spec.number < prev and prev >= 8:
            break
        if prev and spec.number > prev + 8:
            continue
        if spec.number in by_num:
            if spec.number <= 5 and prev > 15:
                break
            if len(spec.stem_text) > len(by_num[spec.number].stem_text):
                by_num[spec.number] = spec
        else:
            by_num[spec.number] = spec
        prev = spec.number

    nums = sorted(by_num.keys())
    if 1 not in nums:
        return [by_num[n] for n in nums]

    end = 1
    for n in nums:
        if n > end + 2:
            break
        end = max(end, n)
    valid = [n for n in nums if n <= end]

    return [by_num[n] for n in valid]


def guess_exercise_count(pdf_path: str, section_id: str) -> int:
    info = extract_section_exercises(pdf_path, section_id)
    return infer_exercise_count(section_id, info.total_count)
