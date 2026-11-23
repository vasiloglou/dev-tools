# Findings ledger: phase-2-r2

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
| F1 | A tracked symbolic link whose target is outside the commit is not found in the folder read, so the apply deletes the project's copy | yes | blocking | fixed | e6a5c28 | Reproduced 2026-11-23 with a link `skills/demo/guide.md -> ../../../shared-guide.md`: introduced by the r1 F1 repair. `read_commit` now refuses a commit holding a link (`upstream-unreadable`), so the checkout is delivered as it is. Regression test: `test_an_upstream_holding_a_symbolic_link_is_not_read`, red at 90dca94 |
| F2 | An exception in the tool comparison, after the read, leaves the folder | yes | hardening | fixed | e6a5c28 | Reproduced: a `KeyboardInterrupt` from `read_bytes` of the tool left the folder. The whole stretch up to the return is protected. Regression test: `test_an_error_after_the_read_still_removes_the_folder`, red at 90dca94 |
| F3 | `core.fileMode=false` (and, found while reproducing it, assume-unchanged and skip-worktree) hide tracked work from the dirty check | yes | hardening | fixed | e6a5c28 | Reproduced for all three: `resolve_source` returned `upstream`. `status` runs with `-c core.fileMode=true`, and `ls-files -v` flags count as changes. Regression test: `test_git_settings_do_not_hide_tracked_work` (3 cases), red at 90dca94 |
| F4 | `rstrip` removes a newline that ends the path itself | yes | hardening | fixed | e6a5c28 | Reproduced on the function: git's answer for a path ending in a newline lost both newlines. `git_line` removes exactly one terminator. Regression test: `test_only_git_s_line_terminator_is_removed` |
