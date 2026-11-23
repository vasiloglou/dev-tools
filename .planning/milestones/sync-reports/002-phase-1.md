---
milestone: sync-reports
station: "phase-1"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-1
date: 2026-11-23
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests/test_sync.py -q"
    exit: 0
    output: "89 passed in 11.45s"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "393 passed in 185.74s (0:03:05)"
    note: "run at 51140d5, the phase's head"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base 811b4a3 --strict"
    exit: 0
    output: "changed against 811b4a3 (811b4a3): 25 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "none beyond the full suite"
  trigger: "n/a"
  reason: "the full suite is the repository's only test lane, and it ran (above)"
evidence:
  - path: devtools/sync.py
    sha256: cb0652a6ea353f0982308b26538f315958a5d2015085bc41be70307edfa5e28f
  - path: tests/test_sync.py
    sha256: c6db60b7ec704450a4c46252de810791d3961dd52b498e7cf7d191fb69aba278
  - path: examples/milestone-project.devtools.toml
    sha256: 7221089d737f9e94711e1da7eed26a1140d4e5e50d41b139e376f5351945a2e3
  - path: examples/phase-project.devtools.toml
    sha256: 71caa4a90c9d365c5a9e77dde8267fa6a74a962ca9c085bc82074b58647b8769
  - path: README.md
    sha256: e33eb8757f2af0504d9de842ed20a5dae7e86d46428753272224f034e5444b69
  - path: docs/adopt.html
    sha256: 41bba3c24f71518a75b404d0315fbc4ec7bcea1ffc31a7c5ad55145ded20ba24
  - path: skills/adopt-devtools/SKILL.md
    sha256: a3ca78aff2ec9615aa0dac40e7b6ab3c8835e2edc29aa5b20e58f7dcd201a111
  - path: .devtools/components/COMPONENTS.md
    sha256: 53528dfe833f8cf820e64df525ebc2236bb7dd086f51bc17cf4623eb4a2213a5
  - path: .devtools/components/modules/_root.md
    sha256: d48782eafc7d7299c83c12764d6b3265ec43d91d2a47d66506011861f50936ce
  - path: .planning/milestones/sync-reports/notes/phase-1-spec.md
    sha256: 778a2dcb124adee54e08847fdeed55bbea1bc7ae121de80ab656843f97dad41f
  - path: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/BRIEF.md
    sha256: 15e25faae48491b3c1accddc937363594c3c444cf65737f5e89d1be1d0148355
  - path: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/review.md
    sha256: 0d0aa0b73f57e97c878d0ef4d7c6c871003a6a6cd7f3313a0480951fc991386a
  - path: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/FINDINGS.md
    sha256: 01f6aae49ba7804db9430a2b49cba2d28eb7aa93f8e66f8af1a541a58743f29f
---

# Claim

Phase 1's selected gates each exited 0 on the phase's head: `apply` and `check` name a
unit the config does not take when a delivered file names it, and a unit new since the
last receipt; `declined` silences a unit; `check` against a source says how many files an
apply would change; `check --strict` exited 5 on the observed case.

## What shipped

- **`devtools/sync.py`** (250 lines added, 12 removed against `811b4a3`):
  - `read_config` accepts `declined`, and turns a file it cannot read or parse, and a
    config of the wrong shape, into a configuration error (exit 2) (plan r1 F1; phase
    r1 F1).
  - `covers`, `takes`, `declined_paths`, `unit_names`, `workflow_folder`, `names_in`:
    the rule of section 6 of the spec, by whole path segments and literal names.
  - `unit_report` returns the rows (`named`, `new`, `unlisted`, `stale_declined`);
    `report_lines` and `print_report` print them. The normative order is in its
    docstring and in the spec, section 6.
  - `pending` counts `plan`'s actions where the source differs from the receipt
    (implementation finding 1; phase r1 F3).
  - The receipt gains `shipped`. `cmd_apply` prints the report after its summary line.
  - `cmd_check` gains `--source`, `--receipt-only` and `--strict` (exit 5);
    `default_source` makes a checkout's own `sync.py` compare with it.
  - `survey` marks a declined unit and a named one; the starter config's closing
    comment names `declined`.
