# Phase 1 — Training Data Generation

**Duration:** 3–4 days
**Prerequisites:** Phase 0 gate fully passed
**Deliverable:** A validated `.jsonl` file containing 500–800 training examples, manually reviewed for quality

---

## Purpose

The model learns exactly what you show it. Nothing more. Nothing less. If your training data is inconsistent, the model learns inconsistency. If your labels are ambiguous, the model learns ambiguity. If your JSON is malformed in 10% of examples, the model will produce malformed JSON 10% of the time.

This phase is the highest-leverage phase of the entire project. A mediocre training script with excellent data produces a better model than an excellent training script with mediocre data. This is not an opinion — it is an empirically established principle in ML: **garbage in, garbage out** is not a cliché, it is a law.

You will generate data with Claude's assistance. You own quality review. These roles are not interchangeable.

---

## Understanding JSONL Format

JSONL stands for JSON Lines. Each line in the file is a complete, valid JSON object. There are no commas between lines. There are no outer brackets. Just one JSON object per line.

**Valid JSONL:**

```jsonl
{"prompt": "remind me to buy groceries", "completion": "{\"type\": \"task\", \"priority\": \"low\", \"has_deadline\": false, \"deadline\": null, \"summary\": \"Buy groceries\"}"}
{"prompt": "the Nile flows north through Egypt", "completion": "{\"type\": \"note\", \"priority\": null, \"has_deadline\": false, \"deadline\": null, \"summary\": \"Nile flows north through Egypt\"}"}
```

**Why JSONL and not CSV or regular JSON:**

- ML training libraries (`datasets` from HuggingFace) expect this format
- Each example is independent — if one line is malformed, the rest are unaffected
- The file can be streamed line by line without loading everything into memory

---

## The Output Schema

Every training example must conform to this exact schema. No exceptions. No additional fields. No missing fields.

```json
{
  "type": "task" | "note",
  "priority": "low" | "medium" | "high" | null,
  "has_deadline": true | false,
  "deadline": "string describing deadline" | null,
  "summary": "clean, concise restatement of the input"
}
```

**Schema rules:**

- `type` is always either `"task"` or `"note"` — never anything else
- `priority` is `null` for notes (a note has no actionable priority)
- `priority` is always one of the three values for tasks — never `"urgent"`, never `"normal"`, never anything else
- `has_deadline` is always a boolean — never a string, never null
- `deadline` is `null` when `has_deadline` is `false` — there must be no contradiction between these two fields
- `summary` is always a clean, grammatically correct, third-person action or statement

**Common mistakes to catch during review:**

- `"has_deadline": false` paired with `"deadline": "soon"` — contradiction, reject
- `"type": "note"` paired with `"priority": "high"` — contradiction, reject
- `"summary": "remind me to call dentist"` — first person leaking into summary, reject — it should be `"Call dentist"`
- `"deadline": ""` (empty string instead of null) — reject
- Any field name with a typo (`"priorit"`, `"summry"`) — reject

---

## Distribution Requirements

Your dataset must be intentionally diverse. A model trained on 600 examples where 580 are tasks will misclassify notes. Plan your distribution before generating:

| Category | Target Count | Notes |
| --- | --- | --- |
| Tasks with deadline | 180–200 | Clear time reference in prompt |
| Tasks without deadline | 120–140 | Action needed, no time reference |
| Tasks high priority | 80–100 | Urgent language, critical context |
| Tasks medium priority | 100–120 | Normal action items |
| Tasks low priority | 80–100 | Minor, non-urgent actions |
| Pure notes | 150–180 | Facts, observations, ideas |
| Ambiguous inputs | 40–60 | Edge cases that require judgment |

**Why ambiguous inputs matter:** The model must learn to make a decision even when the input is unclear. If you train only on obvious examples, the model fails on everything real-world. Include things like "dentist appointment" (no verb, is it a task or a note?), "the meeting was good" (past tense, likely a note), "maybe I should exercise more" (uncertain intent).

---

## Prompt Diversity Requirements

Your input prompts must represent the real variety of how people write. Not just clean English. Include:

**Phrasing styles:**

- Imperative: "Call the dentist"
- Reminder framing: "Remind me to call the dentist"
- Casual note-to-self: "dentist — Thursday 3pm"
- Fragmented: "groceries, eggs, milk, bread"
- Past observation: "the deployment went smoothly today"
- Uncertainty: "might need to renew passport soon"
- Mixed language (Arabic/English Arabizi): "3aiz afham el-docker containers" — yes, include this

**Deadline variety:**

- Specific dates: "before Friday", "by the 15th", "end of next week"
- Relative time: "tomorrow", "this afternoon", "in 3 days"
- Vague urgency: "soon", "ASAP", "as soon as possible" — these map to `has_deadline: false` with high priority, because "ASAP" is urgency, not a deadline
- No deadline indicators at all

**Domains:**
Do not cluster all examples in one life domain. Spread across:

- Work/study tasks
- Personal errands
- Health and appointments
- Financial reminders
- Ideas and observations
- Technical notes (code-related, developer context)
- Arabic-language inputs

