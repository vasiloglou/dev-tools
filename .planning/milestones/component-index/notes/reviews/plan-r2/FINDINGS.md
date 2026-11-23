# Findings ledger: plan-r2

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
| F1 | Phase 2's T4 cannot give its expected exits: the fixture makes no commit, and a new extra-folder file makes `modules/tools.md` stale whatever the setting | yes | blocking | fixed | bfc5be1 | Reproduced in a scratch synced project on 2026-11-21: `changed --base main` exited 1 with `no branch or commit named main`; after `write` and a commit, adding `tools/new.py` with the setting absent exited 1 on `fail: stale or missing: docs/components/modules/tools.md`. Repaired: T4 commits first and reruns `write` before `changed`. Regression test: T4 itself, in phase 2 |
| F2 | A bullet whose path holds a backtick is skipped by `takeover`'s pattern, so that path is never checked | yes | hardening | fixed | bfc5be1 | Reproduced: today's pattern finds nothing in the line for a path holding a backtick, and the anchored greedy pattern reads it. Hardens phase 1's own deliverable, so it is fixed in-phase. Repaired: the bullet pattern in the phase 1 design; new test T9 |
| F3 | Section 8 says `auto=false` while a2 records `auto=true` | yes | completeness | fixed | bfc5be1 | Reproduced by reading section 8 against a2. Fixed in this round, though it is completeness, because a wrong statement of the delegation in the plan would be bound by the plan gate's ruling |
