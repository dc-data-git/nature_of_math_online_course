"""
Category A (algorithmic) generators for the Section 1.1 pilot bank -- DEEP PASS.

Goal of this pass: deep pools per skill (practice-quiz-ready, not just
homework-assembly-ready) plus two new templates that close real content
gaps found while mapping a hand-written assignment spec against the bank:
  - infinite-set cardinality (#27-36 block includes infinite sets; the old
    generator only ever produced finite integer answers)
  - set-builder notation construction (#7-12 block was entirely unbuilt)

Every answer here is still COMPUTED, not authored. Two things that read as
"content banks" below (CATEGORY_NOUNS, and the well-defined-set banks that
moved to gen_bc_deep.py) are NOT factual claims that could be wrong -- they
are grammatical slot-fillers for templates whose correctness is guaranteed
by the template's structure, not by looking anything up. See notes on each
generator for the specific argument.
"""
import random
import json

random.seed(7)

TODAY = "2026-07-03"
SOURCE_BASE = {"book": "OpenStax Contemporary Mathematics", "chapter": 1, "section": "1.1"}
LICENSE = {
    "type": "CC BY 4.0",
    "attribution_text": "Adapted from Contemporary Mathematics (OpenStax), Section 1.1, "
                         "available for free at openstax.org. Licensed under CC BY 4.0."
}

items = []


# ---------------------------------------------------------------------------
# A1: Cardinality of a finite roster set  (mirrors #27-32, #35-36)
# ---------------------------------------------------------------------------
THEMED_POOLS = {
    "kitchen tools": ["whisk", "spatula", "ladle", "peeler", "grater", "tongs", "colander", "rolling pin"],
    "planets": ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"],
    "board game pieces": ["hat", "car", "dog", "boot", "thimble", "wheelbarrow", "iron", "battleship"],
    "musical instruments": ["violin", "trumpet", "clarinet", "cello", "flute", "trombone", "tuba", "oboe"],
    "chess pieces": ["king", "queen", "rook", "bishop", "knight", "pawn"],
    "constellations": ["Orion", "Cassiopeia", "Ursa Major", "Lyra", "Cygnus", "Draco", "Perseus"],
}

a1_count = 0
for theme, pool in THEMED_POOLS.items():
    for _ in range(3):
        n = random.randint(min(4, len(pool)), min(7, len(pool)))
        chosen = random.sample(pool, n)
        a1_count += 1
        stem = f"Compute the cardinal value of the following set:\nP = {{{', '.join(chosen)}}}"
        items.append({
            "id": f"contemath-1.1-pilot-A1-{a1_count:03d}",
            "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
            "source": {**SOURCE_BASE, "exercise_number": "27-32,35-36 (pattern)", "page": 13},
            "license": LICENSE, "question_type": "cardinality_numeric", "item_format": "numeric_entry",
            "qti_support_level": "direct", "generation_strategy": "algorithmic",
            "topic": "sets.cardinality.finite", "learning_objective": "Compute the cardinal value of a set.",
            "difficulty": "intro", "bloom_level": "apply",
            "randomization_group": "sets.cardinality.finite", "reuse_risk": "fresh_each_use",
            "stem": stem, "variables": {"theme": theme, "n": n, "elements": chosen},
            "generator_ref": "gen_a_deep.py::A1_cardinality_finite", "answer": n, "options": None,
            "distractor_rationale": None,
            "feedback": {"correct": f"n(P) = {n}, since there are {n} distinct elements listed.",
                         "incorrect": "Count each distinct element once. Cardinality is the number of "
                                      "elements in the set, not the number of characters or duplicates."},
            "media": [], "status": "approved", "verification_method": "computed",
            "notes": "Answer computed directly from len(chosen); no factual/world-knowledge risk.",
            "created_at": TODAY, "created_by": "pipeline:gen_a_deep.py",
        })


# ---------------------------------------------------------------------------
# A1-INF: Cardinality of a countably infinite set  (closes gap: #27-36 also
# contains infinite sets, e.g. C = {n^3 | n in N}, S = {7n | n in N}; the
# original generator only ever produced finite integer answers)
#
# Any set defined as {f(n) | n in N} where f is injective on N is countably
# infinite, so n(set) = aleph-null. This is computed from the mathematical
# fact of injectivity for the specific f chosen, not asserted.
# ---------------------------------------------------------------------------
INF_FORMULA_KINDS = ["multiple", "power", "shift"]

