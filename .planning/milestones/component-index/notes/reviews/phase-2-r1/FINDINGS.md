# Findings ledger: phase-2-r1

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
| F1 | `draft` raises `StopIteration` when a folder is written with a leading `./` (an extra folder with `count_extra_dirs` true, or `package_dir` with the setting absent), since the folder is matched as a string | yes | blocking | fixed | cc00107 | Reproduced: both cases of `test_draft_takes_a_folder_written_with_a_leading_dot` failed with `StopIteration` before the repair. The second is a regression against `ca6712a` for a project that never sets the key. Folders are now matched with `Path.is_relative_to` |
| F2 | `docs/components.html` does not name `count_extra_dirs`, which spec section 6 requires | yes | completeness | fixed | cc00107 | Reproduced: `grep -n count_extra_dirs docs/components.html` printed nothing. One sentence added to "It notices when the code moves on", where strict coverage is described. This refutes the premise, written before the review, that the page names no setting and so has no place for it |
