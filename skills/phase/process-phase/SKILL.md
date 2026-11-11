---
name: process-phase
description: Runs one roadmap phase through the .planning/ contract, test first. Steps are Orient, Discuss, Specify, Plan, Implement with focused red/green tests, Verify with one final full regression run, and Close. Human gates follow Discuss, Specify and Plan, and Close has one too. Reuse valid test results; no repeated replay or evidence-review loops. phase_tool.py owns every status transition. Use when the user explicitly invokes /process-phase to start, resume or advance a phase, or asks what comes next on the roadmap. Explicit invocation only. Not for ad-hoc fixes outside the roadmap or for amending MANIFESTO.md outside a phase close.
argument-hint: "[NN|next] [--step discuss|specify|plan|implement|verify|close] [--mode guided|fast]"
disable-model-invocation: true
allowed-tools: Read Grep Glob Edit Write Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git add *) Bash(git commit *) Bash(git switch *) Bash(git merge *) Bash(git stash *) Bash(git worktree *) Bash(python3 .claude/skills/process-phase/scripts/phase_tool.py *) Bash(python3 .claude/skills/process-phase/scripts/codex_gate.py *) Bash(python3 .claude/skills/process-phase/scripts/coder_pool.py *) Bash(python3 scripts/components_index.py *) Bash(.venv/bin/pytest *) Bash(.venv/bin/python -m pytest *) Bash(codex exec *) Bash(codex --version) Bash(gemini *) Bash(claude -p *) Bash(claude --version) Bash(git checkout -- *)
---

# process-phase

Run one approved roadmap phase through `.planning/`, with tests first. Use
`phase_tool.py` for all status transitions; never hand-edit phase status fields.
Explicit invocation only; ad-hoc fixes do not start a roadmap phase.

## Validation policy

This policy supersedes older execution requirements for repeated replays,
independent evidence reviews, fresh-context re-verification and duplicate suite
runs, including those in existing plans. Product acceptance criteria, locked
tests, data safety and approval boundaries remain in force.

1. **TDD:** write or identify a focused test that fails for the actual defect,
   make the smallest fix, then run that test and directly affected tests.
2. **Reuse results:** record the command, result and tested revision/diff. A
   handoff, reviewer, report, status transition or commit containing only those
   same tested bytes does not justify another run. Unrelated edits do not
   invalidate focused results.
3. **One final full regression run:** once fixes and focused tests are complete,
   run the default full suite once in Verify. Do not also run it at Orient,
   Implement, a fresh verifier handoff or Close. Reuse it for golden,
   architecture and skill checks it already covers.
4. **No replay/review loops:** replay fixtures may be ordinary tests. Express
   required end-to-end outcomes as tests and run only the relevant tests for a
   fix. Do not start separate before/after full-model replays, oracle-validation
   campaigns, evidence packets or independent rerun rounds unless the user
   explicitly requests them. Code review is optional, not a new validation gate.
5. **If final regression fails:** diagnose with focused tests and report actual
   failures. Do not automatically repeat the whole suite. A source change that
   invalidates the final result must be disclosed; do not claim that the old run
   validates the new code. A second full run requires the user's instruction.
6. **Minimal record:** retain useful red/green output and one final regression
   log. Write a short final summary of commands, results and remaining failures.
   `evidence-check` only checks cited paths; it does not start an evidence review.

Always run from `.venv`. In a worktree without one, use the repository venv's
Python with worktree `src` first on PYTHONPATH, for example
`PYTHONPATH=src /path/to/.venv/bin/python -m pytest <test>`.

The commands here and in the references are for a Python project with pytest.
In a project in another language, `project.md` in this skill's `references/`
directory names the test command, how one phase's tests are run, and what a
failing run looks like. The rest holds as written: the acceptance tests of
phase NN live under the phase's acceptance folder, and the test lock hashes
whatever files that folder holds.

## Status and artifacts

| Step | Requires | Leaves with | Human gate |
|---|---|---|---|
| 0 Orient | any | unchanged | only unresolved scope/access choices |
| 1 Discuss | not_started | context_approved | CONTEXT with goals/targets and `prove.md` (prototype verdicts) |
| 2 Specify | context_approved | tests_approved | tests, red result and TESTLOCK |
| 3 Plan | tests_approved or gaps_found | plan_approved | implementation plan |
| 4 Implement | plan_approved | implemented | explicit checkpoint tasks only |
| 5 Verify | implemented | verified or gaps_found | only actual human acceptance criteria |
| 6 Close | verified | complete | manifesto amendment, merge or release |

`phase_tool.py status --phase NN --format json` gives the current step, missing
artifacts and applicable check IDs. The PG ids in `scripts/gates.json` remain for
compatibility; `references/gates.md` defines how existing results satisfy them without reruns.
Use `advance --to <status>` and `complete --phase NN` for transitions. `advance`
refuses a transition while a file the step should have produced is missing, or
while the phase depends on one that is not complete.

A project with no `.planning/` yet starts with `phase_tool.py setup`, which writes
the starter planning files (`references/artifact-formats.md`).

Inserted phases accept `N.M` or `NN.M`; paths use `NN.M` and acceptance packages
use underscores, for example `tests/acceptance/p06_1_<slug>/`.

## Step 0 — Orient

- Read status, the ROADMAP block, STATE lessons and only relevant requirements,
  decisions, risks and prior results. Honor prerequisites and explicit blockers.
