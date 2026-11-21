---
milestone: component-index
station: "plan gate"
skill: process-milestone (dvt-milestone 0.1.3)
scope: plan
date: 2026-11-21
gate:
  command: "ruling: delegated (auto=true) approved .planning/milestones/component-index/notes/component-index-plan.md sha256 42ac8f116b426ad9589c6f9224b99a188d34ae03e75f2a1cceac6d84bf0b460c"
  exit: "n/a -- ruling"
evidence:
  - path: .planning/milestones/component-index/notes/component-index-plan.md
    sha256: 42ac8f116b426ad9589c6f9224b99a188d34ae03e75f2a1cceac6d84bf0b460c
  - path: .planning/milestones/component-index/notes/reviews/plan-r1/BRIEF.md
    sha256: b64a960e46ad450113a22d40af7d55c78c95145054d9b71cc550e723b1ea06e4
  - path: .planning/milestones/component-index/notes/reviews/plan-r1/review.md
    sha256: 92bea45cd4deedbb3510f07938d545d33f441291d1ccb6a1547ce6f8705f2d21
  - path: .planning/milestones/component-index/notes/reviews/plan-r1/FINDINGS.md
    sha256: a4a7cf69afb0f8f13c78e1aec681da7d14ad23592084a761816b9483d4cb8049
  - path: .planning/milestones/component-index/notes/reviews/plan-r2/BRIEF.md
    sha256: fc912dc8da465b01c6895b59f577fb595ea2ed7bfddb892062761b5f89078b1e
  - path: .planning/milestones/component-index/notes/reviews/plan-r2/review.md
    sha256: dbca17f44cea1c5096c26a0179a6179bca9177a58e0b1c7a7adf4615be765725
  - path: .planning/milestones/component-index/notes/reviews/plan-r2/FINDINGS.md
    sha256: d728d6b1360f8f0d4dc78449f854abadfd443d844ebafe262a5f91c64ae1e990
  - path: .planning/milestones/component-index/notes/reviews/plan-r3/BRIEF.md
    sha256: 92d7eadd722d588543504414dddc6401e5c215361d880cb0d5ed70cad48449f2
  - path: .planning/milestones/component-index/notes/reviews/plan-r3/review.md
    sha256: 68e7db51123fce280cd1a394a4579886e5f462be35885f789f8058d077ccd29c
  - path: .planning/milestones/component-index/notes/reviews/plan-r3/FINDINGS.md
    sha256: 8bd62b7ac80b7bcc79336dc0b879c303965e35a98ca9b31013b46d91a8433507
---

# Claim

The milestone plan `notes/component-index-plan.md`, at the SHA-256 above, is approved by
delegated approval (auto=true), with decisions D1 to D5 ruled as the plan proposes.

## Gate output (verbatim)

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/component-index/notes/component-index-plan.md
    sha256: 42ac8f116b426ad9589c6f9224b99a188d34ae03e75f2a1cceac6d84bf0b460c
    date: 2026-11-21
    authorization: the owner's invocation "/dvt-milestone:process-milestone auto" in this
      session, on 2026-11-21, for the milestone in hand (component-index)
    scope: the plan, spec and close rulings of component-index, and their amendments
    not covered: merging a pull request, release_plugins.py tag, posting to GitHub
      (.devtools/project.md, "What needs the owner each time")
    decisions:
      D1 the index lives in .devtools/components/            -- as proposed
      D2 phase 2 (count_extra_dirs) is in the milestone      -- as proposed
      D3 a stale index is caught by a test and gate rows     -- as proposed
      D4 shared helper names are distinct_from, left alone   -- as proposed
      D5 the milestone keeps the name component-index        -- as proposed
    budget: plan review at most r1 to r3, declared in the plan before r2; spent
    review instrument: review_tool.py, reviewer Codex (read-only, effort high),
      .devtools/project.md "Review instrument"

This is an agent's ruling under the owner's delegation. It is not the owner's own reading
of the plan.

## Plan review

The project's plan-review bar is one independent reviewer in a different tool. Three
rounds ran, each with one seat (Codex). One reviewer is one reviewer.

| Round | Reviewed brief SHA-256 | Findings | Blocking | Self-inflicted | Verdict |
|---|---|---|---|---|---|
| r1 | `b64a960e…06e4` | 8 | 3 | 0 / 8 | CHANGES_REQUESTED |
| r2 | `fc912dc8…8b1e` | 3 | 1 | 1 / 3 | CHANGES_REQUESTED |
| r3 | `92d7eadd…49f2` | 1 | 0 | 1 / 1 | CHANGES_REQUESTED |

Every finding was reproduced before it was believed, and every one is `fixed`. The
ledgers have the reproduction and the repair commit of each: `ada0d1a` (r1), `bfc5be1`
(r2), `b57d122` (r3). After r3 the stop rule of `review-convergence.md` fired, since the
self-inflicted ratio was above one half. The budget declared before r2 was also spent. The
next instrument is the code.

`review_tool.py status .planning/milestones/component-index/notes/reviews` reports
`unreviewed` for these two files, which changed after r3 read them:

- the plan: the r3 convergence row and the ruling lines in its status and section 10;
- `notes/phase-1-spec.md`: the r3 F1 repair, the bullet rule and its test T10.

No review opinion covers those bytes. Phase 1's diff review reads the code that
implements T10. `notes/phase-2-spec.md` is `reviewed` at r3.

## Boundary -- what this result did NOT establish

- The ruling approves a plan. It establishes nothing about code, which does not exist yet.
- Three single-seat rounds are one reviewer's reading, by inspection and in-memory probes,
  without running pytest. Each round said so under "Could not check".
- The plan bytes this record binds are not the bytes r3 read; the difference is listed
  above and carries no review opinion.
- The known red (R5) was proven on 2026-11-21 in a throwaway worktree at `c9648dd`:
  `pytest tests/test_tools.py -k test_suggestions_and_generated_cases_with_newer_gnd`
  gave `1 failed, 62 deselected`. On the plan branch the full suite gave
  `1 failed, 287 passed in 132.76s`, the same test. The output lives outside history.

## Open questions

- Q1 and Q2 of the plan, section 10, carried to the close sweep.

## Refuted premises

- "The milestone's planning files go in with phase 1's pull request" rested on their being
  committable. On main, `.gitignore` line 7 (`notes/`) ignored every folder named `notes`,
  this milestone's included (`git check-ignore -v` named that line). Amendment a2 anchors
  the line to `/notes/` in phase 1, and the files were committed at `ada0d1a`.
