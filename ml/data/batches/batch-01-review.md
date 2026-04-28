# Batch 1 Review

## Line 22

```jsonl
{
  "prompt": "URGENT: server is down fix it now",
  "completion": {
    "type": "task",
    "priority": "high",
    "has_deadline": false,
    "deadline": null,
    "summary": "Fix server outage"
  }
}
```

- **Flagged**: shouldn't there be a deadline?

## Line 24

```jsonl
{
  "prompt": "اتصل بالدكتور فورا",
  "completion": {
    "type": "task",
    "priority": "high",
    "has_deadline": false,
    "deadline": null,
    "summary": "Call doctor immediately"
  }
}
```

- **Flagged**: shouldn't there be a deadline?

## Reason for keeping them as is

- **Urgent** & **فورا (immediately)**: these are indicators of **Priority** not dealines
- **Now** or any time indicator for it: has a problem of being stale once created that is why ***has_deadline*** is ```false``` and ***deadline*** is ```null```
