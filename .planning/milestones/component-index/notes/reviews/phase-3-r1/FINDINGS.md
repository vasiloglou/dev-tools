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
| F1 | `phase.test_selection`'s `does` says acceptance tests run only once their phase is complete or with `--phase NN`; a named acceptance test path also runs | yes | completeness | fixed | bdb0287 | Reproduced by reading `phase_selection.py:44-55` (the `named` list wins over the phase's status) and the module docstring, which says so. `does` and `verbs` now name it; `search "run a named acceptance test"` finds `phase.test_selection` first. No code test: the catalog is data, and phase 4's test checks it is current, not true |
| F2 | `subsystem.rule_check`'s `notes:` puts the `importlib` load of `phase_tool.py` under `check --phase` and gives one order for every command | yes | completeness | fixed | bdb0287 | Reproduced by reading `rules_check.py`: `check_phase` calls `read_plan_facts` (phase_tool.py facts) before `read_facts` (components_index.py facts); `test` calls `vocabulary`, which reads the index facts and then loads `phase_tool.py` with `importlib`. `notes:` now says which command does what; the spec gains IF1, with its earlier wording kept |
