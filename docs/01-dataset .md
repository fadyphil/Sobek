# Phase 1 — Training Data

**Status:** Complete  
**Gate:** Passed  
**Final dataset:** 599 examples across 12 batches, fully validated

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

**Rule:** `has_deadline: true` only when the input contains a specific point in time — a date, a day of the week, a relative time like "tomorrow" or "in 3 days," a scheduled external event like "before the demo" or "before the release," or when the prompt explicitly uses a word meaning deadline/appointment (ميعاد, موعد).

Words like "ASAP," "urgent," "immediately," and "soon" indicate **priority**, not a deadline. These map to `has_deadline: false`, `deadline: null`, `priority: "high"`.

**The three-way rule locked during review:**

- "before Friday" → `has_deadline: true` — specific calendar point
- "before the demo" → `has_deadline: true` — scheduled external event
- "before upgrading" → `has_deadline: false` — user-controlled sequencing, not a fixed event

**Conditionals are not deadlines:**

- "before seats fill up" → `has_deadline: false` — unpredictable conditional
- "before it expires" → `has_deadline: false` — implied event, no date stated
- "before the Colab session breaks" → `has_deadline: false` — unpredictable conditional

---

## Dataset Distribution

### Target vs Final

| Category | Target | Final | Status |
| --- | --- | --- | --- |
| Tasks with deadline | 180–200 | 207 | ⚠️ Slightly over |
| Tasks without deadline | 120–140 | 209 | ❌ Over |
| Priority high | 80–100 | 135 | ❌ Over |
| Priority medium | 100–120 | 168 | ❌ Over |
| Priority low | 80–100 | 113 | ⚠️ Slightly over |
| Notes | 150–180 | 183 | ⚠️ Marginal |

### Ratio Assessment (what training actually sees)

| Category | Target % | Final % | Status |
| --- | --- | --- | --- |
| Tasks vs notes | ~70/30 | 69/31 | ✅ |
| Deadline vs no deadline (tasks) | ~55/45 | 50/50 | ⚠️ |
| High priority (of tasks) | ~22% | 32% | ⚠️ |
| Medium priority (of tasks) | ~30% | 40% | ⚠️ |
| Low priority (of tasks) | ~25% | 27% | ✅ |

**Why distribution matters:** A model trained on 580 tasks and 20 notes will perform poorly on note classification — not because it doesn't understand notes conceptually, but because the pattern was underrepresented in training. Skewed distribution → biased output.

---

## Prompt Diversity Requirements

Training data must reflect the actual variety of how people write. Clean English sentences are not sufficient.

**Included styles:**

- Imperative: "Call the dentist"
- Reminder framing: "Remind me to call the dentist"
- Casual note-to-self: "dentist — Thursday 3pm"
- Fragmented: "groceries, eggs, milk, bread"
- Single word: "medication", "laundry", "نوم"
- Past observation: "the deployment went smoothly today"
- Uncertainty: "might need to renew passport soon"
- Arabizi: "3aiz afham el-docker containers"
- Arabic: "اتصل بالطبيب قبل الخميس"
- Mixed Arabic/English: "لازم اخلص الـ documentation"

**Why Arabizi specifically:** The target audience is Egyptian developers and users. Egyptian users frequently write in Arabizi — Arabic words transliterated into Latin characters with digit substitutions (3=ع, 2=ء, 7=ح). Arabizi has no fixed spelling — "3aiz," "3ayez," "3ayz" are all valid. The model generalizes across variants through exposure to diverse examples, not exhaustive enumeration of every spelling.

**Domains covered:** work/study tasks, personal errands, health and appointments, financial reminders, ideas and observations, technical/developer notes, ML-specific notes in Arabic and Arabizi, graduation and university tasks.

---

## What "Ambiguous" Examples Teach

Real input is ambiguous. "Dentist" with no verb — is it a note about dentists or a reminder to go? "The meeting was good" — past tense, so a note, but the phrasing is thin.

Training only on clean, obvious examples produces a model that fails on anything that is not obvious. Including ambiguous examples — with a consistent, defensible classification decision — teaches the model to make a judgment call rather than fail.

---

## JSONL Format

Each line in the training file is a complete, independent JSON object:

