# Prompt Log — Book of Prompts
**Version:** 1.00 | **Project:** Fourier Frequency App (Neural Signal Decoder)

This document is the mandatory "Book of Prompts" required by INSTRUCTIONS.md.
Every major AI-generated component must have an entry here recording the context, the prompt used, and any iterative refinements made before the output was accepted.

---

## Entry Format

```
### [ENTRY-NNN] — <Component Name>
**Date:** YYYY-MM-DD
**Model:** claude-sonnet-4-6
**File(s) affected:** path/to/file.py

#### Context
What problem were we solving? What constraints applied?

#### Prompt (final version used)
> The exact prompt sent to the model.

#### Refinements
1. First attempt — what was wrong or incomplete.
2. Second attempt — what was adjusted.
(Add as many as needed.)

#### Accepted Output Summary
What was actually used from the generation, and any manual edits made after.
```

---

## Log Entries

### [ENTRY-000] — Initial Planning & Vision (Pre-Development)
**Date:** 2026-05-01
**Model:** Google Gemini (via Google AI Studio) → claude-sonnet-4-6
**File(s) affected:** *(no code files — planning and orientation phase only)*

#### Context
Before any code or documentation was written, a **demo app was built on Google AI Studio** using Gemini as a personal planning and vision tool. The purpose was to prototype ideas, think through the product shape, and form a concrete mental picture of the project scope and direction before involving Claude Code. This phase had two parallel tracks:

1. **Demo app & visioning** — A working demo was assembled on Google AI Studio to explore what the app should look like, what problems it should solve, and how to structure the work at a high level.
2. **Course material analysis** — The lecturer's Moodle assignment file was fed directly into Gemini for deep analysis. Gemini extracted and explained the key technical concepts mandated by the assignment: **RNN (Recurrent Neural Networks)**, **LSTM (Long Short-Term Memory)** networks, and the software-writing standards and submission instructions embedded in the file.

Once the vision was clear and the course requirements were fully understood, the session moved to Claude Code to begin describing the existing app and building the mandatory documentation suite per INSTRUCTIONS.md.

#### Prompt (final version used)
> *(Google AI Studio — Gemini)*
> App vision prompt: open-ended planning conversation to map out the app's purpose, the ML feature set (RNN vs. LSTM classifier on a 1-second windowed signal), and the high-level architecture before writing any code.
>
> Course file analysis prompt: uploaded the Moodle assignment PDF/file and asked Gemini to analyze it — specifically to extract the LSTM and RNN requirements, the software engineering standards (SDK-first, 150-line rule, gatekeeper, etc.), and the mandatory deliverable list.

#### Refinements
1. Multiple back-and-forth turns on Google AI Studio to refine the vision until the scope felt concrete enough to hand off to Claude Code.
2. Gemini's analysis of the Moodle file clarified the distinction between RNN and LSTM expectations and confirmed the mandatory documentation structure (PRD, PLAN, TODO, Prompt Log), which later became the basis for INSTRUCTIONS.md compliance.

#### Accepted Output Summary
- A clear product vision for the Fourier Frequency App with an ML identification feature.
- A thorough understanding of the assignment's RNN and LSTM requirements derived from the Moodle file.
- Confidence in the software engineering standards required (documented in `DOCS/INSTRUCTIONS.md`).
- A decision to hand off to Claude Code starting with app description (`ENTRY-001`), followed by mandatory docs (`ENTRY-003`).

---

### [ENTRY-001] — Project Description
**Date:** 2026-05-01
**Model:** claude-sonnet-4-6
**File(s) affected:** `DOCS/Project_Description.md`

#### Context
Initial project analysis. The existing `fourier-freq-app/app.py` (380 lines, single file) needed a comprehensive written description covering architecture, signal processing concepts, UI design, and limitations.

#### Prompt (final version used)
> "analyze the app under 'fourier-freq-app'"

