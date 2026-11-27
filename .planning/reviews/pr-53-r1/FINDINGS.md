# Findings ledger: pr-53-r1

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
| F1 | A module whose name is not UTF-8 stops `write` and plain `changed`: the generated page is encoded as strict UTF-8 (components_index.py:1046, :1015) | yes | blocking | fixed | 24d43a1 | Reproduced by local CI on 0e241de: both Linux jobs fail `test_changed_prints_a_file_whose_name_is_not_utf8` with `surrogates not allowed` inside `write`. Older than this PR for `write`, but it refutes the PR's claim. Generated pages are now written and checked through one encoder, `generated_bytes`, which escapes the byte as the output does. The test now passes on Linux |
| F2 | An ignored file moved between a name in one entry and a folder in another asks only one component (components_index.py:1292) | yes | blocking | fixed | 24d43a1 | Reproduced: `test_changed_asks_both_components_when_an_ignored_file_moves_between_a_name_and_a_folder`, both directions, fails on 0e241de (only one line). The candidates now take every entry's named files, now and at the base |
| F3 | A tracked link whose target is gone, moved by a folder regrouping, asks neither component: `is_file()` follows the link (components_index.py:1294) | yes | blocking | fixed | 24d43a1 | Reproduced: `test_changed_asks_both_components_when_a_tracked_link_without_its_target_moves` fails on 0e241de with `0 to reread`. A regression of this PR. What git tracks is now kept whatever it is here; only untracked candidates must be files |
| F4 | A line break in the project's folder name under the checkout breaks the request for base blobs; `.strip()` also changed a prefix ending in a space (components_index.py:1087) | yes | hardening | fixed | 24d43a1 | Reproduced: `test_changed_reads_a_project_whose_folder_name_holds_a_line_break` fails on 0e241de with `git cannot read src/widget/sizes.py`. The whole request is now built as bytes and checked for a line break; the prefix is read as bytes with only git's final line break dropped. The space and non-UTF-8 prefixes have no test |
| F5 | Splitting the paths into the batch and the rest is quadratic: `p not in batch` scans a list (components_index.py:1094) | yes | hardening | fixed | 24d43a1 | Reproduced by timing the two splits alone, without git: 0.099 s, 0.349 s and 1.372 s for 6,000, 12,000 and 24,000 names on 0e241de; 0.001 s, 0.003 s and 0.006 s on 24d43a1. The split now tests each request for a line break directly. No test: a timing test would be flaky |
| F6 | `--help` can still stop on an encoding error: argparse prints before the streams are set to escape (components_index.py:1773) | yes | hardening | fixed | 24d43a1 | Reproduced: `test_help_prints_on_a_stream_that_takes_ascii_only` (script named `índice.py`, `PYTHONIOENCODING=ascii`) fails on 0e241de. Older than this PR, but it refutes the claim on output. The streams are set before the arguments are read |
