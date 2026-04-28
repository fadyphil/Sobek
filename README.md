# Sobek

**Project Sobek** is an end-to-end machine learning engineering journey to build an on-device note intent classifier. The system classifies raw text into structured JSON entirely offline using a fine-tuned small language model (SLM) integrated into a Flutter application.

---

## 🏗️ Architecture

Sobek is organized as a monorepo, separating the machine learning development from the mobile application frontend.

### Machine Learning (`ml/`)

- **Base Model:** `Qwen2.5-0.5B-Instruct`.
- **Fine-tuning:** LoRA (Low-Rank Adaptation) for strict JSON schema adherence.
- **Quantization:** 4-bit (Q4_K_M) quantization for mobile performance.
- **Validation:** Automated Pydantic-based dataset validation to enforce schema integrity.

### Flutter Application (`app/`)

- **Framework:** Flutter (Android/iOS/Desktop).
- **Inference Engine:** `llama.cpp` integrated via Dart FFI.
- **Execution:** Heavy inference tasks run in a dedicated background isolate.

---

## 🗺️ Roadmap

We follow a 6-phase implementation plan. Each phase is documented in `docs/plan/`.

1. **Phase 0: [Conceptual Grounding](docs/plan/phase-0-conceptual-grounding.md)** - Completed.
2. **Phase 1: [Training Data Generation](docs/plan/phase-1-training-data.md)** - **Current Phase.**
3. **Phase 2: [Environment Setup](docs/plan/phase-2-environment-setup.md)** - *Pending.*
4. **Phase 3: [Fine-Tuning](docs/plan/phase-3-fine-tuning.md)** - *Pending.*
5. **Phase 4: [Export & Local Inference](docs/plan/phase-4-export-inference.md)** - *Pending.*
6. **Phase 5: [Flutter Integration](docs/plan/phase-5-flutter-integration.md)** - *Pending.*

---

## 🛠️ Quick Start

### ML Data Validation

To validate a new batch of training data:

```bash
python ml/data/validate_dataset.py ml/data/batches/batch-XX/batch-XX.jsonl
```

### Running the App

To run the Flutter application:

```bash
cd app
flutter pub get
flutter run
```

---

## 📜 Documentation

- **[Architecture Decisions (ADRs)](docs/adr/)**: Key technical choices.
- **[Dataset Progress](docs/01-dataset.md)**: Status of synthetic data generation.
- **[Contributing Guidelines](CONTRIBUTING.md)**: Branching strategy and PR standards.
- **[Changelog](CHANGELOG.md)**: History of major additions and changes.

---

## ⚖️ License

[Insert License Here]
