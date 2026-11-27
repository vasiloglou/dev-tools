# Findings ledger: pr-53-r3

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
| F1 | An ignored link whose target is gone, moved from a name to a folder, asks neither component: the filter keeps regular files only (components_index.py:1308) | yes | blocking | fixed | a60a9aa | Reproduced: `test_changed_asks_both_components_when_an_ignored_link_without_its_target_moves` fails on c60b38f. Same class as close-r1 F1. A candidate git does not track is now kept when it is a file or a link |
| F2 | A tracked `.py` link without its target under the package stops `changed` in the inventory before ownership is read (components_index.py:541) | no | hardening | deferred | -- | Not rerun; the reviewer reproduced it on main as well, so it is as old as 0.1.8. Deferred to the owner as a proposed issue: the inventory would have to skip or report a module it cannot open |
| F3 | A stale page's name and a validation message bypass the escaping: a package folder with a line break, a modules path with U+2028 (:1032, :1271, :351) | yes | hardening | fixed | a60a9aa | Reproduced: `test_a_name_with_a_line_break_or_a_backslash_is_one_line_everywhere_it_is_printed` fails on c60b38f. changed and --check now escape every printed line whole |
| F4 | A name with a line break and one with a literal backslash-n print alike (:1074) | yes | hardening | fixed | a60a9aa | Reproduced by the same test. shown() now doubles a backslash |
| F5 | A generated page's module heading keeps a line break in a name, against the index entry's claim (:505) | yes | hardening | fixed | a60a9aa | Reproduced by the same test (the page check). The heading's group, dotted and file names are escaped; the index entry now says which lines of a page are |
| F6 | The PR's claim that every added test fails on main is wrong for the tracked link without its target (test_tools.py:2651) | yes | completeness | fixed | a60a9aa | Confirmed by reading: that case broke in 0e241de and was repaired in 24d43a1, so it passes on main. The commit body and the PR body say so |
