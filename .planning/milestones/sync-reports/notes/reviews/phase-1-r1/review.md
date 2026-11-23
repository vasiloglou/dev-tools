<!-- Edited by review_tool.py sanitize: 5 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 12 listed hashes match. No files were changed. Reproductions below ran the real functions with an in-memory filesystem; subprocess failures and source identities were mocked where indicated.

**Findings**

- **F1 — Blocking: invalid config values crash `check`.** [sync.py:386](<repo>/devtools/sync.py:386). After a successful sync, replace the config with `sync = 42` and run plain `check`. It prints the clean receipt summary, then raises `TypeError`; strict check raises too. `[[sync]]` with `source = 42` also reproduces this. The specified behavior is a warning while preserving exit 0, or exit 5 under strict check. Only `SyncError` is caught.

- **F2 — Hardening: unavailable Git breaks the legacy receipt verdict.** [sync.py:388](<repo>/devtools/sync.py:388). With a clean project and an implicit source checkout, make launching `git` raise `FileNotFoundError`. Plain and strict `check` both raise after printing the summary. Baseline `check` and current `--receipt-only` return 0 on the same project. Source-comparison startup failures should preserve the receipt verdict and warn; strict should return 5.

- **F3 — Blocking: pending counts disagree with what apply would change.** [sync.py:545](<repo>/devtools/sync.py:545). After syncing the fixture, add `new.md` upstream and place identical copies at both project destinations. `check --strict` reports `an apply would create 2 file(s)` and returns 5, while `apply --dry-run` prints `dry run: {"keep": 14}`. Counting receipt differences instead of `plan` actions causes a false pending report and strict failure. The spec explicitly excludes `keep` actions.

- **F4 — Completeness: an empty managed-file receipt suppresses reports.** [sync.py:532](<repo>/devtools/sync.py:532). Apply the valid config `sync = []`, then add `skills/extra/SKILL.md` upstream. Strict check returns 0 and prints only `0 managed file(s), 0 problem(s)`. It should report the new unit and return 5. Removing `shipped` from that receipt also fails to produce the promised one-time list. Both branches incorrectly require a nonempty `files` dictionary.

- **F5 — Completeness: the edited-file capture omits current output.** [adopt.html:152](<repo>/docs/adopt.html:152). Execute the displayed shelf config, then append the displayed line to `references/verify.md`. Current `check` prints the drift and summary, followed by the four-unit named report shown in the preceding capture. This capture jumps directly to `exit code 1`, so C7 is false.

**Checked and found true**

- The observed fixture produces exits 0, 0, 5 for dry-run, check and strict check, including the named file and two pending updates.
- Declined units and untaken workflows stay silent. With nonempty receipts, new and legacy reports end after apply.
- Invalid declined values return 2 without writes; stale paths warn.
- Receipt-only output matches baseline with subprocess execution forbidden; drift returns 1 despite strict notes.
- Matcher checks covered `names_in` with bare, qualified, newline and Unicode names; path coverage with prefix collisions, trailing slashes, `./` and Unicode; and name extraction/workflow slicing with nested agents and scripts. Excluded and binary files name nothing; taken names suppress duplicate reports.
- Both example configs produce empty planned unit reports.
- The first shelf capture and older-source report were reproduced in memory.
- Plugin-build and component-index gates exited 0; the index used `--no-cache`.

**Not checked**

The full pytest suite and physical scratch-project runs create files, so they were not run under the brief’s read-only rule.

VERDICT: CHANGES_REQUESTED