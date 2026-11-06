# Step 5 — Verify

Verify consolidates TDD results and one final full regression run. It requires
`phase_status: implemented`. The supervisor may perform it; a fresh context or
separate reviewer is not required. The validation policy in `../SKILL.md`
supersedes older repeat-run requirements in plans and decisions.

1. Check that each approved acceptance outcome has a meaningful test/result.
   Reuse results for unchanged tested code. Run only any uncovered required tests
   (including relevant slow tests), rather than rerunning whole phase packages.
2. Run the default full suite **once**, after fixes and focused tests are done.
   Run it with `-rfE` so the log names every failed and errored test even if a
   worker crashes. Keep one log with the command, tested revision/diff, counts
   and failures.
   Golden, architecture and skill tests already covered by that run do not get
   separate duplicate runs.
3. Complete only the remaining static checks in `gates.md`. Reuse valid existing
   results; optional code review is not a blocking gate. Replays may be ordinary
   tests, not a separate validation campaign.
4. Write `NN-VERIFICATION.md` from `../templates/VERIFICATION.md`: acceptance
   outcomes, commands/results, remaining failures and dispositions. Link the
   focused results and final log; do not create per-round evidence packets or
   independent evidence audits. Keep records sufficient to reproduce a failure.
5. Run the lightweight `evidence-check --phase NN` and `check --ignored` once.
   They check paths/tracking, not test correctness, and do not start a new review.

An advisory check, not a step: `check --scope NN` compares what the phase branch
changed with what the plans declared. It has not yet been run on real projects and
nothing requires it; run it when you write the summaries' Deviations tables, and treat
each line as a place to look.
- A `warning:` names a changed file that is in no task's `files` or `unit_tests` and
  in no row of a summary's Deviations table. If the change belongs to the phase, add
  the row; if it does not, take it out of the branch.
- An issue names a component that is new in the catalog and on no plan's
  `new_component:` line. Confirm it with the user as a deviation.
- Not judged: planning files, this phase's acceptance tests and locked fixtures
  (written before the plans), and the files of the component index.

If final regression fails, reproduce/fix through focused tests and report the
result honestly. Do not automatically start another full run. If code changes
invalidate that run, state the limitation; a second full run requires the user's
instruction. Never label stale full-suite coverage as current.

A gap is only a failing required test, unmet approved exit criterion or actual
blocking check. Everything else is a concise logged finding. A missing fresh
review, replay report or independent audit is not a gap. After gap fixes, run
focused regressions; do not restart verification from PG1 by default.

UAT applies only to genuinely human acceptance criteria. Existing recorded human
decisions remain valid for their unchanged scope. Do not repeat user ceremonies
merely because a report is being finalized.

A missing report row at Close needs a targeted check, not another full test run.

Use `phase_tool.py advance --to verified` only when required results are current
and no unapproved blocker remains. With a failing required test or unmet exit
criterion, use `advance --to gaps_found`. When only a person's decision is
outstanding (a human acceptance criterion, or a failure that cannot be
attributed), leave the status at `implemented`, write `human_needed` and the
open question in `NN-VERIFICATION.md`, and ask the user. A delegated verifier (the `phase-verifier` agent) reports the result to the supervisor and
does not change status or fix code.
