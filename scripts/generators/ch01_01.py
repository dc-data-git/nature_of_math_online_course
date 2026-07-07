"""Section 1.1 — migrated from pilot bank."""

from __future__ import annotations

import json
from pathlib import Path

SECTION_ID = "1.1"
ROOT = Path(__file__).resolve().parents[2]
PILOT_JSON = ROOT / "pilot" / "1.1-pilot.json"


def generate_items() -> list[dict]:
    with open(PILOT_JSON, encoding="utf-8") as f:
        items = json.load(f)
    for it in items:
        it["status"] = "needs_review"
    return items