- If `project.md` exists in this skill's `references/` directory, read it. The project
  owns it; it lists the project's invariants, extra gates and tool commands, and
  it governs project-specific matters.
- Work on the phase branch, never the base/release branch. Preserve unrelated
  changes and resume known work without discarding it.
- Reuse an existing baseline/CI log if available. Do not run a new full baseline
  suite. Establish any uncertain pre-existing failure with a focused base-revision
  test only when needed; otherwise report that the baseline is unknown.

Details: `references/orient.md`.

## Step 1 — Discuss

Prototype first: set goals with measurable targets (metric,
real asset, target, how measured), take a baseline on a frozen real asset, then
run a timeboxed prototype by hand or with a $0 script (default 2 hours) and give
each goal a Go/Pivot/Kill verdict. Validate the oracle cases the tests will use,
name the smallest outcome contract (the targets that held) and the deferrals.
This `NN-EVIDENCE/prove.md` is mandatory when CONTEXT has
`evidence_gate: required`; no real asset needs a DEC waiver. The prototype
measures once: no before/after replay campaign and no review rounds. Record
CONTEXT (with its Goals and targets) and the user's decisions, approve CONTEXT
and `prove.md` together, then advance to `context_approved`.

Details: `references/discuss.md`.

## Step 2 — Specify

Go straight from the prototype to tests: use `phase-tests` to lock the targets
that held (`prove.md` §5) and every retained exit criterion; Killed goals and
deferrals get no locked test, and one that removes or changes an exit criterion
needs a user-approved DEC amending CONTEXT and ROADMAP first. Helpers cite the
`prove.md` §4 oracle cases. Run them red
for the right reason, record traceability in `NN-TESTS.md`, and lock the tests and
fixtures with `testlock --phase NN --write --fixture ...`. Approve the contract,
then advance to `tests_approved`. Tests and expected outputs must not be weakened
to hide a product defect.

Details: `references/specify.md`.

## Step 3 — Plan

Reuse existing capabilities: search the component index (`components`
skill) for every capability a task builds, including the project's dependencies, and record
the result in each plan's `## Reuse` section. Plan `NN-01` automates the `prove.md` prototype on
the same asset and metric; other non-leaf plans start once it is green. Map tasks
to acceptance tests, list affected files
and focused verification commands, and keep only work needed for the approved
outcome. Plan independent tracks where useful. Plans do not add replay, review
or repeated-full-suite requirements contrary to the validation policy above.
Check the plan, approve it, then advance to `plan_approved`.

Details: `references/plan.md`; template: `templates/PLAN.md`.

## Step 4 — Implement

Implement each task through focused red → green → refactor. The supervisor
coordinates existing coder tooling, checks scope and commits; code review or
delegation is not a mandatory extra round. Reuse trustworthy results rather than
having every role rerun them. After a merge, run tests for changed integration
seams, not entire earlier phases by default. Do not run the full suite here.

A failed test drives a fix, not an evidence-review cycle. Normal corrective work
within approved scope does not need permission because of a write-round count.
Escalate a repeated unresolved cause or an actual scope/contract/safety decision.
Locked test changes still require the user's approval, a DEC, a re-lock and a
separate test commit. Project invariants (`project.md`, Step 0) still apply; no
silent paid calls.

Keep a concise task/plan summary, check the lock, and advance to `implemented`
when required focused/acceptance tests pass.

Details: `references/implement.md`; template: `templates/SUMMARY.md`.

## Step 5 — Verify

Use the current session, or hand off the existing results without making a fresh
verifier mandatory. Run **one final full regression suite** on the finished code.
Reuse focused/acceptance results and default-suite coverage; run only required
tests not yet covered, including relevant slow tests, before that final run.
Complete remaining cheap static checks once and record a concise result in
`NN-VERIFICATION.md`. No duplicate replay, code-review or evidence-review phase.

A gap is an actual failing required test, unmet exit criterion or blocking check,
not a missing reviewer ritual. Report known baseline failures honestly. Do not
mark changed code verified with stale results. Run the mechanical path check,
then advance to `verified` or `gaps_found`.

Details: `references/verify.md`, `references/gates.md`; template:
`templates/VERIFICATION.md`.

## Step 6 — Close

Close uses the completed verification results; it does not repeat tests or
replays. Use `complete --phase NN`, record concise lessons and commit the
bookkeeping, including the component index (assign new modules, update changed
subsystem flows, regenerate, the strict check and the `changed` check clean). Manifesto changes, merge to the base branch and release to main
retain their existing explicit human gates. Push/PR only when authorized.

Details: `references/close.md`.

## Useful checks

- `check --all`: planning, skill and test-lock consistency; template citations
  (`prove.md §N` exists and the words after it match its heading) and a DEC for
  any process-phase rule-text change in the working tree against the base
  branch, renames and untracked files included.
- `check --testlock NN`: locked tests and fixtures match their approved bytes.
- `golden-diff`: golden changes are declared.
- `migration-check`: no imports of modules marked deleted.
- `req-coverage`: requirements remain mapped.
- `evidence-check --phase NN`: cited result paths exist; no reviewer or rerun.
- `check --plans NN` (advisory, no step requires it): lists a contract test in the Traceability table that no plan task turns green, and plan requirements that are not the phase's.
- `check --scope NN` (advisory, no step requires it): lists a changed file that is in no plan task's `files` and no summary's Deviations table, and a new component no plan declared.

These are bookkeeping checks, not triggers for another validation cycle.