```jsonl
{"prompt": "...", "completion": "{\"type\": \"task\", ...}"}
```

The completion field is a JSON string — inner quotes must be escaped with backslashes. This is the most common syntax error in hand-written JSONL and the most likely cause of batch validation failures.

**Why JSONL and not regular JSON or CSV:**

- HuggingFace `datasets` library expects this format
- Each example is independent — one malformed line does not break the rest
- Files can be streamed line-by-line without loading into memory

---

## Data Generation Process

Dataset generated in batches using Claude, reviewed before acceptance. Roles were fixed:

- **Claude:** generates batches
- **Fady:** owns quality review — every example against the checklist
- **Validation script:** automated structural checks after each batch
- **LLM-as-judge:** Claude evaluates labeling judgment on uncertain examples

This mirrors the industry standard pipeline at appropriate scale: programmatic quality control + human review + LLM evaluation.

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

```bash
python3 ml/data/validate_dataset.py ml/data/dataset.jsonl
```

Exit code 0 = clean. Exit code 1 = errors found.

---

## Batch Progress

| Batch | Examples | Status | Notes |
| --- | --- | --- | --- |
| Batch 1 | 50 | ✅ | Initial batch, established review workflow |
| Batch 2 | 50 | ✅ | Higher Arabic/Arabizi density |
| Batch 3 | 50 | ✅ | Fixed: "2abl el-merge" deadline missed in generation |
| Batch 4 | 50 | ✅ | Fixed: 5 "before X" deadlines missed — locked event-based deadline rule |
| Batch 5 | 50 | ✅ | Confirmed: "before upgrading" is sequencing not deadline |
| Batch 6 | 50 | ✅ | Confirmed: "before it expires" without date = conditional not deadline |
| Batch 7 | 50 | ✅ | Fixed: ميعاد in prompt = has_deadline true — locked ميعاد/موعد rule |
| Batch 8 | 50 | ✅ | Fixed: "maybe this weekend" — hedging does not cancel time reference |
| Batch 9 | 50 | ✅ | Confirmed: "before Colab session breaks" = unpredictable conditional |
| Batch 10 | 50 | ✅ | 500 example milestone |
| Batch 11 | 50 | ✅ | Distribution correction — zero high priority, heavy low priority |
| Batch 12 | 40 | ✅ | Final distribution correction — zero high priority, zero notes |
| **Total** | **599** | ✅ | |

---

## Decisions Made and Rejected

**Rejected: scraping real notes/tasks from Reddit or public datasets.**  
Reason: quality is inconsistent, schema labeling would need to be done manually on noisy data, and scraping introduces overhead with no benefit over synthetic generation for a narrow classification task.

**Rejected: including additional output fields (e.g., `category`, `context`).**  
Reason: schema complexity increases the output space and reduces classification reliability on a 500M parameter model. Five fields with constrained values is the right scope.

**Decision: notes always have `priority: null`, no exceptions.**  
Reason: notes are not action items. Introducing priority for notes adds ambiguity about what priority means in the context of a note. Cleaner to make it a hard rule.

**Decision: stopped at 599 examples despite being over target on several categories.**  
Reason: absolute counts exceeded targets because the dataset grew beyond the original 500-example plan. The ratios are within acceptable tolerance. Further generation inflates totals without fixing existing imbalances.

---

## Known Limitations

**High priority is inflated (32% of tasks vs 22% target).** The model will have a mild bias toward classifying tasks as high priority on ambiguous inputs. This is a consequence of early batches generating too many urgent-phrased prompts before the imbalance was detected. Corrective batches 11 and 12 reduced but did not fully close the gap.

**Tasks without deadline exceed target (209 vs 120–140 target).** The "before X" deadline rule was not locked until batch 4. Examples generated before that point had more no-deadline tasks than intended. By the time the rule was locked, the count was already above target.

**Arabizi spelling variants are not exhaustively covered.** The dataset includes common variants but not every possible spelling of every word. The base model's pre-training on Arabic text handles generalization across variants — this is a deliberate design decision, not a gap.

These limitations are documented for the Phase 3 training log. If post-training evaluation shows the model consistently over-predicts high priority, adding targeted low/medium priority examples and retraining is the correct fix.
