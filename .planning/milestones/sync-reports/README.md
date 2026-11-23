# Milestone: sync-reports

A project learns from its ordinary `sync.py apply` and `sync.py check` runs that it lacks a
unit its own synced files name, that dev-tools has added a unit since its last sync, and
that it is behind dev-tools. An `apply` from a dev-tools checkout that is only behind its
upstream delivers the upstream's files.

- **Plan:** [notes/sync-reports-plan.md](notes/sync-reports-plan.md), approved on
  2026-11-23 by delegated approval (auto=true): [001-plan.md](001-plan.md).
- **Plan review:** one round (Codex), `notes/reviews/plan-r1`, 6 findings, each
  reproduced and fixed.
- **Phase specs:** [notes/phase-1-spec.md](notes/phase-1-spec.md) and
  [notes/phase-2-spec.md](notes/phase-2-spec.md).
- **Phases:**
  1. The sync names what a project has not taken, and `check` can say it is behind.
  2. The sync reads the latest dev-tools.
  3. Close.
- **Execution:** `process-milestone sync-reports auto=true`, from 2026-11-23, by the
  owner's lane ruling. Pushing, the pull request, merging, tagging and releasing need the
  owner.
- **Records:** [001-plan.md](001-plan.md), [002-phase-1.md](002-phase-1.md): the unit
  report, `declined`, `check` against a source and `--strict`.
