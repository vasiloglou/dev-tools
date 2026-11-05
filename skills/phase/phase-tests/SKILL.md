---
name: phase-tests
description: Test-first guide for roadmap phases. Turns ROADMAP acceptance bullets, exit criteria and LOCKED CONTEXT decisions into acceptance tests under tests/acceptance/pNN_slug/. The tests run red for the right reason (an ImportError of the missing module or a failing assertion, never a collection error), their files are locked in NN-TESTLOCK.json, and traceability is recorded in NN-TESTS.md. Covers naming, helpers, fixtures, fake and replay providers, deterministic seeds, the pytest --phase plugin and the rules for changing a locked test. Use in process-phase Step 2 (Specify), when asked to write or review acceptance tests for a phase, or when a locked test seems wrong. Not for unit tests written during implementation.
---

# phase-tests

Phases are test-driven ("tests are the phase contract"):
1. each phase starts by committing **acceptance** tests that encode its ROADMAP block;
2. they run **red** for the right reason;
3. they are locked in `NN-TESTLOCK.json`;
4. the code is then written until they pass, without editing them.

This skill is how you write those tests. `/process-phase` Step 2 calls it, and the `phase-test-writer` agent follows it.

## Inputs

0. `NN-EVIDENCE/prove.md` §5, the smallest outcome contract and its method record: one test per row asserting its metric on the real-shaped asset or the pinned prove fixture, failing when a previously passing item is lost.
1. The phase block: `python3 .claude/skills/process-phase/scripts/phase_tool.py roadmap get NN`. Use its **Acceptance tests (written first)** bullets and **Exit criteria**.
2. The `LOCKED` CX rows in `.planning/phases/NN-<slug>/NN-CONTEXT.md`.
3. The normative doc for the phase's topic in `.planning/docs/`.
4. Current code, so that tests pin the target API and do not accidentally depend on internals.

## Rule 1 — One criterion, at least one test

