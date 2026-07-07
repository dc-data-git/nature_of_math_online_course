# Problem Bank Pipeline — Process Specification

Purpose: turn textbook exercises into a reusable, structured problem bank (JSON), from which QTI packages (and later, print tests/quizzes) are rendered. The JSON is the product of this pipeline. QTI is one consumer of it, built in a separate downstream step not covered here.

Piloted against: OpenStax *Contemporary Mathematics*, Section 1.1 "Basic Set Concepts" (CC BY 4.0), 50 end-of-section exercises.

---

## 1. Stages

1. Extraction — pull raw exercise text/images from source PDF.
2. Classification — tag each problem on two axes (question type, generation strategy).
3. Generation — produce the original item plus N variants, per the strategy assigned.
4. Verification — confirm every answer key is correct, and that a small sample has survived an actual Canvas import, before an item is marked usable.
5. Storage — write everything to the canonical JSON, one file per section.
6. (Downstream, separate process) — render JSON to QTI, validate via Canvas sandbox import.

---

## 2. Stage 1: Extraction

- Source each problem's exact page/exercise number from the section PDF. Keep the original wording verbatim in the record (`source.original_text`) even after variants are generated — needed for licensing attribution and for spot-checking later.
- Note the license on the source material up front (e.g., OpenStax = CC BY 4.0). Every JSON file carries an `attribution` block; do not skip this even for internal use.
- If a problem depends on a figure/image, note that now — it changes generation strategy (usually forces Category C, see below).

## 3. Stage 2: Classification

Every problem gets two independent tags.

**Axis A — Question type** (drives QTI item format later): roster construction, set-builder construction, numeric (cardinality/computed value), 2-choice classification (true/false or yes/no judgment), 3-choice classification (e.g., equal/equivalent/neither), open response (short answer or essay).

**Axis B — Generation strategy.** Apply this decision order; stop at the first match:

