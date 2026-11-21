# Findings ledger: plan-r1

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
| F1 | C5 and the phase 1 goal say any missing ignored path blocks, while D2 keeps a missing key file non-blocking | yes | blocking | open |  | Reproduced: read against `takeover` (key files go to `missing_keys`, which `ready` ignores) and the spec's D2. Repair written in the working tree on 2026-11-21, not yet committed: C5, P1.1, the phase 1 goal and O1 now exclude key files explicitly; T4 pins it |
| F2 | A readable `ignored-rest` line with fewer items than `N` would let `takeover` report ready | yes | hardening | open |  | Reproduced: the spec's rule set `unlisted_ignored = 0` for any readable line, with no length check. Repair written in the working tree on 2026-11-21, not yet committed: A line is readable only if its length equals `N`; new test T8 |
| F3 | Sorting the counted paths as strings changes today's order even with the setting off | yes | blocking | open |  | Reproduced: `sorted(Path)` gives `a/z.py, a.py`; `sorted(str)` gives `a.py, a/z.py`. Repair written in the working tree on 2026-11-21, not yet committed: `counted_modules` keeps `sources()` order, with no re-sort; new test T10 |
| F4 | Phase 2 tests expect a clean strict check while the fixture's `src/widget/__init__.py` is unassigned | yes | blocking | open |  | Reproduced: `test_component_check_is_strict_only_on_request` shows strict naming that file on this fixture. Repair written in the working tree on 2026-11-21, not yet committed: Shared setup adds `core.package`; coverage expectations now `1/1` and `1/2` |
| F5 | `show` decides from the package-only list which modules it details, so an extra-folder module gets no section | yes | completeness | open |  | Reproduced: `show` loops over `[p for p in package if covers(entry, p)]`, with `package` from `sources(root, PACKAGE_DIR)`. Repair written in the working tree on 2026-11-21, not yet committed: `show`'s module list is a site; its imports stay package-only; new test T9 |
| F6 | `--check --strict` excuses baseline modules, so C1's "no baseline" part has no gate | yes | hardening | open |  | Reproduced: `write_or_check` drops every module the baseline names before `no component:`. Repair written in the working tree on 2026-11-21, not yet committed: C1 adds `test ! -e .devtools/components/unassigned-baseline.txt`; P4.3 for the phase 4 test |
| F7 | Section 9 uses `…` in place of a command | yes | completeness | open |  | Reproduced: the rows read `… --check --strict`, `… review`, `… changed`. Repair written in the working tree on 2026-11-21, not yet committed: Section 9 defines `INDEX` as the exact built-copy command, and gives one row per command |
| F8 | The baseline says `draft()` raises today for an extra-folder module; today it never reaches one | yes | completeness | open |  | Reproduced: `draft()` drafts only `coverage()`'s list, which is package-only. Repair written in the working tree on 2026-11-21, not yet committed: Section 3 now says it would raise once extra folders count, which is what phase 2's T3 tests |
