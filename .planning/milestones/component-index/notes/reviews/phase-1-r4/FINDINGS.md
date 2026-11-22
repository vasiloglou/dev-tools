# Findings ledger: phase-1-r4

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
| F1 | A tracked paused-phase file under a folder whose name holds line breaks can print a forged ignored heading and end marker, hiding the real inventory, so a note with a missing path reads as ready | yes | blocking | fixed | 22d6258 | Inherited from main (the reviewer reproduced it at 24b2d83 and c9648dd). Reproduced red: two end markers in the note, and `missing_ignored` `[]`. Fixed: uncommitted and paused-phase paths are printed on one line, JSON-escaped like ignored ones. Test: `test_t17_...`. |
| F2 | takeover redacts the note before reading its paths, so an ignored path that looks like a key is checked as `[removed: looks like a key]`, which may exist | yes | blocking | fixed | 22d6258 | Inherited from main. Reproduced red at positions 1 and 26. Fixed: paths are read from the note as written and redacted only in the report. Test: `test_t18_...` (2 cases), which also checks the key never appears in the report. |
| F3 | `doctor` calls `.exists()` on `env_paths` (and `key_files`), which raises on Python 3.11 to 3.13 for a name too long | yes | hardening | fixed | 22d6258 | Inherited from main. Reproduced by making `Path.exists` raise as those versions do. takeover runs doctor, so it hardens this phase's deliverable: both now use `_exists`. Test: `test_t20_...` (2 cases). |

Also fixed at 22d6258: phase-3-r4 F1, a rest line whose cut line is gone (test `test_t19_...`).

Convergence: 3 findings, 2 blocking, 0 of 3 self-inflicted; with phase-3-r4 F1, 4. Every round since r1 has found another way a hand-written or oddly named Markdown note leads `takeover` to say ready (r2 3, r3 4, r4 4 real findings), and severity has not fallen. That is the stop rule's signature from the other side: the design yields, not the repairs. The next instrument is not round 5 but Q3 of record 002, a machine-readable ignored inventory. Round 4 ran on the owner's request of 2026-11-22; the repairs at 22d6258 are unreviewed.
