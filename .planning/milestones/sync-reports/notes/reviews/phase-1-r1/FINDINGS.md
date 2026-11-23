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
| F1 | A config of the wrong shape (`sync = 42`, `source = 42`) raises `TypeError` in `check` after the summary | yes | blocking | fixed | 2120090 | Reproduced 2026-11-23 with the reviewed code: `check --source` on `sync = 42` raised `TypeError: 'int' object is not iterable`. `read_config` now checks the shape of `sync`, its strings and `after_apply`. Regression test: `test_a_config_of_the_wrong_shape_is_a_configuration_error` (4 cases), red before the fix |
| F2 | With no `git` on the machine, `check` raises after the summary | yes | hardening | fixed | 2120090 | Reproduced: `subprocess.run` raising `FileNotFoundError` for `git` made `check --source` raise. Hardens this phase's own `check`, so fixed in-phase: `source_identity` treats a git that cannot start as an unknown commit. Regression test: `test_a_check_with_no_git_keeps_the_receipt_verdict`, red before the fix |
| F3 | A file already as shipped in the project is counted as an apply's `create`, so `check --strict` exits 5 while `apply --dry-run` keeps it | yes | blocking | fixed | 2120090 | Reproduced: `check --strict` printed `an apply would create 1 file(s)` and exited 5; `apply --dry-run` printed `dry run: {"keep": 2}`. Introduced by implementation finding 1. `pending` now counts `plan`'s actions where the source differs from the receipt. Regression test: `test_a_file_already_as_shipped_is_not_counted_as_behind`, red before the fix; T25 still holds |
| F4 | A receipt with no files (`sync = []`) never hears of a new unit, and gets no one-time list | yes | completeness | fixed | 2120090 | Reproduced: `check --strict` exited 0 after a unit was added. Fixed in-phase, though completeness, since the fix is one condition and its test. Regression test: `test_a_receipt_with_no_files_still_hears_of_new_units`, red before the fix |
| F5 | The hand-edit frame of `docs/adopt.html` shows no unit report, which the config the page shows would print | yes | completeness | fixed | 2120090 | Reproduced by reading: the frame was taken on a project that declines the four units, and the page did not say so. The frame is real output and stays; its caption now says the project declines them |
