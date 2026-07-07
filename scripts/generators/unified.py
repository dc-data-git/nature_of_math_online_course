"""Generate bank items: every textbook exercise × intro/practice/challenge."""

from __future__ import annotations

import random
import re

from scripts.lib.answer_key_extract import get_section_answers
from scripts.lib.item_factory import make_item
from scripts.lib.item_templates import DIFFICULTIES, render_exercise
from scripts.lib.pdf_extract import ExerciseSpec, extract_section_exercises
from scripts.lib.section_registry import SectionInfo, load_sections

# Pilot deep pool for 1.1 only (pattern-tagged variants)
PILOT_SECTION = "1.1"
RNG = random.Random(42)


def _topic(section: SectionInfo, suffix: str) -> str:
    ch = section.chapter
    slug = re.sub(r"[^a-z0-9]+", "_", section.title.lower()).strip("_")[:24]
    prefixes = {
        1: "sets", 2: "logic", 3: "numtheory", 4: "bases", 5: "algebra",
        6: "finance", 7: "probability", 8: "statistics", 9: "metric",
        10: "geometry", 11: "voting", 12: "graphs", 13: "applications",
    }
    return f"{prefixes.get(ch, f'ch{ch}')}.{suffix}"


def _learning_objective(section: SectionInfo) -> str:
    return f"Master the skills in {section.title} (Exercise {{ex}})."


def generate_for_section(section: SectionInfo) -> list[dict]:
    info = extract_section_exercises(str(section.pdf_path), section.section_id)
    answers = get_section_answers(section.section_id)

    # Build spec map; fill gaps if AK has more exercises than PDF stems
    spec_by_num = {e.number: e for e in info.exercises}
    total = max(
        info.total_count,
        max(answers.keys()) if answers else 0,
        max(spec_by_num.keys()) if spec_by_num else 0,
    )
    if total == 0:
        return []

    for n in range(1, total + 1):
        if n not in spec_by_num:
            spec_by_num[n] = ExerciseSpec(
                number=n,
                group_hint="general",
                stem_text="",
            )

    items: list[dict] = []
    for ex_num in range(1, total + 1):
        spec = spec_by_num[ex_num]
        ak = answers.get(ex_num, "")
        lo = _learning_objective(section).replace("{ex}", str(ex_num))

        for diff in DIFFICULTIES:
            rng = random.Random(hash((section.section_id, ex_num, diff)) & 0xFFFFFFFF)
            rendered = render_exercise(section, spec, diff, rng, ak or None)
            item_id = f"contemath-{section.section_id}-ex{ex_num:03d}-{diff[0]}"

            items.append(make_item(
                item_id=item_id,
                section=section.section_id,
                chapter=section.chapter,
                exercise_number=str(ex_num),
                page=section.page_start,
                question_type=rendered["question_type"],
                item_format=rendered["item_format"],
                generation_strategy=rendered["generation_strategy"],
                topic=_topic(section, rendered["topic_suffix"]),
                learning_objective=lo,
                stem=rendered["stem"],
                answer=rendered["answer"],
                difficulty=diff,
                bloom_level={
                    "intro": "understand",
                    "practice": "apply",
                    "challenge": "analyze",
                }[diff],
                variables={
                    "exercise_number": ex_num,
                    "difficulty": diff,
                    "group_hint": spec.group_hint[:100],
                    "source_stem": spec.stem_text or None,
                },
                generator_ref=f"unified::{rendered['topic_suffix']}",
                media=rendered.get("media", []),
                qti_support_level=rendered["qti_support_level"],
                notes=(
                    f"Exercise {ex_num} ({diff}); group: {spec.group_hint[:60]}. "
                    + ("Textbook stem used." if spec.stem_text else "Stem synthesized from exercise family.")
                ),
                created_by="pipeline:unified",
            ))

    return items


def load_pilot_extras() -> list[dict]:
    """Optional deep variant pool for section 1.1."""
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[2] / "pilot" / "1.1-pilot.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    for it in items:
        it["status"] = "needs_review"
    return items


def generate_all() -> list[dict]:
    items: list[dict] = []
    for section in load_sections():
        batch = generate_for_section(section)
        items.extend(batch)
    # Add pilot deep pool for 1.1 (extra parameterized variants beyond per-exercise triples)
    items.extend(load_pilot_extras())
    return items
