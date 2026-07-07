#!/usr/bin/env python3
"""Write dashboard_data.json for optional local embed (dashboard fetches bank.json on Pages)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.dashboard_data import build_dashboard_data

BANK_PATH = ROOT / "bank.json"
OUT_PATH = ROOT / "dashboard_data.json"


def main() -> None:
    with open(BANK_PATH, encoding="utf-8") as f:
        bank = json.load(f)
    data = build_dashboard_data(bank["items"], bank.get("sections", {}))
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    n_sections = len(data["sections"])
    n_items = sum(s["total_items"] for s in data["sections"].values())
    print(f"Wrote {OUT_PATH} ({n_sections} sections, {n_items} items)")


if __name__ == "__main__":
    main()
