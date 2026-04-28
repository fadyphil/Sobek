# Phase 5 — Flutter Integration

**Duration:** 3–5 days
**Prerequisites:** Phase 4 gate fully passed, GGUF model verified locally via Ollama
**Deliverable:** A Flutter app running the GGUF model entirely on-device via Dart FFI, accepting text input and rendering structured JSON classification output — no internet required

---

## Purpose

This is the phase that makes everything you have built real. A model that runs in a Python notebook or via Ollama is not a product. A model embedded in a Flutter application, running inference in a background isolate, rendering structured output in a UI — that is a product. That is the CV artifact.

This phase is also where your existing engineering instincts are at full strength. Clean architecture, BLoC state management, freezed models, dependency injection — all of it applies here. The new territory is Dart FFI: the bridge between Dart and native C++ code. Everything else is Flutter development you already know.

---

## What Dart FFI Is

FFI stands for Foreign Function Interface. It is a mechanism that allows Dart code to call functions written in C or C++.

**Why this matters:** llama.cpp is a C++ library. The model inference engine that runs your GGUF file is written in C++. Flutter/Dart cannot call C++ directly — Dart is a managed runtime and C++ is native code. FFI is the bridge.

**How FFI works at a conceptual level:**

1. The C++ library is compiled into a shared library file (`.so` on Android, `.dylib` on macOS/iOS, `.dll` on Windows)
2. Dart uses FFI to load the shared library at runtime
3. Dart declares the C function signatures using Dart's `ffi` package syntax
4. Dart calls those functions as if they were Dart functions — the FFI layer handles marshalling (converting Dart types to C types and back)

**What `llama_cpp_dart` does:** This package wraps llama.cpp's C API with Dart FFI bindings. You do not write FFI code manually. You use the package's Dart API, which internally calls the C functions. But you must understand FFI to debug when things break, because FFI errors are cryptic without the mental model.

---

## Isolates — Why Inference Cannot Run on the Main Thread

In Flutter, the main isolate runs the UI. Every frame must complete in approximately 16ms (for 60fps). Model inference on a 0.5B model takes anywhere from 200ms to 2000ms depending on device hardware.

If you run inference on the main isolate, the UI freezes for every inference call. This is not just bad UX — it will cause Android to show "Application Not Responding" warnings on slower devices.

**Inference must run in a background isolate.** Dart isolates are separate execution environments — they do not share memory with the main isolate. Communication between isolates happens via message passing (ports). `llama_cpp_dart` is designed to run in an isolate.

**How this affects your architecture:**

- The BLoC emits a loading state immediately when input is submitted
- A background isolate is spawned (or a persistent one is reused) to run inference
- When inference completes, the result is passed back to the main isolate via a message
- The BLoC receives the result and emits the success state with the parsed JSON

---

## Architecture

This is a new standalone Flutter project — not integrated into Osserva or Valoqui. Clean, focused, demonstrable on its own.

```Markdown
lib/
├── core/
│   ├── di/                      # Dependency injection (get_it)
│   └── inference/               # LlamaEngine wrapper and isolate management
├── features/
│   └── classifier/
│       ├── data/
│       │   ├── models/          # ClassificationResult (freezed)
│       │   └── repositories/    # ClassifierRepository implementation
│       ├── domain/
│       │   ├── entities/        # ClassificationResult entity
│       │   └── usecases/        # ClassifyInputUseCase
│       └── presentation/
│           ├── bloc/            # ClassifierBloc / ClassifierEvent / ClassifierState
│           └── screens/         # ClassifierScreen
└── main.dart
```

**`ClassificationResult` (freezed model):**

```dart
@freezed
class ClassificationResult with _$ClassificationResult {
  const factory ClassificationResult({
    required String type,
    String? priority,
    required bool hasDeadline,
    String? deadline,
    required String summary,
  }) = _ClassificationResult;

  factory ClassificationResult.fromJson(Map<String, dynamic> json) =>
      _$ClassificationResultFromJson(json);
}
```

---

## Model Bundling Strategy

Your GGUF file needs to be accessible to the app at runtime. There are two strategies:

