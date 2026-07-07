"""Build dashboard view-model from bank.json items."""

from __future__ import annotations

import html as htmlmod
import re
from collections import Counter, defaultdict

from scripts.lib.constants import BLOOM_LABELS, BLOOM_ORDER, STRATEGY_LABELS
from scripts.lib.section_registry import load_sections

TOPIC_DISPLAY_NAMES: dict[str, str] = {
    "sets.cardinality.finite": "Cardinality of finite sets",
    "sets.cardinality.infinite": "Cardinality of infinite sets (ℵ₀)",
    "sets.equal_equivalent": "Equal vs. equivalent vs. neither",
    "sets.roster_method.range": "Roster method: number-range boundary language",
    "sets.roster_method.named_list": "Roster method: named real-world lists",
    "sets.set_builder_notation.multiples": "Set-builder notation: multiples of k",
    "sets.set_builder_notation.descriptive": "Set-builder notation: described categories",
    "sets.well_defined.objective": "Well-defined sets: objective math properties",
    "sets.well_defined.subjective": "Well-defined sets: subjective superlatives",
    "sets.well_defined.real_world_fact": "Well-defined sets: real-world facts",
    "sets.method_choice.empty_set_trick": "Best representation: empty-set trick cases",
    "sets.method_choice.finite_word": "Best representation: small finite sets",
    "sets.method_choice.infinite_setbuilder": "Best representation: infinite sets (set-builder)",
    "sets.method_choice.infinite_roster": "Best representation: infinite sets (ellipsis roster)",
    "sets.method_choice.large_finite": "Best representation: large finite named collections",
    "sets.finite_infinite_classification.objective": "Finite vs. infinite: math-defined sets",
    "sets.finite_infinite_classification.real_world_fact": "Finite vs. infinite: real-world collections",
}


def topic_display_name(topic: str) -> str:
    if topic in TOPIC_DISPLAY_NAMES:
        return TOPIC_DISPLAY_NAMES[topic]
    parts = topic.split(".")
    return " — ".join(p.replace("_", " ").title() for p in parts[-2:])


def parse_exercise_numbers(exercise_str: str) -> set[int]:
    nums: set[int] = set()
    core = exercise_str.split("(")[0]
    for part in core.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            if a.isdigit() and b.isdigit():
                nums.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            nums.add(int(part))
    return nums


def highlight_stem(stem: str, variables: dict | None) -> str:
    if not variables:
        return htmlmod.escape(stem)

    candidates: list[str] = []

    def collect(v):
        if isinstance(v, (list, tuple)):
            for x in v:
                collect(x)
        elif isinstance(v, dict):
            for x in v.values():
                collect(x)
        elif isinstance(v, bool):
            return
        elif isinstance(v, (int, float)):
            candidates.append(str(v))
        elif isinstance(v, str) and v.strip():
            candidates.append(v)
            if "_" in v:
                candidates.append(v.replace("_", " "))
                candidates.extend(w for w in v.split("_") if len(w) >= 4)

    for v in variables.values():
        collect(v)

    candidates = sorted(set(candidates), key=len, reverse=True)
    if not candidates:
        return htmlmod.escape(stem)

    pattern = re.compile("(" + "|".join(r"\b" + re.escape(c) + r"\b" for c in candidates) + ")")
    pieces = pattern.split(stem)
    out = []
    for i, piece in enumerate(pieces):
        if not piece:
            continue
        if i % 2 == 1:
            out.append(f'<mark class="param">{htmlmod.escape(piece)}</mark>')
        else:
            out.append(htmlmod.escape(piece))
    return "".join(out)


def ranges(nums: list[int]) -> list[str]:
    if not nums:
        return []
    nums = sorted(nums)
    out = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        out.append(f"{start}-{prev}" if start != prev else str(start))
        start = prev = n
    out.append(f"{start}-{prev}" if start != prev else str(start))
    return out


