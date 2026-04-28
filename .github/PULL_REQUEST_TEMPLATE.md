## Description

Briefly describe the changes introduced by this PR.

## Type of Change

- [ ] 🧪 Phase/ML (Dataset, training, validation)
- [ ] 📱 App/Flutter (UI, FFI, logic)
- [ ] 🔧 Infrastructure/CI (Actions, templates, docs)
- [ ] 🐛 Bug Fix

## Checklist

### Common

- [ ] I have linked the relevant Phase document in `docs/`.
- [ ] I have updated the `CHANGELOG.md` if applicable.

### ML / Dataset (`ml/`)

- [ ] I have run `python ml/data/validate_dataset.py` on all changed `.jsonl` files.
- [ ] All validations passed.

### App / Flutter (`app/`)

- [ ] I have run `flutter analyze` and fixed all issues.
- [ ] I have run `flutter test` and all tests passed.
- [ ] I have added new tests for the added functionality.

## Context (ADR)

Does this PR implement a significant architectural decision? If so, link the ADR from `docs/adr/`.
