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
| F1 | `check` catches only `SyncError`, but `read_config` raises `TOMLDecodeError` for bad TOML and `PermissionError` for an unreadable file, so plain `check` would end in a traceback | yes | blocking | fixed | e6c3e2b | Reproduced 2026-11-23: the real `read_config` on a folder whose `.devtools.toml` is `[[sync]` raised `TOMLDecodeError`, not `SyncError`. Repaired in the spec: `read_config` turns read and parse errors into `SyncError`. Regression tests: phase 1 T14 (bad TOML, unreadable) and T14b |
| F2 | T6 and T7 expect no block while `review-pr` stays named in `milestone_project` | yes | blocking | fixed | e6c3e2b | Reproduced by walking the spec's normative order over the fixture as written: `review-pr` is not taken, not declined, under a taken workflow folder, and named, so step 4 reports it on every run. Repaired: T6 and T7 decline `review-pr` and `agents`. Regression test: T6, T7 |
| F3 | T18 requires an example's whole output to be `applied: {…}`, but `phase-project.devtools.toml` has `after_apply`, which prints its own line | yes | blocking | fixed | e6c3e2b | Reproduced: `examples/phase-project.devtools.toml` line 9 sets `after_apply`, and `cmd_apply` prints `after_apply: <command>` after a fresh apply. Repaired: T18 asserts the absence of the report's headings only. Regression test: T18 |
| F4 | The strict-exit tests combine causes, so dropping one cause still passes; no named-and-new case | yes | completeness | fixed | e6c3e2b | Reproduced by reading T1 and T6: each has two causes at once. Fixed in this round, though completeness, because the spec claims per-cause coverage and phase 1 builds those tests anyway. Regression tests: T23a to T23c, T24 |
| F5 | Phase 2 gives no outcome for a configured upstream whose ref does not exist | yes | completeness | fixed | e6c3e2b | Reproduced in this worktree with command-scoped config `branch.<b>.merge=refs/heads/no-such-branch`: `git rev-parse --abbrev-ref @{upstream}` and `git rev-list --left-right --count HEAD...@{upstream}` both exited 128. Repaired: a row in the plan's phase 2 table and criterion P2.3b, for phase 2's spec to test |
| F6 | The by-hand gates name bare `apply` and `check`, which do not run as written | yes | completeness | fixed | e6c3e2b | Reproduced by reading plan section 9: no interpreter, no `--project`, no `--source`. Repaired: full commands with `$SCRATCH` paths in plan section 9 and the phase 1 spec, section 8 |
