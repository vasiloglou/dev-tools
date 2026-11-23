---
milestone: sync-reports
station: "phase-2"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-2
date: 2026-11-23
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests/test_sync.py -q"
    exit: 0
    output: "123 passed in 36.88s"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "426 passed in 234.54s (0:03:54)"
    note: "run at fcbb0d7; the one later commit changes tests/test_sync.py only, which the first gate ran"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base f5c6b81 --strict"
    exit: 0
    output: "changed against f5c6b81 (f5c6b81): 20 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "none beyond the full suite"
  trigger: "n/a"
  reason: "the full suite is the repository's only test lane, and it ran (above)"
evidence:
  - path: devtools/sync.py
    sha256: 56759e3a89f25fea1f72bf41eef46577baee0636e7ca82c05599a5acebd872d0
  - path: tests/test_sync.py
    sha256: 668c3b0d1ad71400c011cf6a67d15623633cdcfe46ba66e741e6222f57d285a8
  - path: README.md
    sha256: db3ed84d9df6e4f55082d868dfcab297228c21c2ad22d4cd0aad7cd32acb5208
  - path: docs/adopt.html
    sha256: 077343d19932a2bce664d4d06cda22e493343ea956801090656d31415629485f
  - path: skills/adopt-devtools/SKILL.md
    sha256: 8c735a4db21040d31ab223d78ad47592b8ce3aa0321835cc460e995b50edba09
  - path: .devtools/components/COMPONENTS.md
    sha256: ef998ad19c7fba7b97c4a32e04088decd201618909bd2d679dd8344158dacd2f
  - path: .devtools/components/modules/_root.md
    sha256: 88ef405466968a1aa420ec277d62026e3413821cfb1a95fe878dcac476352524
  - path: .planning/milestones/sync-reports/notes/phase-2-spec.md
    sha256: 5672de6274c77e8a0b2194f0b74e22c96a880a92ac27d1e7257c249ecda4a77a
  - path: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/BRIEF.md
    sha256: d0fc386ddc1769ceb5e38fa0e228b41392283558cd0c96c7bfbbad937faf37af
  - path: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/review.md
    sha256: 9cc2bd90e1d25b144b1c945ae88dd975130e4ed361dd6d754687ad6d22f8de7a
  - path: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/FINDINGS.md
    sha256: 7370d96610c1448571ccf3767860583ca2de7e52e6005c344fb023ccfffcbade
  - path: .planning/milestones/sync-reports/notes/reviews/phase-2-r2/BRIEF.md
    sha256: 1adc16db872d0c558b9c2309fc9d381c0c32cab80744d48e94de9251cb59737c
  - path: .planning/milestones/sync-reports/notes/reviews/phase-2-r2/review.md
    sha256: 1be411f8ae3897d294c2225e40c6f704ced37ae3b921c38e8efcd261ad9e7af7
  - path: .planning/milestones/sync-reports/notes/reviews/phase-2-r2/FINDINGS.md
    sha256: 94cbd6260465822717e5bee6e10fc94d9775983ab93b1209eaf23d26310e6aa1
---

# Claim

Phase 2's selected gates each exited 0 on the phase's head: `apply`, `check`, `survey`
and `compare` fetch the dev-tools checkout's upstream, a checkout only behind it delivers
the upstream's files and is left unchanged, and every other state of the checkout is
delivered as it is, with a warning where the checkout is behind.

## What shipped

- **`devtools/sync.py`** (175 lines added, 8 removed against `f5c6b81`):
  - `resolve_source(path, *, as_is)` decides, in one place, which files a command reads.
    States, in the order decided: `folder`, `detached`, `no-upstream`,
    `upstream-missing`, `current`, `as-is`, `own-work`, `upstream`,
    `upstream-unreadable` (spec section 6, its one home). It runs `git fetch` for the
    branch's remote with `GIT_TERMINAL_PROMPT=0` and a 60-second limit, unless
    `--as-is`, and asks git for `<branch>@{upstream}` (implementation finding 1).
  - `read_commit` writes the upstream commit's files into a temporary folder from
    `ls-tree` and `cat-file --batch`, with mode 0644 or 0755 from the tree; a commit
    holding a symbolic link is not read (r1 F1, F3; r2 F1).
  - The dirty check reads `skills`, `agents`, `devtools`, `examples`, with modes
    compared, untracked files listed and assume-unchanged or skip-worktree paths counted
    (r1 F2; r2 F3). `git_line` removes only git's line terminator (r1 F4; r2 F4).
  - `open_source` prints the decision on standard error and registers the folder's
    cleanup, which `main` runs in a `finally`; `resolve_source` removes the folder on
    any exception before it returns (r1 F5; r2 F2). `identity` gives the receipt the
    upstream commit when that is what was read.
  - `--as-is` on `apply`, `check`, `survey` and `compare`.