a1inf_count = 0
for _ in range(12):
    kind = random.choice(INF_FORMULA_KINDS)
    if kind == "multiple":
        k = random.randint(2, 12)
        formula = f"{k}n"
        coefficient_trap = str(k)
    elif kind == "power":
        k = random.choice([2, 3])
        formula = f"n^{k}"
        coefficient_trap = str(k)
    else:
        k = random.randint(2, 20)
        formula = f"n + {k}"
        coefficient_trap = str(k)
    a1inf_count += 1
    stem = f"Let S = {{{formula} | n is a member of ℕ}}. What is the cardinal value of set S?"
    correct = "ℵ₀ (aleph-null) -- S is countably infinite"
    options = [correct, coefficient_trap,
               "0", "undefined -- cardinality only applies to finite sets"]
    random.shuffle(options)
    items.append({
        "id": f"contemath-1.1-pilot-A1INF-{a1inf_count:02d}",
        "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "33-34 (pattern)", "page": 13},
        "license": LICENSE, "question_type": "cardinality_numeric", "item_format": "multiple_choice",
        "qti_support_level": "direct", "generation_strategy": "algorithmic",
        "topic": "sets.cardinality.infinite", "learning_objective": "Differentiate between finite and infinite sets.",
        "difficulty": "challenge", "bloom_level": "analyze",
        "randomization_group": "sets.cardinality.infinite", "reuse_risk": "fresh_each_use",
        "stem": stem, "variables": {"formula": formula, "kind": kind, "k": k},
        "generator_ref": "gen_a_deep.py::A1inf_cardinality_infinite", "answer": correct, "options": options,
        "distractor_rationale": [
            "correct: f(n) is injective on N, so the image is countably infinite",
            "mistakes the formula's constant for the cardinality",
            "confuses infinite with empty",
            "wrongly claims cardinality doesn't apply to infinite sets -- the text explicitly "
            "defines aleph-null for exactly this case",
        ],
        "feedback": {
            "correct": f"Correct: n ↦ {formula} is injective on ℕ, so S has the same "
                       f"cardinality as ℕ itself -- countably infinite, ℵ₀.",
            "incorrect": "Because every natural number n produces a distinct value of the formula, "
                         "S has exactly as many elements as ℕ does -- countably infinite (ℵ₀), "
                         "not a finite count and not empty."
        },
        "media": [], "status": "approved", "verification_method": "computed",
        "notes": "Correctness follows from injectivity of the chosen formula on N, which holds for "
                 "all three formula kinds used here by construction.",
        "created_at": TODAY, "created_by": "pipeline:gen_a_deep.py",
    })


# ---------------------------------------------------------------------------
# A2: Equal / Equivalent / Neither  (mirrors #37-44)
# ---------------------------------------------------------------------------
ELEMENT_POOLS = [
    ["red", "orange", "yellow", "green", "blue", "purple"],
    ["circle", "square", "triangle", "hexagon", "pentagon", "octagon"],
    ["spring", "summer", "fall", "winter"],
    ["north", "south", "east", "west"],
    ["alpha", "beta", "gamma", "delta", "epsilon"],
    ["hydrogen", "helium", "lithium", "carbon", "oxygen", "neon"],
    ["soprano", "alto", "tenor", "bass"],
]
RELATIONSHIPS = ["equal", "equivalent", "neither"]


