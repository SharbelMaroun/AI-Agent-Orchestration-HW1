# Instructions

## 1. The Pre-Development Firewall (Mandatory Docs)
Development cannot begin until these documents exist in the `/docs` folder:
- **PRD.md:** Defines user problems, target audience, measurable KPIs, and functional/non-functional requirements.
- **PLAN.md:** Includes C4 Model diagrams (Context, Container, Component, Code), ADRs (Architectural Decision Records), and API schemas.
- **TODO.md:** A granular task list with "Definition of Done" for every phase.
- **Feature PRDs:** Separate PRDs (e.g., `PRD_auth.md`) for every major algorithm or technical mechanism.

## 2. Structural & Architectural Standards
The app must be structured as a professional Python package:
- **SDK-First Design:** All business logic must be encapsulated in an SDK layer. The UI (CLI/GUI) is merely a "consumer" that calls the SDK.
- **The 150-Line Rule:** No code file may exceed 150 lines (excluding comments). If it does, logic must be split into mixins, auxiliary modules, or base classes.
- **API Gatekeeper:** ALL external API calls must pass through a central Gatekeeper class that handles rate limiting (via config), retries, and logging.
- **Building Block Pattern:** Every core class must include an `__init__` for setup, a `process()` method for execution, and a `_validate_config()` method for internal checks.

## 3. Strict Quality & Tooling Requirements
Claude must use the mandated Python toolchain:
- **Package Management:** `uv` is the only permitted manager (e.g., `uv sync`, `uv run`). `pip` and `venv` are forbidden.
- **Zero-Violation Linting:** All code must pass Ruff checks with zero errors.
- **TDD & Coverage:** Use a Red-Green-Refactor workflow with `pytest`. Global test coverage must be at least 85%.
- **Prompt Engineering Log:** Maintain a "Book of Prompts" documenting the context, prompt, and iterative refinements for every major AI-generated component.

## 4. Security & Configuration Protocol
- **Hardcoding Ban:** Zero hardcoded URLs, timeouts, or limits in the source code. These must live in versioned JSON/TOML files.
- **Secret Management:** Use `.env` for all keys/tokens (never committed) and provide a `.env-example` with dummy values.
- **Global Versioning:** Track versions (starting at 1.00) in a dedicated `src/<package>/shared/version.py` file and within configuration JSONs.

## 5. Deployment & Analysis (The Excellence Factor)
- **Parallelism:** Use Multiprocessing for CPU-bound tasks and Multithreading for I/O-bound tasks with strict thread-safety.
- **Research Notebook:** A Jupyter Notebook detailing sensitivity analysis, mathematical proofs (using LaTeX), and high-resolution visualizations.
- **Cost Analysis:** A precise table tracking Token usage (Input vs. Output) and total estimated costs for AI service integrations.

## Final Project Directory Blueprint
```text
project-root/
├── src/<package>/
│   ├── sdk/          # Single entry point
│   ├── services/     # Business logic
│   ├── shared/       # version.py, constants.py
│   └── gatekeeper.py # API Gatekeeper
├── tests/            # Unit & Integration (85% coverage)
├── docs/             # PRD, PLAN, TODO, Prompt Log
├── config/           # setup.json, rate_limits.json
├── notebooks/        # Research & Analysis
├── pyproject.toml    # Managed via uv
└── README.md         # Full User Manual
```
