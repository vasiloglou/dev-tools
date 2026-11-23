# Findings ledger: pr-47-r1

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
| F1 | The dirty check reads only `skills`, `agents`, `devtools` and `examples`; a local change to a configured source elsewhere is bypassed when the checkout is behind | yes | hardening | fixed | 2679d27 | Reproduced 2026-11-23 at fe1c2c2 with a scratch upstream and a clone one commit behind: `scripts/one.py` edited in the clone, `resolve_source` returned `upstream`, and `apply` delivered `ONE = 2`, not the clone's `ONE = 'mine'`. Every unit dev-tools ships lies under `skills` or `agents`, so no shipped config reaches it today; it refutes the premise of phase 2 decision S2 ("what the sync reads"). Fixed on the owner's "fix": the config's sources are added to the checked paths. Regression test: `test_own_work_in_any_path_the_config_takes_keeps_the_checkout`, red at fe1c2c2 |
| F2 | With `sync = []`, `check --strict --source <a folder that does not exist>` exits 0, as if it had compared | yes | hardening | fixed | 2679d27 | Reproduced at fe1c2c2: a project applied with `sync = []`, then `check --strict` with a missing source printed `0 managed file(s), 0 problem(s)` and exited 0. A config with any entry already exits 5 (`source not found in dev-tools` is caught as not compared). Fixed: a source that is not a folder is a configuration error, reported by check as not compared. Regression test: `test_a_source_that_is_not_a_folder_is_not_compared`, red at fe1c2c2 |
