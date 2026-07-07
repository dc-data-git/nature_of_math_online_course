"""Section 1.5 — Set Operations with Three Sets."""

from __future__ import annotations

import random

from scripts.generators._ch01_common import themed_set
from scripts.lib.item_factory import item_id_prefix, make_item, variant_count

SECTION_ID = "1.5"
CHAPTER = 1
PAGE = 50
RNG = random.Random(15)

LO = "Perform set operations with three sets."


def _roster(items: list[str]) -> str:
    return "{" + ", ".join(sorted(set(items))) + "}" if items else "∅"


def generate_items() -> list[dict]:
    items: list[dict] = []
    seq = 0

    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        pool = themed_set(RNG, 7)
        a, b, c = pool[:3], pool[2:5], pool[4:7]
        op = RNG.choice(["union", "intersection", "symmetric"])
        if op == "union":
            ans = _roster(list(set(a) | set(b) | set(c)))
            stem = f"A = {_roster(a)}, B = {_roster(b)}, C = {_roster(c)}. Find A ∪ B ∪ C."
        elif op == "intersection":
            ans = _roster(list(set(a) & set(b) & set(c)))
            stem = f"A = {_roster(a)}, B = {_roster(b)}, C = {_roster(c)}. Find A ∩ B ∩ C."
        else:
            ab = set(a) ^ set(b)
            ans = _roster(list(ab ^ set(c)))
            stem = f"A = {_roster(a)}, B = {_roster(b)}, C = {_roster(c)}. Find (A △ B) △ C."
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "three_set", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="1-25 (pattern)", page=PAGE,
            question_type="set_operation_three",
            item_format="short_answer",
            generation_strategy="algorithmic",
            topic=f"sets.operations.three_set_{op}",
            learning_objective=LO,
            stem=stem,
            answer=ans,
            variables={"A": a, "B": b, "C": c, "operation": op},
            generator_ref=f"ch01_05::{op}",
            bloom_level="apply",
        ))

    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        region = RNG.choice([
            "A ∩ B ∩ C",
            "A ∩ B only",
            "A only",
            "(A ∪ B) ∩ C′",
        ])
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "three_venn", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="venn-3 (pattern)", page=PAGE,
            question_type="venn_three_region",
            item_format="short_answer",
            generation_strategy="algorithmic",
            topic="sets.operations.venn_three_set",
            learning_objective=LO,
            stem=(
                f"In a three-set Venn diagram with sets A, B, and C, describe the region "
                f"corresponding to: {region}"
            ),
            answer=region,
            variables={"region": region},
            generator_ref="ch01_05::venn_three_region",
            qti_support_level="manual_rebuild",
            bloom_level="understand",
            notes="Three-set Venn diagram template pending SVG generator; region description is parameterized.",
        ))

    for _ in range(variant_count("static", RNG)):
        seq += 1
        n_u = RNG.randint(40, 100)
        n_a, n_b, n_c = RNG.randint(15, 40), RNG.randint(15, 40), RNG.randint(15, 40)
        n_ab = RNG.randint(5, 12)
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "three_survey", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="app (pattern)", page=PAGE,
            question_type="set_operation_word",
            item_format="numeric_entry",
            generation_strategy="static",
            topic="sets.operations.three_set_application",
            learning_objective=LO,
            stem=(
                f"In a group of {n_u} people, {n_a} read magazine A, {n_b} read magazine B, "
                f"and {n_c} read magazine C. If {n_ab} read both A and B, how many read at least "
                f"one of A or B? (Assume no one read all three unless stated.)"
            ),
            answer=n_a + n_b - n_ab,
            variables={"total": n_u, "A": n_a, "B": n_b, "C": n_c, "AB": n_ab},
            generator_ref="ch01_05::survey_three",
            bloom_level="apply",
        ))

    return items