---

## The ASAP vs Deadline Distinction

This is a judgment call that must be consistent across your entire dataset.

**Rule:** `has_deadline` is true only when there is a specific point in time referenced — a date, a day of the week, a relative time like "tomorrow" or "in 3 days." The word "ASAP" or "urgent" or "immediately" signals **priority**, not a deadline. These inputs get `has_deadline: false` and `priority: "high"`.

**Apply this rule to every example you review.** Inconsistency here directly degrades model performance.

---

## Generation Process

You will generate this dataset in batches of 50 examples at a time using Claude. Each batch will be reviewed by you before being accepted into the final file.

**Batch review checklist (apply to every single example in every batch):**

- [ ] Is the JSON valid? (No trailing commas, no missing quotes, all values are the correct type)
- [ ] Does the prompt look like something a real person would write?
- [ ] Is `type` correctly assigned? Would you personally classify this the same way?
- [ ] If `type` is `"note"`, is `priority` null?
- [ ] If `has_deadline` is false, is `deadline` null?
- [ ] If `has_deadline` is true, does the prompt actually contain a time reference?
- [ ] Is the `summary` in third person, clean, and concise?
- [ ] Is the prompt in the correct JSONL format with escaped inner quotes?

---

## Understanding Escaped Quotes in JSONL

This trips up almost everyone the first time. In JSONL, the entire line is a JSON object. The `completion` field is a string — meaning the JSON inside it must have its quotes escaped with backslashes.

**Wrong (this breaks the outer JSON):**

```json
{"prompt": "call dentist", "completion": "{"type": "task"}"}
```

**Correct (inner quotes escaped):**

```jsonl
{"prompt": "call dentist", "completion": "{\"type\": \"task\", \"priority\": \"medium\", \"has_deadline\": false, \"deadline\": null, \"summary\": \"Call dentist\"}"}
```

When you open the final `.jsonl` file, every completion field will look like a string full of backslashes. This is correct. When the training library reads it, it unescapes the string automatically.

---

## Dataset Validation

Before Phase 2, you must run a validation pass on the complete dataset. Claude will provide a Python script for this. The script checks:

1. Every line is valid JSON (no malformed lines)
2. Every object has exactly the 5 required fields
3. No field has an unexpected value type
4. `has_deadline`/`deadline` contradictions are flagged
5. `type`/`priority` contradictions are flagged
6. Distribution summary is printed (count of tasks vs notes, deadline vs no deadline)

You read every line of the validation script before running it. You understand what each check does.

---

## Gate 1 — You May Not Proceed Until You Can Answer All Of These

---

### **Section A — JSONL and Schema**

1. What is the difference between a JSON file and a JSONL file? Why does ML tooling prefer JSONL?

2. Write a valid JSONL line for the following input: *"I need to renew my car insurance before the end of the month"*. Your answer must be syntactically correct JSONL with properly escaped inner quotes.

3. Write a valid JSONL line for the following input: *"Flutter uses a widget tree to represent the UI"*. Your answer must be syntactically correct JSONL with properly escaped inner quotes.

4. The input is *"ASAP finish the API integration."* What are the correct values for `has_deadline`, `deadline`, and `priority` in the completion? Explain your reasoning.

5. A colleague submits a training example where `type` is `"note"` and `priority` is `"medium"`. What is wrong and why does it matter if this slips through into the final dataset?

---

### **Section B — Data Quality**

1. Why is data quality more important than training script quality in fine-tuning? Give a concrete example using our project — what would a model trained on inconsistent `has_deadline` labeling actually do wrong?

2. You are reviewing a batch and find this prompt: *"remind me"*. Should this be included? Why or why not?

3. You find this completion summary: *"I need to buy groceries"*. What is wrong with it and what should it be?

4. You find `"deadline": ""` (empty string) in an example where `has_deadline` is false. Is this acceptable? Why or why not?

---

### **Section C — Distribution**

1. You generate 600 examples but 520 of them are tasks and only 80 are notes. What is the likely consequence when you run inference on a real input that is genuinely a note?

2. Why did we include Arabizi (Arabic written in Latin characters) as a prompt style? What does including it teach the model?

3. What is the purpose of "ambiguous" examples in the dataset? Why not just exclude them and keep only clear-cut cases?

---

### **Section D — Validation**

1. Before training, you run the validation script. It reports: "14 lines failed JSON parsing." What is the most likely cause, and what is the consequence if you train on this data without fixing it?

2. The validation script reports your dataset has 600 examples: 430 tasks and 170 notes. Is this distribution acceptable? If not, what would you change and how would you generate the missing examples?

---

## **Practical Exercise (mandatory)**

1. Without Claude's help, write 5 original training examples covering: one high-priority task with deadline, one low-priority task without deadline, one pure note in Arabic, one ambiguous edge case, and one Arabizi input. Format them as correct JSONL. These must be your own invention — not copied from this document.

---

## How To Submit Your Gate

Paste all answers including the 5 JSONL examples to Claude. Every answer is evaluated. The JSONL examples are checked for syntax, schema correctness, and quality before the gate opens to Phase 2.
