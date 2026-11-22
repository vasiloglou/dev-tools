# Findings ledger: phase-3-r2

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
| F1 | `handoff.notes` says takeover is not ready while any ignored path is missing, but a missing key file does not block | yes | blocking | fixed | 27ca753 | Reproduced at handoff.py's key branch (`missing_keys`). The entry is the deliverable, so a false statement in it is a wrong answer. Fixed: the note names the key-file exception. Not self-inflicted (the note is the reread's, not a repair's). |
| F2 | `phase.coder_pool` says a linked worktree reads the main checkout's local file; its own comes first | yes | blocking | fixed | 27ca753 | Reproduced at coder_pool.py:338 (`local.is_file()` returns the worktree's own first). Fixed: "without a local file of its own". |
| F3 | `phase.state` does not name normative-document ownership, which `check` enforces | yes | completeness | fixed | 27ca753 | Reproduced: `search normative document ownership` printed `no component matched`; check_docs at phase_tool.py:725. Fixed now since it is one verb pair: the search now puts `phase.state` first. |
| F4 | The handoff reading table has 74 rows; the module has 77 definitions since e2b2762 | yes | completeness | fixed | 27ca753 | Reproduced with the ast count (77). Fixed: an addendum to handoff.md lists `_inside`, `_split_end` and `_exists` and what the repair changed. |
| F5 | `handoff.notes` does not name `show` | yes | completeness | fixed | 27ca753 | Reproduced at handoff.py:1218. `show note` was already a verb; `does` now names it. |

Convergence: 5 findings, 2 blocking, 0 of 5 self-inflicted. Under the budget declared in notes/phase-3-reading/README.md before this round, the blocking findings earn one further round, `phase-3-r3`, and no more.