def make_equal_equivalent_item(idx, relationship):
    pool = random.choice(ELEMENT_POOLS)
    n = random.randint(3, min(5, len(pool)))
    set_a = random.sample(pool, n)
    if relationship == "equal":
        set_b = set_a[:]
        random.shuffle(set_b)
    elif relationship == "equivalent":
        other_pool = random.choice([p for p in ELEMENT_POOLS if p != pool])
        set_b = random.sample(other_pool, n)
    else:
        other_pool = random.choice([p for p in ELEMENT_POOLS if p != pool])
        m = n
        while m == n:
            m = random.randint(2, min(6, len(other_pool)))
        set_b = random.sample(other_pool, m)

    same_elements = set(set_a) == set(set_b)
    same_cardinality = len(set_a) == len(set_b)
    correct = "equal" if same_elements else ("equivalent" if same_cardinality else "neither")

    stem = (f"Determine whether set A and set B are equal, equivalent, or neither.\n\n"
            f"A = {{{', '.join(set_a)}}}\nB = {{{', '.join(set_b)}}}")
    return {
        "id": f"contemath-1.1-pilot-A2-{idx:03d}",
        "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "37-44 (pattern)", "page": 14},
        "license": LICENSE, "question_type": "classification_3choice", "item_format": "multiple_choice",
        "qti_support_level": "direct", "generation_strategy": "algorithmic",
        "topic": "sets.equal_equivalent", "learning_objective": "Differentiate between equal and equivalent sets.",
        "difficulty": "practice", "bloom_level": "analyze",
        "randomization_group": "sets.equal_equivalent.classification",
        "reuse_risk": "fresh_each_use", "stem": stem, "variables": {"set_a": set_a, "set_b": set_b},
        "generator_ref": "gen_a_deep.py::A2_equal_equivalent_neither", "answer": correct,
        "options": ["equal", "equivalent", "neither"],
        "distractor_rationale": ["equal" if correct != "equal" else None,
                                  "equivalent" if correct != "equivalent" else None,
                                  "neither" if correct != "neither" else None],
        "feedback": {"correct": f"Correct: the sets are {correct}.",
                     "incorrect": "Compare elements first (equal requires identical membership), "
                                  "then compare cardinality (equivalent requires the same count "
                                  "with different elements)."},
        "media": [], "status": "approved", "verification_method": "computed",
        "notes": "Label is derived from actual set comparison, not the intended relationship.",
        "created_at": TODAY, "created_by": "pipeline:gen_a_deep.py",
    }


for i, rel in enumerate(RELATIONSHIPS * 5, start=1):  # 5 of each relationship = 15 items
    items.append(make_equal_equivalent_item(i, rel))


# ---------------------------------------------------------------------------
# A3: Roster range with boundary-error distractors (mirrors #3, #4, #6)
# Six boundary-language templates, three instances each = 18 items.
# ---------------------------------------------------------------------------
def roster_closed(nums):
    if len(nums) <= 4:
        return "{" + ", ".join(str(n) for n in nums) + "}"
    return "{" + f"{nums[0]}, {nums[1]}, {nums[2]}, ..., {nums[-1]}" + "}"


def roster_open_above(start):
    return "{" + f"{start}, {start + 1}, {start + 2}, ..." + "}"


def roster_open_below(end):
    return "{..., " + f"{end - 2}, {end - 1}, {end}" + "}"


BOUNDARY_TEMPLATES = ["through_inclusive", "strictly_between", "greater_than",
                       "less_than", "at_least", "at_most"]