### Option A — Bundle with App Assets

Add the GGUF file to `assets/` in `pubspec.yaml`. Flutter packages it inside the APK/IPA.

**Pros:** No download required, works fully offline from first launch
**Cons:** APK size increases by the model size (~300MB for Q4_K_M). Google Play has a 100MB base APK limit — you would need to use Android App Bundle with asset packs, or TestFlight/direct distribution for iOS.

### Option B — Download on First Launch

Ship the app without the model. On first launch, download the GGUF file to the app's documents directory.

**Pros:** Small initial APK size
**Cons:** Requires internet on first launch, adds complexity (download progress, failure handling, storage management)

**For this project:** Use Option A with direct distribution (no Play Store). The goal is a demonstrable portfolio artifact, not a production deployment. An APK with the model bundled is simple and entirely offline.

---

## The Inference Flow (Step by Step)

1. User types text into the `TextField` and taps the classify button
2. `ClassifierBloc` receives `ClassifyInputEvent(rawText: "remind me to call dentist Thursday")`
3. BLoC emits `ClassifierState.loading()`
4. `ClassifyInputUseCase.call(input)` is invoked
5. `ClassifierRepository.classify(input)` is invoked
6. `LlamaEngine.infer(prompt)` is called — this runs in a background isolate
7. The prompt is formatted with the ChatML template before being passed to the engine
8. The engine runs inference, returns raw string output
9. Raw output is parsed with `jsonDecode()` wrapped in a try-catch
10. On success: `ClassificationResult.fromJson()` produces the entity
11. Repository returns `Right(result)` (fpdart Either)
12. BLoC emits `ClassifierState.success(result: result)`
13. UI rebuilds, renders the classification card

**Step 9 is a critical failure point.** If the model produces any text outside the JSON object, `jsonDecode()` will throw. You must sanitize the raw output before parsing: trim whitespace, extract only the JSON substring between `{` and `}` using a simple regex or string search.

---

## The System Prompt

When calling `LlamaEngine.infer()`, you pass a fully formatted ChatML prompt. The system message is critical — it is your primary mechanism for enforcing JSON-only output behavior at inference time.

**System prompt:**

```Markdown
You are a precise note and task classifier. 
Given raw text input, you output ONLY a valid JSON object. 
No explanations. No preamble. No text after the JSON.
The JSON must have exactly these fields: type, priority, has_deadline, deadline, summary.
Valid values for type: "task" or "note".
Valid values for priority: "low", "medium", "high", or null.
has_deadline is always a boolean.
deadline is a string when has_deadline is true, null otherwise.
summary is a clean, concise restatement.
```

This system prompt, combined with `temperature=0` and the model's fine-tuned behavior, enforces structured output.

---

## BLoC Design

**Events:**

```dart
@freezed
class ClassifierEvent with _$ClassifierEvent {
  const factory ClassifierEvent.classifyInput(String rawText) = ClassifyInput;
  const factory ClassifierEvent.reset() = Reset;
}
```

**States:**

```dart
@freezed
class ClassifierState with _$ClassifierState {
  const factory ClassifierState.initial() = Initial;
  const factory ClassifierState.loading() = Loading;
  const factory ClassifierState.success(ClassificationResult result) = Success;
  const factory ClassifierState.error(String message) = Error;
}
```

The UI listens to state and renders accordingly:

- `initial` → empty prompt screen
- `loading` → input disabled, loading indicator
- `success` → classification result card with all 5 fields displayed
- `error` → error message with retry option

---

## UI Design Principles

This is a portfolio artifact. The UI must be clean and professional. Minimal, readable, focused.

**Screen structure:**

- Top: App name/title
- Middle: Large `TextField` for input, multiline
- Below field: "Classify" button — disabled during loading
- Result area: A card that appears after successful classification

**Result card fields to display:**

- Type as a colored badge: blue for note, orange for task
- Priority as a subtle label (only shown for tasks)
- Deadline indicator (only shown when `has_deadline` is true)
- Summary in large, readable text
- A small "copy JSON" icon that puts the raw JSON on clipboard

