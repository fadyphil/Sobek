# 💎 Flutter & Dart: Golden Standards & Clean Code

This document defines the uncompromising standards for Flutter and Dart development within Project Sobek. By adhering to these principles, we ensure the codebase remains maintainable, testable, highly performant, and resilient—especially critical when bridging high-level UI with low-level C/C++ ML inferences.

---

## 1. 🏛️ Architectural Boundaries (Clean Architecture)

We strictly separate concerns to ensure that UI components do not handle business logic, and business logic does not know about the UI or the low-level FFI implementation.

* **Feature-Driven Organization:** Group files by feature (e.g., `lib/features/intent_parser/`), not by layer (`lib/models/`, `lib/controllers/`).
* **The 3 Layers:**
    1. **Presentation (UI & State):** Widgets and state holders (e.g., Riverpod Notifiers/Blocs).
    2. **Domain (Business Logic):** Pure Dart entities, repositories interfaces, and use cases. **No Flutter dependencies here.**
    3. **Data (Infrastructure):** API clients, local storage, and the `llama.cpp` FFI bindings.
* **Dependency Rule:** Dependencies must point *inward* toward the Domain layer. The UI depends on Domain; Data depends on Domain.

---

## 2. 🛡️ Immutability & Type Safety

Dart 3 provides powerful tools for safe, predictable code. We enforce immutability to prevent race conditions, especially across Isolates.

* **Everything `final`:** Unless a variable explicitly needs to mutate, declare it `final`.
* **Deep Immutability:** Use packages like `freezed` or `equatable` for complex data models to generate `copyWith` methods and value equality.
* **`const` Everywhere:** If a Widget or object can be `const`, it must be `const`. This drastically reduces the garbage collector's workload.
* **Sealed Classes & Exhaustive Matching:** Use Dart 3 `sealed class` for states (e.g., `Loading`, `Success`, `Error`). Use `switch` statements to force exhaustive checking at compile time.

```dart
// ✅ GOOD: Exhaustive state matching
sealed class IntentState {}
class IntentLoading extends IntentState {}
class IntentSuccess extends IntentState { final IntentData data; IntentSuccess(this.data); }
class IntentError extends IntentState { final String message; IntentError(this.message); }

Widget build(BuildContext context) {
  return switch (state) {
    IntentLoading() => const CircularProgressIndicator(),
    IntentSuccess(:final data) => IntentResultView(data: data),
    IntentError(:final message) => ErrorView(message: message),
  };
}
```

---

## 3. 🚀 Performance Optimization & Isolates

Given that Sobek runs a local LLM, the UI thread (Main Isolate) must remain completely unblocked to guarantee 60/120fps.

* **Widgets vs. Methods:** Always extract complex UI into smaller `StatelessWidget` classes rather than helper methods (e.g., `_buildHeader()`). Classes can be marked `const` and cache their contexts; methods cannot.
* **Isolate Everything Heavy:** FFI calls to `llama.cpp` and heavy JSON parsing must run in a background `Isolate`.
* **Use `TransferableTypedData`:** When moving large strings or raw bytes (like model outputs) across the Isolate boundary, use `TransferableTypedData` to prevent expensive memory copying.
* **RepaintBoundaries:** Wrap constantly updating widgets (like a typing indicator or a streaming ML output) in a `RepaintBoundary` to prevent the entire screen from repainting.

---

## 4. 🧪 Testability & Golden Standards

"Code without tests is bad code. Code that cannot be tested is worse."

* **F.I.R.S.T Principles:** Tests must be Fast, Independent, Repeatable, Self-Validating, and Timely.
* **Dependency Injection:** Never instantiate infrastructure (like the ML Engine) directly inside a UI or Domain class. Always inject it via the constructor or a DI framework so it can be mocked during testing.
* **Unit Tests:** 100% coverage mandated for the Domain layer (parsing, validation, formatting).
* **Golden Tests:** Use Golden Tests (e.g., via the `alchemist` or `golden_toolkit` packages) for complex UI components to catch pixel-level regressions automatically in CI.

---

## 5. 🛑 Error Handling (The Functional Approach)

Throwing exceptions is essentially a `GOTO` statement. It breaks control flow and hides failures.

* **Return Errors as Values:** Use the `Result` or `Either` monad (via packages like `fpdart` or `dartz`) for all repository and use-case methods.
* **No Silent Failures:** Never write an empty `catch (e) {}` block. If an error is caught, it must be logged to our observability platform, or gracefully handled.
* **FFI Crash Boundaries:** C/C++ crashes can take down the whole Dart VM. Wrap FFI calls carefully and handle memory allocations/deallocations (`malloc`/`free`) using strict `try/finally` blocks to prevent memory leaks.

```dart
// ✅ GOOD: Returning errors as values
Future<Either<Failure, IntentData>> parseIntent(String input) async {
  try {
    final rawJson = await _mlEngine.runInference(input);
    final data = IntentData.fromJson(rawJson);
    return Right(data);
  } catch (e) {
    return Left(InferenceFailure(e.toString()));
  }
}
```

---

## 6. 🧹 Clean Code & Readability Rules

Following Uncle Bob's Clean Code principles translated for Flutter:

* **Small Functions:** Functions should do one thing. If a method exceeds 20 lines, consider refactoring.
* **No Magic Numbers:** Replace raw numbers with named constants (e.g., `const double kDefaultPadding = 16.0;`).
* **Descriptive Naming:** Prefer `calculateIntentConfidenceScore()` over `calcConf()`. Variables should reveal intent.
* **Early Returns:** Avoid deep nesting. Return early to keep the "happy path" at the outermost indentation level.

```dart
// ❌ BAD: Deep nesting
void processInput(String? input) {
  if (input != null) {
    if (input.isNotEmpty) {
      if (input.length > 5) {
        // do work
      }
    }
  }
}

// ✅ GOOD: Early returns
void processInput(String? input) {
  if (input == null || input.isEmpty) return;
  if (input.length <= 5) return;
  
  // do work
}
```

---

## 7. 👮 Proactive Enforcement (Tooling)

We rely on tools, not memory, to enforce these standards.

* **Strict Linting:** We use a highly opinionated `analysis_options.yaml`. We recommend adopting `very_good_analysis` or `flutter_lints` combined with custom rules.
  * *Rule to enable:* `require_trailing_commas` (for clean git diffs).
  * *Rule to enable:* `avoid_print` (force the use of a proper logging package like `logger`).
* **Custom Lints:** For project-specific rules (e.g., "Do not import `dart:ffi` inside `lib/features/UI`"), we will implement `custom_lint`.
* **CI Gate:** As defined in our `app-ci.yml`, `flutter analyze` must pass with **0 warnings and 0 infos** before a PR can be merged.