a3_count = 0
for rep in range(3):
    for template in BOUNDARY_TEMPLATES:
        a3_count += 1
        if template == "through_inclusive":
            a = random.randint(1, 40); b = a + random.randint(6, 15)
            stem = f"Which of the following correctly represents the set of natural numbers from {a} through {b}, inclusive, using the roster method?"
            correct = roster_closed(list(range(a, b + 1)))
            opts = [correct, roster_closed(list(range(a + 1, b))),
                    roster_closed(list(range(a + 1, b + 1))), roster_closed(list(range(a, b)))]
            rationale = ["correct: inclusive of both endpoints", "excludes both endpoints",
                         "excludes the lower endpoint only", "excludes the upper endpoint only"]
            fb_correct = f"Correct: {correct} includes both {a} and {b}."
            fb_incorrect = "'From A through B, inclusive' means both endpoints belong to the set."
            variables = {"a": a, "b": b}
        elif template == "strictly_between":
            a = random.randint(1, 40); b = a + random.randint(8, 16)
            stem = f"Which of the following correctly represents the set of natural numbers strictly between {a} and {b}, using the roster method?"
            correct = roster_closed(list(range(a + 1, b)))
            opts = [correct, roster_closed(list(range(a, b + 1))),
                    roster_closed(list(range(a, b))), roster_closed(list(range(a + 1, b + 1)))]
            rationale = ["correct: excludes both endpoints ('strictly')", "wrongly includes both endpoints",
                         "wrongly includes the lower endpoint", "wrongly includes the upper endpoint"]
            fb_correct = f"Correct: 'strictly between' excludes both {a} and {b}, so the set starts at {a+1} and ends at {b-1}."
            fb_incorrect = "'Strictly between A and B' excludes both endpoints -- neither A nor B belongs to the set."
            variables = {"a": a, "b": b}
        elif template == "greater_than":
            n = random.randint(1, 40)
            stem = f"Which of the following correctly represents the set of natural numbers greater than {n}, using the roster method?"
            correct = roster_open_above(n + 1)
            opts = [correct, roster_open_above(n), roster_open_above(n + 2), roster_open_below(n)]
            rationale = ["correct: excludes n, starts at n+1", "wrongly includes n", "wrongly skips n+1",
                         "wrong direction (this is 'less than', not 'greater than')"]
            fb_correct = f"Correct: 'greater than {n}' excludes {n} itself, so the set starts at {n+1} and continues without bound."
            fb_incorrect = f"'Greater than {n}' means {n} itself is NOT included, and the set continues upward without end."
            variables = {"n": n}
        elif template == "less_than":
            n = random.randint(5, 40)
            stem = f"Which of the following correctly represents the set of natural numbers less than {n}, using the roster method?"
            correct = roster_closed(list(range(1, n)))
            opts = [correct, roster_closed(list(range(1, n + 1))), roster_closed(list(range(2, n))), roster_open_above(n)]
            rationale = ["correct: excludes n, starts at 1 (smallest natural number)", "wrongly includes n",
                         "wrongly excludes 1", "wrong direction (this is 'greater than', not 'less than')"]
            fb_correct = f"Correct: 'less than {n}' excludes {n} itself, and natural numbers start at 1, so the set is {correct}."
            fb_incorrect = f"'Less than {n}' means {n} itself is NOT included. Natural numbers start at 1, not 0."
            variables = {"n": n}
        elif template == "at_least":
            n = random.randint(1, 40)
            stem = f"Which of the following correctly represents the set of natural numbers that are at least {n}, using the roster method?"
            correct = roster_open_above(n)
            opts = [correct, roster_open_above(n + 1),
                    roster_open_above(n - 1) if n > 1 else roster_open_above(n + 2), roster_open_below(n)]
            rationale = ["correct: 'at least n' includes n itself", "wrongly excludes n", "off-by-one start", "wrong direction"]
            fb_correct = f"Correct: 'at least {n}' includes {n} itself, so the set starts at {n} and continues without bound."
            fb_incorrect = f"'At least {n}' means {n} itself IS included (at least = greater than or equal to)."
            variables = {"n": n}
        else:
            n = random.randint(5, 40)
            stem = f"Which of the following correctly represents the set of natural numbers that are at most {n}, using the roster method?"
            correct = roster_closed(list(range(1, n + 1)))
            opts = [correct, roster_closed(list(range(1, n))), roster_closed(list(range(2, n + 1))), roster_open_above(n)]
            rationale = ["correct: 'at most n' includes n itself, starts at 1", "wrongly excludes n",
                         "wrongly excludes 1", "wrong direction"]
            fb_correct = f"Correct: 'at most {n}' includes {n} itself, and natural numbers start at 1, so the set is {correct}."
            fb_incorrect = f"'At most {n}' means {n} itself IS included (at most = less than or equal to). Natural numbers start at 1."
            variables = {"n": n}

        if len(set(opts)) < 4:
            continue  # skip rare collision, don't crash a deep batch over one bad draw
        shuffled = opts[:]
        random.shuffle(shuffled)
        items.append({
            "id": f"contemath-1.1-pilot-A3-{template}-{rep+1}",
            "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
            "source": {**SOURCE_BASE, "exercise_number": "3,4,6 (pattern)", "page": 13},
            "license": LICENSE, "question_type": "roster_construction", "item_format": "multiple_choice",
            "qti_support_level": "direct", "generation_strategy": "algorithmic",
            "topic": "sets.roster_method.range", "learning_objective": "Represent sets in a variety of ways.",
            "difficulty": "intro", "bloom_level": "understand",
            "randomization_group": "sets.roster_method.range", "reuse_risk": "fresh_each_use",
            "stem": stem, "variables": {**variables, "boundary_template": template},
            "generator_ref": "gen_a_deep.py::A3_roster_range_mc", "answer": opts[0], "options": shuffled,
            "distractor_rationale": rationale, "feedback": {"correct": fb_correct, "incorrect": fb_incorrect},
            "media": [], "status": "approved", "verification_method": "computed",
            "notes": "One of six boundary-language templates so phrasing varies, not just the numbers.",
            "created_at": TODAY, "created_by": "pipeline:gen_a_deep.py",
        })


