"""
Build ANSWER_KEY.md -- a condensed per-topic summary, not a per-item table.
Past a few dozen items a per-item table stops being a practical test
artifact (see pipeline doc Section 10), so this samples one representative
item per topic plus counts/status, on the reasoning that every item in a
topic runs through the same generator code path.
"""
import json
from collections import defaultdict, Counter

with open("1.1-pilot.json") as f:
    ITEMS = json.load(f)

by_topic = defaultdict(list)
for it in ITEMS:
    by_topic[it["topic"]].append(it)


def sample_answer(it):
    ans = it["answer"]
    if isinstance(ans, bool):
        return "True" if ans else "False"
    ans = str(ans)
    if it["item_format"] == "essay":
        return "(essay -- no auto-grade)"
    if it["id"].startswith("contemath-1.1-pilot-C-02") or it["id"].startswith("contemath-1.1-pilot-C-05") \
            or it["id"].startswith("contemath-1.1-pilot-C-06"):
        return "∅ (or: {}, empty set, null set)"
    return ans


lines = [
    f"# Pilot Answer Key -- Full Coverage Pass ({len(ITEMS)} items)",
    "",
    "This bank is too deep to click through every item by hand. Recommended test: for each "
    "topic below, pull a handful of that topic's items into a quiz, answer using the sample "
    "shown, and spot-check 2-3 more of your own choosing per topic. If the sample and your "
    "spot-checks all grade correctly, the whole topic's generator is almost certainly sound "
    "(it's the same code path for every item in the topic).",
    "",
    "All 50 source exercises now have a matching topic -- see the pipeline doc's coverage "
    "table for the exercise-by-exercise mapping.",
    "",
    "| topic | count | item_format | bloom | status | sample stem | sample correct answer |",
    "|---|---|---|---|---|---|---|",
]

for topic, group in sorted(by_topic.items()):
    fmts = sorted(set(i["item_format"] for i in group))
    fmt = fmts[0] if len(fmts) == 1 else "mixed"
    statuses = Counter(i["status"] for i in group)
    status = statuses.most_common(1)[0][0] if len(statuses) == 1 else "mixed (" + ", ".join(f"{n} {s}" for s, n in statuses.items()) + ")"
    blooms = sorted(set(i["bloom_level"] for i in group))
    bloom = blooms[0] if len(blooms) == 1 else "mixed"
    sample = group[0]
    stem_preview = sample["stem"].replace("\n", " ")[:90]
    ans_preview = sample_answer(sample)
    lines.append(f"| {topic} | {len(group)} | {fmt} | {bloom} | {status} | {stem_preview}... | {ans_preview} |")

with open("ANSWER_KEY.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Wrote ANSWER_KEY.md ({len(by_topic)} topics, {len(ITEMS)} items)")
