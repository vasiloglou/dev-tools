---
milestone: component-index
station: "phase-3"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-3 reread, and round 3 of the phase 1 and phase 2 reviews
date: 2026-11-22
gates:
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py write"
    exit: 0
    output: "(no output)"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
    output: "(no output)"
  - command: "test ! -e .devtools/components/unassigned-baseline.txt"
    exit: 0
    output: "(no output)"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py review"
    exit: 0
    output: "## Components that import each other (0); ## Flow steps that no earlier step imports (wrong order, or reached another way?) (4); ## Entries marked as checked in part (0)"
    note: >-
      The four flow steps are the run-time loads the three subsystems' notes state.
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py search <each case of search-cases.md>"
    exit: 0
    output: "9 of 9 cases put the expected component first; the negative case printed 'no component matched'"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
    output: "(no output)"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "334 passed in 141.33s (0:02:21)"
  - command: "uv run --no-project --with pytest python -m pytest tests -q   (claude/component-index-phase-1 at e2b2762)"
    exit: 0
    output: "320 passed in 139.73s (0:02:19)"
  - command: "uv run --no-project --with pytest python -m pytest tests -q   (claude/component-index-phase-2 at d4e05eb)"
    exit: 0
    output: "334 passed in 141.77s (0:02:21)"
slow_cadence:
  command: "uv run --no-project --with pytest python -m pytest tests -q"
  trigger: "n/a -- run on each of the three branches"
  reason: "this repository has no broader lane than the full suite"
evidence:
  - path: .devtools/components/COMPONENTS.md
    sha256: 4c1713a7dd55ef0751caecb92f1476a2a0cc91490fb0e04547abfaf8e065c07e
  - path: .devtools/components/REVIEW.md
    sha256: 821c841181d8bd82b95cfc4019e461381d03c5589a12cf53f012f09cf6d390e7
  - path: .devtools/components/modules/skills.md
    sha256: 6f20216aecde910a8c1cd16b5f406c11588fc3a75b71ee72a6264ec4fdae20db
  - path: .planning/milestones/component-index/notes/phase-3-reading/README.md
    sha256: 043adaf210b1b37c4add163371ccba7ae73810cd9d8df299ae66663046b44e51
  - path: .planning/milestones/component-index/notes/phase-3-reading/handoff.md
    sha256: db4b38baff1254c2b551b0c12f784271644fb6c2c90852680a7d165df6c5ea91
  - path: .planning/milestones/component-index/notes/reviews/phase-1-r3/BRIEF.md
    sha256: d21cf1e9daaba5e8ddd727f681084f1b2c73c6ce949a10429ca862967ad72775
  - path: .planning/milestones/component-index/notes/reviews/phase-1-r3/FINDINGS.md
    sha256: 6a560e53be153c5111fa3f2db12c09076d6ef78a4f5e616b1c727ccdf4b6a09c
  - path: .planning/milestones/component-index/notes/reviews/phase-2-r3/BRIEF.md
    sha256: 4f8b4e160b8e0a024e30b2cd5a17426590e6bef85646c05d43ff7ca055b5ad04
  - path: .planning/milestones/component-index/notes/reviews/phase-2-r3/FINDINGS.md
    sha256: d45d53ddb0c9462cd3a8664c8bcfa568a2968c6ad6ad15b91c6aa3580a2c2d30
  - path: .planning/milestones/component-index/notes/reviews/phase-3-r2/BRIEF.md
    sha256: 901ac741a94b73ee97e07e7a29f9320a21bad5175ac706818dfe5ebb48368752
  - path: .planning/milestones/component-index/notes/reviews/phase-3-r2/FINDINGS.md
    sha256: 3d8b4824d94a55cc7e75bff6ebf273baf378c4a92319d760e978b54a07072ca9
  - path: .planning/milestones/component-index/notes/reviews/phase-3-r3/BRIEF.md
    sha256: a2ebf7187d0bb9a7851d4be573be894e43f5252464a84b0bc32a5950bfcc2f88
  - path: .planning/milestones/component-index/notes/reviews/phase-3-r3/FINDINGS.md
    sha256: dfe3f6c78259bf7be14ca1f20b4b141f8d7387d5a0d5de64d22be2a63bf3cb06
