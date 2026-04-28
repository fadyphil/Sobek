# Contributing to Sobek

Thank you for contributing to Project Sobek! This is a specialized monorepo that blends Machine Learning and Flutter. To keep the project stable and its history clean, please follow these guidelines.

## Branching Strategy

We use a phase-aligned branching strategy to make the project's evolution clear and portfolio-friendly.

* `main`: Always stable. Represents the latest validated progress.
* `phase/<number>-<name>`: The "Epic" branch for a specific roadmap phase (e.g., `phase/1-dataset`).
* `feature/<name>`: Small tasks or UI features within a phase.
* `ml/<name>`: ML-specific tasks (e.g., `ml/data-pipeline`).
* `app/<name>`: Flutter-specific tasks (e.g., `app/ffi-integration`).

**Workflow:**

1. Branch from the current active `phase/*` branch.
2. Complete your task.
3. Open a Pull Request into the `phase/*` branch.
4. Once the phase is complete, the `phase/*` branch is merged into `main`.

## Development Setup

### ML Environment (`ml/`)

* Ensure Python 3.10+ is installed.

* Always run the validation script before submitting data changes:

  ```bash
  python ml/data/validate_dataset.py ml/data/batches/batch-XX/batch-XX.jsonl
  ```

### Flutter Environment (`app/`)

* Ensure the latest Flutter stable version is installed.

* Run analysis and tests:

  ```bash
  cd app
  flutter analyze
  flutter test
  ```

## Pull Requests

Please use the provided PR template. Every PR should:

1. Explain **why** the change is needed.
2. Provide evidence that validation scripts or tests were run.
3. Reference any relevant Architecture Decision Records (ADRs).
