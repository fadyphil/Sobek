# Phase 2 — Environment Setup

**Duration:** 1 day
**Prerequisites:** Phase 1 gate fully passed, validated `.jsonl` file in hand
**Deliverable:** A running Colab notebook that loads the base model, prints its configuration, and tokenizes one sample input correctly — without training anything yet

---

## Purpose

Environment setup is not a formality. In ML work, environment failures are the most time-consuming class of failure because they look like model failures. If your library versions are incompatible, if your model loads incorrectly, if your tokenizer is misconfigured — the training will run, loss will look normal, and the model will produce wrong outputs. You will spend days debugging something that was broken before training started.

This phase is about verifying every component of the pipeline *independently* before connecting them together. You do not train anything in this phase.

---

## Google Colab — What It Is and What It Isn't

Google Colab is a cloud-hosted Jupyter notebook environment. It gives you temporary access to a GPU (T4 on free tier) and a Linux machine with Python pre-installed.

**Critical constraints you must internalize:**

- **Sessions are temporary.** When your Colab session ends (timeout, browser close, disconnection), all files on the runtime machine are gone. Your trained model, your dataset file, everything. You must save artifacts to Google Drive or download them before the session ends.
- **Free tier time limits.** Colab free tier has GPU usage quotas. You may be disconnected after a few hours of GPU use. Training will be interrupted. Plan for this.
- **RAM limits.** T4 GPU has 15GB VRAM. The system RAM is 12–13GB. Loading a model in 4-bit leaves room for training state, but barely. Do not open multiple heavy notebooks simultaneously.
- **No persistent state.** Every new session starts fresh. You must reinstall libraries every session. This is normal.

---

## Understanding the Python Libraries

Before running a single cell, you must understand what each library does. Not API documentation — conceptual purpose.

### `transformers` (HuggingFace)

The core library for loading pre-trained models and tokenizers. When you write `from transformers import AutoModelForCausalLM`, you are using this. It handles downloading model weights from HuggingFace Hub, instantiating the model architecture, and providing the tokenizer.

### `peft` (HuggingFace)

Parameter-Efficient Fine-Tuning library. This is what implements LoRA. You use it to wrap your loaded model with LoRA adapters, specifying which layers to target and what rank to use. Without PEFT, you would have to implement LoRA from scratch.

### `datasets` (HuggingFace)

A library for loading, processing, and streaming datasets. It reads your JSONL file and converts it into a format the training loop can consume. It handles batching, shuffling, and mapping functions over data efficiently.

### `bitsandbytes`

The library that implements 4-bit and 8-bit quantization. When you pass `load_in_4bit=True` to a model loader, bitsandbytes is doing the actual quantization work. It has specific CUDA version dependencies — this is one of the most common setup failure points.

### `trl` (HuggingFace)

Transformer Reinforcement Learning library — despite the name, it contains `SFTTrainer` (Supervised Fine-Tuning Trainer), which is the training loop we will use. It handles the training iterations, loss computation, logging, and checkpointing.

### `accelerate` (HuggingFace)

Handles hardware abstraction for training. Makes code work whether you're on one GPU, multiple GPUs, or CPU. Usually installed alongside transformers but sometimes needs explicit installation.

---

## The Notebook Structure

Your Colab notebook will be organized into clearly labeled cells. Each cell has one purpose. You do not combine multiple concerns into one cell. This is not aesthetic — it is diagnostic. When something breaks, you need to know exactly which component failed.

**Cell structure:**

```Markdown
Cell 1: Install libraries
Cell 2: Import libraries and verify versions
Cell 3: Mount Google Drive (for saving outputs)
Cell 4: Upload and verify dataset file
Cell 5: Load tokenizer and inspect it
Cell 6: Test tokenization on one example
Cell 7: Load base model in 4-bit
Cell 8: Inspect model configuration
Cell 9: Apply LoRA configuration (no training yet)
Cell 10: Print trainable parameter count
```

The Phase 2 deliverable is completing all 10 cells successfully, understanding what each one does, and being able to explain the output of cells 6, 8, and 10.

---

## Understanding Cell 6 — Tokenization Inspection

This is the most important verification step in Phase 2. Before training, you must confirm:

1. The tokenizer correctly encodes and decodes a sample input
2. The ChatML template is being applied correctly
3. The special tokens (`<|im_start|>`, `<|im_end|>`) are in the vocabulary
4. The token count of a typical input is reasonable (not 1500 tokens for a short prompt)

**What you will do:** Take one example from your training data, pass the prompt through the tokenizer with the chat template applied, print the token IDs, and decode them back to text. The decoded text must exactly match the ChatML-formatted version of your input. If it does not, your template alignment is broken and training will produce a corrupt model.

---

## Understanding Cell 8 — Model Configuration

When the model loads, you will print its configuration. This shows you the architecture: number of layers, hidden size, number of attention heads, vocabulary size. You do not need to memorize these values. You need to understand what they represent.

**Hidden size:** The dimensionality of the internal representation at each layer. Larger = more expressive, more memory.

**Number of attention heads:** How many parallel attention operations run at each layer. Each head learns to attend to different aspects of the context.

**Vocabulary size:** How many tokens the model knows. For Qwen2.5, this is around 151,936. This number matters because your Arabic text must tokenize to IDs within this vocabulary — if a character is out of vocabulary, it gets mapped to an `[UNK]` token and information is lost.

