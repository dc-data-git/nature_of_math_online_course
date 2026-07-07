"""Section 1.3 — Venn Diagrams."""

from __future__ import annotations

import random

from scripts.diagrams.venn_2set import media_entry, venn_two_set
from scripts.generators._ch01_common import themed_set
from scripts.lib.item_factory import item_id_prefix, make_item, variant_count

SECTION_ID = "1.3"
CHAPTER = 1
PAGE = 30
RNG = random.Random(13)

LO = "Represent sets and set relationships using Venn diagrams."

REGIONS = [
    ("A", "elements in A only"),
    ("B", "elements in B only"),
    ("A∩B", "elements in both A and B"),
    ("A∪B", "elements in A or B or both"),
    ("A-B", "elements in A but not in B"),
    ("outside", "elements in neither A nor B"),
]

SHADE_PROMPTS = {
    "A": "Shade the region representing A.",
    "B": "Shade the region representing B.",
    "A∩B": "Shade the region representing A ∩ B.",
    "A∪B": "Shade the region representing A ∪ B.",
    "A-B": "Shade the region representing A − B.",
    "outside": "Shade the region representing elements outside both A and B.",
}


def generate_items() -> list[dict]:
    items: list[dict] = []
    seq = 0
    labels_pool = [
        ("Students", "Faculty"),
        ("Cats", "Dogs"),
        ("Jazz", "Blues"),
        ("Soccer", "Basketball"),
    ]

    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        la, lb = RNG.choice(labels_pool)
        shade, desc = RNG.choice(REGIONS)
        svg = venn_two_set((la, lb), shade=shade)
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "venn_shade", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="venn (pattern)", page=PAGE,
            question_type="venn_region",
            item_format="short_answer",
            generation_strategy="algorithmic",
            topic="venn.region_shading",
            learning_objective=LO,
            stem=(
                f"In the Venn diagram below, sets A and B represent {la} and {lb} respectively. "
                f"{SHADE_PROMPTS[shade]}\n\n(Describe or identify the shaded region.)"
            ),
            answer=desc,
            variables={"label_a": la, "label_b": lb, "shade": shade},
            generator_ref="ch01_03::venn_shade",
            media=[media_entry("venn_two_set", {"labels": [la, lb], "shade": shade}, svg)],
            qti_support_level="manual_rebuild",
            bloom_level="understand",
            notes="Diagram is parameterized; Canvas may need manual Venn upload or image embed.",
        ))

    for _ in range(variant_count("algorithmic", RNG)):
        seq += 1
        la, lb = RNG.choice(labels_pool)
        shade = RNG.choice(["A", "B", "A∩B"])
        a_only = themed_set(RNG, 2)
        b_only = themed_set(RNG, 2)
        both = themed_set(RNG, 1)
        stem = (
            f"Set A = {{{', '.join(a_only + both)}}} and B = {{{', '.join(b_only + both)}}}. "
            f"Which elements belong to {shade.replace('∩', ' ∩ ')}?"
        )
        if shade == "A":
            ans = ", ".join(a_only + both)
        elif shade == "B":
            ans = ", ".join(b_only + both)
        else:
            ans = ", ".join(both)
        svg = venn_two_set((la, lb), shade=shade)
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "venn_elements", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="1-20 (pattern)", page=PAGE,
            question_type="venn_elements",
            item_format="short_answer",
            generation_strategy="algorithmic",
            topic="venn.identify_elements",
            learning_objective=LO,
            stem=stem,
            answer=ans,
            variables={"A": a_only + both, "B": b_only + both, "region": shade},
            generator_ref="ch01_03::venn_elements",
            media=[media_entry("venn_two_set", {"labels": [la, lb], "shade": shade}, svg)],
            qti_support_level="requires_conversion",
            bloom_level="apply",
        ))

    for _ in range(variant_count("templated", RNG)):
        seq += 1
        universal = themed_set(RNG, 5)
        subset = RNG.sample(universal, RNG.randint(2, 4))
        comp = [x for x in universal if x not in subset]
        items.append(make_item(
            item_id=item_id_prefix(SECTION_ID, "venn_complement", seq),
            section=SECTION_ID, chapter=CHAPTER, exercise_number="complement (pattern)", page=PAGE,
            question_type="venn_complement",
            item_format="short_answer",
            generation_strategy="templated",
            topic="venn.complement",
            learning_objective=LO,
            stem=(
                f"Given universal set U = {{{', '.join(universal)}}} and A = {{{', '.join(subset)}}}, "
                f"list the elements of A′ (the complement of A)."
            ),
            answer="{ " + ", ".join(comp) + " }",
            variables={"U": universal, "A": subset},
            generator_ref="ch01_03::complement",
            bloom_level="apply",
        ))

    return items
