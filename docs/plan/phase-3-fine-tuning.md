# Phase 3 — Fine-Tuning

**Duration:** 2–3 days
**Prerequisites:** Phase 2 gate fully passed, running Colab notebook with verified tokenization and model loading
**Deliverable:** A trained LoRA adapter saved to Google Drive, with training loss curve reviewed and validated

---

## Purpose

This is where the model learns. Everything in Phase 0–2 was preparation for this phase. The quality of your data (Phase 1) and the correctness of your environment (Phase 2) now determine whether this phase succeeds.

The actual training script is short. The understanding of what it does is deep. This phase will feel fast technically — maybe 30–40 minutes of GPU time — and slow intellectually, because you must understand every hyperparameter before setting it.

---

## What Happens During Training

At the mechanical level, training works like this:

1. A batch of examples from your dataset is loaded
2. For each example, the model is shown the prompt portion and asked to predict each token of the completion, one at a time
3. The model's predicted probability distribution is compared to the actual next token — this difference is the **loss**
4. The loss is propagated backward through the network using an algorithm called **backpropagation** — this calculates how much each trainable parameter contributed to the error
5. The optimizer adjusts the trainable parameters (your LoRA adapters) by a small amount in the direction that reduces loss
6. Steps 1–5 repeat for every batch in the dataset. One complete pass = one epoch.

Note: In step 2, the prompt tokens are excluded from loss computation. You only compute loss on the completion tokens. This is critical — if you compute loss on the prompt too, the model learns to predict the prompt, which is meaningless. Only the completion (your JSON output) should be what the model is trained to generate.

---

## Hyperparameters You Must Understand

These are the values you set that control how training runs. They are not magic numbers. Each one has a specific mechanical effect.

---

### Learning Rate

The learning rate controls how large a step the optimizer takes when adjusting weights.

- **Too high:** The optimizer overshoots the minimum. Loss may spike, oscillate, or the model catastrophically forgets the base language knowledge. This is called **catastrophic forgetting** and it is irreversible.
- **Too low:** Training takes too long to converge. With only 3 epochs on 600 examples, a too-low learning rate may not move the model far enough to learn the pattern.
- **Our value:** `2e-4` (0.0002). This is standard for LoRA fine-tuning on instruction-following tasks.

Learning rate is the single most impactful hyperparameter. If training behaves unexpectedly, this is the first thing to adjust.

---

### Batch Size and Gradient Accumulation

**Batch size** is how many examples the model sees before updating its weights. Larger batches provide more stable gradient estimates but consume more memory.

With a T4 GPU and 4-bit quantization, we can fit a per-device batch size of 4. This is small. To simulate a larger effective batch size without running out of memory, we use **gradient accumulation**.

**Gradient accumulation steps:** Instead of updating weights after every batch, you accumulate the gradients across N batches and update once. If batch size is 4 and gradient accumulation steps is 4, the effective batch size is 16.

**Our values:** `per_device_train_batch_size=4`, `gradient_accumulation_steps=4`, effective batch size = 16.

---

### Number of Epochs

An epoch is one full pass through the dataset. With 600 examples and 3 epochs, the model sees every example 3 times.

- **Too few epochs:** The model doesn't learn the pattern fully
- **Too many epochs:** The model memorizes the training examples instead of generalizing (overfitting). At extreme overfitting, the model produces correct output for inputs similar to training data and garbage for anything else.

**Our value:** `num_train_epochs=3`. Standard for small datasets on narrow tasks.

---

### Warmup Steps

At the start of training, the optimizer starts with a very small learning rate and gradually increases it to the target learning rate over the warmup period. This prevents the model from making large, destructive weight updates in the first steps when gradients are noisy.

**Our value:** `warmup_steps=10`. A small warmup appropriate for a short training run.

---

### Optimizer

We use `paged_adamw_8bit` — a memory-efficient version of the Adam optimizer that stores optimizer states in 8-bit precision. The Adam optimizer maintains running statistics for each trainable parameter (mean and variance of gradients). For 1.2M trainable parameters, this adds memory. The 8-bit version reduces this overhead significantly.

---

### Max Sequence Length

The maximum number of tokens in a combined prompt + completion pair. Examples longer than this are truncated. Examples shorter are padded.

**Our value:** `max_seq_length=512`. Our inputs are short. A typical example uses 50–120 tokens. 512 gives ample headroom without wasting memory on padding.

---

## What SFTTrainer Does

`SFTTrainer` from the `trl` library wraps the entire training loop. You pass it:

- The model (with LoRA applied)
- The tokenizer
- The training dataset
- A `TrainingArguments` object containing all hyperparameters
- The dataset text field name (so it knows which field to train on)

It handles:

- Iterating over batches
- Applying the chat template to format inputs
- Computing loss only on completion tokens (not prompt tokens)
- Calling the optimizer to update weights
- Logging loss at intervals
- Saving checkpoints

You do not write the training loop manually. `SFTTrainer` abstracts it. But you must understand what it is abstracting.

---

## Reading the Training Output

During training, you will see logging output like:

```Markdown
{'loss': 2.3421, 'learning_rate': 0.0002, 'epoch': 0.1}
{'loss': 1.8932, 'learning_rate': 0.0002, 'epoch': 0.3}
{'loss': 1.2341, 'learning_rate': 0.0002, 'epoch': 0.6}
{'loss': 0.8721, 'learning_rate': 0.0002, 'epoch': 1.0}
{'loss': 0.6543, 'learning_rate': 0.0002, 'epoch': 1.5}
{'loss': 0.4821, 'learning_rate': 0.0002, 'epoch': 2.0}
{'loss': 0.3912, 'learning_rate': 0.0002, 'epoch': 2.5}
{'loss': 0.3401, 'learning_rate': 0.0002, 'epoch': 3.0}
```