def build_dashboard_data(items: list[dict], section_meta: dict | None = None) -> dict:
    section_meta = section_meta or {}
    title_map = {s.section_id: s.title for s in load_sections()}

    by_section: dict[str, list] = defaultdict(list)
    for it in items:
        by_section[it["source"]["section"]].append(it)

    sections_out = {}
    for sid, group in sorted(by_section.items()):
        meta = section_meta.get(sid, {})
        total_exercises = meta.get("total_exercises")
        if total_exercises is None:
            covered = set()
            for it in group:
                covered |= parse_exercise_numbers(it["source"]["exercise_number"])
            total_exercises = max(covered) if covered else len(group)

        by_topic: dict[str, list] = defaultdict(list)
        for it in group:
            by_topic[it["topic"]].append(it)

        topics_out = {}
        review_queue = []
        all_covered: set[int] = set()

        for topic, tgroup in by_topic.items():
            formats = sorted({i["item_format"] for i in tgroup})
            strategies = sorted({i["generation_strategy"] for i in tgroup})
            statuses = Counter(i["status"] for i in tgroup)
            exercise_strs = sorted({i["source"]["exercise_number"] for i in tgroup})
            for es in exercise_strs:
                all_covered |= parse_exercise_numbers(es)

            items_out = []
            for it in tgroup:
                media_html = ""
                for m in it.get("media") or []:
                    if m.get("render") == "inline_svg" and m.get("svg"):
                        media_html += m["svg"]
                stem_html = highlight_stem(it["stem"], it.get("variables"))
                if media_html:
                    stem_html = f'<div class="diagram">{media_html}</div>' + stem_html
                items_out.append({
                    "id": it["id"],
                    "stem_html": stem_html,
                    "item_format": it["item_format"],
                    "answer": it["answer"] if not isinstance(it["answer"], bool) else ("True" if it["answer"] else "False"),
                    "options": it.get("options"),
                    "status": it["status"],
                    "generation_strategy": it["generation_strategy"],
                    "bloom_level": it["bloom_level"],
                    "difficulty": it.get("difficulty"),
                    "qti_support_level": it.get("qti_support_level", "direct"),
                    "source_exercise": it["source"]["exercise_number"],
                    "notes": it.get("notes"),
                })
                if it["status"] == "needs_review":
                    review_queue.append({
                        "topic": topic,
                        "id": it["id"],
                        "stem": it["stem"][:100],
                        "notes": it.get("notes") or "",
                    })

            bloom_levels = sorted({i["bloom_level"] for i in tgroup}, key=BLOOM_ORDER.index)
            topics_out[topic] = {
                "name": topic_display_name(topic),
                "learning_objective": tgroup[0]["learning_objective"],
                "source_exercises": ", ".join(exercise_strs),
                "item_formats": formats,
                "generation_strategies": strategies,
                "strategy_label": (
                    STRATEGY_LABELS.get(strategies[0], strategies[0])
                    if len(strategies) == 1
                    else "Mixed"
                ),
                "bloom_level": bloom_levels[0] if len(bloom_levels) == 1 else "mixed",
                "status_counts": dict(statuses),
                "count": len(tgroup),
                "items": items_out,
            }

        missing = sorted(set(range(1, total_exercises + 1)) - all_covered)
        bloom_present = sorted(
            {t["bloom_level"] for t in topics_out.values() if t["bloom_level"] != "mixed"},
            key=BLOOM_ORDER.index,
        )
        bloom_counts: Counter = Counter()
        for t in topics_out.values():
            if t["bloom_level"] != "mixed":
                bloom_counts[t["bloom_level"]] += t["count"]

        lo_map: dict = defaultdict(lambda: {"topics": [], "count": 0})
        for topic, t in topics_out.items():
            lo = t["learning_objective"]
            lo_map[lo]["topics"].append(topic)
            lo_map[lo]["count"] += t["count"]

        chapter = group[0]["source"]["chapter"]
        sections_out[sid] = {
            "title": f"{sid} {title_map.get(sid, meta.get('title', ''))}".strip(),
            "chapter": int(chapter) if str(chapter).isdigit() else chapter,
            "source": f"OpenStax Contemporary Mathematics, Chapter {chapter}",
            "license": "CC BY 4.0",
            "total_items": len(group),
            "total_exercises": total_exercises,
            "coverage_gaps": ranges(missing),
            "learning_objectives": [
                {"text": lo, "topics": v["topics"], "count": v["count"]}
                for lo, v in sorted(lo_map.items())
            ],
            "bloom_levels": [
                {"level": lvl, "label": BLOOM_LABELS[lvl], "count": bloom_counts[lvl]}
                for lvl in bloom_present
            ],
            "topics": topics_out,
            "review_queue": review_queue,
        }

    return {"sections": sections_out}