---

# Claim

Phase 3's P3.3 is now met: every entry of `.devtools/components/COMPONENTS.md` was written
from a full reading of its module, and `review` lists no entry as checked in part. The 10
entries record 004 listed as partial were reread in full at `3963a46`, one reading file per
module under `notes/phase-3-reading/`, and rewritten from those files. The gates of
record 004 still exit 0 at `b52c714`. A third review round over phase 1's repairs found
four defects in `takeover`, fixed on the phase 1 branch at `e2b2762`; a third round over
phase 2's approved them. Both branches were merged upward, so phase 3 carries all of it.

## Authority

The owner's "go on" of 2026-11-22, to three steps proposed in this session: ignore
`review.log`, run a review round on the unreviewed phase 1 and phase 2 repairs, and reread
the 10 partial entries with four reader agents before phase 3's pull request. Phase 3's
spec and its delegated approval (record 004) are unchanged; D4 (A), the reading depth it
approved, was not enough for P3.3, and the reread is what P3.3 asked for. Nothing was
pushed, merged into `main`, tagged or posted.

## What shipped

On `claude/component-index-phase-3` (local):

- `3963a46`: `.gitignore` takes `.planning/**/review.log` (Q5 of record 002), which was
  kept out only by this machine's `.git/info/exclude`.
- `176d7a4`: the reread. 10 entries and 3 subsystems rewritten, `REVIEW.md` updated (three
  new suggestions, the two leads of "Not confirmed" settled), the reading files and their
  method. `0b95fbb` declared the review budget before round 2.
- `27ca753` and `b471ff5`: the repairs of phase rounds 2 and 3 of the reread.
- `caffae7`: phase 2 merged in, with phase 1's round 3 repair.

On `claude/component-index-phase-1` (local, ahead of vasiloglou/dev-tools#29 by two
commits): `e2b2762`, the repair of phase-1-r3 with 13 new test cases, each seen failing
first; `d584362`, the round folder. Plugin version stays 0.1.4, which is not tagged.

On `claude/component-index-phase-2` (local, ahead of vasiloglou/dev-tools#30 by four
commits, two of them phase 1's): `b41d257`, the phase-2-r3 folder; `d4e05eb`, phase 1
merged in.

## What the reread changed

The readers' definition tables cover 506 definitions in 10,363 lines (110, 29, 88, 41,
55, 46, 74, 41, 10 and 12). The driving agent checked 3 claims per reader at the cited
lines, 12 in all, before any entry changed; each held. Four statements of the first build
were false, not merely short:

- `subsystem.rule_check`'s flow put `phase.state` after `components.index`, but
  `components_index.py` never runs `phase_tool.py`; `rules_check.py` runs each.
- `subsystem.release` said `bump` loads `build_plugins.py` at run time; it is loaded when
  `release_plugins.py` is imported, and every command uses it.
- `components.index` said it generates the catalog; the catalog is hand-written.
- `handoff.notes` said it takes a branch over; `takeover` only checks and reports.

The rest were incomplete: `phase.state` named 8 of its 15 commands, `components.index` left
out `init` and `list`, `sync.copies` left out deletion and the journal, `migrate.from_gsd`
most of what `convert` writes, and five notes misstated or left out exit codes.

## Criteria, measured

| Criterion | Measurement |
|---|---|
| P3.1 `write`, then `--check --strict`, exit 0 | G1, G2 at `b52c714` |
| P3.2 No components importing each other; no unstated flow step | G4: `(0)`; the 4 flow steps are the loads stated in `notes:` |
| P3.3 Every entry read from the code; partial ones listed | `review`: `Entries marked as checked in part (0)`; 12 of 12 read in full |
| C1 Every module has a component, with no baseline | G2 at `12/12`; G3 |
| C2 Each search case puts its component first | G5: 9 of 9; the negative case matched nothing |

