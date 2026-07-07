"""
Build the interactive HTML dashboard -- a human-viewable rendering of the
JSON problem bank. This script is the only thing that should ever produce
dashboard.html; the file itself is never hand-edited, same rule as the QTI
and answer-key artifacts. Re-run this after any change to 1.1-pilot.json.
"""
import json
import re
import html as htmlmod
from collections import defaultdict, Counter

with open("1.1-pilot.json") as f:
    ITEMS = json.load(f)

SECTION_ID = "1.1"
SECTION_TITLE = "1.1 Basic Set Concepts"
SECTION_SOURCE = "OpenStax Contemporary Mathematics, Chapter 1"
SECTION_LICENSE = "CC BY 4.0"
TOTAL_EXERCISES = 50  # exercises in this section's original problem set

TOPIC_NAMES = {
    "sets.cardinality.finite": "Cardinality of finite sets",
    "sets.cardinality.infinite": "Cardinality of infinite sets (aleph-null)",
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

STRATEGY_LABELS = {
    "algorithmic": "Auto-generated -- unlimited variety, answer computed",
    "templated": "Verified content bank -- moderate variety, fact-checked",
    "static": "Hand-crafted -- low variety, human-authored",
}

# Canonical Bloom's (revised) order, low to high cognitive demand. Rated per
# topic/randomization_group (see gen_category_a.py / gen_category_bc.py
# comments), not per individual item -- a family of items sharing a group is
# doing the same cognitive task, so it gets one Bloom level, same as the
# grouped-comparison logic used for difficulty.
BLOOM_ORDER = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
BLOOM_LABELS = {
    "remember": "Remember -- recall a fact",
    "understand": "Understand -- translate/represent",
    "apply": "Apply -- execute a known procedure",
    "analyze": "Analyze -- differentiate/reason about structure",
    "evaluate": "Evaluate -- judge against a criterion",
    "create": "Create -- produce something new",
}


def parse_exercise_numbers(exercise_str):
    """'27-32,35-36 (pattern)' -> {27,28,...,32,35,36}"""
    nums = set()
    core = exercise_str.split("(")[0]
    for part in core.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            nums.update(range(int(a), int(b) + 1))
        else:
            if part.isdigit():
                nums.add(int(part))
    return nums


def highlight_stem(stem, variables):
    """Wrap substrings of `stem` that came from `variables` in <mark class=param>.
    Heuristic: search for each variable's flattened values as literal
    substrings, longest first so e.g. 'kitchen tools' matches before 'tools'
    alone, and every candidate (not just numbers) is word-boundary-protected
    so a short word like 'car' doesn't match inside unrelated text like
    'cardinal'.

    Some variables (e.g. A3's boundary_template: 'strictly_between') store an
    internal slug, not the literal English phrase that ends up in the stem
    ('strictly between'). That phrasing choice is itself parameterized -- it's
    randomly selected per item just like the numbers are -- so it should
    highlight too. For any slug-shaped candidate (contains '_'), also try the
    space-joined phrase, and fall back to its individual words (len >= 4, to
    avoid flagging short generic words) in case the phrase isn't contiguous in
    the stem (e.g. 'through {b}, inclusive' isn't one contiguous run)."""
    if not variables:
        return htmlmod.escape(stem)

    candidates = []

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

    parts = [r"\b" + re.escape(c) + r"\b" for c in candidates]
    pattern = re.compile("(" + "|".join(parts) + ")")

    pieces = pattern.split(stem)
    out = []
    for i, piece in enumerate(pieces):
        if not piece:
            continue
        if i % 2 == 1:  # matched group
            out.append(f'<mark class="param">{htmlmod.escape(piece)}</mark>')
        else:
            out.append(htmlmod.escape(piece))
    return "".join(out)


# --- group items by topic ---------------------------------------------------
by_topic = defaultdict(list)
for it in ITEMS:
    by_topic[it["topic"]].append(it)

topics_out = {}
covered_exercise_nums = set()
review_queue = []

for topic, group in by_topic.items():
    formats = sorted(set(i["item_format"] for i in group))
    strategies = sorted(set(i["generation_strategy"] for i in group))
    statuses = Counter(i["status"] for i in group)
    exercise_strs = sorted(set(i["source"]["exercise_number"] for i in group))
    for es in exercise_strs:
        covered_exercise_nums |= parse_exercise_numbers(es)

    items_out = []
    for it in group:
        stem_html = highlight_stem(it["stem"], it.get("variables"))
        items_out.append({
            "id": it["id"],
            "stem_html": stem_html,
            "item_format": it["item_format"],
            "answer": it["answer"] if not isinstance(it["answer"], bool) else ("True" if it["answer"] else "False"),
            "options": it.get("options"),
            "status": it["status"],
            "generation_strategy": it["generation_strategy"],
            "bloom_level": it["bloom_level"],
            "source_exercise": it["source"]["exercise_number"],
            "notes": it.get("notes"),
        })
        if it["status"] == "needs_review":
            review_queue.append({
                "topic": topic, "id": it["id"],
                "stem": it["stem"][:100], "notes": it.get("notes") or "",
            })

    bloom_levels = sorted(set(i["bloom_level"] for i in group), key=BLOOM_ORDER.index)

    topics_out[topic] = {
        "name": TOPIC_NAMES.get(topic, topic),
        "learning_objective": group[0]["learning_objective"],
        "source_exercises": ", ".join(exercise_strs),
        "item_formats": formats,
        "generation_strategies": strategies,
        "strategy_label": STRATEGY_LABELS.get(strategies[0], strategies[0]) if len(strategies) == 1 else "Mixed",
        "bloom_level": bloom_levels[0] if len(bloom_levels) == 1 else "mixed",
        "status_counts": dict(statuses),
        "count": len(group),
        "items": items_out,
    }

all_covered = set()
for es in set(i["source"]["exercise_number"] for i in ITEMS):
    all_covered |= parse_exercise_numbers(es)
missing = sorted(set(range(1, TOTAL_EXERCISES + 1)) - all_covered)


def ranges(nums):
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


coverage_gaps = ranges(missing)

# --- bloom-level rollup (for the filter control) -----------------------------
bloom_present = sorted(set(t["bloom_level"] for t in topics_out.values() if t["bloom_level"] != "mixed"),
                        key=BLOOM_ORDER.index)
bloom_counts = Counter()
for t in topics_out.values():
    if t["bloom_level"] != "mixed":
        bloom_counts[t["bloom_level"]] += t["count"]

# --- learning objective rollup ----------------------------------------------
lo_map = defaultdict(lambda: {"topics": [], "count": 0})
for topic, t in topics_out.items():
    lo = t["learning_objective"]
    lo_map[lo]["topics"].append(topic)
    lo_map[lo]["count"] += t["count"]

DATA = {
    "sections": {
        SECTION_ID: {
            "title": SECTION_TITLE,
            "source": SECTION_SOURCE,
            "license": SECTION_LICENSE,
            "total_items": len(ITEMS),
            "total_exercises": TOTAL_EXERCISES,
            "coverage_gaps": coverage_gaps,
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
    }
}

DATA_JSON = json.dumps(DATA, indent=None)
print(f"Dashboard data: {len(ITEMS)} items, {len(topics_out)} topics, "
      f"{len(coverage_gaps)} gap range(s), {len(review_queue)} in review queue")
print("Coverage gaps:", coverage_gaps)

with open("dashboard_template.html") as f:
    template = f.read()

output = template.replace("__DASHBOARD_DATA_JSON__", DATA_JSON)
with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(output)
print("Wrote dashboard.html")
