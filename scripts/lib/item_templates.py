"""Classify exercises and render stems/answers by type and difficulty."""

from __future__ import annotations

import random
from typing import Any

from scripts.diagrams.venn_2set import media_entry, venn_two_set
from scripts.lib.pdf_extract import ExerciseSpec
from scripts.lib.section_registry import SectionInfo

DIFFICULTIES = ("intro", "practice", "challenge")


def classify_exercise(section: SectionInfo, spec: ExerciseSpec) -> str:
    blob = f"{section.title} {spec.group_hint} {spec.stem_text}".lower()
    if spec.has_figure or any(k in blob for k in ("venn", "diagram", "figure", "graph", "sketch", "shade")):
        return "figure"
    if any(k in blob for k in ("true or false", "true/false", "determine whether")):
        return "true_false"
    if any(k in blob for k in ("subset", "proper subset", "⊂", "⊆")):
        return "subset"
    if any(k in blob for k in ("truth table", "truth tables")):
        return "truth_table"
    if any(k in blob for k in ("percent", "%")):
        return "percent"
    if any(k in blob for k in ("interest", "loan", "investment", "tax", "budget")):
        return "finance"
    if any(k in blob for k in ("probability", "odds", "permutation", "combination")):
        return "probability"
    if any(k in blob for k in ("mean", "median", "mode", "standard deviation", "percentile")):
        return "statistics"
    if any(k in blob for k in ("order of operations", "precedence", "perform the indicated calculation", "calculate")):
        return "order_of_ops"
    if any(k in blob for k in ("explain", "describe", "why", "what is", "define", "state")):
        return "conceptual"
    if any(k in blob for k in ("list", "write", "represent", "roster", "set-builder", "set builder")):
        return "set_representation"
    if any(k in blob for k in ("solve", "evaluate", "compute", "find", "simplify", "convert")):
        return "compute"
    return "general"


