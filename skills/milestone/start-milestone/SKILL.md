---
name: start-milestone
description: Prepare or resume a development milestone plan, turning requirements and carryovers into phased deliverables, measurable gates and the first draft phase spec. Use when asked to start, plan or initialize a repository milestone. Does not execute phases or close a milestone.
---

# Start Milestone

Prepare a milestone for execution under this repository's development protocol.
This skill owns planning; [process-phase](../process-phase/SKILL.md) owns numbered
phase execution and its owner gates.

**Project hook.** If `references/project.md` exists in the process-phase skill
directory, read it first. The project owns it; it names the project's review
instrument, test and gate commands, standing design rules and any
project-specific record fields, and it governs project-specific matters.

## Resolve the milestone and scope

Accept `start-milestone <milestone>` or “plan the next milestone.” This is
a skill invocation, not a shell command. Resolve the named subject from the
request and existing plans. Ask only if ownership or scope remains ambiguous.
Do not infer a milestone from an unrelated project's roadmap.

All planning output belongs under `{{devtools:planning_dir}}/milestones/<milestone>/`.
Validate the resolved path stays inside the repository and is not a symlink to
another location. Existing milestones keep their canonical plan path and phase
IDs. A new plan normally lives at `notes/<milestone>-plan.md`, not a competing
`PLAN.md` or a second planning directory.

Read before authoring:

- The repository's `AGENTS.md` and applicable local instructions.
- The repository's `CONTRIBUTING.md` where present, the process-phase protocol
  and its relevant planning/approval/review references.
- `{{devtools:planning_dir}}/PROJECT.md`, the complete effective plan/roadmap if present,
  and the applicable open-question register.
- Prior plans, phase/close records and amendments assigning carryovers; relevant
  source, tests and docs for feasibility. Status summaries alone are insufficient.

If `{{devtools:planning_dir}}` is absent, report that prerequisite and offer the
project's own scaffold workflow (`references/project.md`); do not silently
invoke another skill or create an
alternative scaffold. In an existing project, a request to start a milestone
authorizes appending that milestone's planning artifacts. Preserve PROJECT.md,
other milestone records and unrelated user files.

## Harvest, reconcile and partition

Build an obligations table citing source path and section for each deliverable,
constraint, dependency, cross-cutting gate and carried limitation. Distinguish
observed evidence, inherited claims and proposed targets.

In a project with a component index (the `components` skill), search it for
each capability the milestone proposes to build, and carry what already exists
into the table as observed evidence with the component id. Run
`components_index.py review` once: if many entries are older than their code,
say so and offer a review of the index (that skill's Review mode) before the
plan relies on it. The offer is the owner's to accept; planning continues
either way.

Check readiness from records and evidence. Unresolved prerequisites may leave
dependent phases blocked; name what unblocks them. Inspect a completed milestone
as complete unless the user asks to reopen it. On resumption retain approvals,
phase IDs, records and evidence; amend the canonical plan with clear provenance
instead of resetting history or silently invalidating approvals.

Perform an implementability pass before declaring the plan ready:

- Can each input and upstream capability exist when its phase needs them?
- Can the selected tools meet dependency, isolation and public-interface rules?
- Do evaluation partitions, runtime lanes, tuning rules and budgets agree?
- Are outcomes, thresholds, refusals and comparison denominators measurable?
- Does every promised capability have a falsifiable end-to-end result?

Record conflicting clauses with source locations, a proposed resolution and the
required ruling. Do not rewrite approved gates or treat a proposal as accepted.
Continue unaffected planning while decisions remain pending. Preserve explicit
owner authorization or delegated approval for its named scope; never transfer
another milestone's delegation.

Partition work into stable phase IDs with coherent, testable outcomes. Each
implementation phase owns a spec, approval, implementation, focused tests,
independent review, refactoring review and record. Cross-cutting documentation,
graphics, packaging and integration requirements need named phase owners and
gates. Optional work cannot supply mandatory prerequisites. Milestone closure
has its own gate/record rather than pretending it is a feature phase.

## Write the planning artifacts

Preserve an existing plan's effective structure. For a new plan use the shape
consumed by process-phase, with a goal/status and completion predicates followed
by these sections:

| Section | Content |
|---|---|
| 0 | Binding design rules |
| 1 | Scope, sources and authority |
| 2 | Contract proposal and product behavior |
| 3 | Dependencies and artifact homes |
| 4 | Phases, deliverables, named criteria and inherited residuals |
| 5 | Documentation/skill/compatibility surfaces |
| 6 | Risks and required controls |
| 7 | Out-of-scope work |
| 8 | Execution, approval and review protocol |
| 9 | Per-phase verification story, expected results and affected consumers |
| 10 | Owner decisions and open questions |

Include the harvested obligation-to-phase/gate mapping, baseline, relevant
budgets and closure evidence requirements. Label unresolved exact commands as
unresolved rather than inventing executable gates. Distinguish proposed,
owner-approved and explicitly delegated rulings, with dates/scope/hashes for
actual approval. Planning authorship is not approval or publication authority.

Prepare detailed contracts only for the first ready phase, at
`notes/phase-<ID>-spec.md`, following the
[spec note contract](../process-phase/references/spec-note-contract.md) and
[standing rules](../process-phase/references/standing-rules.md). Authoring this
draft does not run process-phase or record its owner gate. If required decisions
or inputs are absent, retain a clearly blocked draft naming those gaps; do not
claim execution readiness. Later phases remain actionable outlines until their
prerequisites are known. Preserve an existing approved spec rather than replacing
it during planning.

A milestone-local README can link the canonical plan/spec, readiness, pending
decisions and next action. Do not add a global STATE.md, duplicate roadmap, empty
review/evidence records or implementation-started status merely because planning
files exist. Material execution records follow the
[milestone record format](../process-phase/references/milestone-record-format.md)
when execution is explicitly selected.

## Verify and hand off

Check obligation ownership, acyclic dependencies, mandatory versus optional
prerequisites, phase counts and local links. Review the diff for unrelated edits
or credential/private-data inclusion. Planning uses authorized read-only evidence;
do not run paid tools, reserved test splits or acceptance lanes merely to
fill a plan. Missing measurements remain missing evidence.

Plan review and milestone close are held to the project's plan-review bar
(`references/project.md`; default: one independent reviewer in a different
tool) and the bounded convergence rules from
[process-phase review guidance](../process-phase/references/review-convergence.md).
Select a review instrument explicitly; using this skill does not activate
any review instrument or authorize reviewer subagents. Never claim a review
opinion over amended bytes that were not reviewed.

The plan review and the plan gate are recorded in the plan-gate record of the
[milestone record format](../process-phase/references/milestone-record-format.md).
Before that record exists, say in the plan's status line and in the report
whether the plan review ran (instrument and reviewed SHA-256) or did not (and
why), so an unreviewed plan never reads as reviewed.

Report the canonical plan and first draft spec, phase count, readiness, decisions
and next action. Default `auto=false`; implementation follows the concrete spec's
owner gate. Existing explicit delegation remains effective within its scope.
Hand off to process-phase only when the user selects that execution workflow;
otherwise leave the reviewable planning artifacts. Contributions use a topic
branch and PR; merge, publication and opt-in gates retain their separate owner
authorization. This skill does not close milestones or change repository policy.
