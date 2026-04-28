"""
validate_dataset.py
-------------------
Project Sobek v2 — Training Data Validator
Run this script after every batch before accepting examples into the final dataset.
It checks structure, schema rules, value constraints, and prints a distribution summary.
"""

import json
import sys
from pathlib import Path


# ── Constants ────────────────────────────────────────────────────────────────

# The exact 5 fields every completion must have. No more, no less.
REQUIRED_FIELDS = {"type", "priority", "has_deadline", "deadline", "summary"}

# Only these two values are valid for the "type" field
VALID_TYPES = {"task", "note"}

# Only these three strings (or null) are valid for "priority"
VALID_PRIORITIES = {"low", "medium", "high", None}


# ── Per-example validation ────────────────────────────────────────────────────

def validate_example(line_number: int, line: str) -> list[str]:
    """
    Validates a single JSONL line.
    Returns a list of error strings. Empty list means the example is clean.
    
    Each check is independent — we collect all errors, not just the first one,
    so you can fix everything in one pass rather than re-running repeatedly.
    """
    errors = []

    # ── Step 1: Parse the outer JSONL object ─────────────────────────────────
    # The outer object must have "prompt" and "completion" keys.
    # "completion" is a JSON string (with escaped inner quotes).
    try:
        outer = json.loads(line)
    except json.JSONDecodeError as e:
        # If this fails, the JSONL line itself is broken — likely unescaped quotes.
        errors.append(f"Line {line_number}: outer JSON parse failed — {e}")
        return errors  # No point checking further if the line won't parse at all

    # ── Step 2: Check outer keys ──────────────────────────────────────────────
    if "prompt" not in outer:
        errors.append(f"Line {line_number}: missing 'prompt' key")
    if "completion" not in outer:
        errors.append(f"Line {line_number}: missing 'completion' key")
        return errors  # Can't validate completion if it doesn't exist

    # ── Step 3: Parse the inner completion JSON ───────────────────────────────
    # The completion value is itself a JSON string. Parse it into a dict.
    try:
        completion = json.loads(outer["completion"])
    except json.JSONDecodeError as e:
        errors.append(f"Line {line_number}: completion JSON parse failed — {e}")
        return errors

    # ── Step 4: Check all 5 required fields are present ──────────────────────
    missing = REQUIRED_FIELDS - completion.keys()
    if missing:
        errors.append(f"Line {line_number}: missing fields in completion — {missing}")

    extra = completion.keys() - REQUIRED_FIELDS
    if extra:
        errors.append(f"Line {line_number}: unexpected extra fields — {extra}")

    # Stop detailed checks if fields are wrong — comparisons below would be meaningless
    if missing or extra:
        return errors

    # ── Step 5: Validate "type" ───────────────────────────────────────────────
    if completion["type"] not in VALID_TYPES:
        errors.append(
            f"Line {line_number}: invalid type '{completion['type']}' — must be 'task' or 'note'"
        )

    # ── Step 6: Validate "priority" ───────────────────────────────────────────
    if completion["priority"] not in VALID_PRIORITIES:
        errors.append(
            f"Line {line_number}: invalid priority '{completion['priority']}' — "
            f"must be 'low', 'medium', 'high', or null"
        )

    # ── Step 7: Schema rule — notes must have null priority ──────────────────
    if completion["type"] == "note" and completion["priority"] is not None:
        errors.append(
            f"Line {line_number}: type is 'note' but priority is '{completion['priority']}' — "
            f"notes must have null priority"
        )

    # ── Step 8: Validate "has_deadline" is strictly boolean ──────────────────
    # Must be True or False. Not null, not a string, not 0/1.
    if not isinstance(completion["has_deadline"], bool):
        errors.append(
            f"Line {line_number}: has_deadline is '{completion['has_deadline']}' "
            f"(type: {type(completion['has_deadline']).__name__}) — must be boolean true or false"
        )

    # ── Step 9: Contradiction check — has_deadline vs deadline ───────────────
    # If has_deadline is false, deadline must be null.
    # If has_deadline is true, deadline must be a non-empty string.
    if isinstance(completion["has_deadline"], bool):  # Only check if it parsed correctly
        if completion["has_deadline"] is False and completion["deadline"] is not None:
            errors.append(
                f"Line {line_number}: has_deadline is false but deadline is "
                f"'{completion['deadline']}' — must be null"
            )
        if completion["has_deadline"] is True and not isinstance(completion["deadline"], str):
            errors.append(
                f"Line {line_number}: has_deadline is true but deadline is "
                f"'{completion['deadline']}' — must be a non-empty string"
            )
        if completion["has_deadline"] is True and isinstance(completion["deadline"], str) \
                and completion["deadline"].strip() == "":
            errors.append(
                f"Line {line_number}: has_deadline is true but deadline is an empty string — "
                f"must be a descriptive string or null"
            )

    # ── Step 10: Validate "summary" is a non-empty string ────────────────────
    if not isinstance(completion["summary"], str) or completion["summary"].strip() == "":
        errors.append(
            f"Line {line_number}: summary is missing or empty"
        )

    # ── Step 11: Soft check — first-person leakage in summary ────────────────
    # These are warning-level, not hard failures. Flags for manual review.
    first_person_phrases = ["remind me", "i need to", "i want to", "i should", "my "]
    summary_lower = completion.get("summary", "").lower()
    for phrase in first_person_phrases:
        if summary_lower.startswith(phrase):
            errors.append(
                f"Line {line_number}: WARNING — summary may have first-person leakage: "
                f"'{completion['summary']}'"
            )
            break  # One warning per example is enough

    return errors


