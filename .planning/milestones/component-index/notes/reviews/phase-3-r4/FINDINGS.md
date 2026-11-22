# Findings ledger: phase-3-r4

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
| F1 | `handoff.notes` says a line of the ignored list that cannot be parsed withholds ready, but a rest line whose cut line was deleted is passed over, and a missing path after the 25th goes unchecked | yes | blocking | fixed | 22d6258 | Reproduced red as `test_t19_...` (`unlisted_ignored` 0). A defect of `takeover`, not of the wording: fixed in the code on the phase 1 branch, merged here, so the entry's sentence is now true. Self-inflicted for the index (it attacks round 3's sentence). |

Convergence: 1 finding, 1 blocking, 1 of 1 self-inflicted. Round 4 ran on the owner's request of 2026-11-22, after the stop rule fired at round 3. No round 5: what it found is phase 1's, and phase-1-r4/FINDINGS.md says why the next instrument is not another round.