# ---------------------------------------------------------------------------
# A4 (NEW): Set-builder notation for "multiples of k greater than zero"
# (closes part of the #7-12 gap -- mirrors #9, #10)
# ---------------------------------------------------------------------------
a4_count = 0
for _ in range(15):
    k = random.randint(2, 12)
    a4_count += 1
    stem = f"Which of the following correctly represents the set of all integer multiples of {k} that are greater than zero, using set-builder notation?"
    correct = f"{{{k}n | n is a member of ℕ}}"
    opts = [correct,
            f"{{n{k} | n is a member of ℕ}}",          # swapped operator (juxtaposition vs multiplication)
            f"{{{k}n | n is an element of ℤ}}",          # wrong domain -- allows negatives/zero
            f"{{{k}n + 1 | n is a member of ℕ}}"]        # wrong formula entirely
    random.shuffle(opts)
    items.append({
        "id": f"contemath-1.1-pilot-A4-{a4_count:02d}",
        "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "9,10 (pattern)", "page": 13},
        "license": LICENSE, "question_type": "set_builder_construction", "item_format": "multiple_choice",
        "qti_support_level": "direct", "generation_strategy": "algorithmic",
        "topic": "sets.set_builder_notation.multiples", "learning_objective": "Represent sets in a variety of ways.",
        "difficulty": "practice", "bloom_level": "apply",
        "randomization_group": "sets.set_builder_notation.multiples",
        "reuse_risk": "fresh_each_use", "stem": stem, "variables": {"k": k},
        "generator_ref": "gen_a_deep.py::A4_setbuilder_multiples", "answer": correct, "options": opts,
        "distractor_rationale": [
            "correct: kn for n in N is exactly the positive multiples of k",
            "swapped multiplication for exponent-style juxtaposition -- not valid notation",
            f"uses ℤ instead of ℕ, which wrongly allows zero and negative multiples",
            "wrong formula -- shifts every value by 1, no longer 'multiples of k'",
        ],
        "feedback": {
            "correct": f"Correct: {{{k}n | n is a member of ℕ}} generates exactly {k}, {2*k}, {3*k}, ... -- "
                       f"the positive multiples of {k}.",
            "incorrect": f"'Multiples of {k} greater than zero' means {k} times each natural number "
                         f"starting at 1 -- domain must be ℕ (not ℤ, which would include 0 and negatives)."
        },
        "media": [], "status": "approved", "verification_method": "computed",
        "notes": "Correct answer and all distractors are computed from k; no factual content.",
        "created_at": TODAY, "created_by": "pipeline:gen_a_deep.py",
    })


# ---------------------------------------------------------------------------
# A5 (NEW): Set-builder notation for a described category
# (closes rest of the #7-12 gap -- mirrors #7, #8, #11, #12)
#
# CATEGORY_NOUNS below is a one-time-reviewed grammar bank, not a set of
# factual claims. The template "the set of all X" -> "{x | x is X}" is
# correct by construction for any X in the bank -- we are never asserting
# anything about lizards or elements, only that the set-builder notation
# correctly restates the English description. That's why this is Category
# A (computed) rather than Category B (each entry would need fact-checking
# only if the *content* of the category were in question).
# ---------------------------------------------------------------------------
CATEGORY_NOUNS = [
    ("types of lizards", "a type of lizard"),
    ("stars in the universe", "a star in the universe"),
    ("edible plants", "an edible plant"),
    ("even numbers", "an even number"),
    ("prime numbers", "a prime number"),
    ("types of clouds", "a type of cloud"),
    ("chemical elements", "a chemical element"),
    ("constellations", "a constellation"),
    ("programming languages", "a programming language"),
    ("types of cheese", "a type of cheese"),
    ("U.S. state capitals", "a U.S. state capital"),
    ("musical scales", "a musical scale"),
    ("types of polygons", "a type of polygon"),
    ("types of tea", "a type of tea"),
    ("moons of Jupiter", "a moon of Jupiter"),
]

