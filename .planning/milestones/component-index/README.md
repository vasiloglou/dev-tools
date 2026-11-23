# Milestone: component-index

dev-tools gets a component index of its own code that can be searched by capability. Every
shipped module is covered, and a gate refuses a module without a component. Before that,
the milestone fixes issue 28: `dev-takeover` reports ready while an ignored path that the
note did not list is missing.

- **Plan:** [notes/component-index-plan.md](notes/component-index-plan.md), approved on
  2026-11-21 by delegated approval (auto=true): [001-plan.md](001-plan.md).
- **Plan review:** three rounds (Codex), `notes/reviews/plan-r1` to `plan-r3`, 12 findings
  in all, each reproduced and fixed. The stop rule fired after r3.
- **Phase specs:** [notes/phase-1-spec.md](notes/phase-1-spec.md),
  [notes/phase-2-spec.md](notes/phase-2-spec.md),
  [notes/phase-3-spec.md](notes/phase-3-spec.md) and
  [notes/phase-4-spec.md](notes/phase-4-spec.md).
- **Phases:**
  1. `takeover` checks every ignored path the note was written with (issue 28), released
     as plugin 0.1.4.
  2. An index can count more than one source folder, released as plugin 0.1.5.
  3. Build dev-tools' index in `.devtools/components/`.
  4. Keep it current: a test, gates in `.devtools/project.md`, and the documentation.
  5. Close.
- **Execution:** `process-milestone component-index auto`, from 2026-11-21. Merges, release
  tags and anything posted to GitHub still need the owner each time.
- **Branches:** phases 1, 2 and 3 are vasiloglou/dev-tools#29, #30 and #32, merged into
  `main` in that order on 2026-11-23, after `main`'s vasiloglou/dev-tools#34 was merged
  into each. Phase 4 is on `claude/component-index-phase-4`, cut from `main` at `827e766`.
- **Index:** [`.devtools/components/`](../../../.devtools/components/COMPONENTS.md), built in
  phase 3.
- **Records:** [001-plan.md](001-plan.md), [002-phase-1.md](002-phase-1.md),
  [003-phase-2.md](003-phase-2.md), [004-phase-3.md](004-phase-3.md),
  [005-phase-3-reread.md](005-phase-3-reread.md): every entry read in full, and the
  third review rounds of phases 1 and 2;
  [006-phase-4.md](006-phase-4.md): the test that keeps the index current, the gate rows
  and the pages.
