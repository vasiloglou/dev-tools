# Process checks (PG ids in `scripts/gates.json`)

IDs remain compatible with `scripts/gates.json` and `phase_tool.py`. They are
coverage categories, **not independent test runs or review rounds**.
The validation policy in `../SKILL.md` takes precedence over older instructions.
Use the venv Python with the worktree's src first on PYTHONPATH.

## Execution

- During TDD, run the red/green test and directly affected tests for each fix.
- Before final regression, run any required acceptance/slow test not covered yet.
- Run the default full suite once on the finished code. Reuse its results for
  every category it covers. No baseline full run, fresh-verifier repeat, duplicate
  golden runs, or replay/evidence-review loop.
- A result is reusable while the code it tests and relevant inputs are unchanged.
  A handoff, documentation update or status transition does not invalidate it.
- If the final run fails or is invalidated by a fix, report that fact and continue
  focused tests. Do not automatically launch a second full run.

## Checks and minimal record

`PT` means the venv Python running `scripts/phase_tool.py`; `P` is the phase
directory. Keep useful focused output and `P/NN-EVIDENCE/runs/pytest.txt`.

| ID | Check | Satisfy it without duplicate execution |
|---|---|---|
| PG1 | Final full regression (all phases) | One `.venv/bin/python -m pytest -q -rfE -p no:cacheprovider` run after focused fixes (`-rfE` names every failed and errored test in the log). Compare with an available prior baseline; report unknown baseline honestly. No unexplained regression or silently waived failure. |
| PG2 | Approved acceptance tests | Reuse current focused/default results; run only uncovered required cases, including relevant slow tests. No mandatory separate slow-critical campaign. |
| PG3 | Test lock | `PT check --testlock NN --format json`; no dirty lock. |
| PG5 | Declared goldens (from1) | `PT golden-diff --format json`; undeclared[]. Reuse final PG1 golden-test results. |
| PG6 | Architecture/layering (from1; report in0) | Reuse final PG1 architecture results; retained exceptions must be explicit and applicable, not inferred from an old failing ID. |
| PG8 | Skill/planning consistency | `PT check --all`; reuse PG1 skill-fact results. No live skill evals unless requested. |
| PG9 | Requirement mapping | `PT req-coverage --format json`;100% coverage. |
| PG10 | Migration (from1) | `PT migration-check --format json` and check touched-module rows; no deleted-module imports. |
| PG11 | Result paths | `PT evidence-check --phase NN --format json`; cited paths exist. Mechanical check only, no evidence reviewer. |
| PG12 | Outcome/benchmark targets (from1) | Reuse required focused/integration tests for plan targets. No separate benchmark or full-model replay unless explicitly requested. Identify any genuinely uncovered acceptance outcome before the final run. |
| PG13 | Optional code review (from1) | Not required by default. If requested or needed for a concrete correctness concern, review the relevant diff once; reproduce uncertainty with a focused test, not a broad rerun. |
| PG14 | No TODO/stub (from1) | Inspect changed product code once; no unfinished implementation presented as complete. |

## Scope and safeguards

No acceptance test may be silently skipped, xfailed or weakened. Locked changes
retain the existing approval/re-lock contract. Known baseline defects need exact
causal dispositions; ordinary logging does not turn a red test green.

Preserve project invariants (`references/project.md`) and network/spend boundaries
for any required test execution. Fake/replay providers are test mechanisms, not
a requirement for a separate replay workflow.

A separate release to main retains its explicit authorization and
exact-release-commit requirements.