#### Refinements
1. First pass — returned a high-level summary. Requested a structured breakdown covering tech stack, algorithms, architecture, and UI separately.

#### Accepted Output Summary
Full 9-section Project_Description.md covering executive summary, core functionality (synthesis, visualization, discrete sampling, reset), architecture (hybrid client-server design, key constants, component structure), signal processing concepts (Fourier synthesis, continuous vs. discrete, phase relationships), UI design, dependencies, run instructions, educational use cases, and limitations table.

---

### [ENTRY-002] — ML Identification Feature (Section 10 of Project Description)
**Date:** 2026-05-01
**Model:** claude-sonnet-4-6
**File(s) affected:** `DOCS/Project_Description.md` (Section 10)

#### Context
New feature request: add a 1-second graphical window selector on the Summation Chart, plus RNN and LSTM classifiers to identify the dominant harmonic component in the selected window. The feature also required a "Both" mode with a side-by-side diff view.

#### Prompt (final version used)
> "i want you now to update the Project_Description.md file to include this feature: give the user to choose graphically a range of 1 second (from the whole 10 seconds range that we display), this 1 seconds that the user will choose is only from the summation graph. so our app's algorithms will try to find which sin graph from the 4 functions are the one from the 1 second range from the summation graph that the user chose. the app will give the user to choose between algorithms [...] 1) RNN [...] 2) LSTM [...] 3) both of them and display the 2 results and the diffs. now only update the description in the file with that feature, and explain exactly how the implementation should be."

#### Refinements
1. No refinements needed — accepted on first pass.

#### Accepted Output Summary
Section 10 added with 10 sub-sections: feature overview, UI window selection design (slider + vrect highlight, rationale for slider over free-drag), algorithm selector UI, data extraction and preprocessing (50-point slice, normalization, reshape to (1,50,1)), RNN classifier architecture and training strategy, LSTM classifier architecture and training strategy, single-algorithm results panel design, both-algorithms comparison panel with diff table, callback architecture (client vs. server split), and new dependencies.

---

### [ENTRY-003] — Mandatory Documentation Suite (PRD, PLAN, TODO, Feature PRDs)
**Date:** 2026-05-01
**Model:** claude-sonnet-4-6
**File(s) affected:** `DOCS/PRD.md`, `DOCS/PLAN.md`, `DOCS/TODO.md`, `DOCS/PRD_RNN.md`, `DOCS/PRD_LSTM.md`

#### Context
INSTRUCTIONS.md mandates that PRD.md, PLAN.md, TODO.md, and Feature PRDs must exist before development begins. None of these existed. All content was derived from Project_Description.md (Section 10 for ML features) and RNN.md / LSTM.md.

#### Prompt (final version used)
> "ok, so start building the files that needed according to INSTRUCTIONS.md, and you should always work as this file says, its CRITICAL."

#### Refinements
1. No refinements — all five documents generated and accepted on first pass.

#### Accepted Output Summary
- **PRD.md:** Problem statement, 3 personas, 8 functional requirements (FR-01–FR-08), 10 non-functional requirements, 5 measurable KPIs, out-of-scope list.
- **PLAN.md:** C4 model (all 4 levels), 6 ADRs (client-side JS, pre-trained weights, PyTorch, uv, SDK-first, Gatekeeper), API schemas for all SDK methods and both config files, full directory blueprint.
- **TODO.md:** 7 phases, 35 tasks, each with a Definition of Done.
- **PRD_RNN.md:** RNN math, FRs, architecture, parameter count (~4,484), training settings, failure modes, DoD checklist.
- **PRD_LSTM.md:** LSTM four-gate math, FRs, 2-layer architecture, parameter count (~132,612), training settings, failure modes, comparison diff schema, DoD checklist.

---

### [ENTRY-004] — README.md Full User Manual
**Date:** 2026-05-01
**Model:** claude-sonnet-4-6
**File(s) affected:** `README.md`

