# Batch-03 Review

## Line 10

```json
{
  "prompt": "3aiz a3mel PR review 3ala el-feature branch 2abl el-merge",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Review PR before merging feature branch"
  }
}

```

- **Flagged** : doesn't that task a have a deadline which is before the merge?

> That's a good catch

## Line 37

```json
{
  "prompt": "3aiz akhod break mn el-screen",
  "completion": {
    "type": "task",
    "priority": "low",
    "has_deadline": false,
    "deadline": null,
    "summary": "Take a break from screen"
  }
}

```

- **Flagged** : this seems more like a note than a task

- **Reasoning** : It's a task. "3aiz" (I want to) is intent to act — the user is telling themselves to do something. Compare with notes in the dataset which are observations, facts, or past-tense statements. "I want to take a break" is an action item with low urgency, not an observation. Keep it as task.
The line between "weak task" and "note" is genuinely thin here, which is why this is a useful ambiguous example. The classification is defensible and consistent with how similar prompts are handled.
