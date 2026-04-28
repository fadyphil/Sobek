# Batch-04 Review

## Line 31

```jsonl
{
  "prompt": "3aiz a3mel clean architecture course 3ala YouTube",
  "completion": {
    "type": "task",
    "priority": "low",
    "has_deadline": false,
    "deadline": null,
    "summary": "Watch clean architecture course on YouTube"
  }
}

```

- **Flagged** : isn't the summary supposed to say 'make' istead of ```watch```?

> Reasoning : Claude  said: Line 31 — "a3mel" → watch or make "Watch" is correct. "a3mel course" in Egyptian Arabic colloquially means "take a course" — the same way you'd say "a3mel gym" to mean "go to the gym." The user is not creating content. Summary stands.

- **Final Decision**

> I didn't agree , i am Egyptian and that is flat out wrong so i changed it, aamel --> atfarag

## Line 38

```jsonl
{
  "prompt": "شوف لو في أوبة أرخص قبل ما تاخد Uber",
  "completion": {
    "type": "task",
    "priority": "low",
    "has_deadline": false,
    "deadline": null,
    "summary": "Check if Oba is cheaper before taking Uber"
  }
}

```

- **Flagged** :
  - what does that ```Oba``` mean?
  - and isn't there a deadline "before ordering uber"?

> Good catch

## Line 40

```jsonl
{
  "prompt": "rebase the feature branch before opening the PR",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Rebase feature branch before opening PR"
  }
}

```

- **Flagged** : isn't there a deadline "before opening the PR"?

> Good catch

## Line 45

```jsonl
{
  "prompt": "3aiz a7ot el-model fel-assets folder 2abl ma abda el-Flutter integration",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Add model to assets folder before starting Flutter integration"
  }
}

```

- **Flagged** : isn't there a deadline "before starting Flutter integration"?

> Good catch

## Line 47

```json
{
  "prompt": "write the README for the sobek repo before pushing to GitHub",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Write README before pushing to GitHub"
  }
}

```

- **Flagged** : isn't there a deadline "before pushing to GitHub"?

> Good catch

## Line 48

```json
{
  "prompt": "خد screenshot من الـ loss curve قبل ما تقفل الـ Colab",
  "completion": {
    "type": "task",
    "priority": "high",
    "has_deadline": false,
    "deadline": null,
    "summary": "Take screenshot of loss curve before closing Colab"
  }
}

```

- **Flagged** : isn't there a deadline "before closing Colab"?

> Good catch
