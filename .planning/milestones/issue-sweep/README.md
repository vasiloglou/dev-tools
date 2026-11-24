# Milestone: issue-sweep

Eight of the ten issues open on 2026-11-23 are fixed, each with a test that fails without
the fix. Issues 39 and 40 are left for milestones of their own.

- **Plan:** [notes/issue-sweep-plan.md](notes/issue-sweep-plan.md), approved by the owner
  at the plan gate on 2026-11-23, with D3 to D11 as proposed.
- **Plan review:** one round (Codex), `notes/reviews/plan-r1`, 5 findings, each reproduced
  and repaired. The repaired bytes are unreviewed.
- **The issues as read:** [notes/issues-2026-11-23.md](notes/issues-2026-11-23.md).
- **Phase specs:** [notes/phase-1-spec.md](notes/phase-1-spec.md),
  [notes/phase-2-spec.md](notes/phase-2-spec.md), [notes/phase-3-spec.md](notes/phase-3-spec.md).
- **Phases:**
  1. The suite tests what it claims, and one list of other planning tools (issues 31, 42,
     41).
  2. The index tool can refuse a baseline, name a stale base, mark a reread, and review
     every counted module (issues 46, 45, 44).
  3. Starter rules that pass where they are written, and scripts that exit as they say
     (issues 33, 43).
  4. Close.
- **Ruled by the owner, 2026-11-23:** the lane, a milestone (D2); the eight issues (D1);
  D3 to D11, as proposed.
- **Execution:** `process-milestone issue-sweep auto`, from 2026-11-23: each spec's owner
  gate and the close ruling are delegated approvals (auto=true). Pushing, the pull
  request, merging, tagging and anything posted to GitHub need the owner.
- **Next action:** phase 3, under its spec, approved by delegated approval on 2026-11-23.
- **Records:** [001-plan.md](001-plan.md): the plan gate; [002-phase-1.md](002-phase-1.md):
  the GND guard, the plugin's tests, one list of other planning tools.
  [003-phase-2.md](003-phase-2.md): the index tool refuses a baseline, reads a stale base's
  upstream, takes a `reread:` line, and reviews the counted folders.
