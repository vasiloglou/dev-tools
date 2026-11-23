---
milestone: component-index
station: "phase-4"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-4
date: 2026-11-23
gates:
  - command: "ruling: delegated (auto=true) approved .planning/milestones/component-index/notes/phase-4-spec.md, committed at 0a56e0f"
    exit: "n/a -- ruling"
  - command: "uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q"
    exit: 0
    output: "8 passed in 2.75s"
  - command: "uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q   (in a checkout of b807ca1 with the modules path of plugins.build removed from COMPONENTS.md)"
    exit: 1
    output: "no component: devtools/build_plugins.py (add it to the modules of an entry in .devtools/components/COMPONENTS.md); 4 failed, 4 passed"
    note: >-
      Expected to exit 1 (P4.2). The four that fail are the test of this checkout and
      the three that expect a copy of it to be current.
  - command: "uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q   (in a checkout of b807ca1 with an empty .devtools/components/unassigned-baseline.txt)"
    exit: 1
    output: ".devtools/components/unassigned-baseline.txt exists: every module has a component here, so no baseline is kept"
    note: >-
      Expected to exit 1 (P4.3). At 076c91d the script's own --check --strict exited 0
      in the same state: the baseline line is what fails the test.
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base main"
    exit: 0
    output: "changed against main (b685e82): 171 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
    note: >-
      The plan's command as written. The local branch main is eight days old in this
      checkout, so it judged 171 files (spec IF1).
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main"
    exit: 0
    output: "changed against origin/main (827e766): 10 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base 827e766 --strict"
    exit: 0
    output: "changed against 827e766 (827e766): 10 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "348 passed in 174.29s (0:02:54)"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
    output: "(no output)"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
    output: "(no output)"
  - command: "test ! -e .devtools/components/unassigned-baseline.txt"
    exit: 0
    output: "(no output)"
  - command: "uv run --no-project --python <3.11|3.12|3.13|3.14> --with pytest python -m pytest tests/test_own_index.py -q"
    exit: 0
    output: "8 passed, under each of the four versions"
slow_cadence:
  command: "uv run --no-project --with pytest python -m pytest tests -q"
  trigger: "n/a -- the spec mandates the full suite for this phase, and it ran (G5)"
  reason: "this repository has no broader lane than the full suite"
evidence:
  - path: tests/test_own_index.py
    sha256: 20eb2fa283b4ece497665e188eceecea50581193c7119b729fcc0b7b69e9f405
  - path: .devtools/project.md
    sha256: 1e485b868fde627032c65f9bf311899d4cb18d8a5a0ba91c8ffec8b9de54ff3e
  - path: AGENTS.md
    sha256: 2aa20beafc95d7fda49583f5c852b8091f40ff64e1d21c5c0ee0c1c3c9730e60
  - path: CONTRIBUTING.md
    sha256: 21f65706f46e6c6677d7202170dbc5f834e75832c88926324fbc611acc19d64f
  - path: README.md
    sha256: 18ff55e0a7cadc3ce46ec668699ae83a768742eff82b7e7282359c07fc90462d
  - path: docs/milestone.html
    sha256: ae396d9aa8b15fe00afd6c5f7309d65ae0f5d8add1e43839e95e42c1e9ab0522
  - path: docs/components.html
    sha256: c19c726f27e2d62245acd14ed3f5ef7673cca36ee802a784eda203531bbf3d03
  - path: docs/contribute.html
    sha256: 376da66c13656492193418b236ea674b3c29e690326c3003b2bc100f6d3f05c5
  - path: .planning/milestones/component-index/notes/phase-4-spec.md
    sha256: a629877e7cb50f16ee231c243fa13932adb309ca832fcbb04310ba14515721f7
  - path: .planning/milestones/component-index/notes/reviews/phase-4-r1/BRIEF.md
    sha256: 8949cdb17e8fe0e105594f41bd8ee58208a689b981a8a3e4f550932060f2c3f5
  - path: .planning/milestones/component-index/notes/reviews/phase-4-r1/review.md
    sha256: 20692804bd3fd2f8e9a83cc4c872aa1722248a8893fd5e31c1e7cbbbee2a303c
  - path: .planning/milestones/component-index/notes/reviews/phase-4-r1/FINDINGS.md
    sha256: 138304951e9aed0fac8f416726f7b0db968d842309f8c83a532cebb153906d1c
