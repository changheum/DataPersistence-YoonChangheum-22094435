# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Scope

This is the **DataPersistence PoC** module — one of four independent PoC repositories feeding into the `SampleOrderSystem` integration. The scope of this repo is strictly limited to:

> **JSON 기반 데이터 저장·불러오기 구조 구현 (CRUD 포함)**

Do not implement business logic beyond data persistence (no order state transitions, no production-line scheduling, no monitoring). That belongs in the integration repo.

The domain entities (from `PRD.md`) relevant to this PoC are:
- **Sample (시료)**: `sample_id`, `name`, `avg_production_time`, `yield`
- **Order (주문)**: `order_id`, `sample_id`, `customer`, `quantity`, status (`RESERVED` / `REJECTED` / `PRODUCING` / `CONFIRMED` / `RELEASE`)

## Commands

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. --cov-report=term-missing

# Run a single test file
pytest tests/test_<module>.py

# Run a single test by name
pytest tests/test_<module>.py::test_function_name -v
```

Target coverage: as close to 100% as possible. Check coverage after every Green phase.

## Development Workflow (TDD + Phase Gates)

All development follows a strict **Red → Green → Refactor** cycle driven by `PRD.md`.

**Phase gate protocol:**
1. Write failing tests (Red) → show user → **wait for approval**
2. Write minimal production code to pass (Green) → run tests → **wait for approval**
3. Refactor (apply OCP/SOLID where warranted) → verify tests still pass → **wait for approval**
4. On approval: `git push` to remote

Never proceed to the next phase without explicit user approval. Update `PRD.md` with phase status as each phase completes.

## Available Agents

Use these agents at the appropriate moments — do not skip them:

| Agent | When to invoke |
|-------|---------------|
| `tdd-ocp-implementer` | Starting a new feature from PRD requirements |
| `code-quality-validator` | After Green or Refactor phase completes |
| `prd-compliance-reviewer` | Before requesting phase approval from user |
| `planning-consistency-validator` | After all phases complete, before final push |

Agent definitions live in `agents/`.

## Architecture

```
DataPersistence-YoonChangheum-22094435/
├── PRD.md                  # Requirements and phase tracking
├── agents/                 # Agent instruction files
├── src/                    # Production code (create during implementation)
│   ├── repository.py       # Abstract base for storage operations
│   └── json_repository.py  # Concrete JSON file implementation
└── tests/                  # pytest test files
    └── test_*.py
```

Key design constraint from `tdd-ocp-implementer`: storage backends must be extensible without modifying existing classes (OCP). Define an abstract `Repository` interface first; `JsonRepository` is one concrete implementation.

## Git

Branch: `master`. Remote: `github.com/YoonChangheum/DataPersistence-YoonChangheum-22094435`

Push only after user explicitly approves the completed phase. Commit message should reference the phase (e.g., `Phase 1: Red - failing tests for Sample CRUD`).
