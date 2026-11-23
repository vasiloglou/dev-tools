# Findings ledger: pr-37-r1

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
| F1 | `_snapshot_text` prints the git remote's path unescaped (`handoff.py:711`). A remote whose path holds line breaks can print a second "Files git ignores" section and an early snapshot end marker, so a note written by the present code reads as ready while an ignored path is missing. The close record's C5 row says this cannot happen | yes | blocking | fixed | 17e63c6 | Reproduced on real files, not in memory: `git remote add origin` with the review's path, `write_note`, a clone without `out0/`, then `takeover` returned `head: ok, ready: True, missing_ignored: [], unlisted_ignored: 0`; the note held 2 end markers and 2 ignored headings. Blocking: a counterexample to completion predicate C5, and the same class as phase-1-r4 F1. Fixed in vasiloglou/dev-tools#38 on the owner's word ("Yes, fix it first"), merged `823a55f`: every line the writer generates is kept to one line. Regression tests `test_t21` (this case, a real remote) and `test_t22` (every string of the note, each line break Python splits at), both seen failing first. The fix was reviewed in `pr-38-r1` (APPROVE). |
| F2 | The record's paragraph on which files a review covers lists the milestone's `README.md` among those the close review read, but this pull request changed that file after the review read it (the close declaration and the link to `007-close.md`) | yes | completeness | fixed | 171aa4a | Reproduced: `review_tool.py status` over `close-r1` exits 1 and calls `007-close.md` and `README.md` unreviewed (`README.md` read at `b5930774…`, then `fe2a7ddc…`). A record is not edited after its commit, so the correction is `008-close-correction.md`, "Corrections to record 007", item 2. No test: it is a statement in a record. |

Convergence: 2 findings, 1 blocking, 0 of 2 self-inflicted. F1 is the eighth round to find a way that the Markdown of a hand-off note misleads `takeover` (plan r2 and r3, phase 1 r1 to r4, phase 3 r4, now this one), which is what Q3 of the close record says of the format. The repairs are at `17e63c6` and `171aa4a`; the pull request's head has moved since this round read it, and no second round has read the new head.
