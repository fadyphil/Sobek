# Phase 4 — Export & Local Inference

**Duration:** 2 days
**Prerequisites:** Phase 3 gate fully passed, trained LoRA adapter saved to Google Drive
**Deliverable:** A quantized GGUF model file running locally on your machine via Ollama, producing correct JSON output from test prompts

---

## Purpose

The model you have trained lives in a format designed for Python-based ML training frameworks. It cannot run in a Flutter app. It requires the HuggingFace `transformers` library, Python, and a GPU — none of which exist in a mobile environment.

This phase converts your trained model into a format called **GGUF** — a portable, compressed binary format designed to run on consumer hardware, including CPUs, with no Python dependency. GGUF is what makes on-device inference on mobile possible.

This phase also serves as a quality gate. You will run your model locally and evaluate its output before investing time in Flutter integration. If the model is not producing reliable JSON here, you address it now, not in Phase 5.

---

## What Needs to Happen

The process has four steps:

1. **Merge** the LoRA adapter weights into the base model weights, producing a single complete model
2. **Convert** the merged model from HuggingFace format (PyTorch `.safetensors`) to GGUF format using llama.cpp tooling
3. **Quantize** the GGUF model (apply inference quantization — Q4_K_M format)
4. **Run** the quantized GGUF model locally using Ollama, verify output

---

## Step 1 — Merging the Adapter

The LoRA adapter you saved is not a standalone model. It is a small set of weight matrices that modify the base model's behavior. Before exporting, you must mathematically merge the adapter into the base model weights.

**What merging does:** Takes each frozen base weight matrix and the corresponding LoRA adapter matrices, computes the update: `W_new = W_original + (B × A) × scale`, and produces a new weight matrix that incorporates the adapter's learned behavior. The result is a standard HuggingFace model — no more adapter, no more base model separately — just one combined model.

**Why you must merge before converting:** GGUF conversion tools (llama.cpp) expect a standard HuggingFace model directory. They do not understand the PEFT adapter format.

**This step runs in Colab** before your session ends, because it needs the base model loaded. The merged model is saved to Google Drive. It will be approximately 1GB (the full model in float16).

---

## Step 2 — GGUF Format

GGUF stands for GPT-Generated Unified Format. It is a binary file format developed by the llama.cpp project as a replacement for the older GGML format.

**Why GGUF:**

- Single file — the entire model (weights, config, tokenizer, everything) in one `.gguf` file
- No Python dependency — runs via C++ (llama.cpp)
- Designed for CPU inference on consumer hardware
- Supported by Ollama, LM Studio, and dozens of other local inference tools
- Supports multiple quantization levels in the same ecosystem

**What information is inside a GGUF file:**

- Model architecture metadata (number of layers, hidden size, context window)
- Tokenizer vocabulary and merges
- All model weight tensors
- Configuration values (attention heads, etc.)

A GGUF file is fully self-contained. Give someone the file, they can run the model. No additional downloads required.

---

## Step 3 — GGUF Quantization Formats

When converting to GGUF, you choose a quantization level. These are named formats:

| Format | Bits per weight (approx) | File size (0.5B model) | Quality loss |
| --- | --- | --- | --- |
| F16 | 16 bits | ~1GB | None (reference) |
| Q8_0 | 8 bits | ~500MB | Minimal |
| Q4_K_M | 4 bits (mixed) | ~300MB | Low |
| Q4_0 | 4 bits | ~290MB | Moderate |
| Q2_K | 2 bits | ~190MB | High |

**We will use Q4_K_M.** The "K_M" suffix means it uses a more sophisticated quantization scheme (k-quantization, medium variant) that preserves quality better than the simpler Q4_0. For a narrow classification task, Q4_K_M output is essentially indistinguishable from F16.

**The trade-off spectrum:** Lower bit depth = smaller file = faster inference = more quality loss. For a task where the output space is constrained (5 fields, limited values), quality loss tolerance is high. You could arguably go to Q2_K and still get acceptable results. We use Q4_K_M as a reasonable balance.

---

## Step 4 — Ollama

Ollama is a tool that manages and runs GGUF models locally. It wraps llama.cpp inference with a clean CLI and an OpenAI-compatible REST API.

**What Ollama provides:**

- `ollama run <model>` — interactive CLI chat with a model
- `ollama serve` — runs a local REST API server on port 11434
- Model management (list, delete, import custom GGUF files)

**To use your custom GGUF with Ollama**, you create a `Modelfile` — a simple text file that tells Ollama how to load and configure your model:

```Markdowwn
FROM ./your-model-q4_k_m.gguf

SYSTEM """
You are a note and task classifier. Given raw text input, output only a valid JSON object with exactly these fields: type, priority, has_deadline, deadline, summary. Output nothing else.
"""

PARAMETER temperature 0
PARAMETER top_p 0.9
```

