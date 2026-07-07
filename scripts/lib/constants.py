"""Shared constants for the problem bank pipeline."""

BOOK = "OpenStax Contemporary Mathematics"
BOOK_SLUG = "contemporary-mathematics"
LICENSE = {
    "type": "CC BY 4.0",
    "attribution_text": (
        "Adapted from Contemporary Mathematics (OpenStax), available for free at "
        "openstax.org. Licensed under CC BY 4.0."
    ),
}

ATTRIBUTION_FOOTER = (
    "Content adapted from OpenStax Contemporary Mathematics (CC BY 4.0). "
    "https://openstax.org/details/books/contemporary-mathematics"
)

# POC variant depths
VARIANT_COUNTS = {"algorithmic": (8, 12), "templated": (3, 4), "static": (2, 3)}

BLOOM_ORDER = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
BLOOM_LABELS = {
    "remember": "Remember — recall a fact",
    "understand": "Understand — translate/represent",
    "apply": "Apply — execute a known procedure",
    "analyze": "Analyze — differentiate/reason about structure",
    "evaluate": "Evaluate — judge against a criterion",
    "create": "Create — produce something new",
}

STRATEGY_LABELS = {
    "algorithmic": "Auto-generated — unlimited variety, answer computed",
    "templated": "Verified content bank — moderate variety, fact-checked",
    "static": "Hand-crafted — low variety, human-authored",
}
