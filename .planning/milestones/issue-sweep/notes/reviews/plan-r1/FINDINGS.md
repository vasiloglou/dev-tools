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
| F1 | Issue 43 pairs exit 2 with an envelope for `phase_tool.py`; the plan chose exit 2 with plain text, and no criterion or decision row carries the envelope | yes | blocking | fixed | 3663a15 | Reproduced by reading: the issue (`notes/issues-2026-11-23.md`, "What would help" of issue 43) says "exit 2 (with an envelope, for `phase_tool.py`)"; the plan's section 2 chose plain text and D10 offered no reading with an envelope. Repaired in the plan: decision row D11 (proposed: the envelope), criterion P3.4b, C6, section 2 and the obligation map. Regression: P3.4b, a test of `phase_tool.py --format json status` for phase 3's spec |
| F2 | The requirement that `review_tool.py` stays lint-clean is mapped to criteria that run no linter | yes | hardening | fixed | 3663a15 | Reproduced by reading the map row, which named P3.4, P3.5 and D10. The linter and its configuration were then found in pull request 34 (`ruff` 0.16.2 with gnd-public's `pyproject.toml`) and run here: the three scripts #34 cleaned exit 0, five other scripts exit 1 and were never clean. Repaired in the plan: criterion P3.6, a gate row in section 9, a baseline row in section 3, the map row split. Fixed in this round because phase 3 edits two of the three scripts. Regression: the section 9 gate |
| F3 | `base_snapshot` also serves `facts --base`, so D6 changes the base `rules_check.py check --base` compares with, and the plan specified `changed` only | yes | blocking | fixed | 3663a15 | Reproduced: `components_index.py facts --base main` wrote revision `b685e82` with 0 rows of `component_has_status`; `--base origin/main` wrote `cecebc6` with 12. `rules_check.py:393` passes `--base` straight to `facts`. Repaired in the plan: section 2 (both follow the rule; `facts` keeps one JSON document on standard output), criterion P2.2b, section 5, K5, D6, a baseline row. Regression: P2.2b, for phase 2's spec |
| F4 | S3 of the phase 1 spec expects two tests where plain pytest keeps three (`test_unit` too) | yes | blocking | fixed | 3663a15 | Reproduced against this session's own scratch run of the plugin: plain pytest kept `test_unit` in every run, and S1 of the same spec lists it. An equality check on S3's set would fail on the unchanged plugin. Repaired in the spec: S3 names the three tests. Regression: S3 |
| F5 | A test of the pytest plugin already exists (`tests/test_tools.py:1879`), and the plan said nothing it builds exists | yes | hardening | fixed | 3663a15 | Reproduced: `sed -n 1879,1894p tests/test_tools.py` shows `test_plain_pytest_leaves_out_phases_that_are_not_complete`; `examples/phase-project.devtools.toml:70` delivers the plugin as `conftest.py`, which the `project` fixture applies. It refutes part of issue 42's premise. Repaired: the plan's status, C2, section 2, the baseline, "What the index says", P1.3 and the map; the spec's section 6.2, reuse table, index entry (it lists both test files) and a new decision row D5 (keep the test and add a file; extend it; or list it and add nothing). Regression: gate G-review of the spec |
