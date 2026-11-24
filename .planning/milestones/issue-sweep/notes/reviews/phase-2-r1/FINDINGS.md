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
| F1 | With a tag and a local branch of one name, git reads the name as the tag, and `resolve_base` substituted the branch's upstream | yes | blocking | fixed | ba1d686 | Reproduced in a scratch repository (`git rev-parse main` gave the tag's commit, `refname 'main' is ambiguous`) and by the new B2 case "a tag of the same name", red before. Repaired: the name is read through `git rev-parse --symbolic-full-name`, which refuses an ambiguous name. Regression tests: `tests/test_tools.py::test_changed_reads_every_other_base_as_it_is[a tag of the same name]` and `[a tag]`, and `test_changed_reads_a_branch_named_in_full_like_its_short_name` (the reviewer's note on `refs/heads/main`), red before |
| F2 | Settling a one-second tie by history also orders `does` and `verbs`, so a default-settings output changed, which S0.1 did not name | yes | hardening | fixed | ba1d686 | Reproduced with every commit's time fixed to one second: the entry listed on the code before the tie rule, not after. The behaviour is kept (the earlier answer depended on blame order); fixed in the spec, which names the exception at 4 and 6.3. Regression test: `tests/test_tools.py::test_a_tie_in_commit_time_is_settled_by_history_without_a_reread_line`, red on the code before the tie rule |
