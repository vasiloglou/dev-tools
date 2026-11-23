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
| F1 | `git archive` leaves out `export-ignore` paths, so an apply from a behind checkout deletes a file still shipped | yes | blocking | fixed | 90dca94 | Reproduced 2026-11-23: with `skills/demo/guide.md export-ignore` in the upstream, `apply` did not deliver the guide. The upstream is now read with `ls-tree` and `cat-file --batch` (`read_commit`). Regression test: `test_an_export_ignore_attribute_does_not_drop_a_shipped_file`, red before the fix |
| F2 | `status.showUntrackedFiles=no` hides untracked work, so a dirty checkout is read at the upstream | yes | blocking | fixed | 90dca94 | Reproduced: with that setting and an untracked `skills/demo/LOCAL.md`, no own-work warning and the upstream delivered. The dirty check passes `--untracked-files=all`. Regression test: `test_status_settings_do_not_hide_untracked_work`, red before the fix |
| F3 | `tar.umask` changes the modes delivered from the archive | yes | hardening | fixed | 90dca94 | Reproduced: with `tar.umask=0077`, `SKILL.md` was delivered `0600`. Hardens this phase's own read; fixed by F1's change, which sets 0644 or 0755 from the tree's mode. Regression test: `test_tar_umask_does_not_change_delivered_modes`, red before the fix |
| F4 | A checkout whose path ends in a space reads as a plain folder, because git's answer is stripped | yes | hardening | fixed | 90dca94 | Reproduced: `resolve_source` on a clone at `clone ` returned `folder`. Git's answers lose only their line terminator now. Regression test: `test_a_checkout_whose_path_ends_in_a_space_is_still_a_checkout`, red before the fix |
| F5 | An interrupt while the upstream is read leaves the temporary folder behind | yes | hardening | fixed | 90dca94 | Reproduced: a `KeyboardInterrupt` from the read left the `devtools-upstream-*` folder. The folder is removed on any exception before `resolve_source` returns. Regression test: `test_an_interrupted_read_of_the_upstream_leaves_no_folder`, red before the fix |
