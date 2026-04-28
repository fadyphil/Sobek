# ADR-0001: Use Qwen2.5-0.5B-Instruct for On-Device Intent Classification

## Status

Accepted

## Context

Sobek requires a small language model capable of running entirely offline on a mobile device (Flutter app) with minimal latency and high accuracy for JSON intent classification.

## Decision

We selected `Qwen2.5-0.5B-Instruct`.

**Rationale:**

- **Size:** 0.5B parameters is small enough for mid-range mobile devices after 4-bit quantization.
- **Instruct Tuning:** The base model already has a strong grasp of instruction following, making it easier to fine-tune for JSON output.
- **Performance:** Outperforms similarly sized models (like Phi-1.5 or TinyLlama) on reasoning benchmarks.

## Consequences

- Requires LoRA fine-tuning to ensure strict adherence to the Sobek JSON schema.
- Inference will be performed via `llama.cpp` using Dart FFI.
- Limited reasoning capacity compared to larger models (e.g., 7B+), requiring a highly focused training dataset.
