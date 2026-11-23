# Findings ledger: pr-47-r2

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
| F1 | The round 1 repair passes config paths to git as pathspecs; a source named `:(unknown)one.py` makes `status` and `ls-files` fail, and the failure reads as no local work | yes | hardening | fixed | 8a11673 | Reproduced 2026-11-23 at fc7bd28: with a local edit to `skills/demo/SKILL.md` and that source, `resolve_source` returned `upstream`. Introduced by the round 1 repair (self-inflicted 1/1: the stop rule fires, no round 3). Fixed on the owner's "fix": `--literal-pathspecs`, and a failed query counts as own work. Regression tests: `test_a_source_name_git_would_read_as_a_pattern_does_not_hide_own_work`, `test_a_dirty_check_that_fails_keeps_the_checkout`, both red at fc7bd28 |