# ── Distribution counter ──────────────────────────────────────────────────────

def count_distribution(examples: list[dict]) -> dict:
    """
    Counts how examples are distributed across categories.
    Prints after validation so you know if your dataset is balanced.
    """
    counts = {
        "total": len(examples),
        "tasks": 0,
        "notes": 0,
        "task_with_deadline": 0,
        "task_no_deadline": 0,
        "priority_high": 0,
        "priority_medium": 0,
        "priority_low": 0,
        "priority_null": 0,
    }

    for ex in examples:
        try:
            # Re-parse the completion from the outer object
            c = json.loads(ex["completion"])
        except Exception:
            continue  # Already caught by validation, skip here

        if c.get("type") == "task":
            counts["tasks"] += 1
            if c.get("has_deadline") is True:
                counts["task_with_deadline"] += 1
            else:
                counts["task_no_deadline"] += 1
        elif c.get("type") == "note":
            counts["notes"] += 1

        p = c.get("priority")
        if p == "high":
            counts["priority_high"] += 1
        elif p == "medium":
            counts["priority_medium"] += 1
        elif p == "low":
            counts["priority_low"] += 1
        elif p is None:
            counts["priority_null"] += 1

    return counts


# ── Main entry point ──────────────────────────────────────────────────────────

def main(filepath: str):
    """
    Reads a JSONL file, runs all validations, and prints a report.
    Usage: python validate_dataset.py your_dataset.jsonl
    """
    path = Path(filepath)

    # Check the file actually exists before trying to open it
    if not path.exists():
        print(f"Error: file not found — {filepath}")
        sys.exit(1)

    all_errors = []       # Collects every error from every line
    valid_examples = []   # Collects successfully parsed outer objects for distribution counting
    total_lines = 0
    empty_lines = 0

    print(f"\n── Validating: {filepath} ──\n")

    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            # Skip blank lines — they are not errors, just whitespace
            if not line:
                empty_lines += 1
                continue

            total_lines += 1
            errors = validate_example(line_number, line)

            if errors:
                for error in errors:
                    print(error)
                all_errors.extend(errors)
            else:
                # Only add to valid pool if the line passed all checks
                try:
                    valid_examples.append(json.loads(line))
                except Exception:
                    pass  # Already handled above

    # ── Summary report ────────────────────────────────────────────────────────
    print(f"\n── Validation Summary ──")
    print(f"Total lines processed : {total_lines}")
    print(f"Empty lines skipped   : {empty_lines}")
    print(f"Lines with errors     : {len(set(e.split(':')[0] for e in all_errors))}")
    print(f"Clean examples        : {len(valid_examples)}")
    print(f"Total errors found    : {len(all_errors)}")

    # ── Distribution report ───────────────────────────────────────────────────
    if valid_examples:
        dist = count_distribution(valid_examples)
        print(f"\n── Distribution (clean examples only) ──")
        print(f"Tasks                 : {dist['tasks']}")
        print(f"  With deadline       : {dist['task_with_deadline']}")
        print(f"  Without deadline    : {dist['task_no_deadline']}")
        print(f"Notes                 : {dist['notes']}")
        print(f"Priority high         : {dist['priority_high']}")
        print(f"Priority medium       : {dist['priority_medium']}")
        print(f"Priority low          : {dist['priority_low']}")
        print(f"Priority null (notes) : {dist['priority_null']}")

    # ── Exit code ─────────────────────────────────────────────────────────────
    # Exit code 1 signals failure to any tool or CI system that runs this script.
    # Exit code 0 means clean.
    if all_errors:
        print(f"\n❌ Dataset has errors. Fix before training.\n")
        sys.exit(1)
    else:
        print(f"\n✅ Dataset is clean.\n")
        sys.exit(0)


# ── Entry point guard ─────────────────────────────────────────────────────────
# This block only runs when you execute the script directly.
# It won't run if another script imports this file as a module.
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_dataset.py <path_to_jsonl_file>")
        sys.exit(1)
    main(sys.argv[1])
