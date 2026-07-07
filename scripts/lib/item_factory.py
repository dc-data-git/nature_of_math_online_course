"""Factory helpers for constructing problem bank items."""

from __future__ import annotations

import random
from datetime import date
from typing import Any

from scripts.lib.constants import BOOK, LICENSE

TODAY = date.today().isoformat()


def make_item(
    *,
    item_id: str,
    section: str,
    chapter: int,
    exercise_number: str,
    page: int | None,
    question_type: str,
    item_format: str,
    generation_strategy: str,
    topic: str,
    learning_objective: str,
    stem: str,
    answer: Any,
    difficulty: str = "intro",
    bloom_level: str = "understand",
    qti_support_level: str = "direct",
    origin: str | None = None,
    variables: dict | None = None,
    generator_ref: str | None = None,
    options: list | None = None,
    distractor_rationale: list | None = None,
    feedback: dict | None = None,
    media: list | None = None,
    status: str = "needs_review",
    verification_method: str | None = None,
    notes: str | None = None,
    randomization_group: str | None = None,
    reuse_risk: str | None = None,
    created_by: str = "pipeline",
    parent_id: str | None = None,
    derivation_type: str | None = "inspired_by",
) -> dict:
    if origin is None:
        origin = {
            "algorithmic": "algorithmic_variant",
            "templated": "templated_variant",
            "static": "static_variant",
        }[generation_strategy]
    if verification_method is None:
        verification_method = "computed" if generation_strategy == "algorithmic" else "llm_reviewed"
    if randomization_group is None:
        randomization_group = topic
    if reuse_risk is None:
        reuse_risk = "fresh_each_use" if generation_strategy == "algorithmic" else "static_low_risk"
    if feedback is None:
        feedback = {
            "correct": f"Correct. The answer is {answer}.",
            "incorrect": "Review the section material and try again.",
        }
    if media is None:
        media = []

    return {
        "id": item_id,
        "parent_id": parent_id,
        "origin": origin,
        "derivation_type": derivation_type,
        "source": {
            "book": BOOK,
            "chapter": chapter,
            "section": section,
            "exercise_number": exercise_number,
            "page": page,
        },
        "license": {**LICENSE, "attribution_text": LICENSE["attribution_text"].replace(
            "Contemporary Mathematics (OpenStax),",
            f"Contemporary Mathematics (OpenStax), Section {section},",
        )},
        "question_type": question_type,
        "item_format": item_format,
        "qti_support_level": qti_support_level,
        "generation_strategy": generation_strategy,
        "topic": topic,
        "learning_objective": learning_objective,
        "difficulty": difficulty,
        "bloom_level": bloom_level,
        "randomization_group": randomization_group,
        "reuse_risk": reuse_risk,
        "stem": stem,
        "variables": variables,
        "generator_ref": generator_ref,
        "answer": answer,
        "options": options,
        "distractor_rationale": distractor_rationale,
        "feedback": feedback,
        "media": media,
        "status": status,
        "verification_method": verification_method,
        "notes": notes,
        "created_at": TODAY,
        "created_by": created_by,
    }


def variant_count(strategy: str, rng: random.Random | None = None) -> int:
    rng = rng or random
    lo, hi = {"algorithmic": (8, 12), "templated": (3, 4), "static": (2, 3)}[strategy]
    return rng.randint(lo, hi)


def item_id_prefix(section: str, topic_slug: str, seq: int) -> str:
    slug = topic_slug.split(".")[-1][:12]
    return f"contemath-{section}-{slug}-{seq:03d}"
