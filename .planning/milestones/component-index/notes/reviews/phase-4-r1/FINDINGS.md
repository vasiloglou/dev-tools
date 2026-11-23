# Findings ledger: phase-4-r1

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
| F1 | The fixture of the six copy-based tests runs `git init`, which reads the user's git settings; a setting git refuses makes them error with a current index, and the claim that the tests read nothing outside the checkout and `tmp_path` is not met | yes | hardening | fixed | b807ca1 | Reproduced with the review's command (`GIT_CONFIG_COUNT=1 … include.path=README.md`): exit 1, `fatal: bad config line 3`. The script finds a project by a `.git` entry and runs no git command for `--check`, `write` or `stats`, so the fixture makes that folder itself. Regression test `test_the_copy_and_the_check_run_without_git`, seen failing first (`FileNotFoundError: … 'git'`). After the fix the review's command exits 0, 8 passed. |
| F2 | The milestone's `README.md` is unchanged, though spec section 6 lists it: it still calls phases 3 and 4 outlines and phase 3 stacked | yes | completeness | fixed | b807ca1 | Reproduced: `git diff --name-only 827e766 d49bdf4` does not name it. It was planned for the record's commit; the specs and the merged pull requests are now named at `b807ca1`, and the record's link is added with the record. No test: it is a navigation page. |

Convergence: 2 findings, 0 blocking, 0 of 2 self-inflicted (first round). The reviewer found no defect in the judgment (`problems`). By its read-only rule it did not run the copy-based tests, the full suite, or the two failing-case gates; it ran `test_the_index_is_current` directly under Python 3.11 to 3.14, the strict check, the build check and the three `changed` commands. The spec's budget allows a second round only after a blocking finding, so there is none. The bytes repaired at `b807ca1` carry no review opinion.