---

# Claim

At `b807ca1`, `tests/test_own_index.py` exits 0 with 8 tests, and exits 1 in a checkout
where one entry's module path is removed, naming the module, and in one where an
`unassigned-baseline.txt` is present, naming the file. The full suite exits 0 with 348
passed. `.devtools/project.md` names the index, the copy of the script that runs here,
the plugin version it needs and two gate rows; `AGENTS.md`, `CONTRIBUTING.md`,
`README.md` and three pages of the site name the index. No file under `skills/`,
`agents/`, `devtools/` or `plugins/` changed. The tree is phase 4 of the plan, on
`claude/component-index-phase-4`, cut from `main` at `827e766`; it is not pushed.

## Spec gate (verbatim)

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/component-index/notes/phase-4-spec.md
    committed: 0a56e0f, sha256 f6d8e1942be8fe1bb775b04b0a564093352c48c7710e1bbe44192ffdd322fb46
    date: 2026-11-23
    authorization: the owner's invocation "/dvt-milestone:process-phase 4 auto", within
      the milestone-wide delegation of 2026-11-21 ("/dvt-milestone:process-milestone auto")
    decisions:
      D1 the failing cases are tests on a copy, and run once each on the real tree -- as proposed (A)
      D2 a contributor is told in CONTRIBUTING, the site, README and the failure   -- as proposed (A)
      D3 the two sentences the milestone made untrue are replaced here            -- as proposed (A)
      D4 the test file is listed under no entry's tests                           -- as proposed (A)
    instrument: prose, with the case table of section 8 as the corpus
    budget: one review round over the diff; a second only after a blocking finding

This is an agent's ruling under the owner's delegation, not the owner's own reading. No
code existed at `0a56e0f`. The spec then gained IF1 to IF5 and a new status line, with
earlier wording kept: the SHA-256 above is the approved bytes, and the evidence list holds
the present ones.

## Since record 005

No record covers these, so they are stated here.

- vasiloglou/dev-tools#34 (lint-clean scripts, plugins 0.1.4) was merged into `main` on
  2026-11-23 while phases 1 to 3 were open, and conflicted with phase 1 in one hunk of
  `handoff.py`. `main` was merged into phase 1, phase 1 into phase 2, and phase 2 into
  phase 3 (`47250ed`, `ff3c263`, `4e5b7b8`); phase 3 also regenerated
  `modules/skills.md`. On each: the full suite exited 0 (326, 340 and 340 passed, the
  last before the regeneration commit), `build_plugins.py --check` exited 0, and ruff
  0.16.2 with gnd-public's configuration exited 0 on the three scripts #34 cleaned.
- The owner merged #29, #30 and #32 into `main` in that order on 2026-11-23 (`2b5173a`,
  `938c4e6`, `827e766`), by asking the agent to, with merge commits. `main`'s tree at
  `827e766` is the tested tree of `4e5b7b8`.
- Plugin version 0.1.4 now covers both #34's change and phase 1's. Neither 0.1.4 nor
  0.1.5 is tagged.

## What shipped

- `tests/test_own_index.py`, 118 lines (estimated: about 120), 8 tests.
  - `problems(root)` is the judgment: the built copy's `--no-cache --check --strict`,
    run in `root`, and a refusal of `unassigned-baseline.txt`.
  - `test_the_index_is_current` judges this checkout. Its message names the commands that
    regenerate the index.
  - Six tests change a copy of the checkout in one way each and assert on the line the
    judgment gives; one checks the unchanged copy; one builds and judges the copy with no
    `git` on `PATH` (r1 F1).
- `.devtools/project.md`: the *Component index* item, and two rows in "Gates".
- `AGENTS.md`: search the index before writing a module or a function, with the command.
- `CONTRIBUTING.md` and `docs/contribute.html`, step 3: a test fails while the index is
  out of date, and the failure names the command.
- `README.md`: a bullet for the index, the contributor bullet, two table rows, and the
  intro sentence the milestone made untrue.
- `docs/milestone.html#own-use`: a row for `.devtools/components/`, the gate list, and two
  sentences the milestone made untrue. `docs/components.html`: a pointer to the index.
- The milestone's `README.md`.

