# Findings ledger: phase-1-r1

One row per finding the review returned, under the reviewer's own id. Fill every cell:

- Reproduced: yes or no. A finding is believed only once it is reproduced against the bytes.
- Class: blocking, hardening or completeness, assigned here, not by the reviewer
  (review-convergence.md).
- Disposition: fixed, deferred, rejected or open.
- Repaired at: for a fixed finding, the commit or tag that holds the repaired bytes. Those
  bytes are unreviewed until a later round reads them; `review_tool.py status` says which.
- Notes: the regression test for a fixed finding, the target for a deferred one, the reason
  for a rejected one.

If the review returned no findings, replace the table with the line: No findings.

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | The guard skips on the refusal's note before the exit of `rules_check.py test` is looked at, so a GND without the extra hides an example that is wrong | yes | blocking | fixed | 1e4d5ff | Reproduced with the stand-in `gnd` and the starter rules' examples left in: exit 1, six `wrong:` lines and the note, and the guard as written answered skip. Repaired: the guard takes the exit and skips only on 0. Regression test: `tests/test_tools.py::test_the_guard_does_not_hide_a_rule_that_is_wrong`, red before the repair (`TypeError`, the guard had one argument; its old body returned true on that output) |
| F2 | With `PY_COLORS=1` pytest colours its summary line and S9's anchored match fails | yes | hardening | fixed | 1e4d5ff | Reproduced: `PY_COLORS=1 … pytest tests/test_phase_selection.py -q` gave `1 failed, 14 passed`. Repaired: the fixture passes `--color=no`. Fixed in-phase because the test file is this phase's deliverable. Regression test: `tests/test_phase_selection.py::test_the_checks_do_not_depend_on_the_colour_settings_of_whoever_runs_them`, red before the repair. The two older tests of the plugin in `tests/test_tools.py` had the same defect and take the same option |
