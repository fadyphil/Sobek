# Phase 0 — Conceptual Grounding

**Status:** Complete  
**Duration:** ~4 days  
**Gate:** Passed

---

## What This Phase Was

Before writing a single line of training data or code, I needed a mental model of what I was actually building. ML fails silently — a model trains, loss decreases, output looks plausible, and the model is still completely wrong. You cannot catch that without understanding what is happening at each layer.

This phase was about building that understanding from scratch. I had Python basics and no ML background.

---

## What a Language Model Actually Is

A language model is a probability machine. It processes integers, not text. The component that converts between them is called a **tokenizer** — it maps words (or subword fragments) to integer IDs and back.

The model I am fine-tuning — Qwen2.5-0.5B-Instruct — is a **decoder-only** model. It generates tokens left to right, one at a time, each conditioned on all previous tokens. It cannot look ahead. This is the architecture used by GPT, Llama, Mistral, and Qwen — all modern instruction-following models.

The alternative is **encoder-decoder** (T5, mT5), which reads the full input first and then generates. Used for translation and summarization. Not what we are using, and fine-tuning methodology differs between the two.

One consequence of tokenization that matters for this project: Arabic and non-Latin scripts tokenize inefficiently. A 5-word Arabic sentence can produce 20+ token IDs where an equivalent English sentence produces 6–8. This means Arabic training examples consume more of the model's context window and require slightly more careful handling in the dataset.

---

## Fine-Tuning vs RAG — The Most Important Distinction

Fine-tuning adjusts **behavior**, not knowledge. Showing the model 600 examples of "raw text → structured JSON" teaches it a response pattern. It does not inject new facts.

This means fine-tuning is the wrong tool if you want a model to know specific facts, documents, or updateable information. The right tool for that is **RAG (Retrieval Augmented Generation)** — injecting relevant context at inference time. Fine-tuning cannot be "updated" without retraining from scratch.

For this project: the behavior I am instilling is "given raw text input, always respond with a valid JSON object following a specific 5-field schema." That is a pattern, not a fact. Fine-tuning is the correct tool.

---

## LoRA — Why It Exists and How It Works

Full fine-tuning of a model modifies every parameter — billions of floating point numbers. This requires enormous GPU memory. Not viable on a free Colab T4.

LoRA (Low-Rank Adaptation) solves this by exploiting a mathematical property: the weight updates needed during fine-tuning are **low-rank**. Instead of training the full weight matrix, you train two much smaller matrices whose product approximates the full update.

Concretely: if a weight matrix is (4096 × 4096) = 16M values, LoRA with rank 8 trains (4096 × 8) + (8 × 4096) = 65,536 values instead. The original weights are **frozen** — they never change. Only the small adapter matrices are trained.

At inference time, the adapters are mathematically merged into the original weights. No runtime overhead.

**Parameters I chose and why:**

| Parameter | Value | Reason |
| --- | --- | --- |
| Rank (r) | 8 | Sufficient for narrow classification; higher rank = more parameters = more memory |
| lora_alpha | 16 | Convention: 2× rank. Controls how strongly adapters influence output. |
| Target layers | q_proj, v_proj | Query and value projections in the attention mechanism — highest behavioral impact |
| lora_dropout | 0.05 | Prevents overfitting on small dataset |

---

## Quantization

Model weights are stored as floating point numbers. Default precision: float32 (32 bits per value). A 500M parameter model at float32 ≈ 2GB just for weights.

4-bit quantization stores each weight in 4 bits. Memory drops by ~8×. The cost: slight numerical imprecision. For a classification task with a constrained output space (5 fields, limited enum values), this loss is negligible.

Two distinct uses of quantization in this project:

- **Training quantization** — loading the model in 4-bit during fine-tuning to fit in T4 VRAM. Handled by `bitsandbytes`.
- **Inference quantization** — GGUF format (Q4_K_M) for on-device deployment. Handled by llama.cpp tooling.

Same concept, different tools, different purposes.

---

## The Prompt Template

Qwen2.5-Instruct uses **ChatML** format. The model was trained to generate tokens after seeing `<|im_start|>assistant`. Using any other template — or missing a single tag — causes the model to not know where instruction ends and response begins. Training will appear to succeed, loss will decrease, and the model will produce malformed output on real prompts. Silent failure.

Correct ChatML structure for one training example:

```ChatML
<|im_start|>system
You are a note and task classifier. Output only valid JSON.<|im_end|>
<|im_start|>user
remind me to call the dentist before Thursday<|im_end|>
<|im_start|>assistant
{"type": "task", "priority": "medium", "has_deadline": true, "deadline": "Thursday", "summary": "Call dentist"}<|im_end|>
```

Rule: always verify the template on the model card at HuggingFace before writing training data.

---

## Training Loss

Loss measures how wrong the model's predictions are on training data. Specifically: the difference between the probability the model assigned to the correct next token versus all other tokens.

- **High loss (2.0–3.0):** Model is very wrong — expected at the start of training
- **Low loss (0.3–0.6):** Model is confident and correct on training patterns
- **Near-zero loss (0.01–0.08):** Likely overfitting — model memorized examples rather than learning the pattern

A healthy loss curve starts high, decreases consistently across epochs, and levels off. It does not drop to near-zero rapidly, and it does not stay flat.

**Epoch:** One full pass through the training dataset. Training for 3 epochs = every example seen 3 times.

---

## The Full Pipeline (Conceptual)

Raw training examples → tokenized into integers using ChatML template → fed to the frozen base model with LoRA adapters attached → model predicts next tokens in the completion → loss computed only on completion tokens (not prompt) → loss propagated backward through the adapter matrices (backpropagation) → optimizer adjusts adapter weights by a small amount → repeat for every batch, every epoch.

After training: adapter merged into base model → exported to GGUF format with Q4_K_M quantization → loaded into Flutter via Dart FFI → inference runs in background isolate → raw output sanitized → JSON parsed into typed Dart model → rendered in UI.

The base model provides general language understanding. LoRA teaches it one narrow behavior. Quantization makes it portable. FFI makes it callable from Dart. The architecture keeps inference off the main thread.

---

## Resources Used

- Sam Witteveen — LoRA/PEFT video
- Umar Jamil — "LoRA explained" (YouTube)
- Qwen2.5-0.5B-Instruct model card: <https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct>
- LoRA paper abstract: <https://arxiv.org/abs/2106.09685>
