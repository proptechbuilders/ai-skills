---
name: test
description: Professional-grade guide for creating, refactoring, and reviewing deterministic tests across web applications (backend, frontend, scraping, and image/data pipelines). Use when writing tests, improving branch coverage, and enforcing behavior-first quality gates.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Test Skill

Use this skill when creating, refactoring, or reviewing tests in any web application domain.

## Goals (priority order)

1. **Correctness first**: verify behavior contracts, not implementation trivia.
2. **Determinism**: no flaky network/time/randomness/ordering side effects.
3. **Fast feedback**: minimal fixtures, targeted runs first, no sleep-based tests.
4. **Maintainability**: shared harnesses/factories over duplicated setup.
5. **Coverage quality**: cover critical branches and invariants, not just line count.

---

## Required Workflow

1. **Write a micro-spec first (3 bullets minimum)**
   - Preconditions
   - Action
   - Expected result (including error code/type when relevant)

2. **Define contract boundaries**
   - Inputs, outputs, and side effects.
   - Authorization, validation, and boundary behavior.
   - Persisted/emitted artifacts (DB rows, files, queues, emails, cache entries, events).

3. **Create/extend fixture manifest**
   - Use scenario-specific fixture names:
     - `create_valid.json`
     - `create_invalid_schema.json`
     - `fetch_timeout.json`
     - `image_corrupt.png`
   - Prefer deterministic paths:
     - `__tests__/fixtures/<domain>/<feature>/<scenario>`

4. **Use shared test harnesses/factories**
   - Keep feature test files thin.
   - Centralize repetitive setup and assertions in helpers/builders.
   - Parameterize for providers/sources that share the same contract.

5. **Add branch + regression tests intentionally**
   - Cover happy + error + boundary branches.
   - Add regression tests for real bugs by reproducing bug conditions first.

6. **Run targeted, then full suite**
   - Fast, focused run while iterating.
   - Full suite before commit; CI command should match local behavior.

---

## Core Rules

### 1) Every test must be able to fail
Invert the expected outcome mentally; confirm the test would catch wrong behavior.

### 2) Arrange -> Act -> Assert (exactly one Act)
One behavior per test, one primary action call.

### 3) Assert contracts, not internals
Test public API/observable behavior, not private methods, internals, or incidental call ordering.

### 4) Name tests as scenario + expected outcome
Examples: `rejects upload when mime type is unsupported`, `returns 403 for non-admin user`.

### 5) Cover happy path + error path + boundary path
Each feature should include all three.

### 6) Verify side effects for mutations
For writes/mutations, assert persisted or emitted side effects in addition to return values.

### 7) Assert stable error contracts
Prefer error code/type/status over exact message text unless message is contractually required.

### 8) Use specific assertions
Prefer exact value/shape/length/type checks over `truthy`/`defined` style assertions.

### 9) No branching in test bodies
No `if/switch/ternary` controlling assertions in a single test.

### 10) Expect failures explicitly
Use explicit exception/rejection assertions; never swallow errors.

### 11) Keep tests isolated and parallel-safe
Fresh setup per test; avoid shared mutable global state.

### 12) Pin all nondeterminism
Control time, randomness, UUIDs, ordering, and concurrency-sensitive timing.

### 13) Use realistic, minimal test data
Purpose-built fixtures with production-like constraints; override only what matters.

### 14) Mock boundaries, not the SUT
Mock network/filesystem/third-party services, not the core logic under test.

### 15) Test invariants where applicable
Validate properties such as idempotency, authorization, referential integrity, and monotonic counters.

---

## Domain Guidance

### Backend/API
- Assert status code + response contract + persistence effects.
- Include permission-denied, validation, and missing-prerequisite scenarios.

### Frontend/UI
- Test user-visible behavior and accessibility semantics.
- Assert loading, error, empty, and success states explicitly.

### Scraping/ETL
- Fixture-drive parser behavior for valid/missing/malformed input.
- Separate transport, parse, and save failures into distinct tests.

### Image/Document Processing
- Use deterministic fixtures (golden files/checksums/metadata).
- Cover corrupt input, unsupported format, and size/limit boundaries.

---

## Anti-Patterns (Reject Immediately)

| Anti-Pattern | Why It Fails |
|---|---|
| Tautological test | Mirrors implementation instead of validating intended behavior |
| Mocking the SUT | Mocks the answer, creating circular tests |
| Testing setup only | Proves helpers, not production logic |
| Loose assertions | `truthy/defined/not null` where specific checks are needed |
| Hidden branching in tests | Causes conditional assertions and silent misses |
| Swallowed errors | Hides failure paths and creates false positives |
| Order-coupled assertions | Brittle unless ordering is contractual |
| Snapshot-by-default testing | Hides intent and increases noisy diffs |
| Over-mocking | Tests mock wiring more than behavior |
| Debug noise in committed tests | Reduces signal (`console.log`, prints) |
| Real external calls in normal runs | Creates flakiness and environment coupling |

---


## Codebase Structure Discipline (File & Directory Size)

Apply these rules when adding/refactoring tests and related support code.

### Do
- Keep files focused and small (single responsibility per file).
- Split files that grow beyond ~300-500 lines (hard cap ~800).
- Split directories that exceed ~10-15 cohesive files.
- Organize by domain/feature (`auth/`, `billing/`, `scraper/image-pipeline/`), not junk drawers.
- Mirror source architecture in tests (test structure should reflect module boundaries).
- Group validation, service behavior, and persistence assertions in the same domain folder.
- Extract cohesive submodules when one file mixes multiple concerns.
- Keep configuration/setup separate from business-behavior assertions.
- Use barrel/index files sparingly and only when import ergonomics clearly improve.
- Enforce clean dependency direction; avoid upward/circular imports in test utilities.

### Don't
- Don't create god files (1000+ lines with mixed responsibilities).
- Don't use dumping-ground directories (`utils/`, `helpers/`, `misc/`, `common/`) without domain scoping.
- Don't mix unrelated domains in one folder.
- Don't split arbitrarily; split by cohesive responsibility.
- Don't hide breaking changes inside broad structural refactors.
- Don't allow deep nesting without reason (>3-4 levels is usually a smell).
- Don't let test files greatly exceed the complexity of code under test without review.

### Structural Smells (refactor triggers)
- A file requires multiple screens to understand one behavior.
- A directory cannot be described in one sentence.
- Frequent merge conflicts in the same large file.
- Imports span a full screen.
- One folder contains unrelated domains (`auth`, `billing`, `email`, `scheduler`).

---

## Generic Test Layout

```text
<project>/
└── __tests__/
    ├── _helpers/          # shared setup, builders, custom matchers
    ├── fixtures/          # domain + feature + scenario fixtures
    ├── unit/              # pure deterministic tests
    ├── integration/       # boundary and persistence tests
    └── e2e/               # critical user workflows only
```

---

## Review Checklist

Reject any test that fails one or more checks:

1. Includes a clear precondition/action/expected-result intent
2. Calls production behavior (not only mocks/helpers)
3. Uses specific, contract-level assertions
4. Would fail if logic were inverted
5. Contains no branching that conditionally skips assertions
6. Controls time/randomness/ordering/network deterministically
7. Verifies mutation side effects
8. Covers at least one negative path for critical behaviors
9. Uses scenario + expected-outcome naming
10. Keeps one behavior focus per test
11. Avoids debug noise and sleep-based waits
12. Remains parallel-safe and independent

---

## Run Commands (adapt to project)

```bash
npm test
npm run test:watch
npx vitest run --coverage
npx vitest run path/to/specific.test.ts
npx vitest run -t "scenario name"
```
