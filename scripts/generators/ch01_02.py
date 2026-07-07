"""Section 1.2 — Subsets."""

from __future__ import annotations

import random

from scripts.generators._ch01_common import themed_set
from scripts.lib.item_factory import item_id_prefix, make_item, variant_count

SECTION_ID = "1.2"
CHAPTER = 1
PAGE = 19
RNG = random.Random(12)

LO_SYMBOLIC = "Represent subsets and proper subsets symbolically."
LO_COUNT = "Compute the number of subsets of a set."
LO_EQUIV = "Apply concepts of subsets and equivalent sets to finite and infinite sets."


def _proper_subset_count(n: int) -> int:
    return max(0, 2**n - 1)


def generate_items() -> list[dict]:
    items: list[dict] = []
    seq = 0

    # Exercises 1-4 pattern: proper subsets of a finite set
    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        elements = themed_set(RNG, k=RNG.randint(2, 4))
        n = len(elements)
        roster = "{" + ", ".join(elements) + "}"
        count = _proper_subset_count(n)
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "proper_subset_count", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="1-4 (pattern)", page=PAGE,
            question_type="subset_count",
            item_format="numeric_entry",
            generation_strategy="algorithmic",
            topic="subsets.proper_subset_count",
            learning_objective=LO_COUNT,
            stem=f"How many proper subsets does the set {roster} have?",
            answer=count,
            variables={"elements": elements, "n": n},
            generator_ref="ch01_02::proper_subset_count",
            bloom_level="apply",
            feedback={
                "correct": f"A set with {n} elements has 2^n = {2**n} subsets total; proper subsets exclude the set itself, so {count}.",
                "incorrect": "Use 2^n − 1 for the number of proper subsets (all subsets except the set itself).",
            },
        ))

    # Exercises 5-14 pattern: symbolic subset relationships
    relations = [
        ("{2, 4, 6}", "{2, 4, 6, 8, 10}", "⊂", "proper subset"),
        ("{a, e, i}", "{a, e, i, o, u}", "⊂", "proper subset"),
        ("{1, 3, 5}", "{1, 2, 3, 4, 5}", "⊂", "proper subset"),
        ("{x, y}", "{x, y}", "=", "equal"),
        ("{m, n}", "{p, q}", "⊄", "neither subset nor equal"),
    ]
    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        a_el = themed_set(RNG, k=RNG.randint(2, 3))
        if RNG.random() < 0.6:
            extra = themed_set(RNG, k=RNG.randint(1, 2))
            b_el = list(dict.fromkeys(a_el + extra))
            rel, label = "⊂", "proper subset"
        elif RNG.random() < 0.5:
            b_el = list(a_el)
            rel, label = "=", "equal"
        else:
            b_el = themed_set(RNG, k=RNG.randint(2, 3))
            while set(b_el) == set(a_el):
                b_el = themed_set(RNG, k=RNG.randint(2, 3))
            rel, label = "⊄", "neither subset nor equal"
        a, b = "{" + ", ".join(a_el) + "}", "{" + ", ".join(b_el) + "}"
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "subset_relation", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="5-14 (pattern)", page=PAGE,
            question_type="subset_relation",
            item_format="multiple_choice",
            generation_strategy="algorithmic",
            topic="subsets.symbolic_relation",
            learning_objective=LO_SYMBOLIC,
            stem=f"Determine the relationship between A = {a} and B = {b}. Write the correct symbolic relationship.",
            answer=rel,
            options=["⊂", "⊆", "=", "⊄"],
            variables={"A": a_el, "B": b_el, "relationship": label},
            generator_ref="ch01_02::subset_relation",
            bloom_level="understand",
        ))

    # Exercises 15-16 pattern: total number of subsets 2^n
    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        n = RNG.randint(3, 8)
        elements = [str(i) for i in RNG.sample(range(2, 20), n)]
        roster = "{" + ", ".join(elements) + "}"
        total = 2**n
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "subset_total", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="15-16 (pattern)", page=PAGE,
            question_type="subset_count",
            item_format="numeric_entry",
            generation_strategy="algorithmic",
            topic="subsets.total_count",
            learning_objective=LO_COUNT,
            stem=f"Calculate the total number of subsets of {roster}.",
            answer=total,
            variables={"n": n, "elements": elements},
            generator_ref="ch01_02::total_subsets",
            bloom_level="apply",
            feedback={
                "correct": f"|S| = {n}, so the number of subsets is 2^{n} = {total}.",
                "incorrect": "The number of subsets of a finite set with n elements is 2^n.",
            },
        ))

    # Equivalent subset pairs (infinite / finite themes from section)
    for _ in range(variant_count("templated", RNG)):
        seq += 1
        k = RNG.randint(2, 4)
        pool = themed_set(RNG, k=6)
        s1 = sorted(RNG.sample(pool, k))
        s2 = sorted(RNG.sample(pool, k))
        while s1 == s2:
            s2 = sorted(RNG.sample(pool, k))
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "equiv_subset", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="equiv (pattern)", page=PAGE,
            question_type="subset_equivalent",
            item_format="short_answer",
            generation_strategy="templated",
            topic="subsets.equivalent_pairs",
            learning_objective=LO_EQUIV,
            stem=(
                f"Create two equivalent but not equal subsets of {pool} "
                f"that each have exactly {k} members. List both in roster form."
            ),
            answer=f"Example: {{{', '.join(s1)}}} and {{{', '.join(s2)}}}",
            variables={"pool": pool, "k": k, "set1": s1, "set2": s2},
            generator_ref="ch01_02::equivalent_subsets",
            qti_support_level="requires_conversion",
            bloom_level="analyze",
        ))

    return items
