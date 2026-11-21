# Milestone: component-index

dev-tools gets a component index of its own code that can be searched by capability. Every
shipped module is covered, and a gate refuses a module without a component. Before that,
the milestone fixes issue 28: `dev-takeover` reports ready while an ignored path that the
note did not list is missing.

- **Plan:** [notes/component-index-plan.md](notes/component-index-plan.md). It is a draft,
  amended on 2026-11-21 to add issue 28. There has been no plan review and no plan gate.
- **First phase spec:** [notes/phase-1-spec.md](notes/phase-1-spec.md), for issue 28. It
  is a draft awaiting its owner gate.
- **Phase 2 spec:** [notes/phase-2-spec.md](notes/phase-2-spec.md), also a draft. It was
  written first, as phase 1, before issue 28 was added.
- **Phases:**
  1. `takeover` checks every ignored path the note was written with (issue 28), released
     as plugin 0.1.4.
  2. An index can count more than one source folder, released as plugin 0.1.5.
  3. Build dev-tools' index in `.devtools/components/`.
  4. Keep it current: a test, gates in `.devtools/project.md`, and the documentation.
  5. Close.
- **Readiness:** phases 1 and 2 have draft specs. Phases 3 and 4 are outlines.
- **Decisions pending at the plan gate:** D1 to D5 (plan, section 10).
- **Plan review:** round 1 ran on 2026-11-21 (Codex, `notes/reviews/plan-r1`). It returned
  8 findings, 3 of them blocking. All 8 were reproduced and repaired in the working tree,
  and the repairs are unreviewed and uncommitted.
- **Next action:** round 2 over the repaired bytes, or the owner's plan gate. The gate is
  recorded as `001-plan.md`.