a5_count = 0
for plural_desc, singular_predicate in CATEGORY_NOUNS:
    a5_count += 1
    stem = f"Using set-builder notation, write the set of all {plural_desc}."
    correct = f"{{x | x is {singular_predicate}}}"
    opts = [correct,
            f"{{x | x = {plural_desc}}}",              # malformed: '=' instead of 'is'
            f"{{y | x is {singular_predicate}}}",       # mismatched bound variable
            "{" + plural_desc + "}"]                    # roster-style, not set-builder at all
    random.shuffle(opts)
    items.append({
        "id": f"contemath-1.1-pilot-A5-{a5_count:02d}",
        "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "7,8,11,12 (pattern)", "page": 13},
        "license": LICENSE, "question_type": "set_builder_construction", "item_format": "multiple_choice",
        "qti_support_level": "direct", "generation_strategy": "algorithmic",
        "topic": "sets.set_builder_notation.descriptive", "learning_objective": "Represent sets in a variety of ways.",
        "difficulty": "intro", "bloom_level": "understand",
        "randomization_group": "sets.set_builder_notation.descriptive",
        "reuse_risk": "static_low_risk", "stem": stem, "variables": {"plural_desc": plural_desc},
        "generator_ref": "gen_a_deep.py::A5_setbuilder_descriptive", "answer": correct, "options": opts,
        "distractor_rationale": [
            "correct: '{x | x is <predicate>}' restates the English description in set-builder form",
            "malformed notation -- uses '=' where the description needs 'is'",
            "mismatched bound variable between the left and right side of the bar",
            "roster-style braces around the description -- conflates roster and set-builder methods",
        ],
        "feedback": {
            "correct": f"Correct: {{x | x is {singular_predicate}}} reads as 'the set of all x such that "
                       f"x is {singular_predicate}' -- exactly the given description.",
            "incorrect": "Set-builder notation needs the form {x | x is <predicate>} -- the bound "
                         "variable must match on both sides, and 'is' (not '=') connects it to the predicate."
        },
        "media": [], "status": "approved", "verification_method": "computed",
        "notes": "reuse_risk=static_low_risk because the noun bank is finite (15 entries) and could "
                 "repeat within a large class; grow CATEGORY_NOUNS if that becomes a problem.",
        "created_at": TODAY, "created_by": "pipeline:gen_a_deep.py",
    })


# ---------------------------------------------------------------------------
# A6 (NEW): Finite vs. infinite classification -- direct test of LO4
# (closes #45, #46, #48)
#
# Distinct skill from A1/A1-INF: those compute the CARDINAL VALUE of a set
# (LO3). This tests only whether a description names a finite or infinite
# set (LO4) -- a strictly simpler binary judgment, and one the source
# exercises test on its own (#45-50) without ever asking for a cardinality
# number. Every entry below is finite/infinite by a structural mathematical
# fact (a named number system's cardinality, or "any explicit roster/bounded
# count is finite," or "any set generated by n -> f(n) for all n in N is
# infinite"), never a fact that could be individually wrong -- so this stays
# Category A. #47/#49/#50 are the real-world-fact cousins of this family and
# stay Category B -- see gen_bc_deep.py::B3.
# ---------------------------------------------------------------------------
FIXED_FI_ITEMS = [
    ("the set of natural numbers, ℕ", "infinite",
     "ℕ has no largest element -- you can always add one more -- so it is infinite."),
    ("the set of integers, ℤ", "infinite",
     "ℤ is unbounded in both directions, so it is infinite."),
    ("the set of rational numbers, ℚ", "infinite",
     "ℚ contains ℤ as a subset, and ℤ is infinite, so ℚ is infinite."),
    ("the set of real numbers, ℝ", "infinite",
     "ℝ contains ℚ as a subset, and ℚ is infinite, so ℝ is infinite."),
    ("the empty set, ∅", "finite",
     "n(∅) = 0, and 0 is a whole number, so the empty set is finite."),
    ("the set of even natural numbers", "infinite",
     "For every even number you name, the next one (add 2) is also even -- the pattern never ends."),
    ("the set of odd natural numbers", "infinite",
     "For every odd number you name, the next one (add 2) is also odd -- the pattern never ends."),
    ("the set of prime numbers", "infinite",
     "There is no largest prime number -- a classical result (Euclid's proof) guarantees infinitely "
     "many primes."),
]

