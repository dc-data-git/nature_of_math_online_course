"""
Category B (templated) and Category C (static) items -- DEEP PASS.

Key change from the pilot version: most of the "well-defined set" judgment
pool turns out NOT to need per-item human review after all. Once you see
the structural pattern -- "an objective mathematical property is always
well-defined" and "a superlative/opinion adjective is always NOT
well-defined, regardless of the noun it's paired with" -- the correctness
of each generated sentence follows from that structure, not from a fact
that could be individually wrong. So B1 below is split:

  - B1a (objective math property): reclassified as Category A / computed.
    "prime", "even", "multiple of k" are decidable properties; any set
    defined by one is well-defined by definition. No review needed.
  - B1b (subjective superlative): also reclassified as Category A /
    computed. "most X", "best X", "friendliest X" are subjective by the
    superlative structure itself, independent of the noun. No review
    needed.
  - B1c (real-world fact): stays genuine Category B. "U.S. states that
    border the Pacific" IS a factual claim that could be wrong, so this
    one still needs a human/LLM review pass before it's trusted.

B2 (named-list roster) stays Category B throughout -- the correct roster
for "the Great Lakes" is a fact, not a structural guarantee, so there's no
shortcut around reviewing each one.
"""
import json

TODAY = "2026-07-03"
SOURCE_BASE = {"book": "OpenStax Contemporary Mathematics", "chapter": 1, "section": "1.1"}
LICENSE = {
    "type": "CC BY 4.0",
    "attribution_text": "Adapted from Contemporary Mathematics (OpenStax), Section 1.1, "
                         "available for free at openstax.org. Licensed under CC BY 4.0."
}

items = []

# ---------------------------------------------------------------------------
# B1a: objective math-property well-defined sets (mirrors #21-26; ALGORITHMIC)
# ---------------------------------------------------------------------------
import random
random.seed(11)

MATH_TEMPLATES = [
    lambda n: (f"the set of prime numbers less than {n}", True),
    lambda n: (f"the set of even numbers less than {n}", True),
    lambda n: (f"the set of numbers divisible by 3 that are less than {n}", True),
    lambda n: (f"the set of perfect squares less than {n}", True),
]

b1a_count = 0
for _ in range(8):
    n = random.randint(15, 100)
    template = random.choice(MATH_TEMPLATES)
    desc, well_defined = template(n)
    b1a_count += 1
    items.append({
        "id": f"contemath-1.1-pilot-B1A-{b1a_count:02d}",
        "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "21-26 (pattern)", "page": 13},
        "license": LICENSE, "question_type": "classification_2choice", "item_format": "true_false",
        "qti_support_level": "direct", "generation_strategy": "algorithmic",
        "topic": "sets.well_defined.objective", "learning_objective": "Represent well-defined sets and the empty set with proper set notation.",
        "difficulty": "intro", "bloom_level": "evaluate",
        "randomization_group": "sets.well_defined.judgment", "reuse_risk": "fresh_each_use",
        "stem": f"True or False: \"{desc.capitalize()}.\" describes a well-defined set.",
        "variables": {"description": desc, "n": n},
        "generator_ref": "gen_bc_deep.py::B1a_objective_math_property", "answer": True,
        "options": ["True", "False"], "distractor_rationale": None,
        "feedback": {"correct": "A mathematical property like this one is objective -- any number "
                                 "either satisfies it or doesn't, with no room for disagreement.",
                     "incorrect": "This category is defined by a decidable mathematical property, "
                                  "so membership is never ambiguous -- it IS well-defined."},
        "media": [], "status": "approved", "verification_method": "computed",
        "notes": "Well-defined=True is guaranteed by the property being a decidable math property, "
                 "not asserted as a standalone fact.",
        "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
    })

# ---------------------------------------------------------------------------
# B1b: subjective superlative NOT-well-defined sets (mirrors #21-26; ALGORITHMIC)
# ---------------------------------------------------------------------------
SUBJECTIVE_ADJECTIVES = ["most exciting", "best", "friendliest", "most beautiful",
                          "tastiest", "most interesting", "most impressive", "funniest"]
