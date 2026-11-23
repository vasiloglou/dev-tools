---
milestone: issue-sweep
station: "plan gate"
skill: start-milestone (dvt-milestone 0.1.3)
scope: plan
date: 2026-11-23
gate:
  command: "ruling: owner approved .planning/milestones/issue-sweep/notes/issue-sweep-plan.md sha256 309c6e556ac85f24e71f3c63f79356421392e570cdf143472b02f1acd90481a4"
  exit: "n/a -- ruling"
evidence:
  - path: .planning/milestones/issue-sweep/notes/issue-sweep-plan.md
    sha256: 309c6e556ac85f24e71f3c63f79356421392e570cdf143472b02f1acd90481a4
  - path: .planning/milestones/issue-sweep/notes/issues-2026-11-23.md
    sha256: 7584fec3d861c1113450fa58207fbc671f1ad9e77f2db673d6b1df1f575dc84c
  - path: .planning/milestones/issue-sweep/notes/reviews/plan-r1/BRIEF.md
    sha256: 80d522f4ec9daa46d0f3b7d39efce53f5cb37a2bbc114e1c03ca14d714120c62
  - path: .planning/milestones/issue-sweep/notes/reviews/plan-r1/review.md
    sha256: e41d8425064cad535fc23ba4fbd2202b4b8ff668319beaa26d8bbe68ade7e527
  - path: .planning/milestones/issue-sweep/notes/reviews/plan-r1/run.json
    sha256: d9944906f9dd9a3341866f06f94cf78e8aa74ca22af61d78fde238de528150f0
  - path: .planning/milestones/issue-sweep/notes/reviews/plan-r1/FINDINGS.md
    sha256: 8372be7a6e66307fcb8edd3eebe9b8aeec2e3c8de748617068fd38b8171aece8
---

# Claim

The milestone plan `notes/issue-sweep-plan.md`, at the SHA-256 above, is approved by the
owner, with D1 and D2 ruled by the owner earlier the same day and D3 to D11 ruled as the
plan proposes.

## Gate output (verbatim)

    ruling: owner approved
    artifact: .planning/milestones/issue-sweep/notes/issue-sweep-plan.md
    sha256: 309c6e556ac85f24e71f3c63f79356421392e570cdf143472b02f1acd90481a4
    date: 2026-11-23
    authorization: the owner, in the session that wrote the plan. To "Approve the plan at
      the plan gate, with D3 to D11 as proposed?", offered beside "Run round 2 first", the
      owner answered "Approve as proposed".
    scope: the plan, and its decisions D3 to D11
    not covered: the phase 1 spec and its decisions D1 to D5; starting a phase; pushing,
      the pull request, merging, tagging, releasing, and anything posted to GitHub
    decisions:
      D1  eight issues are in: 31, 33, 41 to 46; 39 and 40 are not   -- owner, "Yes, eight"
      D2  the evidence lane, as this milestone                       -- owner, the request
      D3  one pull request for the milestone                         -- as proposed
      D4  one plugin version, bumped in phase 2                      -- as proposed
      D5  a baseline is refused through a setting, allow_baseline    -- as proposed
      D6  a local base strictly behind its remote-tracking branch:
          use that branch and say so                                 -- as proposed
      D7  a reread: line, dated by its own last edit                 -- as proposed
      D8  every review group not built from the import graph
          follows count_extra_dirs                                   -- as proposed
      D9  rules_check.py test leaves out a plan rule where there is
          no phase tool, and says so                                 -- as proposed
      D10 a settings file a script cannot use exits 2, in every
          script under skills/ that reads one                        -- as proposed
      D11 phase_tool.py prints a JSON envelope for that error        -- as proposed
    execution: auto=false. Each phase spec and the close stop for the owner.
    budget: plan review at most r1 and r2, declared in the plan before r1; r1 run, r2 not
    review instrument: review_tool.py, reviewer Codex (read-only, effort high),
      .devtools/project.md "Review instrument"
    commits: the owner said "yes" on 2026-11-23 to committing the plan and its review
      round, then this record, on claude/open-issues-milestone-43c5a0. Nothing is pushed.

