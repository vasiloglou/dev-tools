# Acceptance-test review checklist

Run this before asking the user for the Specify gate. It also serves as the review list for the `phase-verifier` when it audits a phase's tests.

## Coverage
- [ ] Every ROADMAP **Acceptance tests (written first)** bullet maps to ≥1 test id in `NN-TESTS.md`, or is listed there as deferred with its reason.
- [ ] Every **Exit criteria** item maps to ≥1 test id, or sits under "Not testable automatically" with a UAT or review route.
- [ ] Every testable `LOCKED` CX decision is asserted somewhere.
- [ ] Every test id in the files appears in `NN-TESTS.md`, so there are no orphans.
- [ ] The project invariants the phase touches (`references/project.md` beside the process-phase skill) are asserted.

## Layout
- [ ] Files live in `tests/acceptance/pNN_<slug_with_underscores>/`.
- [ ] Test module basenames are unique across `tests/` (`find tests -name 'test_<x>.py'`).
- [ ] Helpers are in `pNN_helpers.py`. `conftest.py` only re-exports fixtures.
- [ ] Fixture data comes from `tests/fixtures/`, and nothing is written into the repo.

## Contract, not internals
- [ ] Behaviour is reached through the CLI or a documented entry point.
- [ ] Assertions use documented outputs, error codes and exit codes.
- [ ] Guard tests on existing behaviour are labelled `guard` in NN-TESTS.md.

## Determinism
- [ ] Every sampling call has an explicit seed.
- [ ] There are no live LLM, external-service or network calls. Fake provider or cassettes only; no real key, and a sentinel value may be set to prove it never leaks. Socket blocks reach subprocess CLI calls too (a `sitecustomize.py` on `PYTHONPATH`), not only `monkeypatch`.
- [ ] Tests read fixture copies (`tmp_path`), never live `.planning` state such as `STATE.md` or `ROADMAP.md`.
- [ ] External data a test needs is vendored before the lock, or recorded as a blocker.
- [ ] There is no wall-clock dependence (the time is passed in, or a clock is injected).
- [ ] Assertions are set-level (counts of distinct results), except in golden tests.
- [ ] Each test runs in under ~30 s on the fixtures, or is marked `slow`.

## Vacuity check
For each test, name the trivial implementation that would pass it (always an error, always "unknown", an empty list, a no-op) and show that it fails. Known traps:
- [ ] A verdict test that accepts an outcome where every case is skipped or inconclusive.
- [ ] A spike-dependent test that branches on the tool's own output instead of the LOCKED CX/DEC verdict.
- [ ] A freshness check that regenerates the thing before checking it.
- [ ] A single-instance fixture that cannot tell two behaviours apart; use at least two distinguishing cases.
- [ ] Monkeypatching a global that hides the real bug.

A test that passes vacuously is a valid reason to re-lock through a DEC (SKILL.md Rule 8).

## Red for the right reason
- [ ] `pytest --phase NN` exits 1 with no `ERROR collecting` lines.
- [ ] Each failure is an ImportError of a module the phase creates, a usage error (exit 2) for a command the phase adds, or an AssertionError about missing behaviour.
- [ ] Imports of not-yet-existing modules are inside functions or fixtures.
- [ ] `NN-EVIDENCE/red.txt` holds the full `-rA` output.

## Lock
- [ ] The user has approved `NN-TESTS.md` and the red summary.
- [ ] `phase_tool.py testlock --phase NN --write` has run, and `check --testlock NN` is clean.
- [ ] The lock covers the helpers and `conftest.py` as well as the test files.