- **`tests/test_sync.py`**: T1 to T25 of the spec and four regression tests of phase r1
  (506 lines added, none of the existing tests edited). The autouse fixture
  `no_implicit_source` keeps plain `check` receipt-only in every test.
- **`examples/milestone-project.devtools.toml`**: `declined = ["skills/components"]`, with
  what the key does (plan D11). **`examples/phase-project.devtools.toml`**: the same
  comment, the key commented out.
- **`README.md`, `docs/adopt.html`, `skills/adopt-devtools/SKILL.md`**: the report, the
  key, `--receipt-only`, `--strict` and exit 5. Two frames of `docs/adopt.html` retaken
  from real runs, one added (below).
- **`.devtools/components/`**: `sync.copies` describes the new capability; the module
  page regenerated.

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests/test_sync.py -q
    89 passed in 11.45s
    $ uv run --no-project --with pytest python -m pytest tests -q
    393 passed in 185.74s (0:03:05)
    $ python3 devtools/build_plugins.py --check
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base 811b4a3 --strict
    changed against 811b4a3 (811b4a3): 25 file(s) differ; 0 to fix, 0 warning(s), 0 to reread

The by-hand run (spec section 8), on a scratch copy of the T1 state built outside the
repository (`$SCRATCH/source` with two commits, `$SCRATCH/project` applied from the
first), with the code at `2120090`:

    $ python3 devtools/sync.py apply --project "$SCRATCH/project" --source "$SCRATCH/source" --dry-run
    update: .claude/skills/process-phase/SKILL.md
    update: .codex/skills/process-phase/SKILL.md
    dry run: {"keep": 10, "update": 2}
    not taken, and named by a file this project has:
      skills/milestone/review-pr
          named by .claude/skills/handle-issue/SKILL.md and 3 more file(s)
    to take a unit, add a [[sync]] entry to .devtools.toml; to stop hearing of one, add its path to `declined` there
    exit 0
    $ python3 devtools/sync.py check --project "$SCRATCH/project" --source "$SCRATCH/source"
    12 managed file(s), 0 problem(s)
    not current: an apply would update 2 file(s) (synced from dev-tools at d47e1d6; this source is at 278a44b)
    not taken, and named by a file this project has:
      skills/milestone/review-pr
          named by .claude/skills/handle-issue/SKILL.md and 3 more file(s)
    to take a unit, add a [[sync]] entry to .devtools.toml; to stop hearing of one, add its path to `declined` there
    exit 0
    $ python3 devtools/sync.py check --project "$SCRATCH/project" --source "$SCRATCH/source" --strict
    12 managed file(s), 0 problem(s)
    not current: an apply would update 2 file(s) (synced from dev-tools at d47e1d6; this source is at 278a44b)
    not taken, and named by a file this project has:
      skills/milestone/review-pr
          named by .claude/skills/handle-issue/SKILL.md and 3 more file(s)
    to take a unit, add a [[sync]] entry to .devtools.toml; to stop hearing of one, add its path to `declined` there
    exit 5

The new-unit case, on a second scratch copy that declines `review-pr`, after a unit was
added to the source (code at `8ec1f91`; the r1 repairs do not touch this path):

    $ sync.py check --project project --source source
    12 managed file(s), 0 problem(s)
    new in dev-tools since this project's last sync:
      skills/milestone/plan-review
    to take a unit, add a [[sync]] entry to .devtools.toml; to stop hearing of one, add its path to `declined` there
    exit 0

