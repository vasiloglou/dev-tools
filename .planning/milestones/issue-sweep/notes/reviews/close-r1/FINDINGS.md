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
| F1 | The close carried 13 same-name leads and two entries older than their code; `review` printed 15 and six | yes | hardening | fixed | 92d936e | Reproduced: `components_index.py --no-cache review` printed `(15)` and `(6)`. Four entries (`components.index`, `components.rules`, `phase.state`, `review.rounds`) had been marked reread in phase 3's work commit and changed again by its repairs at `43f6d83`; each was read beside those repairs and its `reread:` line updated, and `review` then printed `(2)`. The two new leads, `settings_error` and `read_settings_file`, are copies phase 3 made on purpose (S0.2); the close's J7 row and residuals now count 15. Regression: the close's gate output of `review` |
| F2 | C9 marked met while the record still held placeholders | yes | completeness | fixed | e271e57 | Reproduced by reading the draft: `CLOSE_RULING`, `EVIDENCE`, `CLAIM`, `REVIEW_STATUS`, `RULING_BLOCK`, `CLOSE_FINDINGS`. The record is completed in the close commit; its final bytes are not the bytes this round read, and carry no review opinion |
| F3 | `004-phase-3.md` quotes its release status as 30 plugin files changed; it printed 34 | yes | hardening | fixed | 92d936e | Reproduced in scratch worktrees: `release_plugins.py status` printed `34` at `488e143` and `30` at `a981377`, so the line was copied from phase 2's record. A committed record is not edited: corrected by the new record `005-phase-3-correction.md`. The close's own gate output is from a run on its head |
| F4 | The question sweep disposes the `uvx` question twice | yes | completeness | fixed | e271e57 | Reproduced by reading the two rows. Merged into one row |
