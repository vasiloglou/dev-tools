# Findings ledger: pr-53-r4

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
| F1 | A tracked `.py` link without its target under the package stops `changed` in the inventory (components_index.py:541) | no | hardening | deferred | -- | pr-53-r3 F2, deferred there: as old as 0.1.8 by both reviewers' runs. A proposed issue |
| F2 | An ignored named pipe a modules line names moves silently: the filter keeps files and links only (:1309) | yes | hardening | fixed | 29fb172 | Reproduced: `test_changed_asks_both_components_when_an_ignored_pipe_moves` fails on abe61d6. Anything there but a folder is now kept |
| F3 | Under a folder that is not UTF-8, with no catalog at the base, git's message stops the strict text read (:1061, :1250) | yes | hardening | fixed | 29fb172 | `test_changed_runs_when_the_base_has_no_catalog_under_a_folder_not_utf8`, Linux only; it passes in local CI's Linux jobs on 29fb172. Its failure before the repair was not run (macOS refuses the name); the reviewer reproduced the decode error with real git. git() now decodes with surrogateescape |
| F4 | The summary line, an error and the baseline refusal print a base or folder with a line break on two lines (:1375, :1900, :1038) | yes | hardening | fixed | 29fb172 | Reproduced for the summary: `test_changed_prints_its_summary_as_one_line_for_a_base_with_a_line_break` fails on abe61d6. The error and the refusal go through the same shown() and have no test of their own |
| F5 | An external page's module heading keeps a line break in a dotted name (:673) | no | hardening | fixed | 29fb172 | Read in the code, not built: it needs an installed distribution with such a module. Escaped as a local page's heading is. No test |
| F6 | Two names print as the same bytes on a CP932 stream (U+301C and U+FF5E) | no | hardening | rejected | -- | The stream's own encoding maps the two characters to one byte pair; the text this script hands the stream differs. The claim is about the lines the script prints, which stay distinct |
| F7 | The group-heading test cannot fail: it splits on line breaks and then looks for one (test_tools.py:2772) | yes | completeness | fixed | 29fb172 | Reproduced: with the group escaping removed, the old assertion passed. The test now checks the escaped heading whole, and fails with the escaping removed |
| F8 | The index says facts is untouched; `facts --base` shares the snapshot and changed behaviour (COMPONENTS.md:459) | yes | completeness | fixed | 29fb172 | Read in the code. subsystem.rule_check's reread line now says what facts gains |