Outside `.planning/`: 8 files, 166 lines added and 14 removed.

## Criteria, measured

| Criterion | Measurement |
|---|---|
| C3 The suite exits 0 and includes a test that fails while the index is stale | G5: 348 passed, exit 0. G2 and G3 exit 1; T5 and T6 fail a new module and a changed one |
| C4 `.devtools/project.md` names the index, its folder and its two gates; the own-use documentation names the index | By inspection of the files in the evidence list. The review reported no false sentence among them, and checked that the added links exist on `main` |
| P4.1 The new test exits 0 on the phase's head | G1: 8 passed, exit 0 |
| P4.2 With one entry's module path removed, it fails and names the module | G2: exit 1, `no component: devtools/build_plugins.py` |
| P4.3 With a baseline present, it fails | G3: exit 1, naming the file |

## Gate output (verbatim)

All at `b807ca1`. G2 and G3 ran in a second checkout of that commit, restored after each;
`git diff HEAD | shasum -a 256` in the working checkout gave the empty-input hash,
`e3b0c442…`, so nothing uncommitted was under test.

    $ C=plugins/dvt-milestone/skills/components/scripts/components_index.py
    $ uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q
    8 passed in 2.75s                                                   -> exit 0   (G1)
    $ (the modules path of the first one-module entry removed) the same command
    removed: devtools/build_plugins.py
    E         no component: devtools/build_plugins.py (add it to the modules of an entry in .devtools/components/COMPONENTS.md)
    4 failed, 4 passed in 9.86s                                         -> exit 1   (G2)
    $ (an empty .devtools/components/unassigned-baseline.txt) the same command
    E         .devtools/components/unassigned-baseline.txt exists: every module has a component here, so no baseline is kept
                                                                        -> exit 1   (G3)
    $ python3 $C changed --base main
    changed against main (b685e82): 171 file(s) differ; 0 to fix, 0 warning(s), 0 to reread   -> exit 0   (G4)
    $ python3 $C changed --base origin/main
    changed against origin/main (827e766): 10 file(s) differ; 0 to fix, 0 warning(s), 0 to reread   -> exit 0
    $ python3 $C changed --base 827e766 --strict
    changed against 827e766 (827e766): 10 file(s) differ; 0 to fix, 0 warning(s), 0 to reread   -> exit 0
    $ uv run --no-project --with pytest python -m pytest tests -q
    348 passed in 174.29s (0:02:54)                                     -> exit 0   (G5)
    $ python3 devtools/build_plugins.py --check                         -> exit 0   (G6)
    $ python3 $C --check --strict                                       -> exit 0   (G7)
    $ test ! -e .devtools/components/unassigned-baseline.txt            -> exit 0
    $ uv run --no-project --python 3.11 --with pytest python -m pytest tests/test_own_index.py -q
    8 passed in 2.35s                                                   -> exit 0   (G8)
    … --python 3.12 …  8 passed in 7.61s                                -> exit 0
    … --python 3.13 …  8 passed in 2.13s                                -> exit 0
    … --python 3.14 …  8 passed in 2.50s                                -> exit 0

At `076c91d`, before the review's repairs, the same gates exited the same way with 7
tests and 347 passed; `changed --base origin/main` ran there and at `d49bdf4`, with 9
files.

**Each failing case was seen failing** (spec IF2 to IF4), at `076c91d` unless said:

- with the judgment's exit line removed, T7 failed; with the script's lines removed, T3,
  T5, T6 and T7 failed; with the baseline line removed, T4 failed; with nothing returned,
  T3 to T7 failed;
- with `tests` left out of the copy, T2 and T4 failed;
- T8, before its fix: `FileNotFoundError: [Errno 2] No such file or directory: 'git'`.

## Verification-selection ledger (as run)

| Obligation | Disposition | Result |
|---|---|---|
| Plan section 9, phase 4 rows | run | G1, G2, G3, G4 |
| Direct phase tests | run | G1: T1 to T8 |
| Impact closure: the full suite gains a file | run | G5, exit 0 |
| `plugins/` unchanged | run | G6 |
| C1 still true on this head | run | G7 |
| The interpreter the index was written under | run | G8, four versions |
| The component steps of process-phase | run | the reuse table (spec section 6); no index entry changed, since no module did; G4 with `--strict` |

