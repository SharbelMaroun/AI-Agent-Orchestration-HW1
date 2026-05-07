# Software Submission Guidelines (V3.00) - Comprehensive Summary
**Based on: "Guidelines for Writing Professional Software at the Highest Level of Excellence" by Dr. Yoram Segal (March 26, 2026)**

This document provides a highly detailed summary of the 39-page professional software development guidelines PDF. It covers every mandatory standard, workflow, and architectural constraint required for software excellence, particularly when working with AI agents (Vibe Coding).

---

## 1. The Era of AI and AI-Assisted Development (Vibe Coding)
- **Professional Engineering:** Software is not just about writing code; it's about life-cycle management, documentation, testing, and continuous maintenance.
- **The AI Paradigm Shift:** You act as a *Senior Software Architect* orchestrating AI agents. Using AI can multiply productivity 16x.
- **The #1 Rule of Coding:** NEVER start coding without architecture, design, and requirements documents. AI agents must be fed clear specs, not guessed prompts.

## 2. Mandatory Documentation & Project Structure
Development **cannot begin** until all foundational documents exist in the `/docs` folder.

### Required Files:
1. **`README.md` (Root):** Must include installation steps, usage instructions, architecture overview, configuration guide, contribution guidelines, and licensing.
2. **`docs/PRD.md` (Product Requirements Document):** Defines the target audience, the problem to solve, measurable KPIs, acceptance criteria, and user stories.
3. **`docs/PLAN.md` (Architecture & Planning):** Contains C4 Models (Context, Container, Component, Code), ADRs (Architectural Decision Records), API definitions, and data schemas.
4. **`docs/TODO.md` (Task Tracking):** A strict, granular task list containing owners, statuses (not started/in-progress/done), and a clear "Definition of Done".
5. **Feature PRDs (`docs/PRD_<mechanism>.md`):** Separate PRD files for core algorithms, machine learning models, or complex logic (e.g., `PRD_auth.md`, `PRD_search.md`).

### The Golden Workflow:
1. Write PRD -> Approved.
2. Write PLAN -> Approved.
3. Write TODO -> Approved.
4. Begin Development (TDD).

## 3. The 150-Line Rule
- **Absolute Limit:** No Python file may exceed 150 lines of code (excluding comments/docstrings).
- **Solution:** If a class or file is too large, split it into auxiliary modules, base classes, or mixins. This forces single-responsibility principles and high modularity.

## 4. Architecture & SDK-First Design
- **SDK-First:** The codebase must be engineered as an SDK package (`src/sdk/`). Interfaces like CLI, GUI, or REST APIs are merely external consumers of the SDK.
- **OOP (Object-Oriented Programming):** Use structured classes. Every core component must use the "Building Block Pattern":
  - `__init__()` for initialization.
  - `_validate_config()` for internal validation.
  - `process()` as the main execution method.

## 5. The API Gatekeeper
- **Centralized Network Access:** All external API requests (e.g., LLM APIs, external data sources) MUST pass through a dedicated `Gatekeeper` class.
- **Responsibilities:** Rate limiting, automatic retries (exponential backoff), circuit breaking, timeout handling, and cost/token tracking. 

## 6. Strict Quality & Tooling Requirements
- **TDD (Test-Driven Development):** Follow the Red-Green-Refactor loop using `pytest`.
- **Test Coverage:** Global test coverage MUST be **at least 85%**. Both `unit` and `integration` tests are strictly required.
- **Linter (Ruff):** `Ruff` is the mandatory linter. **Zero violations** are permitted.

## 7. Package Management & Git
- **Package Manager:** `uv` is the exclusively approved package manager (`uv sync`, `uv run`). Native `pip` and `venv` are forbidden.
- **Dependency Locking:** Always lock dependencies using `uv.lock`.
- **Git workflow:** Use feature branches, descriptive commit messages, and Pull Requests for all changes.

