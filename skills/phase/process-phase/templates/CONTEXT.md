---
phase: "{{PHASE}}"
title: "{{TITLE}}"
slug: {{SLUG}}
status: draft
evidence_gate: required
---

# Phase {{PHASE}}: {{TITLE}} — Context

## Concrete Intent
<!-- One paragraph: what exists at the end of this phase that does not exist now. Cite the ROADMAP Goal. -->

## Goals and targets
<!-- Filled from NN-EVIDENCE/prove.md §1. Each goal: metric, frozen real asset, numeric target, how measured, and the prototype verdict (Go / Pivot / Kill). Specify locks only the targets that held. -->

| Goal id | Goal | Metric | Asset | Target | How measured | Verdict |
|---|---|---|---|---|---|---|
| G1 | | | | | | |

## Components in scope
<!-- From the component index, before any architecture decision (discuss.md §1): one row per capability the phase needs. -->

| Capability | Component id or external name | Status | Reuse / adapt / reject |
|---|---|---|---|
| | | | |

## Time budget
<!-- Phase time budget in hours; scope checkpoints at 50% and every further 25%. -->
-

## Expected Outputs
<!-- Modules, tools, skills, docs, fixtures. Real paths. -->
- 

## Entry Criteria
<!-- Copied from ROADMAP "Depends on", plus the baseline. Orient does not run a new full suite: cite an existing result, or write "unknown". -->
- Phases listed in **Depends on** are `complete`.
- Baseline: an existing suite or CI result with its revision and known failures (`{{PHASE}}-EVIDENCE/baseline.txt`), or "unknown".

## Exit Criteria
<!-- Copied verbatim from the ROADMAP block; each becomes >=1 acceptance test in Step 2. A Killed goal or deferral removes or changes one only through a user-approved DEC that amends it here and in the ROADMAP (cite the DEC). -->
- 

## Decisions

| CX | Tag | Decision | Source |
|---|---|---|---|
| CX-01 | LOCKED | | DISCUSSION-LOG Q1 |

Tags: LOCKED (binding; tests encode it) · DEFERRED (names the phase or OQ that decides) · DISCRETION (implementer decides within bounds; recorded in SUMMARY).

## Not in this phase
<!-- Explicitly excluded scope, with the phase or todo that owns it. -->
- 

## Cross-Phase Dependencies
<!-- What this phase consumes from earlier phases and promises to later ones (interfaces, tool ids, schemas). -->
- 

## Migration Impact
<!-- Legacy modules touched (see MIGRATION.md): keep | shim | move | freeze. -->
- 

## Data & Eval Impact
<!-- Goldens affected (golden_impact), fixtures added, metrics this phase will gate on. -->
- 

## Gates Applicable
<!-- From `phase_tool.py status` gates_applicable. -->
- 

## Open Questions
| Question | Blocking? | Resolution path |
|---|---|---|