The observed case against the real dev-tools: a scratch project with the baseline's
config, applied from a clone of dev-tools at `c9648dd`, checked with this branch's
`sync.py` at `8ec1f91`. This is the new frame of `docs/adopt.html`:

    60 managed file(s), 0 problem(s)
    not current: an apply would update 22 file(s) (synced from dev-tools at c9648dd; this source is at 8ec1f91)
    not taken, and named by a file this project has:
      skills/milestone/review-pr
          named by .claude/skills/handle-issue/SKILL.md and 3 more file(s)
    not taken (this receipt was written before the sync recorded what dev-tools ships; listed this once):
      agents
    to take a unit, add a [[sync]] entry to .devtools.toml; to stop hearing of one, add its path to `declined` there

The scratch projects and their output live outside history.

## Review

Phase review round 1 (`notes/reviews/phase-1-r1`), the review helper with
`--subject phase --base c85728d`; reviewer Codex, read-only, effort `high`; brief SHA-256
`15e25faae48491b3c1accddc937363594c3c444cf65737f5e89d1be1d0148355`. `VERDICT:
CHANGES_REQUESTED`, 5 findings: 2 blocking, 1 hardening, 2 completeness. All five were
reproduced and fixed at `2120090`, each code finding with a test that failed on the
reviewed code. One reviewer is one reviewer.

The repaired bytes (`devtools/sync.py`, `tests/test_sync.py`, the caption in
`docs/adopt.html`) carry no review opinion from this round. Phase 2's review brief takes
its base at `e49b052`, the commit this round read, so its reviewer reads the repairs
with phase 2's diff.

The reviewer confirmed, among others: the observed case's exits 0, 0, 5; declined units
and untaken workflows silent; the four refusals of `declined`; `--receipt-only` output
with no process started; `names_in` tried with bare, qualified, multi-line and Unicode
names; `covers` with prefix collisions, trailing slashes, `./` and Unicode.

## Captures

| Frame of `docs/adopt.html` | What was done |
|---|---|
| "shelf · first sync" | Retaken: a scratch project with the config the page shows, applied and checked from this branch at `8ec1f91`. It now shows the unit report; the counts are 40, not 29 |
| "shelf · a synced file was edited by hand" | Retaken: the same config, declining the four named units; caption says so (r1 F5) |
| "a project synced from an older dev-tools" | New: the observed case above |
| "shelf · had it kept its own copies of the skills", "before anything is replaced", "after the two rules moved to project.md" | Not retaken: the demo project is not in the repository. Already older than main's output before this phase. Open question Q4 |
| "a new project · from empty to ready" | Not retaken: the phase example's `apply` prints no unit report (T18), so this phase adds no line to it |

## Refactoring review

None needed, argued from what the phase touched. The phase added functions beside
`shipped_units`, `plan` and `survey`, and reused each (`pending` calls `plan`;
`unit_report` reads `shipped_units` and `desired_files`'s output; `survey` reads
`unit_report`). Two candidates were looked at and left: the three places that list the
config's sources (`takes` users, `source_identity`, `declined_paths`) each need a
different shape, and a shared helper would save two lines; and the survey's own walk
over units is about what the project holds, not what the config takes, so it does not
duplicate `unit_report`.

## Boundary -- what this phase does NOT establish

- One reviewer is one reviewer. Its review was by reading and in-memory runs, without
  pytest or scratch projects (its "Not checked").
- The repaired bytes of `2120090` carry no review opinion until phase 2's round reads
  them.
- The named rule finds a unit only by its name alone in backticks or as the folder after
  `../` (plan K2). A unit mentioned another way is not reported.
- The rule counts a passing mention as a name (plan K1): on the config the site shows,
  `process-phase` names four units, and a project hears of each until it takes or
  declines it.
- Nothing in this phase reaches the network or reads another commit than the source's
  working tree. A checkout behind its upstream still delivers its own files (phase 2).
- The real downstream project of the brief was not run; its counts (62 files, 21 to
  update) are an inherited claim.

## Open questions

- Q4 (new). The adopt walk-through frames of `docs/adopt.html` come from a demo project
  that is not in the repository and are older than the sync's output on main. Retaking
  them needs the demo project rebuilt. Target: the close, as a residual or a follow-up.
- Q1 to Q3 of the plan, carried.
