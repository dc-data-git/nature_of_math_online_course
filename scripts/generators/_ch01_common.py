"""Shared helpers for Chapter 1 generators."""

from __future__ import annotations

import random

THEMED_POOLS = {
    "fruits": ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"],
    "colors": ["red", "orange", "yellow", "green", "blue", "violet", "indigo"],
    "tools": ["hammer", "wrench", "pliers", "saw", "drill", "level", "tape"],
    "sports": ["soccer", "tennis", "golf", "hockey", "rugby", "cricket", "polo"],
    "animals": ["cat", "dog", "fox", "owl", "bear", "wolf", "deer"],
}


def themed_set(rng: random.Random, k: int | None = None) -> list[str]:
    pool = rng.choice(list(THEMED_POOLS.values()))
    k = k or rng.randint(2, min(5, len(pool)))
    return rng.sample(pool, k)


def pow2(n: int) -> int:
    return 2**n
