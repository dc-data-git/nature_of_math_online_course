#!/usr/bin/env python3
"""Assemble bank.json from all section generators."""

from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generators.auto import generate_all_auto
from scripts.lib.constants import ATTRIBUTION_FOOTER, BOOK, LICENSE
from scripts.lib.section_registry import load_sections

BANK_PATH = ROOT / "bank.json"
GENERATORS_DIR = ROOT / "scripts" / "generators"

DEDICATED_MODULES = [
    "scripts.generators.ch01_01",
    "scripts.generators.ch01_02",
    "scripts.generators.ch01_03",
    "scripts.generators.ch01_04",
    "scripts.generators.ch01_05",
]


def load_dedicated_items() -> list[dict]:
    items: list[dict] = []
    for mod_name in DEDICATED_MODULES:
        mod = importlib.import_module(mod_name)
        batch = mod.generate_items()
        print(f"  {mod_name}: {len(batch)} items")
        items.extend(batch)
    return items


def exercise_counts(items: list[dict]) -> dict[str, int]:
    from scripts.lib.dashboard_data import parse_exercise_numbers

    counts: dict[str, int] = {}
    by_section: dict[str, set[int]] = {}
    for it in items:
        sid = it["source"]["section"]
        by_section.setdefault(sid, set()).update(
            parse_exercise_numbers(it["source"]["exercise_number"])
        )
    for sid, nums in by_section.items():
        counts[sid] = max(nums) if nums else 0
    return counts


def build_bank() -> dict:
    print("Loading dedicated generators...")
    items = load_dedicated_items()
    print("Running auto-generator for remaining sections...")
    auto_items = generate_all_auto()
    print(f"  auto: {len(auto_items)} items")
    items.extend(auto_items)

    sections_meta = {}
    title_map = {s.section_id: s.title for s in load_sections()}
    ex_counts = exercise_counts(items)
    for sid, title in title_map.items():
        if sid in ex_counts:
            sections_meta[sid] = {
                "title": title,
                "total_exercises": ex_counts[sid],
            }

    bank = {
        "meta": {
            "book": BOOK,
            "license": LICENSE["type"],
            "attribution_footer": ATTRIBUTION_FOOTER,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(items),
            "total_sections": len({it["source"]["section"] for it in items}),
        },
        "sections": sections_meta,
        "items": items,
    }
    return bank


def main() -> None:
    bank = build_bank()
    with open(BANK_PATH, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)
    print(f"Wrote {BANK_PATH} ({bank['meta']['total_items']} items, "
          f"{bank['meta']['total_sections']} sections)")


if __name__ == "__main__":
    main()
