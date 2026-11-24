---
milestone: issue-sweep
station: "phase-3 correction"
skill: process-milestone (dvt-milestone 0.1.3)
scope: phase-3
date: 2026-11-23
gate:
  command: "python3 devtools/release_plugins.py status"
  exit: 1
  output: "34 plugin file(s) changed since plugins-v0.1.2"
  note: "run in a scratch worktree at 488e143, the commit of the record corrected here"
evidence:
  - path: .planning/milestones/issue-sweep/004-phase-3.md
    sha256: 4bf9c79564a64825ac23622fec0321b0b48934473b93f5c196a8c06e7ca29068
---

# Claim

The record `004-phase-3.md` (SHA-256 `4bf9c795…9068`, committed at `488e143`) misquotes
one line of its release status: it says `30 plugin file(s) changed since plugins-v0.1.2`,
and the command printed `34` at that commit. Its exit, 1, and its other three lines are
as quoted.

## Gate output (verbatim)

    $ git worktree add --detach <scratch> 488e143; cd <scratch>; python3 devtools/release_plugins.py status
    version in the tree: 0.1.7
    released: 0.1.2 (plugins-v0.1.2)
    34 plugin file(s) changed since plugins-v0.1.2
    0.1.7 is ready: after the merge, run `release_plugins.py tag` on main
    (exit 1)

At `a981377`, phase 2's record, the same command prints `30`, as `003-phase-2.md` says.

## How it happened

The phase 3 record's gate output was written from phase 2's record and the one changed
line was not re-read from a new run. The four plugin files phase 3 changed (the two copies
of `handoff.py`, and `review_tool.py` and `phase_tool.py` in their plugins) account for the
difference. Found by the close review, `notes/reviews/close-r1`, F3.

## Boundary -- what this result did NOT establish

- It corrects one quoted line. It re-establishes nothing else in `004-phase-3.md`, whose
  other gates the close re-ran on the milestone's head (`006-close.md`).
- `004-phase-3.md` is not edited: a record is never edited after its commit.

## Open questions

- None new. The close record says how a record's gate output is now written: from a run
  of the command, never from an earlier record.
