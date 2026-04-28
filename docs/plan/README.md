# Project Sobek v2 — Master Index

**Project:** On-Device Note Intent Classifier
**Stack:** LoRA Fine-Tuning → GGUF Export → Flutter + Dart FFI
**Engineer:** Fady Philip
**Started:** April 2026

---

## What This Is

An end-to-end machine learning engineering journey. You are not following a tutorial. You are building a system, understanding every decision inside it, and finishing with a deployed artifact that runs entirely on-device inside a Flutter application.

This document is the map. Each phase has its own file with full context, concepts, requirements, and gates. You cannot move to the next phase until you can answer every gate question without referencing notes.

---

## The Output

A Flutter app that accepts raw text input and returns structured JSON classification — entirely offline, zero API calls, model running on-device via Dart FFI.

```Markdown
"remind me to submit the report before Friday" 
        ↓
{
  "type": "task",
  "priority": "high",
  "has_deadline": true,
  "deadline": "Friday",
  "summary": "Submit report"
}
```

---

## Phase Map

| Phase | Name | Est. Duration | Status |
| --- | --- | --- | --- |
| [Phase 0](./phase-0-conceptual-grounding.md) | Conceptual Grounding | 3–4 days | ⬜ Not Started |
| [Phase 1](./phase-1-training-data.md) | Training Data Generation | 3–4 days | ⬜ Not Started |
| [Phase 2](./phase-2-environment-setup.md) | Environment Setup | 1 day | ⬜ Not Started |
| [Phase 3](./phase-3-fine-tuning.md) | Fine-Tuning | 2–3 days | ⬜ Not Started |
| [Phase 4](./phase-4-export-inference.md) | Export & Local Inference | 2 days | ⬜ Not Started |
| [Phase 5](./phase-5-flutter-integration.md) | Flutter Integration | 3–5 days | ⬜ Not Started |

**Total realistic duration:** 5–6 weeks alongside existing obligations.

---

## How Gates Work

Every phase ends with a **Gate** — a set of questions you must answer without looking anything up. Not "approximately right." Precisely, clearly, in your own words.

If you cannot answer a gate question, you have not understood the concept. You go back, re-read, re-watch, re-think. You do not proceed.

This is not a punishment mechanism. It is the only honest way to know whether you are learning or just following instructions. Following instructions produces nothing transferable. Understanding produces an engineer.

---

## The CV Line You Are Building

> *"End-to-end on-device LLM pipeline: fine-tuned Qwen2.5-0.5B with LoRA for structured intent extraction, exported to GGUF, integrated into Flutter via Dart FFI and llama.cpp — fully offline, zero API dependency."*

Nobody in the Egyptian Flutter ecosystem has this line. You will.