**Why the UI matters for a portfolio:** A recruiter who runs your app has 60 seconds of attention. If the UI is ugly or unclear, they don't engage long enough to understand the technical depth. The UI is marketing for the engineering.

---

## Gate 5 — You May Not Proceed to Completion Until You Can Answer All Of These

---

### **Section A — Dart FFI**

1. In plain terms, what does FFI stand for and what problem does it solve for our project?

2. A `.so` file is generated during the build process. What is it, what language is the code inside it written in, and how does Dart access functions inside it?

3. If `llama_cpp_dart` already wraps the FFI calls for you, why do you still need to understand FFI conceptually?

---

### **Section B — Isolates**

1. Why would running inference on the main isolate cause visible problems in the app? Be specific about what the user would see.

2. Isolates do not share memory. How does the inference result get back to the main isolate once the background isolate completes?

3. You decide to create a new isolate for every inference call vs. reusing one persistent isolate. What is the trade-off?

---

### **Section C — Architecture**

1. `LlamaEngine` is in `core/inference/`. It could have been in `features/classifier/data/`. Why is it in `core`? What architectural principle guides this decision?

2. The repository returns `Either<Failure, ClassificationResult>` using fpdart. The inference might fail in two distinct ways: the model produces invalid JSON, or llama.cpp throws a native exception. How do you represent these two different failure modes as distinct `Failure` subtypes?

3. Why must the ChatML template be applied in the repository/data layer rather than in the BLoC or UI? What separation of concerns principle governs this?

---

### **Section D — Model Bundling and Output Handling**

1. You bundle the GGUF model in `assets/`. The model is 300MB. What is the consequence for APK size and what constraint does this impose on distribution method?

2. The model returns this raw string:

    ```json
    {"type": "task", "priority": "high", "has_deadline": true, "deadline": "Friday", "summary": "Submit report"} 
    
    Note: I've classified this as a high-priority task.
    ```

    Write the Dart code that safely extracts only the JSON portion from this string before passing to `jsonDecode`. Handle the case where no valid JSON is found.

3. `jsonDecode()` succeeds but `ClassificationResult.fromJson()` throws because the model returned `"priority": "urgent"` instead of a valid enum value. Where in your architecture does this exception get caught, and what does the BLoC emit?

---

### **Section E — The Complete System**

1. Your app is running on a device with no internet connection. A user types a prompt and taps Classify. Trace every step from button tap to result displayed on screen — name every component involved in order, and describe what each one does.

2. Describe in 100+ words why this project is technically significant for someone applying to an enterprise software role (VOIS, IBM, PwC). What specifically demonstrates competence that a typical Flutter developer portfolio does not?

---

## **Final Reflection (mandatory, minimum 200 words)**

1. Looking back across all five phases: what was the single concept that was hardest to internalize and why? What finally made it click? What would you do differently if you started this project again from Phase 0? Be precise — this is not a feelings question, it is an engineering retrospective.

---

## Project Completion Checklist

Before this project is considered done:

- [ ] Flutter app runs on physical Android device
- [ ] Model runs fully offline — airplane mode test passes
- [ ] All 5 classification fields render correctly in UI
- [ ] BLoC test coverage: at least ClassifyInput event → loading → success and ClassifyInput event → loading → error paths
- [ ] README.md written for the repository explaining the architecture, the model, the pipeline, and setup instructions
- [ ] GitHub repository public with meaningful commit history (not a single "initial commit" dump)
- [ ] You can demo the app and explain any component to a technical interviewer without preparation

---

## The README You Will Write

The project README is part of the deliverable. It must contain:

1. One-paragraph project description (what it does, not how)
2. Architecture diagram or ASCII diagram of the pipeline: fine-tune → merge → GGUF → Dart FFI → Flutter
3. Tech stack table: model, training framework, inference engine, Flutter packages
4. Setup instructions: how to build and run
5. A "How it works" section explaining the inference pipeline in plain language
6. Known limitations (honest)

This README is what a recruiter reads. It must be written for someone who understands Flutter but has never done ML. It must make the technical depth immediately visible.