- **`tests/test_sync.py`**: T1 to T17 of the spec and the regression tests of rounds 1
  and 2 (374 lines added at the record's head, 0 removed). The autouse fixture
  `own_checkout_as_is` reads the repository's own checkout as it is and fails a test
  that starts `git fetch` in it; no existing test was edited.
- **`README.md`, `docs/adopt.html`, `skills/adopt-devtools/SKILL.md`**: the fetch, what is
  read, `--as-is`, and which commit the receipt names.
- **`.devtools/components/`**: `sync.copies` describes the fetch; the module page
  regenerated.

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests/test_sync.py -q
    123 passed in 36.88s
    $ uv run --no-project --with pytest python -m pytest tests -q
    426 passed in 234.54s (0:03:54)   (at fcbb0d7)
    $ python3 devtools/build_plugins.py --check
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base f5c6b81 --strict
    changed against f5c6b81 (f5c6b81): 20 file(s) differ; 0 to fix, 0 warning(s), 0 to reread

The by-hand run (spec section 8): `$SCRATCH/upstream` a scratch repository with two
commits, `$SCRATCH/clone` a clone that has seen the first, code at `fcbb0d7`. The clone's
`HEAD` and `git status --short` before and after:

    before: 8f9b993 []
    $ python3 devtools/sync.py apply --project "$SCRATCH/project" --source "$SCRATCH/clone" --dry-run
    note: dev-tools here is 1 commit(s) behind origin/main: delivering origin/main at 5a6c089; the checkout is not changed (git pull in $SCRATCH/clone updates it)
    create: .claude/skills/demo/SKILL.md
    dry run: {"create": 1}
    exit 0
    $ python3 devtools/sync.py apply --project "$SCRATCH/project" --source "$SCRATCH/clone"
    note: dev-tools here is 1 commit(s) behind origin/main: delivering origin/main at 5a6c089; the checkout is not changed (git pull in $SCRATCH/clone updates it)
    applied: {"create": 1}
    exit 0
    delivered: second version
    after: 8f9b993 []
    (a second dry run counted the devtools-upstream-* folders under $TMPDIR before and after: 14 and 14,
     all left by one test, since fixed; a run of the sync leaves none -- test_a_run_that_reads_the_upstream_leaves_no_folder)

The scratch repositories and their output live outside history.

## Review

| Round | Base | Brief SHA-256 | Findings | Blocking | Self-inflicted | Verdict |
|---|---|---|---|---|---|---|
| r1 | `e49b052` (phase 2 and the phase 1 repairs) | `d0fc386d…` | 5 | 2 | 0 / 5 | CHANGES_REQUESTED |
| r2 | `acc9ee3` (the r1 repairs) | `1adc16db…` | 4 | 1 | 4 / 4 | CHANGES_REQUESTED |

Reviewer Codex, read-only, effort `high`, through the review helper. One reviewer is one
reviewer. Every finding was reproduced as a test that failed on the reviewed code, and
fixed: r1 at `90dca94`, r2 at `e6a5c28`. After r2 the stop rule of
`review-convergence.md` fired (4 of 4 findings attacked the r1 repairs), so no third
round ran; the r2 repairs carry no review opinion from a phase round.

Round 1 also read the phase 1 repairs of `2120090` and confirmed each: the four
configuration cases, the machine with no git, the file already as shipped, the receipt
with no files, and the caption.

## Refactoring review

None needed, argued from what the phase touched. `resolve_source` is the one place that
decides which files a command reads, and the four commands call it through
`open_source`; before this phase each command resolved `--source` itself, and that is
now gone. The git helper inside `resolve_source` is a third copy of a pattern already in
`source_identity` and `ignored_by_git`; each answers a different failure differently
(empty string, warning, error object), and a shared helper would need all three modes,
so they were left apart.

## Boundary -- what this phase does NOT establish

- One reviewer is one reviewer; both rounds were by reading and in-memory runs, without
  pytest or a real fetch (their "Not checked"). The r2 repairs (`e6a5c28`) carry no
  review opinion.
- No test reaches a network remote: every upstream is a local repository. A slow or
  hanging network is covered by a test that makes `fetch` raise `TimeoutExpired`, not
  by a real one.
- The tool that runs is never the fetched one (plan D9, Q3). A sync that is older than
  the files it reads says so on standard error and goes on.
- A dev-tools commit holding a symbolic link is never read at the upstream; the
  checkout is delivered as it is, with a warning. dev-tools has no such link today.
- The dirty check reads only `skills`, `agents`, `devtools` and `examples` (S2): work of
  one's own elsewhere in the checkout does not keep the upstream from being read.

## Open questions

- Q1 to Q4, carried.
