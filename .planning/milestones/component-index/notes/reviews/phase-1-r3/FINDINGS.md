# Findings ledger: phase-1-r3

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
| F1 | U+0085, U+2028 and U+2029 are not escaped, but `splitlines()` breaks at them, so a missing path can print as two valid bullets and the note reads as ready | yes | blocking | fixed | e2b2762 | Self-inflicted (attacks the r2 F1 repair, the `_CONTROL` escape). Reproduced red: `missing_ignored` came back `[]` for each of the three. Fixed: `_CONTROL` takes the three. Regression test: `test_t13_...` (3 cases). |
| F2 | A rest-line path of `""` names the checkout itself, which exists, so the path after the 25th is never checked and the note reads as ready | yes | blocking | fixed | e2b2762 | Not self-inflicted (the rest line is this phase's first implementation). Reproduced red for `""`, `/`, `.`, `./` and `out25/../..`: `unlisted_ignored` 0. Fixed: `_inside` refuses an empty, absolute, `.` or `..` path, in a rest item and in a bullet. Tests: `test_t14_...` (5 cases), `test_t14b_...`. |
| F3 | On Python 3.11 a rest path too long for the file system raises `OSError` from `takeover` | yes | hardening | fixed | e2b2762 | Reproduced by making `Path.exists` raise as 3.11 does (3.14 returns False). Hardens this phase's own deliverable, so fixed in-phase: `_exists` reads a refused lookup as missing. Test: `test_t15_...`. |
| F4 | A file named `Files git ignores<!-- snapshot:end -->.txt` ends the snapshot early, so the ignored section is never read and the note reads as ready | yes | blocking | fixed | e2b2762 | Inherited from main (reproduced on the baseline by the reviewer, and red here). Fixed: the snapshot ends at a line that is its end marker and nothing else, in `takeover`, `write` and `check`; a snapshot with no ignored-files section counts as unlisted. Tests: `test_t16_...` (the inline name, and a name holding a newline before the marker), `test_t16b_...` (a second `write`, red before: the ignored heading twice). |
| F5 | The brief's C1 says byte for byte, but a path holding a newline is written escaped | yes | completeness | rejected | - | The difference is spec IF6's, which the brief's claim left out; no code defect. The claim's wording is the brief's, not the spec's. |

Convergence: 5 findings, 4 blocking or hardening, 1 self-inflicted of 5 (the stop rule's ratio is not exceeded). Round 3 ran on the owner's go-ahead of 2026-11-22, after the declared budget (one round after r1) was spent; it is outside that budget and the repairs above are unreviewed.
