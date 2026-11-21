# Findings ledger: plan-r3

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
| F1 | The r2 bullet pattern skips a path holding a newline, which `ls-files -z` allows, so an uncut note still reads as ready | yes | hardening | fixed | REPAIRED_AT | Reproduced: on a snapshot holding the bullet for `out\n1/`, the pattern finds only the other path; the unread line starts with the bullet's opening. Self-inflicted: it attacks the r2 F2 repair. Repaired as a test row, since the stop rule fired: an unreadable bullet line adds 1 to `unlisted_ignored`; new test T10, phase 1 |
