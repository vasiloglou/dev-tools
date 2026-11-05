---
phase: "{{PHASE}}"
plan: "{{PHASE}}-01"
title: "<plan title>"
wave: 1
depends_on: []
requirements: []            # REQ ids, non-empty
turns_green: []             # locked acceptance test ids this plan makes pass
manifesto_refs: []          # T ids
skills: []                  # product or dev skills touched
migration:
  shims_added: []
  modules_frozen: []
  modules_deleted: []
golden_impact: none         # none | regenerate(<reason>)
metrics_expected: {}        # {<metric>: {target: , baseline: , source: PT|DEC-NNN}}
llm_dependency: none        # none | fake | replay
gap_closure: false
autonomous: true
---

# Plan {{PHASE}}-01: <title> (Phase {{PHASE}}: {{TITLE}})

## Objective
<!-- What this plan delivers, in one paragraph, and which acceptance tests it turns green. -->

## Reuse
<!-- components skill, Consult. `check --plan` requires searched: and external:, plus reuse: with existing COMPONENTS.md ids or new_component: with a reason. -->
searched: <queries (scripts/components_index.py search ...), capability index, git grep on earlier phase branches>
external: <dependency names checked, with version>
reuse: <component or subsystem ids, e.g. area.capability (adapt: ...)>
new_component: <area.capability because <reason no existing component fits>; delete this line when nothing new is built>
Proven method: <prove.md section this plan automates, with its measured cost, time and agent turns as the budget; a heavier existing step is not reuse>.

## Constitution check
| Thesis / rule | Touched? | How it is respected |
|---|---|---|
| Locked tests unchanged | yes | no file under tests/acceptance/p{{PHASE}}_* is edited |
| Project invariants (`references/project.md`) | | |
| Software contract | | |

<tasks>

### {{PHASE}}-01-T1 — <task title>
- **type:** auto
- **turns_green:** `tests/acceptance/p{{PHASE}}_<slug>/test_<capability>.py::test_<behaviour>`
- **unit_tests:** `tests/unit/<pkg>/test_<topic>.py` (written first, must fail)
- **read_first:** `src/<package>/...`
- **files:** `src/<package>/<pkg>/<module>.py`
- **action:** <concrete change>
- **verify:** `.venv/bin/python -m pytest tests/unit/<pkg>/test_<topic>.py -q` plus directly affected acceptance ids
- **acceptance:**
  - <checkable statement>
- **done:** [ ]

</tasks>

## Validation

Use focused red/green tests for each fix and reuse valid results. After fixes are
complete, the phase has one final full regression run in Verify. No separate
replay, evidence-review, fresh-verifier or duplicate suite loop.

## Risks and rollback
