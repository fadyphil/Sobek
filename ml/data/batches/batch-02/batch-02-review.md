# Batch-02 Review

## Line 1

```jsonl
{
  "prompt": "مراجعة الكود بتاع المودول الجديد",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Review new module code"
  }
}

```

- **Changed**  : المودول --> الموديول

## Line 2

```jsonl
{
  "prompt": "el-interview 3andy el-yom el-sa3a 3",
  "completion": {
    "type": "task",
    "priority": "high",
    "has_deadline": true,
    "deadline": "today at 3",
    "summary": "Attend job interview"
  }
}

```

- **Changed** : ```el-youm``` --> ```enharda``` because this is the Egyptian way of saying today with possible variations in the vowel placement like (enaharda, enhrda, enahrda)

- **Flagged** : how should we deal with such variations?

## Line 5

```jsonl
{
  "prompt": "لازم اخلص الـ documentation قبل ما أسلم المشروع",
  "completion": {
    "type": "task",
    "priority": "high",
    "has_deadline": true,
    "deadline": "before project submission",
    "summary": "Complete project documentation"
  }
}

```

- **Flagged** : this doesn't seem like a high priority task ?

- **Reasoning** : Line 5 — "لازم اخلص الـ documentation قبل ما أسلم المشروع" → high
Correct as generated. "لازم" (must) signals obligation, and the deadline is project submission — a hard external constraint. High is defensible. Keep it.

## Line 6

```json
{
  "prompt": "follow up with HR about the offer letter",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Follow up with HR about offer letter"
  }
}

```

- **Flagged** : isn't that task a high priority task?

- **Reasoning** : Line 6 — "follow up with HR about the offer letter" → medium
Correct as generated. The prompt contains no urgency signal. Following up with HR is a normal professional action item. The fact that an offer letter matters to you personally does not make it high priority in the schema — priority reflects what the text signals, not external context the model cannot see. Medium stands.

## Line 10

```json
{
  "prompt": "water the plants",
  "completion": {
    "type": "task",
    "priority": "low",
    "has_deadline": false,
    "deadline": null,
    "summary": "Water the plants"
  }
}

```

- **Flagged** : isn't that task a high priority task ? because plants would die if not waterd

- **Reasoning** : Line 10 — "water the plants" → low
Correct as generated. The prompt contains zero urgency signal. You are importing knowledge the model does not have — that plants die without water. The model only sees the text. "Water the plants" reads as a routine low-stakes chore. If the user wanted high priority they would write "water the plants urgently" or "water the plants before they die." Low stands.

## Line 11

```json
{
  "prompt": "أسعار الكهرباء اتزادت تاني المرة السنة دي",
  "completion": {
    "type": "note",
    "priority": null,
    "has_deadline": false,
    "deadline": null,
    "summary": "Electricity prices increased again this year"
  }
}

```

- **Changed** : اتزادت --> زادت , because this is the Egyptian way of saying increased

## Line 26

```json
{
  "prompt": "print and sign the contract",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Print and sign contract"
  }
}

```

- **Flagged** : isn't that task a high priority task?

- **Reasoning** : Line 26 — "print and sign the contract" → medium
Correct as generated. No urgency signal in the prompt. Contracts are important but "important" is not the same as "urgent." Medium stands.

## Line 30

```json
{
  "prompt": "el-akl fel-sharika mesh kwayes khales",
  "completion": {
    "type": "note",
    "priority": null,
    "has_deadline": false,
    "deadline": null,
    "summary": "Food at the company is not good"
  }
}

```

- **Changed** :

  - ```fel-sharika``` --> ```fel sherka``` because this is the Egyptian way of saying it , but there are variants of the word like (f el sherka, fi el sherka, fl sherka) how should we deal with them?
  - ```mesh``` --> ```msh``` , same varient problem (mesh,msh,m4)
  - ```kwayes``` , has variants like (kwys,kwyes,kways)
  - ```khales``` --> ```5ales``` because  this is the Egyptian way of saying it

## Line 32

```json
{
  "prompt": "book appointment at the embassy next week",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": true,
    "deadline": "next week",
    "summary": "Book embassy appointment"
  }
}

```

- **Flagged** : isn't that task a high priority task?

- **Reasoning** :Line 32 — "book appointment at the embassy next week" → medium
Correct as generated. Same reasoning — no urgency language. "Next week" is a soft deadline with advance notice. Medium stands.

## Line 35

```json
{
  "prompt": "تجديد عقد الإيجار",
  "completion": {
    "type": "task",
    "priority": "medium",
    "has_deadline": false,
    "deadline": null,
    "summary": "Renew rental contract"
  }
}

```

- **Flagged** : isn't that task a high priority task?

- **Reasoning** : Line 35 — "تجديد عقد الإيجار" → medium
Correct as generated. No deadline, no urgency signal. A reminder to renew a rental contract with no time pressure in the text is medium. If the prompt said "تجديد عقد الإيجار قبل نهاية الشهر" that would change it. As written, medium.

## Line 44

```json
{
  "prompt": "3aiz agarrab el-quantization levels el-mokhtalefa w ashoof el-far2",
  "completion": {
    "type": "task",
    "priority": "low",
    "has_deadline": false,
    "deadline": null,
    "summary": "Test different quantization levels and compare results"
  }
}

```

- **Flagged** : same variant problem words like ```3aiz``` have (3ayez,3awes,3yez,3ayz) and ```agarrab``` has (agarab, agrab, agarb) and ```el-mokhtalefa``` has (mo5talefa,mo5tlfa,mo5talfa,mo5tlefa) and ```ashoof``` could have (ashuf, a4oof, ashof) , how should we deal with them?

## Notes

> The pattern you need to internalize: Priority is determined by what the text signals, not by the real-world stakes of the action. A model classifying intent cannot know that plants die or that contracts are legally binding. It can only see urgency language. This is the correct and consistent rule — apply it to every batch going forward.

## The Arabizi Variant Problem

> This is a real and important question. Here is the answer.
> You do not need to cover every spelling variant of every word. That is not how the model generalizes.
> The model learns that "3aiz," "3ayez," "3ayz" all appear in contexts that map to task intent. It learns this through exposure to multiple different examples using different words, not through exhaustive enumeration of one word's variants. Linguistic generalization is exactly what the base model's pre-training already handles — it has seen massive amounts of Arabic and Arabizi text. Your fine-tuning is teaching it a behavior (output JSON), not a vocabulary.
> The practical rule: In any single example, pick the most natural variant for that specific prompt. Don't overthink it. Across the full 600-example dataset, natural variation will emerge because different examples will use different words. That coverage is sufficient.
> What you should NOT do: manufacture artificial variant examples like five prompts that are identical except for spelling. That is dataset pollution, not diversity.

## For your specific changes

> el-youm → enharda ✅ good, more natural Egyptian
> اتزادت → زادت ✅ fine either way, keep whichever feels more natural
> fel-sharika → fel sherka ✅ fine
> mesh → msh, kwayes variants, 5ales — all fine, pick the most natural one per example and move on
