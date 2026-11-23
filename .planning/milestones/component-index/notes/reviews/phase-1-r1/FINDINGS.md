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
| F1 | A path holding a newline can print a line that parses as a whole bullet, and its continuation is ignored, so the note reads as ready | yes | blocking | fixed | 4903752 | Reproduced with `out0/` and ``out0` (0.0 MB, 1 file)\n1/``: red before the repair, `assert (0 == 1)`. Regression test: `test_t10_a_bullet_that_cannot_be_read_withholds_ready[out0` (0.0 MB, 1 file)\n1/]` |
| F2 | An `ignored-rest` item whose `kind` is a list or an object raises `TypeError` in `takeover` | yes | blocking | fixed | 4903752 | Reproduced: `TypeError: cannot use 'list' as a set element`, and the same for `dict`. Regression tests: the two new cases of `test_t7_t8_an_unreadable_or_short_rest_line_is_treated_as_absent` |