## 8. Security & Configuration Protocol
- **Zero Hardcoding:** Never hardcode URLs, credentials, paths, limits, or timeouts in the code. All parameters must be stored in external configuration files (e.g., `config/setup.json`, `config/rate_limits.json`).
- **Secrets Management:** Use a `.env` file for API keys and tokens. The `.env` file must never be committed; a `.env-example` with dummy placeholders must be committed instead.
- **Global Versioning:** Create a single source of truth for versioning (starting at `1.00`) inside a dedicated `src/<package>/shared/version.py`, synchronized across the project.

## 9. Logging & Error Handling
- Use Python's built-in `logging` module with a standardized format (Time, Level, Component, Message).
- Include comprehensive error handling with meaningful exceptions.

## 10. Advanced Execution (Multithreading & Multiprocessing)
- Applications must define clear strategies for parallelism:
  - **Multiprocessing:** Use for CPU-bound tasks (e.g., heavy mathematical computations, image processing).
  - **Multithreading:** Use for I/O-bound tasks (e.g., simultaneous network/API requests). Strict thread-safety mechanisms must be implemented.

## 11. Research, Deployment, & Analysis
- **Jupyter Notebooks:** Use `notebooks/analysis.ipynb` for mathematical proofs (formatted with LaTeX), sensitivity analysis, algorithmic exploration, and rendering high-resolution graphs.
- **Cost Analysis:** If using AI APIs, provide a detailed table tracking token consumption (inputs/outputs) and exact cost estimations.
- **Prompt Engineering Logs:** Maintain a log or "Book of Prompts" mapping iterations of complex prompts used within the application.

## 12. Final Directory Structure Blueprint
All software projects must strictly adhere to the following architecture:
```text
project-root/
├── src/                  # Source code
│   └── <package>/
│       ├── __init__.py   # Exposes allowed SDK classes/functions
│       ├── sdk/          # SDK layer (Single entry point)
│       ├── services/     # Business logic
│       ├── shared/       # Shared utilities (config, version.py)
│       ├── constants.py
│       └── gatekeeper.py # API gatekeeper
├── tests/                # unit/ & integration/
├── docs/                 # PRD, PLAN, TODO, Feature PRDs
├── config/               # setup.json, rate_limits.json
├── data/                 # Input data
├── results/              # Experiment results
├── assets/               # Images, graphs, resources
├── notebooks/            # Jupyter Notebooks for analysis
├── pyproject.toml        # Configured for `uv`
├── .env-example          # Placeholders for secrets
├── .gitignore            # Ignore secrets and data
└── README.md             # Mandatory root manual
```

## 13. Code Design and Documentation Best Practices
- **Variables & Functions:** Must be strictly descriptive.
- **DRY Principle:** Do Not Repeat Yourself. No duplicated code.
- **Single Responsibility Principle:** Functions must be short and handle a single task.
- **Docstrings & Comments:** Every function, class, and module must have a Docstring. Comments must explain "WHY", not "WHAT".

## 14. Final Submission Checklist
Before a project is considered complete according to these guidelines, verify the following:
- [ ] **Documentation:** `PRD`, Architecture, `README`, API Documentation, and Prompts Book/Log exist.
- [ ] **Code Quality:** File sizes $\le 150$ lines, properly commented, consistent styling.
- [ ] **Security:** No secrets in code, `.env-example` provided, `.gitignore` configured correctly.
- [ ] **Testing:** Minimum 85% test coverage, error handling robust, edge cases tested, CI/CD automated reports running.
- [ ] **Research & Analysis:** Sensitivity analysis, exploratory parameters (`notebooks/analysis.ipynb`), high-resolution visualization graphs.
- [ ] **Cost Analysis:** Token consumption table and detailed cost calculation provided.
- [ ] **Extensibility:** Explicit injection points (hooks), API-first design.
- [ ] **Git:** Clean Git commit history, branches correctly used, proper licensing and attribution included.