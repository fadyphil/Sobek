# Project Sobek — Technical Context

Project Sobek is an end-to-end machine learning engineering journey to build an on-device note intent classifier. The system classifies raw text into structured JSON entirely offline using a fine-tuned small language model integrated into a Flutter application.

## 🏗️ Architecture & Stack

### Machine Learning (ML)

- **Base Model:** `Qwen2.5-0.5B-Instruct` (decoder-only architecture).
- **Fine-tuning:** LoRA (Low-Rank Adaptation) using ChatML prompt templates.
- **Quantization:** 4-bit quantization (Q4_K_M) for memory-efficient on-device inference.
- **Schema:** Strict 5-field JSON output:
  - `type`: "task" or "note"
  - `priority`: "low", "medium", "high", or `null` (notes must have `null` priority)
  - `has_deadline`: boolean
  - `deadline`: string or `null`
  - `summary`: string (concise, third-person)

### Flutter Application

- **Framework:** Flutter (managed in the `app/` directory).
- **Inference Engine:** `llama.cpp` integrated via Dart FFI.
- **Execution:** Inference runs in a background isolate to maintain UI responsiveness.

## 📁 Project Structure

- `app/`: Flutter application codebase.
  - `lib/main.dart`: Main entry point and likely Dart FFI integration logic.
- `ml/`: Machine learning assets and scripts.
  - `data/`: Training datasets (`.jsonl` files) organized by batches.
  - `data/validate_dataset.py`: Python script to enforce schema and value constraints.
  - `training/`: (Reserved for training scripts and checkpoints).
- `docs/`: Comprehensive project documentation and phased roadmap.
  - `00-concept.md`: Conceptual grounding of the ML choices.
  - `plan/`: Detailed multi-phase implementation plan.

## 🛠️ Key Commands & Workflow

### ML Data Validation

Validate new training batches before inclusion in the master dataset:

```bash
python ml/data/validate_dataset.py ml/data/batches/batch-XX/batch-XX.jsonl
```

### Flutter Development

Standard Flutter commands apply within the `app/` directory:

```bash
cd app
flutter pub get
flutter run
flutter test
```

### Road-map (Phases)

Project progress is tracked via phases in `docs/plan/`:

- **Phase 0:** Conceptual Grounding (Complete)
- **Phase 1:** Training Data Generation
- **Phase 2:** Environment Setup
- **Phase 3:** Fine-Tuning
- **Phase 4:** Export & Local Inference
- **Phase 5:** Flutter Integration

## 📜 Development Conventions

- **Surgical Edits:** When modifying the Flutter app, ensure minimal changes that align with existing styles.
- **Mounted Checks:** Always check `if (!mounted)` after `await` in `StatefulWidget` methods.
- **Immutability:** Prefer `final` properties and `const` constructors where possible.
- **ML Schema Integrity:** Never change the 5-field schema without updating the `validate_dataset.py` script and the fine-tuning prompt template.
- **Testing:** Add or update tests in `app/test/` for every feature change.
