"""Section 1.4 — Set Operations with Two Sets."""

from __future__ import annotations

import random

from scripts.diagrams.venn_2set import media_entry, venn_two_set
from scripts.generators._ch01_common import themed_set
from scripts.lib.item_factory import item_id_prefix, make_item, variant_count

SECTION_ID = "1.4"
CHAPTER = 1
PAGE = 39
RNG = random.Random(14)

LO = "Perform set operations with two sets."


def _roster(items: list[str]) -> str:
    return "{" + ", ".join(items) + "}"


def generate_items() -> list[dict]:
    items: list[dict] = []
    seq = 0
    ops = [
        ("union", "∪", lambda a, b: sorted(set(a) | set(b))),
        ("intersection", "∩", lambda a, b: sorted(set(a) & set(b))),
        ("difference", "−", lambda a, b: sorted(set(a) - set(b))),
    ]

    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        a = themed_set(RNG, RNG.randint(3, 5))
        b = themed_set(RNG, RNG.randint(3, 5))
        name, sym, fn = RNG.choice(ops)
        result = fn(a, b)
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "two_set_op", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="1-30 (pattern)", page=PAGE,
            question_type="set_operation",
            item_format="short_answer",
            generation_strategy="algorithmic",
            topic=f"sets.operations.two_set_{name}",
            learning_objective=LO,
            stem=f"Let A = {_roster(a)} and B = {_roster(b)}. Find A {sym} B.",
            answer=_roster(result) if result else "∅",
            variables={"A": a, "B": b, "operation": name},
            generator_ref=f"ch01_04::{name}",
            bloom_level="apply",
        ))

    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        a = themed_set(RNG, 4)
        b = themed_set(RNG, 4)
        shade = RNG.choice(["A∩B", "A∪B", "A-B"])
        sym = {"A∩B": "∩", "A∪B": "∪", "A-B": "−"}[shade]
        svg = venn_two_set(("A", "B"), shade=shade)
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "two_set_venn", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="venn-op (pattern)", page=PAGE,
            question_type="venn_operation",
            item_format="multiple_choice",
            generation_strategy="algorithmic",
            topic="sets.operations.venn_two_set",
            learning_objective=LO,
            stem=f"The shaded region in the Venn diagram represents which operation on A and B?",
            answer=f"A {sym} B",
            options=["A ∪ B", "A ∩ B", "A − B", "B − A"],
            variables={"shade": shade, "A": a, "B": b},
            generator_ref="ch01_04::venn_operation",
            media=[media_entry("venn_two_set", {"shade": shade}, svg)],
            qti_support_level="manual_rebuild",
            bloom_level="understand",
        ))

    for _ in range(variant_count("static", RNG)):
        seq += 1
        n_a, n_b, n_ab = RNG.randint(5, 20), RNG.randint(5, 20), RNG.randint(2, 8)
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "word_problem", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="app (pattern)", page=PAGE,
            question_type="set_operation_word",
            item_format="numeric_entry",
            generation_strategy="static",
            topic="sets.operations.application",
            learning_objective=LO,
            stem=(
                f"A survey of {n_a + n_b - n_ab} people found that {n_a} like tea, {n_b} like coffee, "
                f"and {n_ab} like both. How many like tea only?"
            ),
            answer=n_a - n_ab,
            variables={"tea": n_a, "coffee": n_b, "both": n_ab},
            generator_ref="ch01_04::survey",
            bloom_level="apply",
            notes="Classic inclusion-exclusion word problem template.",
        ))

    return items
