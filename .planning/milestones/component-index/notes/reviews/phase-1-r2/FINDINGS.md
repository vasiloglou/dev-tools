# Findings ledger: phase-1-r2

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
| F1 | A path holding a newline can print lines that are all valid bullets, so no line rule catches it and the note reads as ready | yes | blocking | fixed | 4903752 | Self-inflicted (attacks the r1 F1 repair). Reproduced red: `assert (3 == 2)` and twice `assert (2 == 2 and False)`. Fixed in the writer: such a path is printed JSON-escaped on one line. Regression test: `test_t10_a_path_holding_a_newline_is_written_escaped_and_checked` (3 cases). Residual for notes from before 0.1.4, in the spec, IF6 |
| F2 | A commit subject or file named like the ignored-files heading moves the section's start, and an ordinary note reads as not ready | yes | blocking | fixed | 4903752 | Self-inflicted (the r1 line rule made the misplaced start visible). Reproduced red: `assert (4 == 0)`. Fixed: the section starts at the last line that begins with the heading. Regression test: `test_t12_snapshot_text_that_names_the_heading_does_not_move_it` |
| F3 | A rest line nested deep enough raises `RecursionError` in `takeover` | yes | hardening | fixed | 4903752 | Reproduced at depth 100000 (2000 decodes on Python 3.14). Hardens this phase's own deliverable, so fixed in-phase. Regression test: the fifth case of `test_t7_t8_an_unreadable_or_short_rest_line_is_treated_as_absent` |