SUBJECTIVE_NOUNS = ["rides at an amusement park", "pizza toppings", "dog breeds",
                     "songs of all time", "vacation destinations", "board games",
                     "ice cream flavors", "superhero movies"]

b1b_count = 0
for _ in range(8):
    adj = random.choice(SUBJECTIVE_ADJECTIVES)
    noun = random.choice(SUBJECTIVE_NOUNS)
    desc = f"the {adj} {noun}"
    b1b_count += 1
    items.append({
        "id": f"contemath-1.1-pilot-B1B-{b1b_count:02d}",
        "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "21-26 (pattern)", "page": 13},
        "license": LICENSE, "question_type": "classification_2choice", "item_format": "true_false",
        "qti_support_level": "direct", "generation_strategy": "algorithmic",
        "topic": "sets.well_defined.subjective", "learning_objective": "Represent well-defined sets and the empty set with proper set notation.",
        "difficulty": "intro", "bloom_level": "evaluate",
        "randomization_group": "sets.well_defined.judgment", "reuse_risk": "fresh_each_use",
        "stem": f"True or False: \"The group of {desc}.\" describes a well-defined set.",
        "variables": {"adjective": adj, "noun": noun},
        "generator_ref": "gen_bc_deep.py::B1b_subjective_superlative", "answer": False,
        "options": ["True", "False"], "distractor_rationale": None,
        "feedback": {"correct": f"'{adj.capitalize()}' is an opinion-based superlative -- different "
                                 f"people will disagree about which {noun} belong in the set.",
                     "incorrect": f"'{adj.capitalize()}' is a matter of opinion, so this set is NOT "
                                  f"well-defined -- people can reasonably disagree on membership."},
        "media": [], "status": "approved", "verification_method": "computed",
        "notes": "Well-defined=False is guaranteed by the adjective being an opinion-based superlative, "
                 "independent of which noun it's paired with.",
        "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
    })

# ---------------------------------------------------------------------------
# B1c: real-world-fact well-defined items (genuine Category B; needs_review)
# ---------------------------------------------------------------------------
b1c_data = [
    ("The set of U.S. states that border the Pacific Ocean.", True,
     "Bordering the Pacific Ocean is a fixed geographic fact (California, Oregon, Washington, "
     "Alaska, Hawaii), not a matter of opinion."),
    ("The set of planets in our solar system that have rings.", True,
     "Ring systems are an observable physical fact (Jupiter, Saturn, Uranus, Neptune all have "
     "rings), not a matter of opinion."),
    ("The set of countries that share a land border with exactly one other country.", True,
     "This is a fixed, checkable geographic fact, even though compiling the actual roster takes "
     "research -- the criterion itself is objective."),
    ("The set of the most walkable cities in the United States.", False,
     "'Most walkable' depends on which ranking/methodology you trust -- different sources "
     "produce different lists, so this is not well-defined."),
]
b1c_count = 0
for desc, well_defined, rationale in b1c_data:
    b1c_count += 1
    items.append({
        "id": f"contemath-1.1-pilot-B1C-{b1c_count:02d}",
        "parent_id": None, "origin": "templated_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "21-26 (pattern)", "page": 13},
        "license": LICENSE, "question_type": "classification_2choice", "item_format": "true_false",
        "qti_support_level": "direct", "generation_strategy": "templated",
        "topic": "sets.well_defined.real_world_fact", "learning_objective": "Represent well-defined sets and the empty set with proper set notation.",
        "difficulty": "practice", "bloom_level": "evaluate",
        "randomization_group": "sets.well_defined.judgment", "reuse_risk": "static_low_risk",
        "stem": f"True or False: \"{desc}\" describes a well-defined set.",
        "variables": {"description": desc}, "generator_ref": None, "answer": well_defined,
        "options": ["True", "False"], "distractor_rationale": None,
        "feedback": {"correct": rationale, "incorrect": rationale},
        "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
        "notes": "Genuine fact-based judgment (not a structural guarantee) -- needs a human pass "
                 "to confirm the objective/subjective call and, for the true items, that the "
                 "underlying fact is accurate.",
        "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
    })

