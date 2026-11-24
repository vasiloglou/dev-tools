<!-- Edited by review_tool.py sanitize: 5 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 22 SHA-256 hashes match the brief. I found five issues in the plan and spec.

1. **F1 — Issue 43’s envelope requirement has no acceptance criterion.**  
   [issue-sweep-plan.md:138](<repo>/.planning/milestones/issue-sweep/notes/issue-sweep-plan.md:138) chooses exit 2 while retaining the settings error message. Issue 43 explicitly couples that choice with an envelope for `phase_tool.py`, but P3.4 checks only the exit and stderr. Plain stderr with exit 2 could satisfy the plan while `phase_tool.py --format json status` still produces no parseable envelope.

   **Reproduction:** By reading: compare issue 43, line 254, with plan lines 138, 309 and D10. Require the envelope in a criterion, or explicitly record the decision to omit it.

2. **F2 — The linter requirement maps to criteria that cannot enforce it.**  
   [issue-sweep-plan.md:440](<repo>/.planning/milestones/issue-sweep/notes/issue-sweep-plan.md:440) maps issue 43’s requirement that `review_tool.py` remain lint-clean to P3.4 and P3.5. Those check settings exits and docstrings. None of section 9’s gates invokes the linter.

   **Consequence:** The milestone can meet every listed criterion while reintroducing the downstream lint failure that #34 corrected. **Reproduction:** By reading: trace issue 43’s final paragraph through this map and the gate table. Add a gate naming the linter version and configuration.

3. **F3 — The shared base resolver changes an additional compatibility surface.**  
   [issue-sweep-plan.md:254](<repo>/.planning/milestones/issue-sweep/notes/issue-sweep-plan.md:254) changes `base_snapshot`, which also serves `facts --base`. The compatibility surface and criteria describe `changed`’s notice and summary, without specifying what happens to `facts` or its consumers.

   **Observed reproduction:** Calling the current `facts` function with `main` returns revision `b685e82` and **0 listed components**; with `origin/main`, it returns `cecebc6` and **12**. Applying the proposed preference in the shared resolver therefore changes the baseline population used by rule checks. Specify whether that change is intended, discharge S0.1 for it, and test that `facts` retains valid JSON output.

4. **F4 — S3’s expected collection set omits the unit test.**  
   [phase-1-spec.md:265](<repo>/.planning/milestones/issue-sweep/notes/phase-1-spec.md:265) lists `test_done` and `test_inserted` for plain pytest after `completed_phases: 01, 6.1`. Under the table’s “set `collected` returns” heading, that is incomplete.

   **Observed reproduction:** Running the actual selection hook against the specified four items and state keeps **`test_done`, `test_inserted`, and `test_unit`**. Equality against the listed two-item set would fail on the unchanged plugin. Include `test_unit`.

5. **F5 — The reuse assessment misses an existing test of the plugin.**  
   [issue-sweep-plan.md:180](<repo>/.planning/milestones/issue-sweep/notes/issue-sweep-plan.md:180) says nothing being built already exists. However, `tests/test_tools.py:1879`, `test_plain_pytest_leaves_out_phases_that_are_not_complete`, already exercises plain pytest, `--phase 2`, and a named acceptance file. Its fixture syncs the plugin to root `conftest.py` through `examples/phase-project.devtools.toml:70`.

   **Reproduction:** Pytest collection finds that existing test; reading its assertions establishes the coverage. I did not execute its writing fixture. The proposed additional branches remain useful, but the plan should identify this existing test and decide whether to extend it or explain the separate fixture.

What I checked and found true:

- `build_plugins.py --check` and the current index’s `--check --strict` exited 0. Release status exited 1 with the recorded 0.1.6-ready output.
- Eight read-only pytest checks exited 0; the full suite collected 447 tests.
- The proposed guard, exercised against the actual note-generation function with filesystem operations mocked, skipped the exit-5 missing-extra case and kept the other specified cases running.
- An in-memory implementation of the proposed adapter preserved rows and ordering across all 256 combinations of the eight planning signs; the G1 list mutation affected both functions.
- Simulating the three index-entry edits produced both required `(0)` review groups, no validation errors and no unassigned modules.
- Current `changed` counts are 271/8 rather than the historical 263/0; the eight untracked milestone files explain the difference.

I could not run the full suite, scratch-project reproductions, plugin installation checks or the real GND-without-extra experiment under the read-only restriction. The proposed phase implementations also do not yet exist, so their final gates cannot be verified. No files were changed.

VERDICT: CHANGES_REQUESTED