## Gate output (verbatim)

    $ C=plugins/dvt-milestone/skills/components/scripts/components_index.py
    $ python3 $C write                          -> exit 0
    $ python3 $C --check --strict               -> exit 0
    $ test ! -e .devtools/components/unassigned-baseline.txt  -> exit 0
    $ python3 $C review                          -> exit 0
    ## Components that import each other (0)
    ## Flow steps that no earlier step imports (wrong order, or reached another way?) (4)
    ## Entries marked as checked in part (0)
    $ python3 $C stats | head -1
    coverage: 12/12 devtools, skills modules assigned to components; external: none
    $ python3 devtools/build_plugins.py --check  -> exit 0
    $ uv run --no-project --with pytest python -m pytest tests -q
    334 passed in 141.33s (0:02:21)
    exit 0

All at `b52c714`, with a clean tree.

## Review

Codex through the review helper, read-only, effort `high`. **One reviewer is one
reviewer.** Each finding was reproduced before it was fixed; the ledgers hold the
reproductions.

| Round | Subject | Findings | Blocking | Self-inflicted | Verdict |
|---|---|---|---|---|---|
| phase-1-r3 | phase 1 at `24b2d83`, base `1a5f14c` | 5 | 3 | 1 / 5 | CHANGES_REQUESTED |
| phase-2-r3 | phase 2 at `a7bc35c`, base `ca6712a` | 0 | 0 | 0 | APPROVE |
| phase-3-r2 | the reread, base `caffae7` | 5 | 2 | 0 / 5 | CHANGES_REQUESTED |
| phase-3-r3 | its repairs, base `0b95fbb` | 1 | 0 | 1 / 1 | CHANGES_REQUESTED |

Phase 1 and phase 2 had spent their declared budgets; their third rounds ran on the
owner's go-ahead, each from a clean checkout of its branch. Phase-1-r3's blocking findings
were all ways `takeover` reads a note as ready while a path is missing: a Unicode line
separator (F1), a path naming the checkout itself (F2), and a file named like the
snapshot's end marker (F4, inherited from `main`). F3 (an `OSError` on Python 3.11) was
hardening of the phase's own deliverable; F5 was the brief's own wording of C1, rejected.
Phase-3's budget, declared at `0b95fbb` before round 2, allowed one more round after a
blocking finding; round 3's one finding attacked round 2's repair, so the stop rule fired
and there is no round 4.

**Unreviewed bytes:** the phase 1 repair at `e2b2762` and the one-sentence phase 3 repair
at `b471ff5`.

## Refactoring review

No code changed in phase 3. The phase 1 repair adds three small helpers to `handoff.py`
(`_inside`, `_split_end`, `_exists`) and routes `write`, `check` and `takeover` through
one end-marker rule where each had split the text its own way.

## Boundary -- what this record does NOT establish

- That the readers read every line: the definition tables and the 12 spot checks are the
  evidence, and round 2 found the tables complete apart from the three helpers added after
  the reading.
- That the phase 1 repair is right beyond its tests: it is unreviewed.
- Anything about the pull requests: #29 and #30 do not yet hold these commits, and phase 3
  has no pull request.

## Open questions

- Q9 (new). dvt-milestone ships `rules_check.py` without the `phase_tool.py` its default
  `phase_script` names, so `check --phase` exits 2 in that install (REVIEW.md suggestion
  4). A defect of the product; an issue is proposed to the owner.
- Q10 (new). `review`'s same-named-definition leads look only under `package_dir`
  (REVIEW.md suggestion 5). Phase 2's `count_extra_dirs` did not reach them. Carried to the
  close sweep.
- Q11 (new). A tracked file whose name holds a newline is still printed raw in the
  snapshot's uncommitted list. `takeover` now withholds ready if that hides the ignored
  section, but `write` would keep the rest of the old snapshot as text. Carried to the close
  sweep.
- Q12 (new). Four docstrings say what their code does not do (REVIEW.md suggestion 6).
  Carried to the close sweep.

## Refuted premises

- "Docstrings, command lines and documented functions are enough to write an entry" (spec
  D4 (A), and the plan's reading estimate: "no readers are fanned out"): four entries said
  something false, and most named only part of what their module does. Repair the plan at
  the close.
- "Phase 1's repairs hold after round 2" (record 002): round 3 found three more ways to
  read a note as ready while a path is missing.
- "The `plugin_root`, `checkout_root` and `load_settings` copies have drifted" (an outside
  read of Q8): `plugin_root` and `checkout_root` are the same code in all six scripts;
  `load_settings` differs because each tool checks its own settings.
