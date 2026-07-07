#!/usr/bin/env python3
"""Assemble bank.json from the unified per-exercise generator."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generators.unified import generate_all
from scripts.lib.constants import ATTRIBUTION_FOOTER, BOOK, LICENSE
from scripts.lib.dashboard_data import parse_exercise_numbers
from scripts.lib.pdf_extract import extract_section_exercises
from scripts.lib.section_registry import load_sections

BANK_PATH = ROOT / "bank.json"


def section_meta(items: list[dict]) -> dict:
    meta = {}
    title_map = {s.section_id: s.title for s in load_sections()}
    for s in load_sections():
        info = extract_section_exercises(str(s.pdf_path), s.section_id)
        total = info.total_count
        meta[s.section_id] = {"title": s.title, "total_exercises": total}

    # Verify coverage from items
    for sid in title_map:
        section_items = [i for i in items if i["source"]["section"] == sid]
        covered: set[int] = set()
        for it in section_items:
            covered |= parse_exercise_numbers(it["source"]["exercise_number"])
        expected = meta.get(sid, {}).get("total_exercises", 0)
        if expected and covered:
            missing = set(range(1, expected + 1)) - covered
            if missing:
                print(f"  WARNING {sid}: missing exercises {sorted(missing)[:10]}{'...' if len(missing)>10 else ''}")
    return meta


def main() -> None:
    print("Generating unified per-exercise bank...")
    items = generate_all()
    sections = section_meta(items)
    bank = {
        "meta": {
            "book": BOOK,
            "license": LICENSE["type"],
            "attribution_footer": ATTRIBUTION_FOOTER,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(items),
            "total_sections": len(sections),
            "items_per_exercise": 3,
        },
        "sections": sections,
        "items": items,
    }
    with open(BANK_PATH, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)
    print(f"Wrote {BANK_PATH} ({len(items)} items, {len(sections)} sections)")


if __name__ == "__main__":
    main()