- Every acceptance bullet, exit criterion and testable LOCKED CX gets at least one test.
- Write the mapping first, as a table in `NN-TESTS.md` (template: the process-phase skill's TESTS template), then write the tests.
- A criterion that cannot be automated (for example "the user finds the report readable") goes under "Not testable automatically" with its verification route, such as UAT.
- A Killed goal, or a ROADMAP bullet deferred by `prove.md` §6, gets no locked test: NN-TESTS.md lists it as deferred, with the reason (process-phase `specify.md` §3).

## Rule 2 — Layout and names

| Item | Convention |
|---|---|
| Directory | `tests/acceptance/pNN_<slug_with_underscores>/`, e.g. `tests/acceptance/p02_reports/` |
| Test files | `test_<capability>.py`, e.g. `test_report_totals.py` |
| Unique basenames | `tests/` has no `__init__.py`, so pytest's default import mode needs every test module basename to be unique across `tests/`. Check with `find tests -name test_<capability>.py` before naming |
| Helpers | `pNN_helpers.py` in the phase directory (never `helpers.py` or `utils.py`, which would clash between phases) |
| Fixtures | Define them in `pNN_helpers.py`, re-export from a 1–3 line `conftest.py` (`from p02_helpers import sample_orders  # noqa: F401`) |
| Test data | `tests/fixtures/` (for example folders named `data/`, `golds/` and `replay/` inside it) |
| Test names | Behaviour sentences: `test_removing_one_order_changes_the_total` |

## Rule 3 — Test the public contract

- **Reach behaviour through the project's public contract:** the CLI, via `subprocess`, or a documented package entry point. The project names its contract in `.claude/skills/process-phase/references/project.md`.
- **Assert on** documented outputs, error codes and exit codes.
- **Do not assert on** private helpers or module internals that the plan is free to reshape.
- **Guard tests** that pin existing behaviour which must not regress may import existing modules directly. They are green at red by design; label them `guard` in NN-TESTS.md.

## Rule 4 — Determinism

- **Seeds.** Use explicit seeds in every sampling call, and assert set-level properties (a count of distinct results), not exact samples, unless the test is a golden.
- **No live calls.** Nothing reaches a live LLM, network or external service.
  - Use a `fake` provider, or replay cassettes recorded once with approval.
  - A test of a spike-dependent capability passes under every verdict the phase allows, branching on the verdict recorded in the LOCKED CX/DEC, never on the tool's own output.
  - External data a test needs is vendored before the lock, or recorded as a blocker.
- **No clock.** No wall-clock dependence: pass the time in, or inject a clock.
- **Temporary state.** Use `tmp_path` for anything a test writes. Never write under the repo, and never write a fixture file.
- **Timing.** Keep each test under ~30 s on the fixtures, and mark slower ones `@pytest.mark.slow`.

## Rule 5 — Red for the right reason

Run the phase:

```bash
.venv/bin/pytest --phase NN -q -rA -p no:cacheprovider 2>&1 | tee .planning/phases/NN-<slug>/NN-EVIDENCE/red.txt
```

| Red outcome | Verdict |
|---|---|
| `ModuleNotFoundError` / `ImportError` of the module the phase creates (`myapp.reports`) | right |
| `AssertionError` naming the missing behaviour | right |
| The CLI reports a usage error (exit 2) for a command the phase adds | right |
| `SyntaxError`, `ERROR collecting`, `fixture ... not found`, `NameError` in test code | **wrong**: fix the test |
| Passes already | wrong, unless it is a labelled `guard` test |

Import not-yet-existing modules **inside** test functions or fixtures, not at module top level. A top-level import turns a clean red into a collection error that hides every other test in the file.

## Rule 6 — How `pytest --phase` selects tests

`--phase` comes from the phase-selection plugin shipped beside the phase skill (`skills/phase/pytest/phase_selection.py` in the shared source), used as the project's root `conftest.py` or loaded from it. A project with its own selection mechanism names the command in `.claude/skills/process-phase/references/project.md`. The plugin reads `completed_phases` in `.planning/STATE.md`:

| Invocation | Selected |
|---|---|
| `pytest` (plain) | all non-acceptance tests + `tests/acceptance/pNN_*` only for NN in `completed_phases` |
| `pytest --phase NN` (`1`, `01`, or `6.1` for an inserted phase) | only `tests/acceptance/pNN_*` (`p06_1_*` for `6.1`); every other test is deselected |
| `pytest --phase NN` after phase NN completes | still runs that phase's package |

A file or directory inside the acceptance directory that is named on the command line always runs, whatever its phase's status; this is how one test of a phase in progress is run on its own.

This is why the plain suite stays green while a phase's tests are red, and why a phase's tests become regression tests after `phase_tool.py complete --phase NN`.

## Rule 7 — The TESTLOCK

After the user sees the red run and the NN-TESTS.md table:

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py testlock --phase NN --write --fixture <each fixture path the tests read>
python3 .claude/skills/process-phase/scripts/phase_tool.py check --testlock NN
```

- `NN-TESTLOCK.json` has the shape `{"phase": "NN", "created": "YYYY-MM-DD", "files": {…}, "fixtures": {…}}`. It covers every file in the phase's acceptance directory (tests, `pNN_helpers.py`, `conftest.py`, data files) and every declared fixture (data, golds, replay cassettes, goldens), so a fixture cannot be edited to turn a test green.
- A lock is written once; a second `--write` fails with `LOCK_EXISTS`.
- `check --testlock NN` is gate PG3. Any edit shows up as a `testlock` issue.

## Rule 8 — Changing a locked test

A locked test changes only if **all** of the following hold:
1. there is a DEC entry in `.planning/DECISIONS.md` with the test id, what is wrong, and the replacement assertion;
2. the user approves it at a human gate;
3. `testlock --phase NN --write --relock --dec DEC-NNN` is run (the DEC row must exist);
4. it is committed as `test(NN): re-lock acceptance tests (DEC-NNN)`.

Valid reasons:
- the test contradicts a LOCKED decision;
- it pins a private detail;
- it is nondeterministic;
- the ROADMAP criterion itself was amended;
- it passes vacuously: a trivial implementation turns it green (see the vacuity check in `references/checklist.md`).

"The implementation is hard" is not a valid reason, and neither is weakening a threshold.

## Examples

`references/examples.md` has complete examples on a placeholder project, with the red reason for each:
- a CLI command's output, exit codes and unchanged input;
- totals checked against gold cases built by construction, and a one-element removal that a constant answer cannot pass;
- an external provider on replay cassettes that passes under a Go and a Kill verdict;
- a seeded sampler producing at least 20 distinct valid results on two fixtures;
- anti-examples.

`references/checklist.md` is the review checklist to run before asking for the Specify gate.

## Output of this skill

- `tests/acceptance/pNN_<slug>/`: tests, `pNN_helpers.py`, `conftest.py`.
- `.planning/phases/NN-<slug>/NN-TESTS.md`: traceability.
- `.planning/phases/NN-<slug>/NN-EVIDENCE/red.txt`: the red run.
- `.planning/phases/NN-<slug>/NN-TESTLOCK.json`: after approval.
- One commit, made by process-phase: `test(NN): acceptance tests (red)`.
