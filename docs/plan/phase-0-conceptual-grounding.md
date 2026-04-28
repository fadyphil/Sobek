# Phase 0 — Conceptual Grounding

**Duration:** 3–4 days
**Prerequisites:** None
**Deliverable:** The ability to answer every gate question in your own words, without notes.

---

## Purpose

You are entering a domain you have never worked in. The biggest mistake a developer makes when entering ML is treating it like a new framework — something you learn by doing before you understand. That works in Flutter because you can feel what's broken. In ML, things fail silently. A model trains, loss decreases, output looks plausible, and the model is still completely wrong. You cannot catch that without conceptual clarity.

This phase builds the mental model you will use to reason about every decision in every phase that follows.

---

## What You Need To Understand

---

### Concept 1 — What a Language Model Actually Is

A language model is a probability machine. Given a sequence of tokens, it predicts the most likely next token. That is the entire mechanism. Everything else — answering questions, writing code, classifying intent — is a consequence of this one operation being performed on a model trained on enough data with enough parameters.

**Tokens are not words.** The model does not see text. It sees integers. The word "submit" might be token 4821. The word "submitting" might be tokens 4821 and 287. A tokenizer is the component that converts text to integers and back. This matters because:

- Arabic and non-Latin scripts often tokenize inefficiently — one word becomes 8–12 tokens instead of 1–2
- If your training data and your inference prompt use different tokenization strategies, output is garbage
- Token limits (context windows) are limits on integers, not words

A **decoder-only** model (which Qwen2.5 is) generates tokens left to right, one at a time, each token conditioned on all previous tokens. It cannot look ahead. This is the architecture used by GPT, Llama, Mistral, Qwen — essentially all modern chat and instruction models.

An **encoder-decoder** model (like T5 or mT5) reads the full input first, builds an internal representation, then generates output. These are used for translation and summarization. We are not using one. Understanding the distinction matters because fine-tuning methodology differs.

---

### Concept 2 — What Fine-Tuning Is and Is Not

A pre-trained model has already seen billions of tokens. It knows language, grammar, reasoning patterns, and general world knowledge. What it does not know is:

- Your specific output format (structured JSON)
- Your specific task framing (note vs task classification)
- The exact response style you need

**Fine-tuning adjusts behavior, not knowledge.** You are not teaching the model new facts. You are teaching it a new pattern of responding. When you show it 600 examples of "raw text input → structured JSON output," you are reinforcing one narrow neural pathway until it becomes the model's dominant response to that input style.

This is why fine-tuning for factual knowledge is a mistake. If you want the model to know about your personal files, your company's documents, or anything specific and updateable — that is RAG (Retrieval Augmented Generation). RAG injects facts at inference time. Fine-tuning cannot be "updated" — you'd have to retrain. Never confuse these two tools.

**What fine-tuning actually modifies:** The weights of the model — billions of floating point numbers that together determine the probability distribution over the next token. Full fine-tuning adjusts all of them. This requires enormous compute and memory. For our purposes it is not an option.

---

### Concept 3 — LoRA: Why It Exists and How It Works

LoRA stands for Low-Rank Adaptation. It is a technique for fine-tuning large models without modifying their original weights at all.

**The problem it solves:** A 7B parameter model stores billions of float32 numbers. Modifying all of them during fine-tuning requires more GPU memory than most researchers have access to.

**The insight:** The changes you want to make to a model's weights during fine-tuning are actually low-rank. This is a mathematical property. It means the weight update matrix — which would normally be enormous — can be closely approximated by two much smaller matrices multiplied together. If the original weight matrix is (4096 × 4096), instead of training 16 million values, you train two small matrices: (4096 × 8) and (8 × 4096) — 65,536 values. You choose the rank (the 8 in this example). Lower rank = fewer parameters = less memory, but less expressive power.

**How it works in practice:**

