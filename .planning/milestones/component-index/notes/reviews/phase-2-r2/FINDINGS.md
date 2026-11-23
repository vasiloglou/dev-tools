# Findings ledger: phase-2-r2

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
| F1 | `draft` exits 1 (`'tools/report.py' is not in the subpath of 'src/widget'`) for an absolute `extra_source_dirs` entry, since the r1 repair compared a repo-relative path with an absolute folder | yes | blocking | fixed | 882aa52 | Reproduced with that exact message before the repair. Self-inflicted: it attacks the r1 F1 repair. Folders are now compared under the project root. Regression test: `test_draft_takes_a_folder_written_with_a_leading_dot[extra_source_dirs-value1-### tools.report]` |
| F2 | With the setting absent, `draft` names package `widget_`'s area `widget` where `ca6712a` printed `widget_` | yes | blocking | fixed | 882aa52 | Reproduced: the stub read `### widget.report`. Self-inflicted: the phase's new id cleanup was applied to the package's name too. The package's area is again `PACKAGE.lower()`, as at `ca6712a`. Regression test: `test_draft_keeps_the_package_name_as_it_is_for_the_area` |