def _scale(rng: random.Random, difficulty: str, lo: int, hi: int) -> int:
    if difficulty == "intro":
        return rng.randint(lo, lo + (hi - lo) // 3)
    if difficulty == "challenge":
        return rng.randint(lo + 2 * (hi - lo) // 3, hi)
    return rng.randint(lo + (hi - lo) // 3, lo + 2 * (hi - lo) // 3)


def _order_of_ops_expr(rng: random.Random, difficulty: str) -> tuple[str, int]:
    a = _scale(rng, difficulty, 2, 25)
    b = _scale(rng, difficulty, 2, 15)
    c = _scale(rng, difficulty, 2, 10)
    templates = [
        (f"{a} + {b} × {c}", a + b * c),
        (f"({a} + {b}) × {c}", (a + b) * c),
        (f"{a} × {c} + {b} × {c}", a * c + b * c),
        (f"{a * b} ÷ {b} + {c}", a + c),
    ]
    if difficulty == "challenge":
        d = _scale(rng, difficulty, 2, 8)
        templates.append((f"{a} + {b} × ({c} + {d})", a + b * (c + d)))
    return rng.choice(templates)


def render_exercise(
    section: SectionInfo,
    spec: ExerciseSpec,
    difficulty: str,
    rng: random.Random,
    answer_key: str | None,
) -> dict[str, Any]:
    """Return stem, answer, item_format, question_type, media, qti_support_level, topic_suffix."""
    kind = classify_exercise(section, spec)
    ex = spec.number
    ch = section.chapter
    blob = f"{section.title} {spec.group_hint}".lower()

    # Verbatim stem from textbook when available
    if spec.stem_text and len(spec.stem_text) > 12 and difficulty == "intro":
        stem = spec.stem_text
        if not stem.endswith("?"):
            stem = stem.rstrip(".") + "?"
        answer = answer_key if answer_key else "See section examples."
        return {
            "stem": stem,
            "answer": answer,
            "item_format": "short_answer",
            "question_type": kind,
            "media": [],
            "qti_support_level": "requires_conversion" if answer_key else "direct",
            "topic_suffix": kind,
            "generation_strategy": "static" if answer_key else "templated",
        }

    if kind == "order_of_ops" or ("order of operations" in section.title.lower() and ex >= 5):
        expr, ans = _order_of_ops_expr(rng, difficulty)
        return {
            "stem": f"Perform the indicated calculation: {expr}",
            "answer": ans,
            "item_format": "numeric_entry",
            "question_type": "order_of_operations",
            "media": [],
            "qti_support_level": "direct",
            "topic_suffix": "order_of_operations",
            "generation_strategy": "algorithmic",
        }

    if kind == "figure" or "venn" in blob:
        labels = ("A", "B") if difficulty != "challenge" else ("Set A", "Set B")
        shade = rng.choice(["A", "B", "A∩B", "A∪B", "A-B"])
        svg = venn_two_set(labels, shade=shade)
        return {
            "stem": (
                f"Refer to the Venn diagram with sets {labels[0]} and {labels[1]}. "
                f"Identify the region described as: {shade.replace('∩', ' ∩ ')}"
            ),
            "answer": shade,
            "item_format": "short_answer",
            "question_type": "venn_region",
            "media": [media_entry("venn_two_set", {"labels": labels, "shade": shade}, svg)],
            "qti_support_level": "manual_rebuild",
            "topic_suffix": "venn_diagram",
            "generation_strategy": "algorithmic",
        }

    if kind == "true_false":
        val = rng.choice([True, False])
        return {
            "stem": spec.stem_text or f"Determine whether the following statement is true or false (Section {section.section_id}, Exercise {ex}).",
            "answer": val,
            "item_format": "true_false",
            "question_type": "classification_2choice",
            "media": [],
            "qti_support_level": "direct",
            "topic_suffix": "true_false",
            "generation_strategy": "algorithmic",
        }

    if kind == "subset" or "subset" in section.title.lower():
        n = _scale(rng, difficulty, 2, 7)
        return {
            "stem": f"How many proper subsets does a set with {n} elements have?",
            "answer": 2**n - 1,
            "item_format": "numeric_entry",
            "question_type": "subset_count",
            "media": [],
            "qti_support_level": "direct",
            "topic_suffix": "subsets",
            "generation_strategy": "algorithmic",
        }

    if kind == "percent" or "percent" in section.title.lower():
        p = _scale(rng, difficulty, 5, 40)
        base = _scale(rng, difficulty, 20, 500)
        ans = round(base * p / 100, 2)
        return {
            "stem": f"What is {p}% of {base}?",
            "answer": ans,
            "item_format": "numeric_entry",
            "question_type": "percent_calculation",
            "media": [],
            "qti_support_level": "direct",
            "topic_suffix": "percent",
            "generation_strategy": "algorithmic",
        }

    if kind == "conceptual":
        stem = spec.stem_text or (
            f"In the context of {section.title}, answer the question for Exercise {ex}."
        )
        return {
            "stem": stem,
            "answer": answer_key or "Refer to the section reading.",
            "item_format": "short_answer",
            "question_type": "open_response",
            "media": [],
            "qti_support_level": "requires_conversion",
            "topic_suffix": "conceptual",
            "generation_strategy": "static" if spec.stem_text else "templated",
        }

    # Default: numeric computation with scaled difficulty
    a, b = _scale(rng, difficulty, 3, 40), _scale(rng, difficulty, 2, 25)
    op = rng.choice(["+", "−", "×"])
    ans = a + b if op == "+" else (a - b if op == "−" else a * b)
    group_short = spec.group_hint.replace("For the following exercises,", "").strip()[:80]
    stem = spec.stem_text if spec.stem_text else (
        f"{group_short or 'Compute the following'}: {a} {op} {b}"
    )
    return {
        "stem": stem,
        "answer": answer_key if answer_key and difficulty == "intro" else ans,
        "item_format": "numeric_entry" if not spec.stem_text else "short_answer",
        "question_type": kind if kind != "general" else "numeric_compute",
        "media": [],
        "qti_support_level": "direct",
        "topic_suffix": kind if kind != "general" else "compute",
        "generation_strategy": "algorithmic",
    }