1. The original model weights are frozen. They do not change. Ever.
2. Small adapter matrices are injected into specific layers (typically the attention mechanism's query and value projections — `q_proj` and `v_proj`).
3. Only the adapter matrices are trained.
4. At inference time, the adapters are mathematically merged with the original weights — this costs nothing extra at runtime.

**What this means for you:** You are not modifying a 500M parameter model. You are training a tiny set of adapters on top of it. This fits in Colab's free T4 GPU.

---

### Concept 4 — Quantization

A model's weights are stored as numbers. By default, high precision: float32 (32 bits per number). A 500M parameter model at float32 = 2GB just for the weights. Not counting the memory needed during training for gradients and optimizer states.

**Quantization reduces precision to save memory.** 4-bit quantization stores each weight in 4 bits instead of 32. Memory usage drops by 8x. The cost is a small loss in numerical precision — meaning the model's outputs are very slightly different from the full-precision version. For our task (classification with structured output), this difference is negligible.

**bitsandbytes** is the library that handles 4-bit quantization loading in Python. When you see `load_in_4bit=True` in a training script, this is what it does.

**Important distinction:** Training quantization (loading the model in 4-bit during fine-tuning to save VRAM) is different from inference quantization (GGUF format, which you will use in Phase 4). You will use both — different purposes, different tools, same underlying concept.

---

### Concept 5 — The Prompt Template

The model was pre-trained and instruction-tuned on data formatted in a specific structure. Qwen2.5-Instruct uses a format called ChatML:

```ChatML
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
remind me to call the dentist before Thursday<|im_end|>
<|im_start|>assistant
{"type": "task", "priority": "medium", "has_deadline": true, "deadline": "Thursday", "summary": "Call dentist"}<|im_end|>
```

**Why this matters absolutely:** The model was trained to respond after seeing `<|im_start|>assistant`. If your training data uses a different template — even one missing tag — the model does not know where the instruction ends and the response begins. Training loss will not reflect this problem. The model will train, appear to work, and produce malformed output on real prompts. This is one of the most common silent failures in fine-tuning.

**Rule:** Always use the exact template the base model was trained with. Never invent your own format. Always verify by checking the model card on HuggingFace before writing a single training example.

---

### Concept 6 — Training Loss

Loss is a number that measures how wrong the model's predictions are on your training data. Specifically, it measures the difference between the probability the model assigned to the correct next token versus the probability of all other tokens.

- **High loss:** The model is very wrong. It assigns low probability to the correct token.
- **Low loss:** The model is confident and correct on training data.
- **Loss should decrease over training.** This is the sign that the model is learning the pattern.

**What a healthy loss curve looks like:** Starts high (2.0–3.0 range), decreases consistently across the first epoch, levels off by the second or third epoch.

**Warning signs:**

- Loss does not decrease at all → learning rate may be too high and overshooting, or data is malformed
- Loss decreases to near zero very fast → overfitting — the model memorized your 600 examples rather than generalizing the pattern
- Loss spikes and drops erratically → learning rate too high, or gradient explosions

**Epoch:** One complete pass through your entire training dataset. Training for 3 epochs means the model sees every example 3 times.

---

### Concept 7 — What PEFT Is

PEFT stands for Parameter-Efficient Fine-Tuning. It is the HuggingFace library that implements LoRA (and other efficient fine-tuning methods). When you import from `peft` in Python, you are using this library. LoRA is the method. PEFT is the software tool that implements it.

---

## Resources

**Watch (concepts only — do not copy code):**

- Sam Witteveen — LoRA/PEFT video (your identified resource)
- "LoRA explained" by Umar Jamil — YouTube search this exact phrase

**Read:**

- The Qwen2.5 model card on HuggingFace: `https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct`
- The LoRA original paper abstract only (not the full paper): `https://arxiv.org/abs/2106.09685` — read the abstract and introduction, understand the problem it solves, stop there

---

## Gate 0 — You May Not Proceed Until You Can Answer All Of These

Answer every question below in your own words. Not copy-pasted. Not paraphrased from a source. Your own understanding, your own phrasing. If you need to think for 10 minutes to formulate an answer, that is correct behavior.

---

### **Section A — The Model**

1. A language model does not understand text. What does it actually process, and what is the name of the component that performs the conversion between text and what the model processes?

2. What is the difference between a decoder-only model and an encoder-decoder model? Which category is Qwen2.5, and why does it matter for our project?

3. Why does Arabic text often consume more tokens than an equivalent English sentence? What is the practical consequence of this for training data size?

---

### **Section B — Fine-Tuning vs RAG**

1. You want to fine-tune a model to always respond in JSON. You also want the model to know the contents of your personal Obsidian notes. Which of these two goals should be achieved via fine-tuning, and which via RAG? Explain why.

2. A colleague says "I'll fine-tune the model on my company's latest documentation so it stays up to date." Identify the specific problem with this plan and explain what they should do instead.

3. Fine-tuning modifies behavior, not knowledge. What does this mean concretely for our project — what behavior are we trying to instill?

---

### **Section C — LoRA**

1. What problem does LoRA solve? Answer in terms of memory — what would happen without it?

2. The original model weights are frozen during LoRA fine-tuning. What exactly does "frozen" mean — what changes and what does not?

3. What is a rank in the context of LoRA? What is the practical trade-off of choosing a lower rank versus a higher rank?

4. LoRA injects adapters into specific layers of the model. Which layers do we typically target, and why those layers specifically (what are they responsible for inside the attention mechanism)?

---

### **Section D — Quantization**

1. What is the difference between float32 and 4-bit quantization in terms of memory usage? Calculate: if a 500M parameter model at float32 uses approximately 2GB, roughly how much does 4-bit quantization reduce this to?

2. We use 4-bit quantization during training. We also use quantization in Phase 4 (GGUF). Are these the same thing? What is each one for?

3. Quantization introduces a trade-off. What is lost, and why is that loss acceptable for our specific task?

---

### **Section E — Prompt Template**

1. What is ChatML format? Write out the correct structure of a single training example for our project — a raw text input and its expected JSON output — using the exact ChatML template.

2. Why does misalignment between the training template and the inference prompt cause silent failure rather than a visible error?

3. Where do you verify the correct prompt template for a specific model before writing training data?

---

### **Section F — Training Loss**

1. In plain terms, what does a loss value of 2.4 mean? What does a loss value of 0.3 mean?

2. Your training loss drops from 2.3 to 0.08 within the first 50 steps. What is likely happening and why is it a problem?

3. Your training loss stays flat at 2.3 for 200 steps without decreasing. Name two possible causes.

4. What is an epoch? If you have 600 training examples and train for 3 epochs with a batch size of 4, how many total gradient update steps will occur? Show your reasoning.

---

## **Final Conceptual Question**

1. Describe the entire fine-tuning pipeline from raw text data to a trained model in your own words — not the code, not the steps, but the *what is happening at each stage* in terms of the concepts you have learned in this phase. Minimum 150 words. This answer should demonstrate that the phases connect into a coherent whole in your mind.

---

## How To Submit Your Gate

Write your answers in a separate document or paste them directly to Claude. Do not answer selectively — all 21 questions must be answered before the gate opens. Claude will evaluate each answer, identify gaps, and tell you exactly which concepts need reinforcement before you proceed to Phase 1.