#### Context
The existing README.md was a placeholder outline with section descriptions instead of real content. INSTRUCTIONS.md requires a full user manual covering installation, usage, and configuration. The instruction tip in the old README specified: "Construct the README.md as a professional User Manual that adheres to the Global Versioning tracked in src/shared/version.py. Ensure the setup instructions strictly forbid pip and mandate uv."

#### Prompt (final version used)
> "now we have all these? [...] README.md: A full user manual (Installation, Usage, Configuration)."
> Triggered by gap analysis — README was identified as a placeholder.

#### Refinements
1. No refinements — generated and accepted on first pass.

#### Accepted Output Summary
Full 8-section README covering: project identity and mission, technical stack, step-by-step installation (uv only, pip forbidden), configuration guide (app_config.json, rate_limits.json, .env), complete usage guide for all features (synthesis, window selection, identification, comparison), documentation map, directory blueprint, and contributing guidelines.

---

### [ENTRY-005] — Phase 1 Shared Layer Implementation (Partial)
**Date:** 2026-05-01
**Model:** gpt-5.3-codex
**File(s) affected:** `fourier-neural-decoder/src/fourier/shared/version.py`, `fourier-neural-decoder/src/fourier/shared/constants.py`, `fourier-neural-decoder/src/fourier/shared/types.py`, `fourier-neural-decoder/tests/conftest.py`, `fourier-neural-decoder/tests/unit/test_shared_version.py`, `fourier-neural-decoder/tests/unit/test_shared_constants.py`, `fourier-neural-decoder/tests/unit/test_shared_types.py`, `DOCS/TODO.md`

#### Context
Phase 1 required foundational shared artifacts (version constant, mathematical/constants module, typed dict contracts) and corresponding unit tests. Work was constrained by command execution limits in the environment (`pwsh.exe` unavailable), so implementation focused on tasks that could be completed with high confidence from static verification.

#### Prompt (final version used)
> "ok implement what you can from phase 1, make them perfectly... choose the tasks from phase 1 that you know that you will make them perfectly and not partially"

#### Refinements
1. Scope intentionally narrowed to Shared Layer tasks that can be fully implemented without runtime command execution.
2. Added `tests/conftest.py` to ensure `src/` imports work consistently under pytest discovery.

#### Accepted Output Summary
- Implemented `version.py` with `VERSION = "1.00"`.
- Implemented `constants.py` with `RESOLUTION`, `DURATION`, `PI2`, `WAVE_NAMES`, `COLORS`, and harmonic `DEFAULTS`.
- Implemented `types.py` with `ChannelConfig`, `WindowSlice`, `ClassifierResult`, and `DiffResult`.
- Added unit tests covering required Phase 1 assertions for version/constants/types.
- Updated `DOCS/TODO.md`: marked Phase 1 tasks `1.01`–`1.21` and `1.23` as done; left `1.22` pending due to blocked Ruff execution in this environment.

---

### [ENTRY-006] — Phase 2 Config System Implementation
**Date:** 2026-05-01
**Model:** gpt-5.3-codex
**File(s) affected:** `fourier-neural-decoder/config/app_config.json`, `fourier-neural-decoder/config/rate_limits.json`, `fourier-neural-decoder/src/fourier/shared/config_loader.py`, `fourier-neural-decoder/tests/unit/test_config_loader.py`, `DOCS/TODO.md`

#### Context
Phase 2 required establishing versioned configuration files and a reusable loader with explicit key validation and failure behavior (`FileNotFoundError`, `ValueError`, and `KeyError`) aligned with project quality constraints.

#### Prompt (final version used)
> "ok implement"

#### Refinements
1. Kept loader focused and deterministic with optional path overrides so missing/malformed file behavior can be unit-tested directly.
2. Preserved strict error signaling (no silent defaults) for missing files, malformed JSON, and missing keys.