**A healthy run:** Loss starts around 2.0–3.0, decreases consistently across all epochs, ends in the 0.3–0.6 range for a narrow classification task.

**A problematic run:**

- Loss starts at 2.4 and stays at 2.3 for 100 steps → data format/template issue, learning rate too low
- Loss drops to 0.08 by end of epoch 1 → overfitting, dataset too small or examples too repetitive
- Loss spikes from 0.8 to 3.2 mid-training → learning rate too high, gradient explosion

After training completes, plot the loss values on a simple graph (Claude will provide code). You should be able to describe what the curve tells you before proceeding to Phase 4.

---

## What Gets Saved

Training saves two things:

**Checkpoints:** Intermediate saves at intervals during training. Useful if training is interrupted — you can resume from the last checkpoint.

**Final adapter:** The trained LoRA adapter — a small folder containing:

- `adapter_config.json` — the LoRA configuration (rank, target layers, etc.)
- `adapter_model.safetensors` — the actual trained adapter weights

**Important:** The adapter is not a complete model. It cannot run on its own. It requires the base model (Qwen2.5-0.5B-Instruct) to operate. In Phase 4, you will merge the adapter with the base model weights to produce a standalone model.

**Save to Google Drive immediately.** Before your session ends. The adapter folder is small (a few MB). There is no reason not to save it. A lost adapter means retraining from scratch.

---

## Post-Training Validation (In-Notebook)

Before closing the notebook, run a quick inference test in Colab:

1. Load the base model + trained adapter
2. Pass 5 prompts from your test set (examples not in training data)
3. Inspect the raw output

**What you're looking for:**

- Is the output valid JSON?
- Is `type` always `"task"` or `"note"` — never any other value?
- Does the classification match your judgment?
- Is the JSON structure correct (all 5 fields present, correct types)?

If 4/5 outputs are correct and well-formed, proceed. If fewer than 4/5 are correct, document the failures — what went wrong, what the model produced vs what was expected. These notes matter for Phase 4 debugging.

---

## Gate 3 — You May Not Proceed Until You Can Answer All Of These

---

### **Section A — The Training Loop**

1. During training, the model is shown the prompt and asked to predict the completion. Why is loss computed only on the completion tokens and not the prompt tokens? What would happen if loss was computed on both?

2. Describe backpropagation in plain terms. You do not need to explain the mathematics. Explain what it calculates and what it is used for in the training loop.

3. What is the optimizer's job? What specifically does it do with the information from backpropagation?

---

### **Section B — Hyperparameters**

1. Explain the learning rate in your own words. What happens mechanically when it is set too high for our training run specifically (not generically)?

2. Our effective batch size is 16 but our per-device batch size is 4. Explain gradient accumulation: what is it doing, why does it achieve an effective batch size of 16, and why do we need it on a T4 GPU?

3. We train for 3 epochs. With 600 training examples, effective batch size of 16, what is the total number of gradient update steps across all 3 epochs? Show your calculation.

4. What is catastrophic forgetting? Under what condition in our training configuration would it be most likely to occur?

5. What is `paged_adamw_8bit`? Why do we use the 8-bit version specifically?

---

### **Section C — Loss Interpretation**

1. You observe this loss curve:
   - Epoch 0.5: 2.1
   - Epoch 1.0: 1.4
   - Epoch 1.5: 0.9
   - Epoch 2.0: 0.6
   - Epoch 2.5: 0.5
   - Epoch 3.0: 0.48

   Is this a healthy training run? What does it tell you about whether the model is learning?

2. You observe this loss curve:
    - Epoch 0.5: 2.3
    - Epoch 1.0: 0.12
    - Epoch 1.5: 0.04
    - Epoch 2.0: 0.01
    - Epoch 3.0: 0.003

    What is happening? What do you expect the model's behavior to be on inputs that are slightly different from the training data?

3. You observe this loss curve:
    - Step 10: 2.4
    - Step 20: 2.38
    - Step 50: 2.35
    - Step 100: 2.33
    - Step 150: 2.31

    Training is not converging. Name the two most likely causes and the first diagnostic step for each.

---

### **Section D — Saving and Artifacts**

1. Training finishes. You have a `./results` folder containing the LoRA adapter. What are the two files inside it and what does each contain?

2. Can you run inference using only the adapter folder? Why or why not?

3. Your Colab session ends before you save the adapter to Google Drive. What are your options?

---

### **Section E — Post-Training Validation**

1. You run your 5 test prompts after training. Three produce valid, correct JSON. One produces valid JSON but classifies a clear task as a note. One produces this output:

    ```jsonl
    {"type": "task", "priority": "high", "has_deadline": true, "deadline": "Friday", "summary": "Call dentist"} Here is the structured classification for your input.
    ```

    What is wrong with the fifth output? What likely caused it and where in your pipeline would you look first?

2. At what point do you stop iterating and accept that the model is good enough to proceed to Phase 4? What is your acceptance criterion?

---

## How To Submit Your Gate

Answer all 16 questions. Loss curve interpretation questions require your own reasoning — there are no lookup answers. Claude evaluates and either opens Phase 4 or sends you back to specific concepts.
