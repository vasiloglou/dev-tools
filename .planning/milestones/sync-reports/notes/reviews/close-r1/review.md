<!-- Edited by review_tool.py sanitize: 2 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 13 SHA-256 hashes match the brief. I found two issues.

1. **F1 — Invalid nested config can crash `check`.** At [devtools/sync.py:553](<repo>/devtools/sync.py:553), only `SyncError` is caught, but malformed nested values can raise other exceptions.

   Reproduction: use a valid receipt and this configuration, then run `check --source <checkout> --as-is`:

   ```toml
   [[sync]]
   source = "skills/handle-issue"
   dest = "copies"
   values = []
   ```

   I reproduced this in memory through `main`: it prints `0 managed file(s), 0 problem(s)`, then raises `AttributeError: 'list' object has no attribute 'items'`, without a warning. Ordinary `check` therefore fails instead of retaining its receipt verdict; strict mode also loses its intended exit 5. Validate nested config shapes and turn these errors into `SyncError`. The record’s general claim about wrong-shaped configurations is broader than the implementation establishes.

2. **F2 — The site incorrectly promises a one-time check report.** [docs/adopt.html:185](<repo>/docs/adopt.html:185) says a new piece is named “once, on the next update or check.”

   Reproduction: keep a receipt whose `shipped` list lacks an eligible unit, then run two checks without applying. I reproduced both calls in memory: each printed the same new-unit report, and each strict check exited 5. Checks do not advance the receipt. Describe the report as continuing until the next successful apply, as the plan specifies. This is a documentation completeness issue with an observable consequence.

The completion predicates stand as follows:

| Predicate | Assessment |
|---|---|
| C1 | The dedicated fixture/test and recorded output establish the requested 0, 0, 5 case. |
| C2 | The entire baseline test file is an unchanged byte-for-byte prefix. Execution is supported by the recorded gates. |
| C3 | Independently confirmed in memory against baseline: identical clean, content-drift and mode-drift output/exits, with subprocess creation forbidden. |
| C4 | Supported by the local-upstream tests, implementation and recorded delivery run. I did not independently execute those filesystem fixtures. |
| C5 | Plugin build check exited 0. Component-index check exited 0 with `--no-cache`. Full-suite evidence is recorded, not independently rerun. |
| C6 | Partially established; F2 needs correction. Both example configurations produced empty unit reports, and the first-sync capture matches the current calculated output of its displayed config. |
| C7 | Outstanding: the close record must follow this review. Its absence at this point is expected. |

The records explicitly disclose the important existing limits: local-only upstream tests, simulated timeout, unchanged running tool, symbolic-link fallback, restricted dirty-check paths, unreviewed repairs and stale walkthrough captures.

I could not rerun pytest, create scratch checkouts, perform a real fetch, test the real downstream project, or independently authenticate historical capture provenance. The review requires read-only operation, and this environment prohibits filesystem writes. No files were changed.

VERDICT: CHANGES_REQUESTED