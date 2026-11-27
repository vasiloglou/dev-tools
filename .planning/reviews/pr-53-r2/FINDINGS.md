# Findings ledger: pr-53-r2

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

This round read 0e241de, not the head bc30815 its brief.json names: GitHub still gave 0e241de as the PR's head when the brief was written, just after the push, so diff.patch is 0e241de's diff. It is no review of 24d43a1 or bc30815.

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | A tracked link without its target, moved by a folder regrouping, asks neither component (components_index.py:1294 at 0e241de) | yes | blocking | fixed | 24d43a1 | Reproduced at 0e241de in pr-53-r1 as its F3; repaired there. A repeat: this round read 0e241de |
| F2 | An ignored file moved between a name and a folder asks one component only (:1292 at 0e241de) | yes | blocking | fixed | 24d43a1 | Reproduced at 0e241de in pr-53-r1 as its F2; repaired there. A repeat: this round read 0e241de |
| F3 | A module whose name is not UTF-8 stops `write` and `--check` (:1046, :1015 at 0e241de) | yes | blocking | fixed | 24d43a1 | Reproduced at 0e241de in pr-53-r1 as its F1; repaired there. A repeat: this round read 0e241de |
| F4 | A project-folder prefix with a line break, a carriage return, a leading space or a byte that is not UTF-8 breaks the base-blob request (:1087 at 0e241de) | yes | hardening | fixed | 24d43a1 | Reproduced at 0e241de in pr-53-r1 as its F4; repaired there. A repeat: this round read 0e241de. The prefix is read as bytes there, so the carriage return and the non-UTF-8 byte go with it; only the line break has a test |
| F5 | A checkout folder whose name is not UTF-8 stops the command as it saves the parse cache: the key hashes the name as UTF-8 (:566) | yes | hardening | fixed | a61898a | Reproduced on bc30815 in a python:3.14 container: `test_changed_runs_in_a_project_whose_folder_name_is_not_utf8` fails with `surrogates not allowed` (in the fixture's `write`). Older than this PR. The key now hashes os.fsencode of the name, the same bytes for every UTF-8 name |
| F6 | `--help` stops on an encoding error before the streams are set (:1773 at 0e241de) | yes | hardening | fixed | 24d43a1 | Reproduced at 0e241de in pr-53-r1 as its F6; repaired there. A repeat: this round read 0e241de |
| F7 | The batch split is quadratic (:1094 at 0e241de) | yes | hardening | fixed | 24d43a1 | Reproduced at 0e241de in pr-53-r1 as its F5; repaired there. A repeat: this round read 0e241de |
| F8 | A line break in a file name prints as two lines, the second of which can read as another `reread:` line (:1340) | yes | hardening | fixed | a61898a | Reproduced on bc30815: `test_changed_prints_a_name_that_holds_a_line_break_as_one_line` fails (two `reread:` lines). Every name changed and --check print is escaped by shown(); the carriage-return and line-break tests now expect the escaped name |