1. **Algorithmic (Category A).** The problem instance and its correct answer can both be produced by a formula or short script, with no factual/world knowledge involved. Test: "could a Python function generate infinite correct variants and grade them with zero human judgment?" If yes → Algorithmic. This includes templates whose correctness follows from *sentence structure* rather than *sentence content* — see the reclassification finding in Section 9.
   Examples from 1.1: cardinality of a given roster or set-builder pattern (#27–36, including the infinite cases), equal/equivalent/neither given two constructed sets (#37–44), number-range or multiples-of-N templates (#3, #4, #6, #9, #10), descriptive set-builder notation (#7, #8, #11, #12), well-defined-set judgments built on objective math properties or opinion-based superlatives (#21–26).

2. **Templated content-swap (Category B).** The problem follows a fixed linguistic/structural pattern, but correctness depends on a real-world fact that must be authored or looked up — it can't be computed. Test: "is the pattern reusable, but does each instance need a human- or LLM-authored fact checked for accuracy?" If yes → Templated.
   Examples: named-list roster problems (#1, #2, #5 — continents, Great Lakes, primary colors), well-defined-set judgments built on a genuine real-world fact (#21–26, e.g. "states that border the Pacific"), finite/infinite judgments on named real-world collections (#47, #49, #50).

3. **Static, hand-built (Category C).** Everything else: multiple valid correct forms, subjective/"best representation" judgment calls, niche cultural knowledge, or figure-dependent problems. Do not attempt to mass-generate these. Draft a small fixed set of equivalents (LLM-assisted is fine) and put every one through human review.
   Examples: #13–20 ("represent using the method of your choice" — includes trick cases like "squares that are circles").

Output of this stage, before any generation happens: a classification worksheet (can be a JSON or CSV) listing every source problem with its two tags. Review this worksheet before proceeding — it's the cheapest point to catch a miscategorized problem.

## 4. Stage 3: Generation

**Category A (algorithmic).** Write one generator per template: input constraints/ranges, a function that renders the stem from the inputs, and a function that computes the answer (and, for classification types, computes which of the fixed answer options is correct). No LLM call is needed for the answer key — only optionally for varying the surface wording of the stem. Target: generate as many variants as needed; cost is near-zero and correctness is guaranteed by construction. **A generator must vary structure/phrasing, not just numeric slot-fills — see Section 8.**

**Category B (templated).** Maintain a curated content bank per template (e.g., a list of enumerable named-item categories with their correct roster, or a list of real-world-fact category descriptions for well-defined-set problems). An LLM may propose candidate entries, but every entry starts as `status: needs_review` and must be confirmed accurate before use. Volume here should stay modest (5–15 variants per source problem) since each one carries real review cost.

**Category C (static).** LLM drafts full equivalent problems, matching the pedagogical intent (not just surface wording) of the original. Every item requires human review before it is marked usable. Lowest volume, highest touch — 2–4 variants per source problem is plenty.

**Distractor rules (multiple-choice items only).** For 3-choice classification items (equal/equivalent/neither), the three category labels themselves serve as the answer options — no separate distractor authoring needed, just make sure the generated instance has an unambiguous correct category. For 2-choice items, no distractors needed (true/false). For any free-generated multiple-choice item, distractors should encode a specific, named misconception (e.g., "confuses equal with equivalent," "mistakes the formula's constant for the cardinality") — tag the misconception in the JSON so distractor quality can be audited later.

## 5. Stage 4: Verification

- Category A items: correctness is guaranteed by the generator (`verification_method: computed`); spot-check a random sample (~10%) per batch rather than every item, then move straight to `approved`.
- Category B and C items: an LLM check (`verification_method: llm_reviewed`) is a filter, not a clearance — it can move an item from `draft` to `needs_review`, but never directly to `approved`. A human reviewer (`verification_method: human_reviewed`) is a required second gate before `status` becomes `approved`. Never let a Category B/C item reach QTI generation while still `needs_review`.
- Flag (don't silently resolve) any item where the "correct" classification is itself debatable (e.g., is "the set of all cheese types" really finite?). Leave a `notes` field explaining the judgment call so a human signs off explicitly.
- Passing schema validation is not the same as being usable. Regardless of category, an item isn't truly production-ready until it has survived the Canvas import gate described in Section 7 — QTI-format correctness can only be confirmed by an actual import, not by inspection.

## 6. Stage 5: JSON Schema & Storage

One JSON file per book section, containing an array of problem objects. Proposed fields per object:

```
id                    string   e.g. "contemath-1.1-ex027" (original) or "contemath-1.1-ex027-v03" (variant)
parent_id             string   null for originals; id of source problem for variants
origin                enum     original | algorithmic_variant | templated_variant | static_variant
derivation_type       enum     (variants only) directly_adapted | inspired_by | independently_authored
source                object   { book, chapter, section, exercise_number, page }
license               object   { type: "CC BY 4.0", attribution_text }
question_type         enum     roster_construction | set_builder_construction | cardinality_numeric |
                                classification_2choice | classification_3choice | open_response
item_format           enum     multiple_choice | true_false | numeric_entry | short_answer | essay
qti_support_level     enum     direct | requires_conversion | manual_rebuild | not_qti_suitable
generation_strategy   enum     algorithmic | templated | static
topic                 string   e.g. "sets.cardinality.finite"
learning_objective    string   ties back to the section's stated learning objectives
difficulty            enum     intro | practice | challenge
bloom_level            enum     remember | understand | apply | analyze | evaluate | create — the
                                revised Bloom's-taxonomy level of the cognitive verb the item family
                                tests (see Section 12). Rated per topic/randomization_group, not per
                                item — a family sharing a group is doing the same cognitive task.
                                Difficulty and Bloom level are related but not identical: difficulty is
                                still a separate field, and the two can disagree (see Section 12).
randomization_group   string   clusters items that shouldn't co-occur in one random draw because they
                                test the identical skill — includes variants of one problem (already
                                linked via parent_id) but also distinct source problems testing the
                                same idea (e.g., #9 and #10, both "multiples of N" set-builder)
reuse_risk            enum     fresh_each_use | static_low_risk | static_searchable — whether the
                                answer is regenerated each serving, and how guessable/searchable it is
                                if not (informs whether an item is exam-safe vs. practice-only)
stem                  string   problem text; {placeholders} for algorithmic variables
variables             object   (algorithmic only) name/type/range/constraints per variable
generator_ref         string   (algorithmic only) name/id of the generator function used
answer                value    correct answer or answer key
options                array   (multiple_choice only) answer choices
distractor_rationale  array    (multiple_choice only) misconception each distractor encodes
feedback              object   { correct, incorrect } explanation text
media                 array    image references, if any
status                enum     draft | needs_review | approved | retired
verification_method   enum     computed | llm_reviewed | human_reviewed
notes                 string   free text, esp. for debatable judgment calls
created_at / created_by
```

Storage layout:

```
/source/{book-slug}/{chapter}.pdf                 original PDFs
/bank/{book-slug}/{chapter}/{section}.json         problem objects for that section
/bank/schema/problem.schema.json                   JSON Schema for the object above
/qti/{book-slug}/{chapter}/{section}.zip           downstream QTI output (separate process)
```

## 7. Pilot procedure

Do not build out the full schema and generator ecosystem before proving Canvas will actually accept the output — that's the main risk in this process. Run in two layers.

**Pilot 1 — minimal viable bank.** 10–15 items from Section 1.1, weighted toward Category A/B so answer keys are cheap to trust. Cover at least one of each `item_format` in scope (multiple_choice, true_false, numeric_entry). Populate only the fields needed to render an item — skip `randomization_group`, `estimated_time`, elaborate `feedback`. Export to QTI, import into a Canvas sandbox course, and confirm items render correctly (math notation especially) and grade correctly. **Nothing proceeds past this point until it passes.** If Canvas mangles something (a format, MathML, a question type), that finding should change the schema before Pilot 2, not after.

**Pilot 2 — full schema, full section.** Once Pilot 1 clears, extend to the complete schema above, run Category A/B/C generation across all 50 exercises in 1.1, and test quiz-assembly behavior (random draws respecting `randomization_group`, feedback display, etc.).

Once Pilot 2 clears for one section, the mechanics are proven and later sections/chapters can reuse the process without re-validating Canvas/QTI behavior each time.

## 8. Findings from Pilot 1 (Section 1.1, 26 items)

Real findings from the first Canvas sandbox import, kept here so the next section doesn't re-discover them:

- **Parameterize structure, not just numbers.** An early version of the roster-range generator (Category A) fixed the boundary phrasing to "from A through B, inclusive" and only varied A and B. That quietly deleted the actual skill being tested — the source exercises vary the *boundary language* ("between," "greater than," "less than"), and translating that language into correct roster notation is the point. A generator that only swaps numeric values inside one fixed sentence isn't testing the same thing the original exercise family tested, even though it "looks" parameterized. When building a Category A generator, enumerate the distinct phrasing/structure variants the source exercises use and sample across them, not just the numbers inside one variant.
- **QTI feedback ident convention matters.** Canvas only shows `general_incorrect_fb` when an answer is wrong. An ident of `general_fb` is treated as "always show," so incorrect-answer feedback was appearing even on correct answers. Fixed in the QTI generator; worth remembering for any future hand-built QTI.
- **Numeric-entry display quirk (cosmetic, not a bug):** Canvas renders an exact-match numeric answer as "Between X and X" in the review screen. That's just how it displays a zero-width accepted range — not an error.
- **What worked on the first pass:** unicode symbols (∅) survived import and rendered correctly; case-insensitive short-answer matching worked; essay items correctly stayed ungraded; multi-line stems rendered with line breaks intact; all Category A (computed) items scored correctly against their own answer key on a full test run.

## 9. The real product: a problem-type library, not a fixed problem set

Clarified after the pilot: the JSON bank isn't "a set of questions for this chapter," it's a library of problem *types*, each with a deep pool of instances. An instructor (or whoever is designing a specific assignment) doesn't hand-pick items one at a time — they describe an assignment declaratively ("2 problems like the roster-range family, 4 problems from the method-choice family with at least one each of empty/finite/infinite set"), and that description is compiled against the bank by filtering on `topic`/`question_type`/tags. This is why depth matters more than breadth-once: a shallow pool can support one demo assignment; a deep pool supports both an assembled homework assignment *and* a retake-friendly practice quiz from the same underlying templates. The next artifact to formalize (not yet built) is an `assignment_spec` format — a short declarative file expressing "N items from topic X, with sub-constraints" — that compiles against the bank the same way a query compiles against a table.

**Reclassification finding: some "Category B" problems are actually Category A.** The well-defined-set judgment family (mirrors #21–26) originally looked like it needed per-item fact-checking. Looking closer, it splits into three genuinely different cases: (1) a category defined by an *objective mathematical property* ("prime," "even," "multiple of k") is well-defined by definition, regardless of which property or threshold is used — this is a structural guarantee, not a fact, so it's Category A; (2) a category defined by an *opinion-based superlative* ("most exciting," "best," "friendliest") is NOT well-defined regardless of the noun it's paired with — also a structural guarantee, also Category A; (3) a category defined by a *real-world fact* ("states that border the Pacific") genuinely does need a human fact-check, and stays Category B. The lesson: before assuming a problem family requires human review, check whether its correctness follows from the *shape* of the sentence rather than from any specific content inside it. Templates with word banks aren't automatically Category B — only the ones where the word bank's content could itself be wrong are.

## 10. Findings from the deep pass (122 items)

- **Two content gaps were found by mapping a real assignment spec against the bank, not by auditing the taxonomy.** The #7–12 (descriptive set-builder notation) and #27–36-infinite (aleph-null cardinality) families had no items at all until an instructor's hand-written assignment draft was checked line-by-line against what existed. Worth doing this check-against-a-real-spec exercise for every new section, rather than assuming the classification worksheet alone guarantees coverage.
- **Answer keys stop being hand-checkable past a few dozen items.** At 122 items, a per-item answer table is no longer a practical test artifact. Switched to a per-topic summary (one sample item + count + status per topic) with a spot-check recommendation, on the reasoning that every item in a topic runs through the same generator code path, so a working sample is strong evidence for the whole topic.
- **Infinite-set cardinality can't be `numeric_entry`.** The answer is ℵ₀, not an integer — this family had to be `multiple_choice` instead, with distractors targeting real misconceptions (mistaking the formula's constant for the cardinality, confusing infinite with empty, claiming cardinality "doesn't apply" to infinite sets).

## 11. Open parameters to set before running

- Target variant count per Category A/B/C problem. Deep-pass pilot used ~15–18 per Category A topic, 4–8 per reclassified-Category-A-via-word-bank topic, and kept genuine Category B/C topics at 3–5.
- Who performs the Category B/C human-review gate (Daniel, or someone else with a spot-check pass).
- Difficulty tagging scale and whether it's assigned per-problem or per-template.
- Which `reuse_risk` levels are acceptable for exam use vs. practice-only use.
- Format and location of the `assignment_spec` artifact once it's built (see Section 9).

## 12. Bloom's-taxonomy pass

Difficulty (`intro`/`practice`/`challenge`) turned out to be doing two jobs at once: signaling surface complexity and signaling cognitive demand, without a rubric for either. Added `bloom_level` as a second, independent field to separate them — rated using the revised Bloom's taxonomy (remember, understand, apply, analyze, evaluate, create), one level per topic/`randomization_group` rather than per item, using the same "rate the family, not the instance" logic already established for difficulty: ask what verb the whole family is asking the student to do, and let that verb pick the level.

**Where Bloom validated the existing difficulty tagging:** the six `sets.roster_method.range` boundary-language templates (through/inclusive, strictly between, greater than, less than, at least, at most) all share one Bloom level (`understand` — translate a described range into roster notation) despite their surface differences in phrasing and distractor logic. Difficulty had already rated all six `intro` uniformly; this confirms that was correct, not an oversight, because the cognitive operation truly doesn't change across the six.

**Where Bloom exposed a real mismatch:** the three `well_defined.*` topics and the `method_choice.*` family were all rated `intro`/`practice` on difficulty, but their actual verb is "judge whether a description meets a criterion" — `evaluate`, one of the two highest levels in the taxonomy. Rating these alongside roster-notation translation understated what they're actually asking a student to do. `difficulty` was deliberately left untouched (not overwritten from Bloom) pending a decision on how the two fields should relate going forward — that decision is still open.

Current Bloom distribution across the bank (see Section 13 for the full item count): `remember` (named-list recall), `understand` (translate/represent — set-builder and roster-notation topics), `apply` (execute a computation — cardinality-of-a-finite-set, multiples-of-k), `analyze` (differentiate/reason about structure — equal vs. equivalent, infinite cardinality), `evaluate` (judge against a criterion — well-defined judgments, all `method_choice.*` topics, both `finite_infinite_classification.*` topics). No topic currently lands on `create`, which is expected for an intro "basic concepts" section — nothing asks a student to originate new mathematical content.

The dashboard has a Bloom-level filter (nav, below Learning Objectives) that combines with the existing Learning-Objective filter.

## 13. Full-coverage pass — all 50 source exercises (154 items)

The deep pass (Section 10, 122 items) was a *pilot depth* pass across the exercise families that had been generated so far — it was never a claim that every one of the 50 source exercises had a matching item family. Re-reading the actual chapter PDF exercise-by-exercise (not just the classification worksheet summary) turned up real gaps and one mislabeling:

- **#14** ("natural numbers divisible by zero") and **#17** ("polar bears that live in Antarctica") are both empty-set-trick cases the existing `method_choice.empty_set_trick` topic didn't have instances for — #13 (triangles/circles) was the only one built. Added as new static items; #17 needed a fact-check flag since it rests on a real-world biology fact (polar bears are Arctic, not Antarctic), not pure logic like #13/#14.
- **#15** (Brady Bunch kids) had been *numerically* tagged as covered — an earlier item (`C-03`, vowels in "mississippi") carried `exercise_number: "15 (pattern)"` even though its actual content tests a completely different named list. The exercise-number tag matched the skill family but not the specific content. Added the real #15 content as a new item rather than relying on the mismatched tag; the lesson for future sections is that an `exercise_number` tag confirms *skill-family* coverage, not *content* coverage — worth a real re-read of the source text per family, not just trusting existing tags.
- **#18** (songs written by Prince) and **#19** (children's books by Mo Willems) are a genuinely new sub-type: a well-defined, finite, but *very large* named collection, where the best representation is set-builder notation rather than roster — the mirror case of the existing small-finite → roster pattern (`method_choice.finite_word`). New topic: `sets.method_choice.large_finite`.
- **#20** (rainbow colors) is a small named list — added as a third instance of `method_choice.finite_word`, alongside mississippi-vowels and Brady-Bunch-kids.
- **#45, #46, #47, #48, #49, #50** had no matching topic at all. These test a distinct skill from anything already built: *classify a given set as finite or infinite* (LO4), as opposed to *compute the cardinal value* of a set (LO3, already covered by `sets.cardinality.*`). Split the same way the well-defined-set family split earlier: `sets.finite_infinite_classification.objective` (Category A — named math sets like ℕ, ℤ, ℚ, ℝ, the empty set, or any explicit roster/bounded-count set, where finite/infinite status is a structural fact) for #45/46/48, and `sets.finite_infinite_classification.real_world_fact` (Category B — jazz venues, cheese types, dictionary words, needing a fact-check that "large" isn't the same as "infinite") for #47/49/50.

**Exercise → topic map (complete):**

| Exercises | Topic | Category |
|---|---|---|
| 1, 2, 5 | `sets.roster_method.named_list` | B |
| 3, 4, 6 | `sets.roster_method.range` | A |
| 7, 8, 11, 12 | `sets.set_builder_notation.descriptive` | A |
| 9, 10 | `sets.set_builder_notation.multiples` | A |
| 13, 14, 17 | `sets.method_choice.empty_set_trick` | C |
| 15, 20 (+ mississippi) | `sets.method_choice.finite_word` | C |
| 16 | `sets.method_choice.infinite_setbuilder`, `sets.method_choice.infinite_roster` | C |
| 18, 19 | `sets.method_choice.large_finite` | C |
| 21–26 | `sets.well_defined.objective`, `sets.well_defined.subjective`, `sets.well_defined.real_world_fact` | A / A / B |
| 27–36 | `sets.cardinality.finite`, `sets.cardinality.infinite` | A |
| 37–44 | `sets.equal_equivalent` | A |
| 45, 46, 48 | `sets.finite_infinite_classification.objective` | A |
| 47, 49, 50 | `sets.finite_infinite_classification.real_world_fact` | B |

Result: 154 items across 17 topics, 0 unreviewed schema errors, 0 exercises without a matching topic (down from 3 gap ranges — #14, #17-20, #45-50 — before this pass). 25 items remain `needs_review` (all genuine Category B/C content, per Stage 4's rule that these never reach `approved` without a human pass).
