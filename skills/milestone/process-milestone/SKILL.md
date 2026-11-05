---
name: process-milestone
description: Execute or resume a named development milestone through its phases, required reviews and closure evidence. Supports auto=true for explicitly delegated milestone approval gates. Use for whole-milestone execution; use process-phase for a single phase and start-milestone for planning only.
---

# Process Milestone

Coordinate a whole milestone using [process-phase](../process-phase/SKILL.md).
The phase skill remains the normative execution protocol; this skill selects
ready phases, preserves milestone-wide authorization and owns the final question
sweep and close record. This is a development-process skill, not a product
command.

**Project hook.** If `references/project.md` exists in the process-phase skill
directory, read it first. The project owns it; it names the project's review
instrument, test and gate commands, standing design rules and any
project-specific record fields, and it governs project-specific matters.

## Invocation and authority

Invoke `process-milestone MILESTONE [auto=true|auto=false]`. Accept the shorthand
`process-milestone MILESTONE auto` as `auto=true`, including an `@` mention or
natural-language request with the same explicit delegation. Omission defaults
to `auto=false`. A request to create/install this skill does not invoke it.

Resolve the named scope from the user's request and existing conversation. A
whole-milestone execution request selects this coordinator and process-phase
for that milestone; no further sibling handoff permission is needed between its
phases. It does not select a paid review instrument or authorize reviewer
subagents.

With `auto=false`, prepare concrete artifacts and stop at outstanding owner
gates required by the effective plan or process-phase. Honor already recorded
approval rather than asking again for the same scope and bytes.

With `auto=true`, explicit owner delegation covers plan/spec/close approval
rulings and amendments within this named milestone. Complete each artifact's
implementability/verification sweep before recording a **delegated approval
(auto=true)** with date, authorization source, exact SHA-256, scope, decisions,
budget and review instrument. Retain prior rulings when amending them. Never
describe delegated rulings as the owner's personal reading of the artifact.
This delegation persists across phases and resumed turns until revoked; another
milestone's delegation never transfers.

Auto advances through satisfied owner gates; it does not manufacture evidence,
skip required reviews, waive stricter scope limits or authorize paid calls,
reserved data, broad historical suites, publication, opt-in gates or PR merge.
Follow the repository's `AGENTS.md` and `CONTRIBUTING.md` where present. An
[opt-in gate](../process-phase/references/architect-overrides.md) needs
its own explicit current owner request for subject and scope.

## Resolve readiness before execution

Read `{{devtools:planning_dir}}/PROJECT.md`, the whole effective canonical milestone plan,
amendments, the plan-gate record
([milestone record format](../process-phase/references/milestone-record-format.md))
and any retained plan-review notes, applicable question registers and prior
phase/close records. Resolve all output beneath
`{{devtools:planning_dir}}/milestones/<milestone>/`; reject paths escaping the repository or
symlinks redirecting planning elsewhere. Preserve canonical plan paths and IDs.

If the plan or scaffold is missing, report the prerequisite and offer
[start-milestone](../start-milestone/SKILL.md) or, for a missing scaffold, the
project's own scaffold workflow (`references/project.md`). Do not invent a plan
or invoke planning or other workflow skills automatically.
A draft plan may be prepared for its required review and owner/delegated gate;
implementation cannot begin before that gate is satisfied. Once ruled, the gate
is recorded as that format's plan-gate record.

Build a phase readiness table from records: phase ID, dependencies, approved
spec/gate, completed criteria, review/record evidence and next action. Completion
labels alone do not establish readiness. Verify cited artifacts/digests; changed
bytes invalidate only affected claims and controls. Preserve historical records
and make missing/stale evidence explicit instead of silently replacing it.

Check the plan's required plan/close review instrument. The project's
plan-review bar (`references/project.md`; default: one independent reviewer in
a different tool) remains binding where the plan or protocol requires it.
Explicitly selected review tools/delegation can be used within their scope and
credential contract.
If no instrument is selected, finish reviewable preparation and request that
specific missing choice; auto is not a tool selection. Follow the
[review convergence rules](../process-phase/references/review-convergence.md)
and never relabel one reviewer as a multi-reviewer review.

## Run the ready phases

Select the first unfinished phase whose hard prerequisites are discharged.
Follow the plan's dependency order; do not launch parallel implementation merely
because phases look independent. Optional phases cannot supply required inputs.
For a completed requested milestone, report its recorded result unless the owner
explicitly asks to reopen it.

For each phase, use `process-phase PHASE MILESTONE` with the effective auto setting:

1. Harvest all phase, cross-cutting and carryover obligations, including the
   plan's sections 0, 4, 9 and 10 and relevant review/compatibility inventories.
2. Prepare the spec and implementability sweep before its owner/delegated gate.
3. Implement, run focused affected gates, review the diff independently, review
   refactoring, and record/commit under process-phase's contracts.
4. Audit every criterion against measured evidence. Skipped lanes,
   collection-only checks and missing reviewer results are not completed gates.
5. Recompute readiness and proceed to the next phase without another permission
   request when the existing authorization covers it.

If a phase is blocked, name the exact missing input/decision/evidence and continue
independent work the plan authorizes. Do not bypass a dependency or mark a phase
complete to keep the walk moving. Record refuted premises and scope-changing
findings through the phase protocol; do not silently rewrite the accepted plan.
Any approved plan repair must identify its new bytes, invalidated claims and
required rechecks before dependent execution resumes.

Use topic branches and explicitly staged commits. Submit/attach PRs for changes;
never push directly to main or merge without explicit owner authorization. Update
the same PR for the named work when appropriate. Preserve unrelated user changes.

## Close the named milestone

After all mandatory phases have their own completed gates and records, evaluate
the milestone's actual exit predicates and impact closure. Perform the required
independent close review; phase reviews do not substitute for it. Review only
within explicitly selected instrument/credential/agent authority.

Sweep inherited and newly discovered questions. Every row is resolved with
evidence, accepted as an explicit residual, or deferred to a named owner/target.
Record missing acceptance evidence honestly; a successful sequence of activities
does not establish closure. A separately required human acceptance or external
prerequisite remains pending unless the effective authorization satisfies it.

Repair the plan. Phases defer plan repairs to this point: for every refuted
premise or open-questions row in which a phase record names a plan repair,
amend the canonical plan with provenance (the raising record's path, the date,
the prior wording retained), or disposition the row in the sweep as carried or
retired with its reason. A repair is a plan amendment and falls under the close
ruling; the close record cites the amended plan's SHA-256.

Write the next numbered milestone close record using the
[milestone record format](../process-phase/references/milestone-record-format.md).
Include phase
record references, exact exit-gate commands/results, artifact SHA-256s, review
scope/findings/dispositions, refuted premises, question sweep, residuals and
boundaries. Record the owner or delegated close ruling distinctly from tests and
review. Update milestone-local navigation with that record; preserve history.

Report the phase count completed, remaining blockers, close status, evidence and
PR. Distinguish local completion, recorded acceptance and merge/publication.
Stop at the named milestone; do not automatically start a successor.
