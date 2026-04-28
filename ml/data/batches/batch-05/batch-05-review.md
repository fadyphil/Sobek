# Batch-05 Review

## Line 16

```json
{
  "prompt": "register for the Arabic NLP workshop before seats fill up",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Register for Arabic NLP workshop"
  }
}

```

- **Flagged** : isn't there a deadline "before seats fill up"?

> Reasoning : No deadline. "Before seats fill up" is a conditional — it depends on an event that may or may not happen, with no specific time attached. Compare with "before the merge" or "before the demo" — those are scheduled events you can point to on a timeline. "Before seats fill up" is more like "before it's too late" — urgency framing, not a deadline. has_deadline: false stands.

## Line 32

```json
{
  "prompt": "check if the new Flutter version broke anything before upgrading the project",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Check for breaking changes before upgrading Flutter version"
  }
}

```

- **Flagged** : isn't there a deadline "before upgrading the project"?

> Reasoning : No deadline. Same reasoning — "before upgrading" describes the logical order of two actions the user controls, not an external time constraint. The user is saying "check first, then upgrade." There is no point on a calendar here. Compare with "before the release" or "before the client's morning" — those are external fixed events. This is not. has_deadline: false stands.

- ***Note*** : The distinction to lock: "before X" is a deadline only when X is a scheduled external event — a meeting, a release, a demo, a standup, a submission. When X is another action the user controls with no fixed time, it is sequencing, not a deadline.
You now have a complete three-way rule:

- "before Friday" → deadline, specific calendar point
- "before the demo" → deadline, scheduled external event
- "before upgrading" → not a deadline, user-controlled sequencing

Apply this going forward. Both lines stand as generated.