## Plan review

The project's plan-review bar is one independent reviewer in a different tool. One round
ran, with one seat (Codex). One reviewer is one reviewer.

| Round | Reviewed brief SHA-256 | Findings | Blocking | Self-inflicted | Verdict |
|---|---|---|---|---|---|
| r1 | `80d522f4…0c62` | 5 | 3 | 0 / 5 | CHANGES_REQUESTED |

- The brief listed 22 files and 8 claims to refute. The reviewer confirmed all 22 hashes.
- Every finding was reproduced before it was believed, and every one is `fixed` at
  `3663a15`. The ledger has each reproduction. The classes (3 blocking, 2 hardening) were
  assigned at disposition, not by the reviewer.
- F5 refuted part of issue 42's premise: a test already runs the pytest plugin
  (`tests/test_tools.py::test_plain_pytest_leaves_out_phases_that_are_not_complete`).
- `review.md` was passed through `review_tool.py sanitize`, which replaced 5 absolute
  paths of this machine and says so on its first line. The digest above is of the
  sanitized file; `run.json` holds the digest of the reviewer's original,
  `6738203bf84111b1d561179048544f59ef1a808b9fc1efe0158892306a4a190e`. `review.log` is
  kept out of history by `.gitignore`.
- Round 2 was not run. It was offered to the owner beside the approval, and the owner
  approved.

`review_tool.py status .planning/milestones/issue-sweep/notes/reviews`, after the ledger
named `3663a15`, exited 1 and reported these three files `unreviewed`, since each changed
after r1 read it:

    unreviewed: .planning/milestones/issue-sweep/README.md (changed since .planning/milestones/issue-sweep/notes/reviews/plan-r1 read 0c40611ef004)
    unreviewed: .planning/milestones/issue-sweep/notes/issue-sweep-plan.md (changed since .planning/milestones/issue-sweep/notes/reviews/plan-r1 read 5ae6fe45eeed)
    unreviewed: .planning/milestones/issue-sweep/notes/phase-1-spec.md (changed since .planning/milestones/issue-sweep/notes/reviews/plan-r1 read 61f817791072)

The other 19 files it called `reviewed`. No review opinion covers the plan's r1 repairs,
the rulings written into it, or the phase 1 spec's repairs.

## Boundary -- what this result did NOT establish

- The ruling approves a plan. It establishes nothing about code, which does not exist yet.
- It does not approve the phase 1 spec, whose decisions D1 to D5 are open.
- One single-seat round is one reviewer's reading, under a read-only sandbox: by its own
  account it ran eight read-only pytest checks and in-memory simulations, and could not
  run the full suite, the scratch-project reproductions or a GND without its extra.
- The plan bytes this record binds are not the bytes r1 read; the difference is listed
  above and carries no review opinion.
- Issue 31's failure was not reproduced: this machine's GND has the `synth` extra.
- The baseline suite run (447 passed, exit 0, at `cecebc6`) lives outside history.
- Nothing is pushed, and no issue was commented on, labelled or closed.

## Open questions

- Q1 to Q3 of the plan, section 10, carried to the close sweep.
- The component index lists 3 of its 12 entries as older than their code. A review of it
  was offered in the plan (section 3) and has not been taken up.

## Refuted premises

- "No test runs the `phase_selection.py` pytest plugin" (issue 42, and this plan's first
  draft). Refuted by `tests/test_tools.py` lines 1879 to 1894 at `cecebc6`, found by plan
  review r1 as F5: `.planning/milestones/issue-sweep/notes/reviews/plan-r1/review.md`,
  SHA-256 `e41d8425064cad535fc23ba4fbd2202b4b8ff668319beaa26d8bbe68ade7e527`. What
  remains true: no file under `tests/` names the plugin, its index entry lists no test,
  and most of its branches have no case.
