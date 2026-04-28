# HANDOFF: Project Sobek v2 — Claude → Claude

## WHO

Fady Philip. 4th-yr CS, MSA Univ New Cairo. Graduating Jun/Jul 2026. Flutter/Dart senior-level: clean arch, BLoC, fpdart, freezed, dio, Firebase. Two flagship projects: Osserva (offline music player, star-schema SQLite analytics, home widget, cold start) and Valoqui (on-device Spanish tutor, sherpa_onnx, ONNX models, espeak-ng, Dart FFI adjacent). McKinsey Step Forward program Apr 2026. Target: VOIS/PwC/IBM Egypt → Europe transfer 2027–2028.

Communication style: dense, zero filler, no flattery, direct pushback. Treat as peer. No encouragement. Dialectical friction welcome.

---

## WHAT WE DECIDED

**Project:** Fine-tune small LLM → on-device Flutter app. Full pipeline: LoRA fine-tune → GGUF export → Dart FFI → Flutter.

**Task:** Note/task intent classifier. Raw text in → structured JSON out:

```json
{"type":"task","priority":"high","has_deadline":true,"deadline":"Friday","summary":"Submit report"}
```

**Model:** Qwen2.5-0.5B-Instruct. Reasoning: instruction-tuned, small enough for Colab free T4, good multilingual baseline, supports ChatML template.

**Why this task:** Small models do classification well. Output space constrained = quantization quality loss negligible. Evaluable. Synthetic training data = no scraping. Flutter integration natural. Enterprise-relevant (intent extraction). Nobody in Egyptian Flutter ecosystem has end-to-end on-device LLM pipeline.

**CV line:** "End-to-end on-device LLM pipeline: fine-tuned Qwen2.5-0.5B with LoRA for structured intent extraction, exported to GGUF, integrated into Flutter via Dart FFI and llama.cpp — fully offline, zero API dependency."

---

## FADY'S ML STARTING POINT

- Python: basics only (loops, conditionals, variables). No ML background.
- Approach: concepts over syntax. AI writes code, Fady reads + debugs direction.
- Agreed: must be able to read Python well enough to trace a training loop line by line. Two weeks exposure alongside project is sufficient.
- Interest is genuine — analogous to his Golang curiosity. Not for CV alone.

---

## PHASE STRUCTURE (6 phases, gates mandatory)

All 7 files delivered and downloadable. Files:

- `README.md` — master index
- `phase-0-conceptual-grounding.md` — 21 gate questions
- `phase-1-training-data.md` — 15 gate questions + practical JSONL exercise
- `phase-2-environment-setup.md` — 16 gate questions
- `phase-3-fine-tuning.md` — 16 gate questions
- `phase-4-export-inference.md` — 14 gate questions
- `phase-5-flutter-integration.md` — 15 gate questions + 200-word retrospective

Gate rule: answer all questions without notes, in own words. No partial pass. Claude evaluates each answer, flags gaps, sends back or opens next phase.

| Phase | Topic | Duration |
| --- | --- | --- |
| 0 | Conceptual grounding | 3–4 days |
| 1 | Training data generation | 3–4 days |
| 2 | Environment setup (Colab) | 1 day |
| 3 | Fine-tuning | 2–3 days |
| 4 | GGUF export + local inference via Ollama | 2 days |
| 5 | Flutter integration (Dart FFI, llama_cpp_dart, BLoC) | 3–5 days |

**Total: 5–6 weeks.**

---

## TECHNICAL DECISIONS LOCKED

| Decision | Value | Reason |
| --- | --- | --- |
| Base model | Qwen2.5-0.5B-Instruct | ChatML template, small, multilingual |
| Fine-tune method | LoRA via PEFT | Memory efficient, fits T4 |
| LoRA rank | r=8 | Sufficient for narrow classification |
| lora_alpha | 16 | Convention: 2× rank |
| Target layers | q_proj, v_proj | Attention mechanism, highest impact |
| Quantization (train) | 4-bit via bitsandbytes | VRAM constraint |
| Epochs | 3 | Small dataset, narrow task |
| Learning rate | 2e-4 | Standard LoRA instruction-following |
| Batch size | 4 per device, GA=4, effective=16 | T4 VRAM limit |
| Inference quantization | Q4_K_M GGUF | Balance size/quality for classification |
| Local inference tool | Ollama | Simple, GGUF-native, API compatible |
| Flutter package | llama_cpp_dart | Dart FFI bindings to llama.cpp |
| Temperature | 0 | Deterministic JSON output |
| Dataset size | 500–800 examples | Narrow task, synthetic generation |
| Training environment | Google Colab free T4 | No local GPU requirement |

---

## DATASET SPEC

**Schema (all 5 fields mandatory, no extras):**

```json
{
  "type": "task"|"note",
  "priority": "low"|"medium"|"high"|null,
  "has_deadline": true|false,
  "deadline": "string"|null,
  "summary": "clean third-person restatement"
}
```

**Rules:**

- note → priority always null
- has_deadline false → deadline always null
- ASAP/urgent = priority high, has_deadline false (urgency ≠ deadline)
- summary always third-person, no "remind me to" leakage

**Distribution target:** ~200 task+deadline, ~130 task no deadline, ~170 notes, ~50 ambiguous. Includes Arabizi, Arabic, fragmented, past-tense inputs.

**Generation method:** Claude generates in batches of 50. Fady reviews every example against checklist before accepting.

---

## FLUTTER ARCHITECTURE (Phase 5)

Standalone new project. Feature-first clean arch:

```Markdown
core/di, core/inference/LlamaEngine
features/classifier/data, domain, presentation
```

Stack: get_it DI, flutter_bloc, fpdart Either, freezed models, llama_cpp_dart.

Inference in background isolate (mandatory — not main thread).
Model bundled in assets (direct APK distribution, no Play Store constraint).
System prompt enforces JSON-only output at inference time.
Output sanitized (extract {…} substring) before jsonDecode.

---

## CURRENT STATUS

Phase 0 not yet started. Fady has the 7 phase files downloaded.

**Next action for Fady:** Start Phase 0. Watch Witteveen LoRA/PEFT video (concepts only, code is outdated). Watch Umar Jamil "LoRA explained" YouTube. Return with all 21 gate questions answered.

**Next action for Claude:** When Fady returns with gate answers — evaluate every question individually, identify gaps, either open Phase 1 or return specific questions for rework. Then generate the 500–800 JSONL dataset in batches of 50.

---

## REJECTED PATHS (do not re-suggest)

- Egyptian Arabic chatbot (Gemini's original suggestion) — no deployable output, wrong task profile for small model
- General fine-tuning on Reddit data — scraping overhead, quality issues, no Flutter story
- FreeCodeCamp ML intro video — too broad, wrong entry point
- Fine-tuning for factual knowledge injection — use RAG instead, this was explicitly discussed and closed

---

## TONE CALIBRATION

No flattery. No "great question." No encouragement padding. Dense answers. Push back when Fady is wrong. He has explicitly corrected previous AI assistants for over-flattery and under-challenging. Treat gate answers seriously — if an answer is partially right, say which part is wrong and exactly why, do not soften it.