**Temperature 0 is critical.** Temperature controls randomness in token selection. Temperature 0 means the model always picks the single most probable next token — deterministic, no randomness. For structured JSON output, you want zero randomness. Temperature > 0 can cause the model to occasionally sample a wrong token, breaking JSON structure.

---

## Evaluating Output Quality

Once Ollama is running your model, you systematically test it with a structured evaluation set.

**Prepare 20 test prompts** that were never in your training data. Include:

- 5 clear tasks with deadlines
- 5 clear tasks without deadlines
- 5 clear notes
- 5 edge cases (ambiguous, Arabizi, fragmented text)

**Evaluation criteria:**

| Check | Pass Condition |
| --- | --- |
| Valid JSON | Output parses without error using `json.decode()` |
| Correct structure | All 5 fields present, no extras |
| Type accuracy | Classification matches human judgment |
| Schema compliance | No invalid enum values |
| Deadline consistency | `has_deadline`/`deadline` never contradictory |
| No extra text | Output contains only the JSON object |

**Acceptance threshold:** 18/20 passing all checks. If below 18/20, document the failures, identify the pattern (all failures on notes? all on Arabizi?), and determine whether it is a data gap that would require adding training examples and retraining.

---

## Common Conversion Failures

**`KeyError: 'model_type'` during conversion**
The merged model directory is missing `config.json` or the config is incomplete. The merge step did not save correctly. Re-run the merge.

**Output contains text after the JSON**
The model generates the JSON correctly but then continues generating additional tokens. This is a stop token issue. In the Ollama Modelfile, add `PARAMETER stop "<|im_end|>"` to tell Ollama to stop generation when it encounters the end-of-turn token.

**Output is truncated mid-JSON**
The `max_tokens` or context length is too small. Increase the generation limit in Ollama.

**Model loads but outputs only in English for Arabic inputs**
Base model tokenization is correct but Arabic training examples were underrepresented in your dataset. May require adding more Arabic training examples and retraining.

**Ollama import fails with GGUF format error**
The GGUF conversion used an incompatible version of llama.cpp. Update llama.cpp to the latest commit and reconvert.

---

## Gate 4 — You May Not Proceed Until You Can Answer All Of These

---

### **Section A — Merging**

1. Why must the LoRA adapter be merged with the base model before GGUF conversion? What would happen if you tried to convert the adapter folder directly?

2. After merging, the resulting model file is approximately 1GB. Before merging, the base model was approximately 1GB and the adapter was approximately 3MB. Why is the merged model the same size as the base model and not 1GB + 3MB?

3. The merge operation computes `W_new = W_original + (B × A) × scale`. In plain terms, what is this doing — what does the final weight represent?

---

### **Section B — GGUF Format**

1. What is the advantage of the GGUF format being a single file? How does this contrast with the HuggingFace model format, which uses multiple files?

2. What information is contained inside a GGUF file that makes it fully self-contained for inference?

3. A GGUF model runs via llama.cpp, which is C++ code. In Phase 5, your Flutter app also needs to run llama.cpp. What is the mechanism that allows Dart/Flutter to call C++ code?

---

### **Section C — Quantization**

1. You have four options: F16, Q8_0, Q4_K_M, Q2_K. You are deploying on a mid-range Android phone with 4GB RAM. Which format would you choose and why? What trade-offs are you making?

2. Explain in plain terms what happens when a weight stored in float16 (16 bits) is quantized to 4 bits. What information is lost and why does this not always matter for classification tasks?

3. The "K_M" in Q4_K_M means it uses k-quantization at the medium variant. Without knowing the mathematical details, what does this imply about Q4_K_M compared to Q4_0?

---

### **Section D — Ollama and Inference**

1. Why is `temperature 0` critical for our task? What would happen with `temperature 0.8`?

2. Your model is producing correct JSON but with extra text after the closing brace:

    ```json
    {"type": "task", "priority": "high", "has_deadline": true, "deadline": "Friday", "summary": "Submit report"} I've classified this input as a high-priority task.
    ```

    What causes this and exactly what do you change in the Modelfile to fix it?

3. You test with 20 prompts. The results:
    - All 5 task-with-deadline prompts: ✅
    - All 5 task-without-deadline prompts: ✅
    - 4/5 note prompts: ✅, 1 classified as task
    - Edge cases: 2/5 ✅, 3 produced invalid JSON

    Score: 16/20. You are below the acceptance threshold of 18/20. Describe your diagnosis process: what do you investigate first, and what two changes to the training pipeline might fix this?

---

### **Section E — Pipeline Coherence**

1. Trace the full journey of your model from trained adapter to running locally in Ollama. Name every file format it passes through and what transformation is applied at each step.

2. You want to share your model with another developer so they can run it. What single thing do you send them and what do they need installed on their machine to use it?

---

## How To Submit Your Gate

Answer all 14 questions. Question 12 in particular is evaluated on your diagnostic reasoning, not just the answer. Phase 5 opens only after all questions pass.