# ---------------------------------------------------------------------------
# B2: named-list roster, multiple choice (mirrors #1, #2, #5; Category B)
# ---------------------------------------------------------------------------
b2_data = [
    {"prompt": "the set of continents",
     "correct": ["Africa", "Antarctica", "Asia", "Australia", "Europe", "North America", "South America"],
     "distractors": [
         ["Africa", "Asia", "Australia", "Europe", "North America", "South America"],
         ["Africa", "Eurasia", "Australia", "North America", "South America"],
         ["Africa", "Antarctica", "Asia", "Australia", "Europe", "North America", "South America", "Greenland"]],
     "distractor_rationale": ["correct: standard 7-continent model", "6-continent model, omits Antarctica",
                               "incorrectly merges Europe and Asia into 'Eurasia'", "adds Greenland, not a continent"]},
    {"prompt": "the set of the Great Lakes",
     "correct": ["Erie", "Huron", "Michigan", "Ontario", "Superior"],
     "distractors": [["Champlain", "Huron", "Michigan", "Ontario", "Superior"],
                      ["Erie", "Huron", "Michigan", "Superior"],
                      ["Erie", "Great Salt Lake", "Huron", "Michigan", "Ontario", "Superior"]],
     "distractor_rationale": ["correct: Erie, Huron, Michigan, Ontario, Superior (HOMES)",
                               "swaps in Lake Champlain, not a Great Lake", "drops Lake Ontario",
                               "adds the Great Salt Lake, not a Great Lake"]},
    {"prompt": "the set of primary colors of light (the RGB model)",
     "correct": ["red", "green", "blue"],
     "distractors": [["red", "yellow", "blue"], ["red", "green", "blue", "yellow"], ["cyan", "magenta", "yellow"]],
     "distractor_rationale": ["correct: additive/light primaries are red, green, blue",
                               "confuses with pigment (subtractive) primaries red/yellow/blue",
                               "adds yellow, a secondary color in RGB", "lists CMY print primaries instead"]},
    {"prompt": "the set of planets in our solar system",
     "correct": ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"],
     "distractors": [["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"],
                      ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn"],
                      ["Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]],
     "distractor_rationale": ["correct: 8 planets per the 2006 IAU definition",
                               "wrongly includes Pluto, reclassified as a dwarf planet in 2006",
                               "drops Uranus and Neptune", "drops Mercury"]},
    {"prompt": "the set of primary colors of pigment (the RYB model)",
     "correct": ["red", "yellow", "blue"],
     "distractors": [["red", "green", "blue"], ["cyan", "magenta", "yellow"], ["red", "yellow", "blue", "green"]],
     "distractor_rationale": ["correct: traditional RYB pigment primaries", "confuses with RGB light primaries",
                               "lists CMY print primaries instead", "adds green, a secondary color in RYB"]},
]
b2_count = 0
for d in b2_data:
    def fmt(lst):
        return "{" + ", ".join(lst) + "}"
    options = [fmt(d["correct"])] + [fmt(x) for x in d["distractors"]]
    b2_count += 1
    items.append({
        "id": f"contemath-1.1-pilot-B2-{b2_count:02d}",
        "parent_id": None, "origin": "templated_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "1,2,5 (pattern)", "page": 13},
        "license": LICENSE, "question_type": "roster_construction", "item_format": "multiple_choice",
        "qti_support_level": "direct", "generation_strategy": "templated",
        "topic": "sets.roster_method.named_list", "learning_objective": "Represent sets in a variety of ways.",
        "difficulty": "intro", "bloom_level": "remember",
        "randomization_group": "sets.roster_method.named_list", "reuse_risk": "static_searchable",
        "stem": f"Which of the following correctly represents {d['prompt']} using the roster method?",
        "variables": {"prompt": d["prompt"]}, "generator_ref": None, "answer": options[0], "options": options,
        "distractor_rationale": d["distractor_rationale"],
        "feedback": {"correct": f"Correct: {options[0]}.",
                     "incorrect": "Check the option against the actual named list -- watch for "
                                  "omitted, added, or substituted members."},
        "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
        "notes": "Fact-based roster; reuse_risk=static_searchable -- treat as practice-only, not "
                 "exam-safe, until this pool is much deeper.",
        "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
    })

# ---------------------------------------------------------------------------
# Category C: static, hand-built (mirrors #13-20)
# ---------------------------------------------------------------------------
word = "mississippi"
vowels_in_word = sorted(set(ch for ch in word if ch in "aeiou"))

items.append({
    "id": "contemath-1.1-pilot-C-01", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "16 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "essay", "qti_support_level": "direct",
    "generation_strategy": "static", "topic": "sets.method_choice.infinite_setbuilder",
    "learning_objective": "Represent sets in a variety of ways.", "difficulty": "practice",
    "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.infinite", "reuse_risk": "static_low_risk",
    "stem": "Represent the set of all real numbers using set-builder notation, and explain in one or "
            "two sentences why the roster method (even with an ellipsis) is not a practical way to "
            "represent this set.",
    "variables": None, "generator_ref": None,
    "answer": "{x | x is a real number}. Explanation: the real numbers are uncountably infinite and "
              "have no natural 'next' element to establish a listing pattern, so no roster/ellipsis "
              "listing can represent them.",
    "options": None, "distractor_rationale": None, "feedback": {"correct": None, "incorrect": None},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "Essay, manually graded. Rubric: set-builder correct (1 pt), explanation references "
             "uncountability/no listing pattern (1 pt).",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

items.append({
    "id": "contemath-1.1-pilot-C-02", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "13 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.empty_set_trick",
    "learning_objective": "Represent well-defined sets and the empty set with proper set notation.",
    "difficulty": "practice", "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.empty_set_trick", "reuse_risk": "static_low_risk",
    "stem": "Represent the set of all triangles that are also perfect circles, symbolically.",
    "variables": None, "generator_ref": None, "answer": "∅", "options": None, "distractor_rationale": None,
    "feedback": {"correct": "Correct -- no shape is both a triangle and a circle, so this set has no "
                             "members: the empty set.",
                 "incorrect": "No shape can be both a triangle and a circle at once, so this set has "
                              "zero elements -- the empty set, written ∅ or { }."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "qti_support_level=requires_conversion: exact-match short answer needs an accepted-answers "
             "list (∅, {}, 'empty set', 'null set') configured on import.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

items.append({
    "id": "contemath-1.1-pilot-C-03", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "15 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.finite_word",
    "learning_objective": "Represent sets in a variety of ways.", "difficulty": "intro",
    "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.finite_word", "reuse_risk": "static_low_risk",
    "stem": f"Determine the best way to represent the set of vowels in the word \"{word}\", and write "
            f"the set using that method.",
    "variables": {"word": word, "vowels": vowels_in_word}, "generator_ref": None,
    "answer": "{" + ", ".join(vowels_in_word) + "}  (roster method -- small, specific, finite set of letters)",
    "options": None, "distractor_rationale": None,
    "feedback": {"correct": f"Correct: the only vowel in \"{word}\" is 'i', so the set is "
                             f"{{{', '.join(vowels_in_word)}}}. Roster method is appropriate because "
                             f"the set is small and finite.",
                 "incorrect": f"List each distinct vowel that appears in \"{word}\" once. Because the "
                              f"set is small and finite, the roster method is the appropriate choice."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "vowels_in_word computed programmatically from `word` to guarantee the answer key is "
             "correct even though this item is hand-authored.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

items.append({
    "id": "contemath-1.1-pilot-C-04", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "16 (pattern, cf. Example 1.5)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.infinite_roster",
    "learning_objective": "Represent sets in a variety of ways.", "difficulty": "practice",
    "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.infinite", "reuse_risk": "static_low_risk",
    "stem": "Determine the best way to represent the set of all integers, and write it using that method. "
            "Include an ellipsis.",
    "variables": None, "generator_ref": None,
    "answer": "{..., -2, -1, 0, 1, 2, ...}  (roster method with a leading AND trailing ellipsis, since "
              "the integers are unbounded in both directions)",
    "options": None, "distractor_rationale": None,
    "feedback": {"correct": "Correct -- the integers are infinite in both directions, so the roster "
                             "method needs an ellipsis at both ends: {..., -2, -1, 0, 1, 2, ...}.",
                 "incorrect": "The set of integers has no smallest or largest value, so unlike ℕ "
                              "(which only needs a trailing ellipsis), ℤ needs an ellipsis at BOTH ends."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "Pairs with C-01 to give the #13-20 block two different infinite-set representation "
             "strategies (set-builder vs. double-ended-ellipsis roster), plus C-02 (empty) and C-03 "
             "(finite) -- covers all four flavors an assignment spec might ask for.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

# ---------------------------------------------------------------------------
# B3: real-world-fact finite/infinite judgment (mirrors #47, #49, #50;
# genuine Category B -- correctness rests on whether a named real-world
# category is actually bounded, which is a fact to check, not a structural
# guarantee like A6 in gen_a_deep.py). The teaching point across this whole
# family: "large" is not the same as "infinite."
# ---------------------------------------------------------------------------
b3_data = [
    ("The set consisting of all jazz venues in New Orleans, Louisiana.", "finite",
     "Even though it isn't practical to list every venue, the number of jazz venues in a specific city "
     "at any given time is a fixed, bounded (if hard-to-pin-down) count -- large, but finite."),
    ("The set of all different types of cheeses.", "finite",
     "Cheese varieties are numerous, but new types are invented by people at a finite rate -- at any "
     "given moment, only finitely many types exist, even if the exact count is impractical to pin down."),
    ("The set of all words in Merriam-Webster's Collegiate Dictionary, Eleventh Edition, published in "
     "2020.", "finite",
     "A specific, published edition of a dictionary contains a fixed number of entries -- large, but "
     "countable and bounded."),
    ("The set of all grains of sand on Waikiki Beach.", "finite",
     "An astronomically large number, but still a fixed physical quantity at any given moment -- not "
     "unbounded."),
    ("The set of all stars visible to the naked eye from Earth on a clear night.", "finite",
     "Human vision has a limiting magnitude -- only a few thousand stars are bright enough to see "
     "without a telescope, a fixed and quite small number."),
    ("The set of all songs available on a major streaming platform right now.", "finite",
     "A streaming catalog is large, but it is added to song by song by real people -- at any instant it "
     "contains a specific, finite number of tracks."),
]
b3_count = 0
for desc, fi_answer, rationale in b3_data:
    b3_count += 1
    items.append({
        "id": f"contemath-1.1-pilot-B3-{b3_count:02d}", "parent_id": None, "origin": "templated_variant",
        "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "47,49,50 (pattern)", "page": 14}, "license": LICENSE,
        "question_type": "classification_2choice", "item_format": "multiple_choice",
        "qti_support_level": "direct", "generation_strategy": "templated",
        "topic": "sets.finite_infinite_classification.real_world_fact",
        "learning_objective": "Differentiate between finite and infinite sets.",
        "difficulty": "practice", "bloom_level": "evaluate",
        "randomization_group": "sets.finite_infinite_classification.real_world_fact",
        "reuse_risk": "static_low_risk",
        "stem": f"Classify the following set as finite or infinite:\n\n{desc}",
        "variables": {"description": desc}, "generator_ref": None, "answer": fi_answer,
        "options": ["finite", "infinite"],
        "distractor_rationale": ["correct" if fi_answer == "finite" else None,
                                  "correct" if fi_answer == "infinite" else None],
        "feedback": {"correct": rationale, "incorrect": rationale},
        "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
        "notes": "Genuine real-world-fact judgment -- 'large' is not the same as 'infinite'; needs a "
                 "human pass to confirm each category is truly bounded and that the rationale holds up.",
        "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
    })

# ---------------------------------------------------------------------------
# Category C additions: full-coverage pass, closing the remaining #13-20 gaps
# (#14, #15, #17, #18, #19, #20)
# ---------------------------------------------------------------------------
items.append({
    "id": "contemath-1.1-pilot-C-05", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "14 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.empty_set_trick",
    "learning_objective": "Represent well-defined sets and the empty set with proper set notation.",
    "difficulty": "practice", "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.empty_set_trick", "reuse_risk": "static_low_risk",
    "stem": "Represent the set of natural numbers divisible by zero, symbolically.",
    "variables": None, "generator_ref": None, "answer": "∅", "options": None, "distractor_rationale": None,
    "feedback": {"correct": "Correct -- division by zero is undefined, so no natural number satisfies "
                             "'divisible by zero.' The set has no members: the empty set.",
                 "incorrect": "No number can be divided by zero (it's undefined), so no natural number "
                              "qualifies -- this set has zero elements, the empty set, written ∅ or { }."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "Second empty-set-trick instance, pairs with C-02 -- this one hinges on division-by-zero "
             "being undefined rather than a geometric impossibility.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

items.append({
    "id": "contemath-1.1-pilot-C-06", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "17 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.empty_set_trick",
    "learning_objective": "Represent well-defined sets and the empty set with proper set notation.",
    "difficulty": "practice", "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.empty_set_trick", "reuse_risk": "static_low_risk",
    "stem": "Represent the set of polar bears that live in Antarctica, symbolically.",
    "variables": None, "generator_ref": None, "answer": "∅", "options": None, "distractor_rationale": None,
    "feedback": {"correct": "Correct -- polar bears are native to the Arctic (the opposite pole); none "
                             "live in Antarctica in the wild, so this set has no members.",
                 "incorrect": "Polar bears live in the Arctic, not Antarctica (that's penguins) -- no "
                              "polar bear meets this description, so the set is empty: ∅ or { }."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "Third empty-set-trick instance -- this one hinges on a real-world biogeography fact rather "
             "than pure logic or an undefined operation, so it needs a fact-check, not just a logic-check.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

items.append({
    "id": "contemath-1.1-pilot-C-07", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "18 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.large_finite",
    "learning_objective": "Represent sets in a variety of ways.", "difficulty": "practice",
    "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.large_finite", "reuse_risk": "static_low_risk",
    "stem": "Determine the best way to represent the set of all songs written by Prince, and write the "
            "set using that method.",
    "variables": None, "generator_ref": None,
    "answer": "{x | x is a song written by Prince}  (set-builder notation -- the set is well-defined and "
              "finite, but far too large to practically list by roster)",
    "options": None, "distractor_rationale": None,
    "feedback": {"correct": "Correct -- this is a well-defined, finite set (Prince wrote a specific, if "
                             "very large, number of songs), but roster is impractical at that scale, so "
                             "set-builder notation is the better choice.",
                 "incorrect": "The set is well-defined and finite, but the roster method breaks down "
                              "when a set is this large -- set-builder notation ({x | x is a song written "
                              "by Prince}) represents it far more practically."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "New topic: method-choice for large-but-finite named collections -- the mirror case of "
             "method_choice.finite_word (small finite -> roster); here large finite -> set-builder.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

items.append({
    "id": "contemath-1.1-pilot-C-08", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "19 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.large_finite",
    "learning_objective": "Represent sets in a variety of ways.", "difficulty": "practice",
    "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.large_finite", "reuse_risk": "static_low_risk",
    "stem": "Determine the best way to represent the set of children's books written and illustrated by "
            "Mo Willems, and write the set using that method.",
    "variables": None, "generator_ref": None,
    "answer": "{x | x is a children's book written and illustrated by Mo Willems}  (set-builder notation "
              "-- well-defined and finite, but impractical to roster in full)",
    "options": None, "distractor_rationale": None,
    "feedback": {"correct": "Correct -- Mo Willems has written and illustrated a specific, sizable "
                             "number of books; set-builder notation describes the set without requiring "
                             "a full list.",
                 "incorrect": "The set is well-defined and finite (a real author has a real, bounded "
                              "catalog), but it's large enough that set-builder notation is more "
                              "practical than a full roster."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "Second instance of the large-finite method-choice family, pairs with C-07.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

items.append({
    "id": "contemath-1.1-pilot-C-09", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "15 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.finite_word",
    "learning_objective": "Represent sets in a variety of ways.", "difficulty": "intro",
    "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.finite_word", "reuse_risk": "static_low_risk",
    "stem": "Determine the best way to represent the set of Mike and Carol's children on the TV show The "
            "Brady Bunch, and write the set using that method.",
    "variables": None, "generator_ref": None,
    "answer": "{Greg, Marcia, Peter, Jan, Bobby, Cindy}  (roster method -- small, specific, finite set of "
              "named children)",
    "options": None, "distractor_rationale": None,
    "feedback": {"correct": "Correct -- six named children is small and finite, so the roster method is "
                             "the practical choice: {Greg, Marcia, Peter, Jan, Bobby, Cindy}.",
                 "incorrect": "List each of the six Brady Bunch children by name. Because the set is "
                              "small and finite, roster method is the appropriate choice."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "Second instance of the small-finite-named-list method-choice family, pairs with C-03 "
             "(mississippi vowels). This is the item that used to be mislabeled as exercise 15 while "
             "actually testing a different word (mississippi) -- now the actual Brady Bunch content "
             "exists too.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

items.append({
    "id": "contemath-1.1-pilot-C-10", "parent_id": None, "origin": "static_variant", "derivation_type": "inspired_by",
    "source": {**SOURCE_BASE, "exercise_number": "20 (pattern)", "page": 13}, "license": LICENSE,
    "question_type": "open_response", "item_format": "short_answer", "qti_support_level": "requires_conversion",
    "generation_strategy": "static", "topic": "sets.method_choice.finite_word",
    "learning_objective": "Represent sets in a variety of ways.", "difficulty": "intro",
    "bloom_level": "evaluate",
    "randomization_group": "sets.method_choice.finite_word", "reuse_risk": "static_low_risk",
    "stem": "Determine the best way to represent the set of the seven colors commonly listed in a "
            "rainbow, and write the set using that method.",
    "variables": None, "generator_ref": None,
    "answer": "{red, orange, yellow, green, blue, indigo, violet}  (roster method -- small, specific, "
              "finite set of colors)",
    "options": None, "distractor_rationale": None,
    "feedback": {"correct": "Correct -- the traditional rainbow color list (ROYGBIV) is small and "
                             "finite, so roster method is appropriate: {red, orange, yellow, green, "
                             "blue, indigo, violet}.",
                 "incorrect": "List each of the seven traditionally named rainbow colors (ROYGBIV). "
                              "Because the set is small and finite, roster method is the appropriate "
                              "choice."},
    "media": [], "status": "needs_review", "verification_method": "llm_reviewed",
    "notes": "Third instance of the small-finite-named-list method-choice family.",
    "created_at": TODAY, "created_by": "pipeline:gen_bc_deep.py",
})

with open("category_bc_items.json", "w") as f:
    json.dump(items, f, indent=2)

from collections import Counter
print(f"Generated {len(items)} Category B/C items -> category_bc_items.json")
print("by generation_strategy:", dict(Counter(i["generation_strategy"] for i in items)))
print("by status:", dict(Counter(i["status"] for i in items)))