a6_count = 0
for desc, fi_answer, explanation in FIXED_FI_ITEMS:
    a6_count += 1
    items.append({
        "id": f"contemath-1.1-pilot-A6-{a6_count:02d}",
        "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "45,46,48 (pattern)", "page": 14},
        "license": LICENSE, "question_type": "classification_2choice", "item_format": "multiple_choice",
        "qti_support_level": "direct", "generation_strategy": "algorithmic",
        "topic": "sets.finite_infinite_classification.objective",
        "learning_objective": "Differentiate between finite and infinite sets.",
        "difficulty": "intro", "bloom_level": "understand",
        "randomization_group": "sets.finite_infinite_classification.objective",
        "reuse_risk": "static_low_risk",
        "stem": f"Classify {desc} as finite or infinite.",
        "variables": {"description": desc}, "generator_ref": "gen_a_deep.py::A6_finite_infinite_fixed",
        "answer": fi_answer, "options": ["finite", "infinite"],
        "distractor_rationale": ["correct" if fi_answer == "finite" else None,
                                  "correct" if fi_answer == "infinite" else None],
        "feedback": {"correct": explanation, "incorrect": explanation},
        "media": [], "status": "approved", "verification_method": "computed",
        "notes": "Finite/infinite status is a fixed structural fact about a named number system, "
                 "not a claim that could be individually wrong.",
        "created_at": TODAY, "created_by": "pipeline:gen_a_deep.py",
    })

# Dynamic templates: parameterized but still structurally guaranteed.
a6d_count = 0
for _ in range(12):
    kind = random.choice(["multiples_infinite", "less_than_finite", "factors_finite", "roster_finite"])
    if kind == "multiples_infinite":
        k = random.randint(2, 15)
        desc = f"the set of all positive integer multiples of {k}"
        fi_answer = "infinite"
        explanation = f"For every multiple of {k} you name, adding {k} again gives another one -- the pattern never ends."
    elif kind == "less_than_finite":
        n = random.randint(5, 200)
        desc = f"the set of natural numbers less than {n}"
        fi_answer = "finite"
        explanation = f"There are exactly {n - 1} natural numbers less than {n} -- a fixed, countable amount."
    elif kind == "factors_finite":
        n = random.randint(12, 96)
        desc = f"the set of positive factors of {n}"
        fi_answer = "finite"
        explanation = f"Every positive integer has a fixed, limited number of factors no larger than itself -- {n} has only finitely many."
    else:
        pool = random.choice(list(THEMED_POOLS.values()))
        n = random.randint(3, min(6, len(pool)))
        chosen = random.sample(pool, n)
        desc = "the set {" + ", ".join(chosen) + "}"
        fi_answer = "finite"
        explanation = "Any set written out completely as an explicit roster has a fixed, countable number of elements."
    a6d_count += 1
    items.append({
        "id": f"contemath-1.1-pilot-A6D-{a6d_count:02d}",
        "parent_id": None, "origin": "algorithmic_variant", "derivation_type": "inspired_by",
        "source": {**SOURCE_BASE, "exercise_number": "45,46,48 (pattern)", "page": 14},
        "license": LICENSE, "question_type": "classification_2choice", "item_format": "multiple_choice",
        "qti_support_level": "direct", "generation_strategy": "algorithmic",
        "topic": "sets.finite_infinite_classification.objective",
        "learning_objective": "Differentiate between finite and infinite sets.",
        "difficulty": "intro", "bloom_level": "understand",
        "randomization_group": "sets.finite_infinite_classification.objective",
        "reuse_risk": "fresh_each_use",
        "stem": f"Classify {desc} as finite or infinite.",
        "variables": {"description": desc, "kind": kind},
        "generator_ref": "gen_a_deep.py::A6_finite_infinite_dynamic",
        "answer": fi_answer, "options": ["finite", "infinite"],
        "distractor_rationale": ["correct" if fi_answer == "finite" else None,
                                  "correct" if fi_answer == "infinite" else None],
        "feedback": {"correct": explanation, "incorrect": explanation},
        "media": [], "status": "approved", "verification_method": "computed",
        "notes": "Finite/infinite status follows from the construction (explicit roster, bounded count, "
                 "or an unbounded generating pattern), not an assertable fact.",
        "created_at": TODAY, "created_by": "pipeline:gen_a_deep.py",
    })


with open("category_a_items.json", "w") as f:
    json.dump(items, f, indent=2)

from collections import Counter
print(f"Generated {len(items)} Category A items -> category_a_items.json")
print("by topic:", dict(Counter(i["topic"] for i in items)))
