# Findings ledger: close-r1

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
| F1 | A [[sync]] entry with `values = []` (or `settings = 1`) makes `check` raise after the summary | yes | blocking | fixed | 0ebf855 | Reproduced 2026-11-23: `test_a_sync_entry_of_the_wrong_shape_is_a_configuration_error` failed for `values = []`, `settings = 1` and a settings block that is not a table (`exclude = "x"` was already refused). `read_config` checks the shape of `exclude`, `values` and `settings` too; 002-phase-1.md's "a config of the wrong shape" covered only the top level and the three strings. Regression test: that test (4 cases) |
| F2 | The site says a new unit is named "once, on the next update or check"; every `check` names it until the next `apply` | yes | completeness | fixed | 0ebf855 | Reproduced by reading `unit_report`: `check` never writes the receipt, so `new` holds until an apply. Fixed in `docs/adopt.html`, `README.md`, `skills/adopt-devtools/SKILL.md` and the module docstring, which said the same. Fixed at the close since a page that misstates the behaviour is the defect C6 forbids |