---

## Understanding Cell 10 — Trainable Parameters

After applying LoRA, you print the count of trainable parameters versus total parameters. The output will look something like:

```Markdown
trainable params: 1,179,648 || all params: 494,032,896 || trainable%: 0.24
```

This means you are training 0.24% of the model's parameters. The rest are frozen. This is the memory efficiency LoRA provides. You should understand why this number is so small and what the trainable parameters correspond to (the LoRA adapter matrices).

---

## LoRA Configuration Parameters You Must Understand

When you configure LoRA via PEFT, you specify:

**`r` (rank):** The rank of the adapter matrices. We will use `r=8`. This means each injected matrix pair has inner dimension 8. Lower rank = fewer trainable parameters = less expressivity. For our narrow classification task, r=8 is sufficient.

**`lora_alpha`:** A scaling factor applied to the LoRA output before adding it to the frozen weights. Convention is to set it to 2× the rank. We will use `lora_alpha=16`. Higher alpha = stronger influence of the adapters. Think of it as the volume knob on how much the LoRA adapters affect the output.

**`target_modules`:** Which layers to inject adapters into. We target `["q_proj", "v_proj"]` — the query and value projection matrices in the attention mechanism. These are the most impactful layers for behavioral adaptation.

**`lora_dropout`:** Randomly zeroes some adapter weights during training to prevent overfitting. We will use `0.05`. Standard practice.

**`bias`:** Whether to also train the bias terms. We use `"none"` — we only train the LoRA matrices.

**`task_type`:** Set to `"CAUSAL_LM"` because Qwen2.5 is a causal language model.

---

## Common Setup Failures and How to Diagnose Them

**`CUDA out of memory`**
The model or batch is too large for available VRAM. Verify 4-bit quantization is enabled. Ensure no other heavy notebooks are running.

**`bitsandbytes` CUDA version mismatch**
This is common. The error message usually contains something like `CUDA version mismatch`. Solution: explicitly install the version of bitsandbytes compatible with Colab's current CUDA version. Claude will give you the exact install command.

**`ValueError: unrecognized model type`**
Transformers version too old to recognize Qwen2.5. Solution: upgrade transformers to latest.

**Tokenizer outputs garbage on Arabic input**
The model's tokenizer supports Arabic but some older HuggingFace tokenizer loading calls miss the `trust_remote_code=True` flag that Qwen requires. This flag allows the model's custom tokenizer code to run.

**`Token indices out of range`**
Your input contains characters not in the model's vocabulary. Usually caused by special Unicode characters or emoji in training data. Strip them during data cleaning.

---

## Gate 2 — You May Not Proceed Until You Can Answer All Of These

---

### **Section A — Colab and Environment**

1. You open Colab, train a model for 2 hours, and your session times out. You reconnect. Where is your trained model? What should you have done to prevent losing it?

2. Why must you reinstall libraries at the start of every Colab session? What does this tell you about how Colab works?

3. You have 15GB of VRAM on the T4 GPU. Loading Qwen2.5-0.5B in float32 uses approximately 2GB. Loading it in 4-bit uses approximately 0.25GB. Why does 4-bit load use so much less, and what is the trade-off?

---

### **Section B — Libraries**

1. What is the role of `transformers` in your pipeline? What would break if it was not installed?

2. What is the role of `peft` specifically? Could you do LoRA fine-tuning without it? What would that require?

3. `trl` is described as a reinforcement learning library but we use it for supervised fine-tuning. What specifically do we use from `trl` and what does it do?

4. What does `bitsandbytes` do that no other library in our stack does?

---

### **Section C — Tokenization**

1. You run Cell 6. The decoded text does not exactly match your expected ChatML-formatted input. The `<|im_end|>` token is missing from the output. What are two possible causes?

2. You tokenize the input: *"اتصل بالطبيب قبل الخميس"* (Call the doctor before Thursday — Arabic). The tokenizer returns 24 token IDs for this 5-word sentence. Is this expected? Why might Arabic produce more tokens than equivalent English?

3. What is `trust_remote_code=True` and why does Qwen2.5 require it when loading the tokenizer?

---

### **Section D — LoRA Configuration**

1. You set `r=64` instead of `r=8`. What changes about your training, and is this strictly better? What is the downside?

2. `lora_alpha` is set to 16 when `r` is 8. Explain in plain terms what lora_alpha controls and why the convention is to set it to 2× rank.

3. After applying LoRA and printing trainable parameters, you see `trainable%: 0.24`. The original frozen model has 494 million parameters. Approximately how many parameters are you actually training? Does this seem right for r=8 on two attention projection layers?

4. You print the model configuration and see `vocab_size: 151936`. Your training data includes some emoji in prompts (🎯 as a bullet point). Should you remove them? Why or why not?

---

### **Section E — Diagnosis**

1. Your Cell 7 (load model) throws a CUDA out of memory error even with 4-bit quantization enabled. You have not run any other cells since starting the session. What are three things you would check?

2. Cell 10 shows `trainable%: 0.00`. LoRA has been applied but no parameters are trainable. What is the most likely cause?

---

## How To Submit Your Gate

Answer all 16 questions. Claude will verify correctness and flag gaps. Only then does Phase 3 open.
