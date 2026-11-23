# Milestone: component-index

dev-tools gets a component index of its own code that can be searched by capability. Every
shipped module is covered, and a gate refuses a module without a component. Before that,
the milestone fixes issue 28: `dev-takeover` reports ready while an ignored path that the
note did not list is missing.

- **Plan:** [notes/component-index-plan.md](notes/component-index-plan.md), approved on
  2026-11-21 by delegated approval (auto=true): [001-plan.md](001-plan.md).
- **Plan review:** three rounds (Codex), `notes/reviews/plan-r1` to `plan-r3`, 12 findings
  in all, each reproduced and fixed. The stop rule fired after r3.
- **Phase specs:** [notes/phase-1-spec.md](notes/phase-1-spec.md) and
  [notes/phase-2-spec.md](notes/phase-2-spec.md). Phases 3 and 4 are outlines.
- **Phases:**
  1. `takeover` checks every ignored path the note was written with (issue 28), released
     as plugin 0.1.4.
  2. An index can count more than one source folder, released as plugin 0.1.5.
  3. Build dev-tools' index in `.devtools/components/`.
  4. Keep it current: a test, gates in `.devtools/project.md`, and the documentation.
  5. Close.
- **Execution:** `process-milestone component-index auto`, from 2026-11-21. Merges, release
  tags and anything posted to GitHub still need the owner each time.
- **Records:** [001-plan.md](001-plan.md), [002-phase-1.md](002-phase-1.md).
