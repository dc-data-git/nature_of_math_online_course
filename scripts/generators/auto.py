"""Auto-generator for sections without dedicated hand-tuned generators."""

from __future__ import annotations

import random
import re
from typing import Callable

from scripts.lib.item_factory import item_id_prefix, make_item, variant_count
from scripts.lib.pdf_extract import extract_section_exercises, guess_exercise_count
from scripts.lib.section_registry import SectionInfo, load_sections

# Sections with dedicated generators — skip in auto
DEDICATED = {"1.1", "1.2", "1.3", "1.4", "1.5"}

RNG = random.Random(99)


def _prefix_from_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    parts = slug.split("_")
    return ".".join(parts[:3]) if parts else "general"


def _topic(section: SectionInfo, family: str) -> str:
    base = _prefix_from_title(section.title)
    ch = section.chapter
    if ch == 2:
        base = "logic." + base.split(".")[-1] if "." in base else "logic." + base
    elif ch == 3:
        base = "numtheory." + family
    elif ch == 5:
        base = "algebra." + family
    elif ch == 6:
        base = "finance." + family
    elif ch == 7:
        base = "probability." + family
    elif ch == 8:
        base = "statistics." + family
    elif ch == 10:
        base = "geometry." + family
    elif ch == 11:
        base = "voting." + family
    elif ch == 12:
        base = "graphs." + family
    elif ch == 13:
        base = "applications." + family
    else:
        base = f"ch{ch}." + family
    return base


def _learning_objective(section: SectionInfo) -> str:
    return f"Apply concepts from {section.title}."


def _numeric_template(section: SectionInfo, ex_num: int, seq: int, hint: str) -> dict:
    a, b = RNG.randint(2, 50), RNG.randint(2, 50)
    op = RNG.choice(["+", "-", "×", "÷"])
    if op == "+":
        ans = a + b
    elif op == "-":
        ans = a - b
    elif op == "×":
        ans = a * b
    else:
        b = RNG.randint(1, 12)
        ans = round(a / b, 2) if a % b else a // b
    return make_item(
        item_id=item_id_prefix(section.section_id, "compute", seq),
        section=section.section_id,
        chapter=section.chapter,
        exercise_number=str(ex_num),
        page=section.page_start,
        question_type="numeric_compute",
        item_format="numeric_entry",
        generation_strategy="algorithmic",
        topic=_topic(section, "compute"),
        learning_objective=_learning_objective(section),
        stem=f"Compute: {a} {op} {b}",
        answer=ans,
        variables={"a": a, "b": b, "operation": op, "group_hint": hint[:80]},
        generator_ref="auto::numeric",
        bloom_level="apply",
    )


def _true_false_template(section: SectionInfo, ex_num: int, seq: int, hint: str) -> dict:
    truth = RNG.choice([True, False])
    stmt = RNG.choice([
        "The result of the operation shown is correct.",
        "The statement follows from the definitions in this section.",
        "The given example satisfies the stated condition.",
    ])
    return make_item(
        item_id=item_id_prefix(section.section_id, "tf", seq),
        section=section.section_id,
        chapter=section.chapter,
        exercise_number=str(ex_num),
        page=section.page_start,
        question_type="classification_2choice",
        item_format="true_false",
        generation_strategy="algorithmic",
        topic=_topic(section, "true_false"),
        learning_objective=_learning_objective(section),
        stem=f"True or false: {stmt} (Section {section.section_id}, exercise family {ex_num})",
        answer=truth,
        variables={"statement": stmt, "group_hint": hint[:80]},
        generator_ref="auto::true_false",
        bloom_level="evaluate",
    )


def _short_answer_template(section: SectionInfo, ex_num: int, seq: int, hint: str) -> dict:
    templates = [
        "Explain the key concept illustrated in this exercise family.",
        "State the definition that applies to this problem type.",
        "Describe the method used to solve this class of problems.",
    ]
    prompt = RNG.choice(templates)
    return make_item(
        item_id=item_id_prefix(section.section_id, "short", seq),
        section=section.section_id,
        chapter=section.chapter,
        exercise_number=str(ex_num),
        page=section.page_start,
        question_type="open_response",
        item_format="short_answer",
        generation_strategy="static",
        topic=_topic(section, "concept"),
        learning_objective=_learning_objective(section),
        stem=f"{prompt}\n\n(Context: {section.title} — exercise {ex_num})",
        answer="See section text and worked examples.",
        variables={"group_hint": hint[:120]},
        generator_ref="auto::short_answer",
        qti_support_level="requires_conversion",
        bloom_level="understand",
        notes="Auto-generated conceptual placeholder — review against source PDF.",
    )


def _pick_templates(section: SectionInfo, hint: str) -> list[Callable]:
    t = (section.title + " " + hint).lower()
    templates: list[Callable] = []
    if any(k in t for k in ("true", "false", "determine whether", "classify")):
        templates.append(_true_false_template)
    if any(k in t for k in ("calculate", "compute", "find", "solve", "evaluate", "percent", "interest")):
        templates.append(_numeric_template)
    if any(k in t for k in ("explain", "describe", "list", "write", "graph", "construct")):
        templates.append(_short_answer_template)
    if not templates:
        templates = [_numeric_template, _short_answer_template]
    return templates


def generate_for_section(section: SectionInfo) -> list[dict]:
    if section.section_id in DEDICATED:
        return []

    info = extract_section_exercises(str(section.pdf_path), section.section_id)
    ex_nums = info.exercise_numbers
    if not ex_nums:
        n = guess_exercise_count(str(section.pdf_path), section.section_id)
        ex_nums = list(range(1, n + 1))
        blocks = {i: "" for i in ex_nums}
    else:
        blocks = {b.number: b.group_hint for b in info.blocks}

    items: list[dict] = []
    seq = 0
    # Group exercises by pattern string for variant sharing
    groups: dict[str, list[int]] = {}
    for n in ex_nums:
        key = blocks.get(n, "general")[:60]
        groups.setdefault(key, []).append(n)

    for hint, nums in groups.items():
        templates = _pick_templates(section, hint)
        n_variants = variant_count("algorithmic", RNG)
        for vi in range(n_variants):
            ex_num = RNG.choice(nums)
            seq += 1
            fn = templates[vi % len(templates)]
            items.append(fn(section, ex_num, seq, hint))

        if "figure" in hint.lower() or "graph" in hint.lower() or "diagram" in hint.lower():
            seq += 1
            items.append(make_item(
                item_id=item_id_prefix(section.section_id, "figure", seq),
                section=section.section_id,
                chapter=section.chapter,
                exercise_number=f"{min(nums)}-{max(nums)} (pattern)",
                page=section.page_start,
                question_type="figure_analysis",
                item_format="short_answer",
                generation_strategy="static",
                topic=_topic(section, "figure"),
                learning_objective=_learning_objective(section),
                stem=(
                    f"Using the diagram described in {section.title} (exercises {min(nums)}–{max(nums)}), "
                    f"answer the question for a parameterized instance of this figure family."
                ),
                answer="Depends on labeled regions in the diagram instance.",
                variables={"exercise_range": nums, "group_hint": hint[:80]},
                generator_ref="auto::figure",
                qti_support_level="manual_rebuild",
                bloom_level="analyze",
                notes="Figure-dependent — verify diagram template matches textbook intent.",
            ))

    return items


def generate_all_auto() -> list[dict]:
    items: list[dict] = []
    for section in load_sections():
        items.extend(generate_for_section(section))
    return items