#### Accepted Output Summary
- Added `config/app_config.json` with required application keys (`resolution`, `duration`, `debug`, `host`, `port`, `version`, `window_duration`, `window_points`, `noise_default`, `noise_max`).
- Added `config/rate_limits.json` with required gatekeeper keys (`max_calls_per_minute`, `max_retries`, `retry_delay_seconds`, `timeout_seconds`).
- Implemented `config_loader.py` with `load_app_config`, `load_rate_limits`, `_load_json_file`, and `_validate_keys`.
- Added `test_config_loader.py` covering dict loads, key-value assertions, missing-file errors, malformed JSON errors, and key-validation behavior.
- Updated `DOCS/TODO.md`: marked Phase 2 tasks `2.01`–`2.26` and `2.28` done; left `2.27` pending due to blocked Ruff execution in this environment.

---

### [ENTRY-007] — Phase 3 SignalGenerator Implementation
**Date:** 2026-05-01
**Model:** gpt-5.3-codex
**File(s) affected:** `fourier-neural-decoder/src/fourier/sdk/signal_generator.py`, `fourier-neural-decoder/tests/unit/test_signal_generator.py`, `DOCS/TODO.md`

#### Context
Phase 3 required a deterministic signal generation SDK component to produce continuous and discrete sine-wave outputs from one channel configuration, with strict validation and mathematical correctness aligned to Fourier controls.

#### Prompt (final version used)
> "ok implement what needed"

#### Refinements
1. Kept `SignalGenerator` focused on one channel config to match current TODO scope and keep file size safely below the 150-line limit.
2. Added explicit helper-level tests for both continuous and discrete formulas to reduce ambiguity and ensure implementation correctness by construction.

#### Accepted Output Summary
- Implemented `SignalGenerator` with:
  - `__init__` + `_validate_config` (required keys + bounds checks),
  - `_build_time_axis`,
  - `_compute_continuous`,
  - `_build_discrete_times`,
  - `_compute_discrete`,
  - `process` returning `{"continuous": np.ndarray, "discrete": {"t": np.ndarray, "y": np.ndarray}}`.
- Added `test_signal_generator.py` covering config validation, output shape/keys, edge cases (zero amplitude, sampling-rate boundaries), phase/frequency behavior, and formula checks.
- Updated `DOCS/TODO.md`: marked Phase 3 implementation/tasks done where code is present; left command-executed verifications pending due to unavailable `pwsh.exe`.

---

### [ENTRY-008] — Phase 4 WindowExtractor Implementation
**Date:** 2026-05-01
**Model:** gpt-5.3-codex
**File(s) affected:** `fourier-neural-decoder/src/fourier/sdk/window_extractor.py`, `fourier-neural-decoder/tests/unit/test_window_extractor.py`, `DOCS/TODO.md`

#### Context
Phase 4 required extracting a 1-second window (50 points) from the composite signal, normalizing it for model input, reshaping to PyTorch-friendly dimensions, and supporting optional Gaussian noise injection with bounded sigma.

#### Prompt (final version used)
> "ok go to phase 4"

#### Refinements
1. Implemented `_slice_window` with explicit time-to-index conversion via `RESOLUTION / DURATION`, while ensuring `window_start=9.0` maps to the last valid 50-point slice.
2. Added reproducibility checks for `_inject_noise` by seeding NumPy in tests to verify deterministic behavior when expected.

#### Accepted Output Summary
- Implemented `WindowExtractor` with config validation, slicing, normalization, reshape, noise injection, and `process`.
- Added `test_window_extractor.py` covering all configured behavior in Phase 4 (validation, slicing correctness, normalization, shape/dtype, noise behavior).
- Updated `DOCS/TODO.md`: marked Phase 4 implementation/tasks done where code exists; left command-executed checks pending (`4.30`, `4.31`) and red-stage import failure task (`4.02`) unchecked.

---

*Add new entries below as development progresses.*
