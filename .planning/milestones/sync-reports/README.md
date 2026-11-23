# Milestone: sync-reports

A project learns from its ordinary `sync.py apply` and `sync.py check` runs that it lacks a
unit its own synced files name, that dev-tools has added a unit since its last sync, and
that it is behind dev-tools. An `apply` from a dev-tools checkout that is only behind its
upstream delivers the upstream's files.

- **Plan:** [notes/sync-reports-plan.md](notes/sync-reports-plan.md). A draft: the plan
  gate has not been ruled, and the lane is itself a proposal (its D1).
- **Phase specs:** [notes/phase-1-spec.md](notes/phase-1-spec.md), a draft, blocked on the
  plan gate. Phase 2's is written when phase 1 is recorded.
- **Phases:**
  1. The sync names what a project has not taken, and `check` can say it is behind.
  2. The sync reads the latest dev-tools.
  3. Close.
- **Pending decisions:** D1 to D7 and D9 to D13 of the plan, section 10. D8 was ruled by
  the owner on 2026-11-23.
- **Next action:** the plan review, then the owner's ruling at the plan gate. No code is
  written before it.
- **Records:** none yet.
