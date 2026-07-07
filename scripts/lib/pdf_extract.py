"""Extract exercise structure from section PDFs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import fitz

EXERCISES_HEADER = re.compile(r"SECTION\s+(\d+\.\d+)\s+EXERCISES", re.I)
EXERCISE_NUM = re.compile(r"^(\d+)\s*\.\s*", re.M)
GROUP_HEADER = re.compile(
    r"For the following exercises,\s*(.+?)(?:\n|$)",
    re.I,
)


@dataclass
class ExerciseBlock:
    number: int
    group_hint: str = ""
    raw_text: str = ""


@dataclass
class SectionExercises:
    section_id: str
    groups: list[tuple[str, list[int]]] = field(default_factory=list)
    exercise_numbers: list[int] = field(default_factory=list)
    blocks: list[ExerciseBlock] = field(default_factory=list)


def extract_section_exercises(pdf_path: str, section_id: str) -> SectionExercises:
    doc = fitz.open(pdf_path)
    full_text = "\n".join(page.get_text() for page in doc)
    doc.close()

    result = SectionExercises(section_id=section_id)
    m = EXERCISES_HEADER.search(full_text)
    if not m:
        return result

    exercise_text = full_text[m.start() :]
    # Split on group headers
    parts = re.split(r"(For the following exercises,[^\n]+)", exercise_text, flags=re.I)
    current_group = "general"
    seen: set[int] = set()

    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if part.lower().startswith("for the following exercises"):
            current_group = part
            i += 1
            continue
        nums = [int(n) for n in EXERCISE_NUM.findall(part)]
        for n in nums:
            if n not in seen and n <= 200:
                seen.add(n)
                result.exercise_numbers.append(n)
                result.blocks.append(ExerciseBlock(number=n, group_hint=current_group))
        i += 1

    result.exercise_numbers.sort()
    return result


def guess_exercise_count(pdf_path: str, section_id: str) -> int:
    info = extract_section_exercises(pdf_path, section_id)
    if info.exercise_numbers:
        return max(info.exercise_numbers)
    return 20
