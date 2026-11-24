# Findings ledger: phase-3-r1

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
| F1 | `phase_tool.py` checked three of its values only; `package_prefix: 7` or `process_skill: null` ended the load in a `TypeError`, exit 1, no envelope | yes | blocking | fixed | 43f6d83 | Reproduced on the built copy in a scratch project: both exited 1 with `TypeError`. Repaired: every value must have its default's type, a list must hold strings, and the load records the error for the envelope. Regression tests: the four `phase_tool.py` cases of `tests/test_tools.py::test_a_setting_of_the_wrong_type_exits_2`, red before |
| F2 | The other four loaders had the same gap: `verb_list: []`, `index_script: 7`, `planning_dir: 7`, `codex_model: 7` | yes | blocking | fixed | 43f6d83 | Reproduced by hand for `components_index.py` and `rules_check.py` (`TypeError`, exit 1); `handoff.py list` exited 0 here because `list` does not read `planning_dir`, so the test uses `write`; `review_tool.py` was held by its test, red before. Repaired by the same rule in each loader. Regression tests: the index and rule-check cases of `test_a_setting_of_the_wrong_type_exits_2`, and the added assertions in `tests/test_handoff.py::test_a_synced_copy_reads_the_settings_beside_it_and_refuses_an_unknown_key` and `tests/test_review_tool.py::test_settings_choose_the_model_and_an_unknown_setting_is_an_error`, each red before |
| F3 | The settings branch of `phase_tool.py` took the format and the command from raw tokens | yes | hardening | fixed | 43f6d83 | Reproduced: `--for=json status` printed Markdown. Repaired: the branch runs after the parser, through `ToolError`. Regression test: `tests/test_tools.py::test_the_settings_envelope_follows_the_parsed_command_line` (3 cases), red before; its second case was red only once it used the reviewer's own command line (`--root status check`) |
