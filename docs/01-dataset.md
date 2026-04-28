# Phase 1 — Training Data

**Status:** In Progress  
**Gate:** Passed  
**Current state:** Batch 1 (50 examples) generated and reviewed. Full dataset generation underway.

---

## Why This Phase Is the Highest-Leverage Phase

The model learns exactly what you show it. A mediocre training script with excellent data produces a better model than an excellent training script with mediocre data. This is not an opinion — it is empirically established in ML.

For a narrow task like this (intent classification → structured JSON), data quality determines almost everything. The model's job is to learn one pattern. If the pattern is inconsistent in the training data, the model learns inconsistency.

---

## The Task

Classify raw text input into a structured JSON object with exactly 5 fields:

```json
{
  "type": "task" | "note",
  "priority": "low" | "medium" | "high" | null,
  "has_deadline": true | false,
  "deadline": "string describing deadline" | null,
  "summary": "clean, concise third-person restatement"
}
```

---

## Schema Rules and Why They Exist

These rules are not arbitrary. Each one exists because an inconsistency here directly degrades model output.

**`type`** — always `"task"` or `"note"`. Never `"reminder"`, `"event"`, or anything else. The model's output space must be constrained to exactly what we define.

**`priority`** — `null` for notes always. Notes are observations or information — they have no actionable urgency. If this leaks into training data (e.g. `type: "note"`, `priority: "medium"`), the model learns that notes can have priorities and will produce this incorrectly.

**`has_deadline`** — always a boolean. Never `null`, never a string. This is the most common type error in training data. A single example with `"has_deadline": null` teaches the model that null is a valid value here.

**`deadline`** — `null` when `has_deadline` is `false`. A non-null deadline with `has_deadline: false` is a direct contradiction. If this slips into training data, the model learns that this contradiction is acceptable and will reproduce it.

**`summary`** — always third-person, clean, no first-person leakage. `"remind me to call dentist"` in the summary field teaches the model to echo back the user's phrasing instead of restating it cleanly.

---

## The ASAP vs Deadline Distinction

This judgment call must be consistent across the entire dataset. Getting it wrong in 10% of examples produces a model that is wrong 10% of the time on this specific edge case.

**Rule:** `has_deadline: true` only when the input contains a specific point in time — a date, a day of the week, or a relative time like "tomorrow" or "in 3 days."

Words like "ASAP," "urgent," "immediately," and "soon" indicate **priority**, not a deadline. These map to `has_deadline: false`, `deadline: null`, `priority: "high"`.

**Examples:**

- "finish this ASAP" → `has_deadline: false`, `priority: "high"` ✅
- "finish this by Friday" → `has_deadline: true`, `deadline: "Friday"` ✅
- "finish this soon" → `has_deadline: false`, `priority: "medium"` ✅

---

## Dataset Distribution Target

| Category | Target Count |
| --- | --- |
| Tasks with deadline | 180–200 |
| Tasks without deadline | 120–140 |
| High priority tasks | 80–100 |
| Medium priority tasks | 100–120 |
| Low priority tasks | 80–100 |
| Pure notes | 150–180 |
| Ambiguous inputs | 40–60 |

**Why distribution matters:** A model trained on 580 tasks and 20 notes will perform poorly on note classification — not because it doesn't understand notes conceptually, but because the pattern was underrepresented in training. Skewed distribution → biased output.

---

## Prompt Diversity Requirements

Training data must reflect the actual variety of how people write. Clean English sentences are not sufficient.

**Included styles:**

- Imperative: "Call the dentist"
- Reminder framing: "Remind me to call the dentist"
- Casual note-to-self: "dentist — Thursday 3pm"
- Fragmented: "groceries, eggs, milk, bread"
- Past observation: "the deployment went smoothly today"
- Uncertainty: "might need to renew passport soon"
- Arabizi: "3aiz afham el-docker containers"
- Arabic: "اتصل بالطبيب قبل الخميس"

**Why Arabizi specifically:** The target audience is Egyptian developers and users. Egyptian users frequently write in Arabizi — Arabic words transliterated into Latin characters. If the model has never seen this input style, it will either misclassify or produce malformed output on a large proportion of real-world inputs from this demographic.

**Domains covered:** work/study tasks, personal errands, health and appointments, financial reminders, ideas and observations, technical/developer notes, Arabic-language inputs.

---

## What "Ambiguous" Examples Teach

Real input is ambiguous. "Dentist" with no verb — is it a note about dentists or a reminder to go? "The meeting was good" — past tense, so a note, but the phrasing is thin.

Training only on clean, obvious examples produces a model that fails on anything that is not obvious. Including ambiguous examples — with a consistent, defensible classification decision — teaches the model to make a judgment call rather than fail.

The classification on ambiguous examples should be documented alongside the example so the decision can be reviewed and is reproducible.

---

## JSONL Format

Each line in the training file is a complete, independent JSON object:

```JsonL
{"prompt": "...", "completion": "{\"type\": \"task\", ...}"}
```

The completion field is a JSON string — inner quotes must be escaped with backslashes. This is the most common syntax error in hand-written JSONL.

**Why JSONL and not regular JSON or CSV:**

- HuggingFace `datasets` library expects this format
- Each example is independent — one malformed line does not break the rest
- Files can be streamed line-by-line without loading into memory

---

## Data Generation Process

Dataset is generated in batches of 50 using Claude, then reviewed before being accepted. Roles are fixed:

- **Claude:** generates batches
- **Fady:** owns quality review — every example against the checklist
- **Validation script:** automated structural checks after each batch
- **LLM-as-judge:** Claude evaluates labeling judgment on uncertain examples

This mirrors the industry standard pipeline at a scale appropriate for a 600-example dataset: programmatic quality control + human review + LLM evaluation.

---

## Tooling

**`validate_dataset.py`** — runs after every batch. Checks:

- Valid JSON on every line
- All 5 required fields present, no extras
- No invalid enum values
- `has_deadline`/`deadline` contradiction detection
- `type`/`priority` contradiction detection
- Soft warning for first-person leakage in summary
- Distribution summary

Usage:

```bash
python validate_dataset.py dataset.jsonl
```

Exit code 0 = clean. Exit code 1 = errors found. Fix all errors before accepting a batch.

---

## Current Progress

| Batch | Count | Status |
| --- | --- | --- |
| Batch 1 | 50 | ✅ Generated and reviewed |
| Batch 2–16 | 550–750 | ⬜ Not yet generated |

Target: 500–800 total examples.

---

## Decisions Made and Rejected

**Rejected: scraping real notes/tasks from Reddit or public datasets.**  
Reason: quality is inconsistent, schema labeling would need to be done manually on noisy data, and scraping introduces overhead with no benefit over synthetic generation for a narrow classification task.

**Rejected: including additional output fields (e.g., `category`, `context`).**  
Reason: schema complexity increases the output space and reduces classification reliability on a 500M parameter model. Five fields with constrained values is the right scope.

**Decision: notes always have `priority: null`, no exceptions.**  
Reason: notes are not action items. Introducing priority for notes adds ambiguity about what priority means in the context of a note. Cleaner to make it a hard rule.
