---
phase: "{{PHASE}}"
title: "{{TITLE}}"
slug: {{SLUG}}
test_dir: tests/acceptance/p{{PHASE}}_<slug_with_underscores>/
lock: {{PHASE}}-TESTLOCK.json
red_evidence: {{PHASE}}-EVIDENCE/red.txt
---

# Phase {{PHASE}}: {{TITLE}} — Acceptance tests

Written in Step 2 (Specify) before any implementation, run red, then locked.
Changing a locked test needs a DEC entry and a human re-lock.

## Traceability

| # | Criterion (ROADMAP bullet / exit criterion / CX) | Test ids | Red reason | Kind |
|---|---|---|---|---|
| 1 | <criterion text, verbatim> | `test_<capability>.py::test_<behaviour>` | ImportError `<package>.<module>` | contract |
| 2 | | | AssertionError: <what is missing> | contract |
| 3 | <existing behaviour that must not regress> | | — (green at red) | guard |

Kinds: `contract` (must go red → green) · `guard` (pins existing behaviour; green at red by design).

## Red run

- Command: `.venv/bin/pytest --phase {{PHASE}} -q -rA`
- Summary line: `<N failed, M passed>`
- Collection errors: none (required)

## Fixtures and providers

| Fixture / provider | Path | Deterministic how |
|---|---|---|
| | `tests/fixtures/...` | seed / cassette / fake |

## Not testable automatically
<!-- Criteria verified by UAT or review instead, with reason. -->
| Criterion | Verified by |
|---|---|
