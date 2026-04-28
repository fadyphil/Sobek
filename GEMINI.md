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
  - `lib/features/`: Feature-driven UI and state logic.
  - `test/`: Widget and unit tests.
- `ml/`: Machine learning assets and scripts.
  - `data/`: Training datasets and validation scripts.
  - `eval/`: Evaluation harness for model intelligence.
  - `tests/`: Tests for ML data pipeline.
- `docs/`: Comprehensive project documentation.
  - `adr/`: Architecture Decision Records.
  - `plan/`: Phased implementation roadmap.

## 🧠 Agentic Mandates

- **Skill Activation:** ALWAYS check `activate_skill` for tasks related to Flutter, Clean Code, Git Hooks, or Documentation. Never proceed without relevant expert guidance if a skill exists.
- **Parallel Orchestration:** Utilize `invoke_agent` (Generalist/Investigator) for independent batch tasks or deep research to maintain context efficiency.
- **Surgical Precision:** Every code change must be minimal and strictly scoped. Never refactor unrelated code. Use `replace` over `write_file` for existing large files.

## 📜 Development Conventions

- **Surgical Edits:** Minimum changes that align with existing styles.
- **Mounted Checks:** Always check `if (!mounted)` after `await` in `StatefulWidget` methods.
- **Immutability:** Mandatory `final` properties and `const` constructors. Use `sealed class` for state.
- **ML Schema Integrity:** Never change the 5-field schema without updating `validate_dataset.py` and prompt templates.
- **Testing:** Add or update tests in `app/test/` or `ml/tests/` for every change.
- **Documentation:** Every feature or architectural change must be reflected in `CHANGELOG.md` and relevant `docs/`.