## Review

One round of the review helper, `--subject phase --base 827e766`, reviewer Codex
(read-only, effort `high`), over the diff, the spec, the plan and the built script at
`d49bdf4`. **One reviewer is one reviewer.**

| Round | Brief | Findings | Blocking | Self-inflicted | Verdict |
|---|---|---|---|---|---|
| r1 | `8949cdb1…2c3f5` | 2 | 0 | 0 / 2 | CHANGES_REQUESTED |

- **F1, hardening, fixed at `b807ca1`.** The copy-based tests ran `git init`, which reads
  the user's git settings. Reproduced with the review's command: exit 1,
  `fatal: bad config line 3`. The copy now makes its `.git` folder itself, and T8 pins it.
- **F2, completeness, fixed at `b807ca1`.** The milestone's `README.md` was not yet
  updated. Reproduced by `git diff --name-only`.

The reviewer found no defect in the judgment. By the brief's read-only rule it did not
run the copy-based tests, the full suite or G2 and G3; it ran T1 directly under the four
Python versions, the strict check, the build check and the three `changed` commands, and
checked that each added link exists on `main`. The spec's budget allows a second round
only after a blocking finding, so there is none. The bytes repaired at `b807ca1`
(`tests/test_own_index.py`, the milestone's `README.md`, spec IF4 and IF5) carry no review
opinion.

## Refactoring review

None executed, and none needed in what the phase touched: it adds one test file and
changes prose, and no script.

- The new file's `index` helper is the fifth `run`-like helper in `tests/`. Each takes
  different arguments (a project and a script, a working directory and standard input, a
  fixed script), and the files share nothing else, so one helper would serve none of them
  as written.
- Two things the phase noticed are in the product, which this phase does not change.
  They are Q13 and Q14 below, for the close sweep to place.

## Boundary -- what this phase does NOT establish

- That the index's descriptions are true. The test checks that every module has a
  component and that the generated pages match the code. It does not read a `does` line.
- That the three entries `review` lists as older than their code since #34
  (`handoff.notes`, `components.rules`, `review.rounds`) are still accurate. #34 says it
  changes no behaviour; nobody reread the entries against it (Q15).
- Any operating system but this one. A checkout whose line endings git rewrites would
  read as stale; nothing here tried one.
- The repairs at `b807ca1` are unreviewed.
- The copy-based tests judge the working tree's files, tracked or not. An untracked `.py`
  file under `skills/` or `devtools/` fails T1, as it fails the script's own check.
- Nothing is pushed, and there is no pull request.

## Open questions

- Q13 (new). `changed` takes `--base main` by default, and compares with the local branch
  of that name. In a worktree that branch is not moved by anything; here it was eight days
  old, and the command judged 171 files for a 10-file change (spec IF1). Should the tool
  say when the base is behind its remote, or prefer the remote branch? A product question,
  for the close sweep.
- Q14 (new). `--check --strict` excuses whatever a baseline names, and has no way to
  refuse a baseline. A project with full coverage has to check for the file itself, as
  the new test does. Whether the script should offer that is a product question, for the
  close sweep.
- Q15 (new). After a change that keeps behaviour (vasiloglou/dev-tools#34), `review`
  lists the entries of the touched modules as older than their code. Is an entry reread
  then, and how is its date brought forward if nothing in it changes? For the close
  sweep.

## Refuted premises

- Plan sections 4 and 9: "`changed --base main` before a pull request". In this
  checkout `main` is not the branch the change will merge into as it now stands, but an
  old local copy of it. The gate row reads `origin/main` (spec IF1). Repair the plan's
  wording at the close.
- Plan section 8, amendment a3: "Once the previous phase merges, the branch is rebased
  onto main." No branch was rebased: `main` was merged into each, bottom up, and each
  pull request's base was changed to `main` before its merge (above, "Since record 005").
  Repair at the close.
- Plan sections 4 and 5: phase 1 is "0.1.4" alone. #34 took that version first; 0.1.4 is
  now both. Repair at the close.
- Spec section 6: the copy "runs `git init -q`". It needs no git (r1 F1, spec IF4).
- Plan C3 and section 9, "except for the known GND `synth` case": already refuted in
  `004-phase-3.md`; the suite exits 0 here.
