# Phase 1 spec: the sync names what a project has not taken, and `check` can say it is behind

## 1. Status

Owner-decided (2026-11-23), by delegated approval (auto=true): the plan gate is
`001-plan.md`; this spec's gate is recorded below, under "Owner gate". Implementation may
begin.

## 2. Provenance

- Derives from `notes/sync-reports-plan.md`, sections 2 ("Phase 1"), 4 ("Phase 1"), 5, 6
  and 9, as drafted on 2026-11-23 with `start-milestone`.
- No prior phase record: this is the milestone's first phase.
- Plan review round 1 (`notes/reviews/plan-r1`, brief SHA-256
  `742e3a0cbb0de4e28fb85eef22d2db713888793bd832488e2e6446932858740c`) read this spec at
  SHA-256 `b69a3e797633…`. Its six findings were repaired here and in the plan, marked
  `(r1 Fn)`. The current bytes are not the reviewed ones, and the repairs carry no review
  opinion.
- Tags used at the site of a change: `(o)` an owner decision, `(rN Fn)` a review finding.

## 3. Obligations

| # | Obligation (source) | Discharged in this spec |
|---|---|---|
| O1 | A unit the config does not take is named on `apply` and `check`, with the file that names it (plan P1.1; brief) | Section 6, `unit_report`; tests T1, T2 |
| O2 | `declined` in `.devtools.toml` silences a unit (plan P1.2, D4) | Section 6, `declined_paths`; T3, T10 |
| O3 | A workflow folder the config takes nothing from is silent (plan P1.3, D3) | Section 6, `workflow_folder`; T4, T7 |
| O4 | A unit added since the receipt is reported as new, until the next `apply` (plan P1.4) | Section 6, the receipt's `shipped`; T6, T7 |
| O5 | A receipt without `shipped` gets a one-time list (plan P1.5, D7) | Section 6; T8 |
| O6 | Without a receipt nothing is new (plan section 2) | T9 |
| O7 | `check` says how many files an `apply` would change, and from which commits (plan P1.1, D5) | Section 6, `pending`; T1, T20 |
| O8 | `check --receipt-only` prints today's lines, reads no source and starts no `git` (plan C3, P1.6) | T16 |
| O9 | `check --strict` exits 5; drift exits 1 and wins (plan D6, D13) | Section 6, exits; T1, T14, T15 |
| O10 | Every existing test exits as on main, unedited (plan C2) | Section 8, "Existing tests"; the autouse fixture |
| O11 | A `declined` entry that covers a taken unit exits 2 and writes nothing (plan P1.7) | T10 |
| O12 | Both examples apply as they are and print no unit report (plan P1.8, D11) | Section 6, "Examples"; T18 |
| O13 | `survey` marks a declined unit and a named one (plan section 2, table) | Section 6, `survey_text`; T17 |
| O14 | The pages, the examples and the adopt skill say it (plan C6, section 5) | Section 6, "Pages" |
| O15 | The lines of `apply --dry-run`, `check` and `check --strict` on a scratch copy of the observed-case fixture, pasted with their exits (plan section 9; brief) | Section 8, "By hand" |
| O16 | The component index is current (plan C5) | Section 8, gates |

## 4. The standing rules, bound to this phase

| Rule | Bound to |
|---|---|
| S0.1 Today's lines and exits stay | `cmd_apply` prints `refused:`, `nothing written;`, `<do>: <dest>`, `dry run:`, `applied:`, `after_apply:` as on main; `cmd_check` prints each problem and `N managed file(s), M problem(s)` as on main. The new lines are printed by `print_report`, after the summary line. T19 compares the whole standard output with main's for a project with nothing to report; the existing tests cover the rest |
| S0.2 The checkout is read, never changed | This phase adds no `git` command. `pending` and `unit_report` read files; `cmd_apply` writes one more key into the receipt it already writes |
| S0.3 A report is rows before it is lines | `unit_report` and `pending` return data; `report_lines` turns it into lines; `print_report` prints. T2 asserts the rows, T1 the lines |
| S0.4 A test brings its own upstream | T1, T6 and T20 need two commits of a source: the fixture runs `git init` under `tmp_path`. The autouse fixture `no_implicit_source` makes `default_source` return `None` in every test; T16 calls the real function |
| S0.5 One file on the standard library | No import is added |
| A script change comes with a test | `devtools/sync.py`: `declined_paths`, `takes`, `workflow_folder`, `unit_names`, `unit_report`, `pending`, `report_lines`, `default_source`, `cmd_check`, `cmd_apply`, `survey_text`. Each has a test in section 8 that fails on main |
| The plugins are rebuilt, and released under a new version | No skill or agent that a plugin holds changes: `skills/adopt-devtools` is in no plugin. The gate `build_plugins.py --check` shows it; if `release_plugins.py status` names a changed plugin file, the phase runs `bump` |
| A wording change says what prompted it | Each changed sentence of `skills/adopt-devtools/SKILL.md`, `README.md` and `docs/adopt.html` describes a behaviour this phase adds; the baseline of plan section 3 is the run behind it |
| Shared skills stay general | `skills/adopt-devtools/SKILL.md` gains the option, the key and the exit, which hold for any project. It names no project |
| Both agents read the same file | The one skill changed names shell commands and no plugin path. Read once as Claude Code and once as Codex for a path only one resolves |
| Captures on the site are real output | Each capture of `apply`, `check` and `survey` in `docs/adopt.html` is compared with a real run on a scratch project built to its caption; one that differs is retaken, and the record lists which. The new capture is the "By hand" run |
| The page that describes it is updated too | `README.md` ("How a project takes it") and `docs/adopt.html` ("Updates that respect your changes"), in this phase's pull request |

## 5. Goal

With a fixture project whose config lacks `skills/milestone/review-pr`, whose delivered
`process-phase` names it, and whose receipt is one commit older than the source: `apply
--dry-run` exits 0 and prints the unit with the file that names it; `check --source`
exits 0 and prints the summary line, then how many files an apply would change; `check
--source --strict` exits 5; `check --receipt-only` exits 0 and prints the summary line
alone. `pytest tests -q`, `build_plugins.py --check` and the built
`components_index.py --check --strict` each exit 0.

## 6. Design

### Reuse

| Capability | Searches run | Found | Decision |
|---|---|---|---|
| List what dev-tools ships | `search units a project has not taken`; `search decline a unit in .devtools.toml` | `devtools.sync.shipped_units` (component `sync.copies`) | reuse |
| What an apply would do to each file | `search receipt source commit behind` | `devtools.sync.plan`, `devtools.sync.source_identity` | reuse: `pending` counts `plan`'s actions |
| Which delivered files come from which entry | `search which shipped file names another skill` | `devtools.sync.desired_files` gives each delivered file its bytes and origin | reuse: the text read for names is `wanted[dest]["data"]` |
| Read a file as it was at a commit | `search fetch upstream git ref` | `components_index.files_at`, `handoff.base_ref`, in shipped scripts that stand alone | not used in this phase (phase 2) |
| Know which unit a text names | the same two searches; `git grep -n "related(" devtools/sync.py` | `devtools.sync.related` compares two folder names; nothing reads names out of text | new: `unit_names` and the two forms of section "Named" |

### `devtools/sync.py` (1,098 lines today; about 170 added)

**The config.** `read_config` accepts one more top-level key, `declined`. It also turns
the errors of reading the file into `SyncError` (exit 2): a file that is not valid TOML
(`tomllib.TOMLDecodeError`), one that cannot be read (`OSError`) and one that is not
UTF-8 (`UnicodeDecodeError`). On main these end in a traceback with exit 1, for `apply`,
`compare` and `survey` alike (r1 F1).

```python
def declined_paths(config: dict, units: list[dict]) -> tuple[list[str], list[str]]:
    """(the paths `declined` lists, those among them that cover no shipped unit).
    Raises SyncError (exit 2) for a value that is not a list of strings, for a path that is
    absolute or holds `..`, and for a path that covers a unit the config takes."""
```

```python
def takes(path: str, unit: str) -> bool:
    """A config path and a unit's source meet: equal, or either lies under the other."""

def covers(path: str, unit: str) -> bool:
    """`path` is the unit's source or a folder above it."""
```

Both compare whole path segments (`pathlib.PurePosixPath.parts`), so `skills/phase` does
not cover `skills/phase-extra`. A trailing `/` is ignored.

**Names.**

```python
def unit_names(source_root: Path, unit: dict) -> set[str]:
    """What a file can call the unit: a skill's folder name; for `agents`, each file's
    name without its extension; for a script, its file name."""

def workflow_folder(unit: str) -> str | None:
    """`skills/<folder>` when the unit lies deeper than one level under `skills/`, else None.
    `skills/phase/process-phase` -> `skills/phase`; `skills/components`, `agents` -> None."""
```

**Named.** A delivered file names a unit when its text, decoded as UTF-8 (a file that
does not decode names nothing), holds for one of the unit's names `<name>` either:

- `` `<name>` ``: the name alone between two backticks;
- `../<name>/`: the name as the folder after `../`.

Both are found with `in` on the text, not with a pattern: the name is a literal, and the
two forms are literal strings built from it. A name that a taken unit also has is dropped
before the search.

**The report.**

```python
def unit_report(source_root: Path, config: dict, wanted: dict[str, dict], receipt: dict) -> dict:
    """What to say about the units the config does not take. Reads only."""
```

It returns exactly these keys:

```json
{
  "named": [{"unit": "skills/milestone/review-pr",
             "by": [".claude/skills/handle-issue/SKILL.md", ".claude/skills/process-phase/references/review-tool.md"]}],
  "new": ["skills/extra"],
  "unlisted": ["agents"],
  "stale_declined": ["skills/retired"]
}
```

The normative order, for each unit of `shipped_units(source_root)`, in that order:

1. taken (`takes` with any entry's `source`): nothing;
2. covered by a `declined` path: nothing;
3. `workflow_folder` is not `None` and no entry's `source` lies under it: nothing;
4. a delivered file names it: a row in `named`, `by` sorted;
5. the receipt has `files` and has `shipped`, and the unit is not in `shipped`: `new`;
6. the receipt has `files` and has no `shipped`: `unlisted`;
7. otherwise nothing.

`stale_declined` is the second value of `declined_paths`. This list is the one home of
the order; the plan's table (section 2) summarises it.

```python
def pending(project: Path, wanted: dict[str, dict], receipt: dict, source: dict) -> dict | None:
    """None when an apply would create, update and delete nothing. Else
    {"from": <receipt commit or None>, "to": <source commit or None>,
     "create": n, "update": n, "delete": n}. Counts `plan`'s actions; `keep` and `forget` are not counted."""

def report_lines(report: dict | None, behind: dict | None) -> list[str]:
    """The lines to print, in order; empty when there is nothing to say."""
```

**The lines**, on standard output, in this order, each block only when it has a row:

```
not current: an apply would update 22 file(s) (synced from dev-tools c9648dd; this source is 811b4a3)
not taken, and named by a file this project has:
  skills/milestone/review-pr
      named by .claude/skills/handle-issue/SKILL.md and 3 more file(s)
new in dev-tools since this project's last sync:
  skills/extra
not taken (this receipt was written before the sync recorded what dev-tools ships; listed this once):
  agents
to take a unit, add a [[sync]] entry to .devtools.toml; to stop hearing of one, add its path to `declined` there
```

- The first line joins the counts that are not zero: `create 2, update 22 and delete 1
  file(s)`. A commit is its first seven characters; an unknown one reads `an unknown
  commit`. When both commits are known and equal the bracket reads `(the same dev-tools
  commit, 811b4a3: the config or the source's files changed)`.
- `named by <first file>` alone when one file names the unit.
- The last line is printed once, when any of the three unit blocks is.
- `stale_declined` is one line per path on standard error:
  `warning: declined names nothing dev-tools ships: skills/retired`.

**The receipt** gains one top-level key, written by `cmd_apply`:

```json
{"files": {}, "source": {"commit": "…", "dirty": false},
 "shipped": ["agents", "skills/components", "skills/milestone/review-pr"]}
```

`shipped` is the sorted `source` of every unit of `shipped_units(source_root)`, taken or
not.

**`cmd_apply`.** Reads the receipt before writing. `declined_paths` runs with
`desired_files`, so its errors exit 2 before anything is written. After the line
`dry run: …` or `applied: …` it prints `report_lines(unit_report(…), None)`. The refusal
path (exit 3) prints no report. The exit is never changed by a report.

**`cmd_check`.**

```
check --project DIR [--source DIR] [--receipt-only] [--strict]
```

1. The receipt comparison, as on main: the same lines, and `problems` decides exit 1.
2. The source: none with `--receipt-only`; else `--source`; else `default_source()`.
   `--receipt-only` with `--source`, or with `--strict`, is a usage error (exit 2).
3. With a source: read the config, `desired_files`, `pending`, `unit_report`, and print
   `report_lines`. A `SyncError` here (no config, one that cannot be read or parsed, an
   invalid one, a source that lacks an entry's path) is caught, and since `read_config`
   raises nothing else for a bad file (r1 F1), nothing else is: one line on standard error,
   `warning: not compared with dev-tools: <the error>`, and the comparison counts as not
   made.
4. Exit: 1 with problems. Else, with `--strict`: 5 when `pending` is not `None`, or
   `named`, `new` or `unlisted` has a row, or the comparison was not made; 5 also when
   there is no source at all, since a strict check that compared nothing must not read as
   clean. Else 0.

```python
def default_source() -> Path | None:
    """The checkout that holds this file, when it is a dev-tools source: every path of
    EXAMPLES is a file under it. None for a sync.py copied somewhere else."""
```

**`survey_text`.** Under "Shipped, with no counterpart here", a unit covered by
`declined` ends with `  [declined in .devtools.toml]`, and a unit that `unit_report`
puts in `named` ends with `  [named by <first file>]`. Without a config, or with one
`desired_files` refuses, the lines are as on main. `starter_config`'s closing comment
gains `, or list it under declined`.

**The module docstring** gains `declined`, `check`'s options and exit 5.

### Examples

- `examples/milestone-project.devtools.toml`: `declined = ["skills/components"]`, with a
  comment that says what the key does and that `phase-project.devtools.toml` shows the
  entry that takes the unit (plan D11). The line comes before the first `[[sync]]`, where
  TOML requires a top-level key.
- `examples/phase-project.devtools.toml`: the same comment, with the key commented out,
  since the example has nothing to decline.

### Pages

- `README.md`, "How a project takes it": what `apply` says about units; `check` against
  the source, `--receipt-only`, `--strict` and exit 5; `declined`.
- `docs/adopt.html`, "Updates that respect your changes": two rows in the table (a unit
  your files name that you do not take; a unit added since your last sync), and one
  capture, taken from the "By hand" run of section 8.
- `skills/adopt-devtools/SKILL.md`: the row for `sync check` in the command table, and
  one sentence where the config is written, on `declined`.

## 7. Decisions

Ruled 2026-11-23 by delegated approval (auto=true), each as proposed (o). Plan decisions
D1 to D7, D11 and D13 are ruled at the plan gate and are not repeated here.

| # | Question | Readings and their cost | Proposed |
|---|---|---|---|
| S1 | The wording of the lines of section 6 | As written. Or the owner's wording: no exit differs | As written |
| S2 | `check --strict` with no source at all (a `sync.py` outside a checkout, or `--receipt-only`) | **Exit 5** for the first and a usage error (2) for `--strict --receipt-only`: strict never reads as clean without a comparison. **Exit 0:** a CI job with no checkout can pass `--strict` and learn nothing | Exit 5, and exit 2 for the two options together |
| S3 | A unit that is both named and new | **Listed under `named` only:** one row per unit. **Under both:** the reader sees it is new, and reads the unit twice | `named` only |
| S4 | How `default_source` knows a dev-tools source | **Every path of `EXAMPLES` exists:** a test on main already asserts the repository has them. **A `skills/` folder exists:** a project with its own `skills/` and a copied `sync.py` would be taken for dev-tools | `EXAMPLES` |
| S5 | `not current` when the receipt's commit and the source's are equal | **Say it, with the bracket of section 6:** the config changed or the source has uncommitted changes, and an apply would still write. **Say nothing:** the same silence as today | Say it |

## 8. Tests

All in `tests/test_sync.py`. New fixtures, built under `tmp_path`:

- `workflows`: a source with `skills/milestone/process-phase` (its
  `references/review-tool.md` holds `` `review-pr` ``), `skills/milestone/review-pr` (its
  `SKILL.md` holds `../process-phase/scripts/review_tool.py`),
  `skills/milestone/start-milestone`, `skills/phase/process-phase`,
  `skills/phase/phase-tests`, `skills/handle-issue` (names `` `review-pr` `` and
  `` `start-milestone` ``), `skills/components`, `agents/phase-implementer.md`, and
  `skills/phase/pytest/phase_selection.py`. It is a git repository with one commit.
- `milestone_project`: a config that takes `process-phase`, `start-milestone` and
  `handle-issue` of the milestone workflow and `skills/components`, each into
  `.claude/skills` and `.codex/skills`.
- `no_implicit_source` (autouse): `default_source` returns `None`.

| # | Case | Expected |
|---|---|---|
| T1 | The observed case. Apply `milestone_project` from `workflows`; change one file of `process-phase` and commit; then `apply --dry-run`, `check --source`, `check --source --strict`, `check --receipt-only` | Exits 0, 0, 5, 0. The dry run prints the `named` block with `skills/milestone/review-pr` and `.claude/skills/handle-issue/SKILL.md and 3 more file(s)`. `check --source` prints the summary line first, then `not current: an apply would update 2 file(s)` with both commits' first seven characters. `--receipt-only` prints the summary line and nothing else |
| T2 | `unit_report` on the T1 state | Equal to the dict: `named` has the one row with four sorted paths; `new`, `unlisted` and `stale_declined` are empty |
| T3 | T1's config with `declined = ["skills/milestone/review-pr"]`, after an apply that leaves nothing pending | `apply` and `check --source` print no unit block; `check --source --strict` exits 0 |
| T4 | A config that takes `skills/phase/process-phase` and `skills/handle-issue` | No block names `review-pr` or `start-milestone`, which `handle-issue` names: `skills/milestone` is untaken |
| T5 | T4's `handle-issue` also holds `` `process-phase` `` | `skills/milestone/process-phase` is not reported in a config that takes `skills/phase/process-phase` and `skills/milestone/start-milestone`: the name is satisfied |
| T6 | `milestone_project` with `declined = ["skills/milestone/review-pr", "agents"]`, applied, then `skills/extra/SKILL.md` added to the source | `apply --dry-run` and `check --source` list `skills/extra` under `new` and print no other block; `check --source --strict` exits 5 (nothing is pending: the source's other files are unchanged); the next `apply` lists it and writes it into `shipped`; the `apply` after that prints no block, and `check --source --strict` exits 0 (r1 F2, F4) |
| T7 | As T6, with the new unit at `skills/phase/extra`; and at `skills/extra` with `skills/extra` added to `declined` | No block in either; `check --source --strict` exits 0 (r1 F2) |
| T8 | Remove `shipped` from the receipt of an applied `milestone_project`, with `review-pr` declined | `check --source` lists `agents` under the one-time heading and nothing else; neither phase unit is listed; `check --source --strict` exits 5; after `apply`, `check --source` prints no block and `--strict` exits 0 |
| T9 | The first `apply` of `milestone_project` | The `named` block; no `new` block and no one-time block |
| T10 | `declined` as a string; with `/abs`; with `../x`; covering a taken unit; covering nothing shipped | Exit 2 for the first four, with no file and no receipt written; exit 0 for the fifth, with the warning on standard error and `check --source --strict` exiting 0 |
| T11 | The only file that names `review-pr` is under the entry's `exclude` | `named` is empty |
| T12 | A delivered file holds `` `phase-implementer` ``; another holds `` `phase_selection.py` ``, in a config that takes one phase skill | `agents` and `skills/phase/pytest/phase_selection.py` are each in `named`, with that file |
| T13 | A delivered file holds the bare words `review-pr`, the token `` `review-pr/SKILL.md` ``, and the path `docs/components/` in a config without `skills/components` | Neither unit is in `named`. The same file with `` `components` `` added puts `skills/components` in `named` |
| T14 | `check --source` with no `.devtools.toml`; with a config that holds an unknown key; with one that is not valid TOML; with one that cannot be read (mode 000, skipped when run as root) | The warning line on standard error; exit 0; with `--strict`, exit 5, for each (r1 F1) |
| T14b | `apply` with a config that is not valid TOML | Exit 2 and one line `error: …` on standard error, where main raises (r1 F1) |
| T15 | T1's state with one managed file edited, `check --source --strict` | Exit 1 |
| T16 | `sync.default_source` as imported, on the repository and on an empty folder; `check --receipt-only` with `subprocess.run` replaced by a function that raises; `check --receipt-only --source X`; `check --receipt-only --strict`; `check --strict` with no source | The repository's root, then `None`; exit 0 and the summary line; exit 2; exit 2; exit 5 |
| T17 | `survey` on T3's project, and on `milestone_project` without `declined` | `skills/milestone/review-pr  [declined in .devtools.toml]`; then `skills/milestone/review-pr  [named by .claude/skills/handle-issue/SKILL.md]` |
| T18 | Each example, applied from the repository | Exit 0; standard output holds none of the four block headings of section 6 and not the closing line. Other lines, such as `after_apply:`, are as on main (r1 F3) |
| T19 | A project with everything current and nothing to report: `apply` and `check --source` | Standard output is exactly `applied: {"keep": N}` and exactly `N managed file(s), 0 problem(s)` |
| T20 | `pending` with one file to create, one to update and one to delete; with a source that is not a git repository | `create 1, update 1 and delete 1 file(s)`; `an unknown commit` |
| T21 | `takes` and `covers` on `skills/phase` against `skills/phase-extra`, `skills/phase/x`, `skills/phase/` | False, True, True |
| T22 | A config that takes `skills/milestone/review-pr` and no `process-phase` | `skills/milestone/process-phase` is in `named`, by `.claude/skills/review-pr/SKILL.md` (the `../` form); `skills/phase/process-phase` is not: its workflow folder is untaken |
| T23 | One cause at a time, for `check --source --strict`: (a) pending only: T3's project after one source file changes; (b) named only: T1's project after `apply`, with nothing declined; (c) new only: T6 | Exit 5 in each; in each the other blocks and the `not current` line are absent, so the exit can come from that cause alone (r1 F4) |
| T24 | A unit that is new and named: after an apply of `milestone_project` with `review-pr` declined, a new unit `skills/milestone/extra` is added, and a delivered file of the source gains `` `extra` `` | `skills/milestone/extra` appears under `named` and not under `new` (S3; r1 F4) |

**Branches, walked against the normative order.** Step 1: T19. Step 2: T3, T7. Step 3:
T4, T7. Step 4: T1, T2, T12. Step 5: T6. Step 6: T8. Step 7: T9. The two name forms:
backticks in T1, T12 and T13; `../` in T22. A satisfied name: T5. `check`'s exits: 0
(T1), 1 (T15), 2 (T16), and 5 for each cause on its own: pending (T23a), named (T23b),
new (T6, T23c), unlisted (T8), not compared (T14), and no source (T16). T3 and T7 show 0
once every cause is gone (r1 F4).

**Existing tests.** None is edited. `no_implicit_source` keeps plain `check` receipt-only
in all of them, as on main.

**Verification selection.**

| Obligation | Disposition | Command | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| The phase's tests (T1 to T24) and every existing sync test (C2) | run | `uv run --no-project --with pytest python -m pytest tests/test_sync.py -q`, exits 0 | `devtools/sync.py`, `tests/test_sync.py`, `examples/*.devtools.toml` | The direct tests of every changed function | Any change to those files |
| Plan section 9: the whole suite | run | `uv run --no-project --with pytest python -m pytest tests -q`, exits 0 | The repository | Plan-mandated; 2.5 minutes here. It holds the consumers: `test_own_index.py` (the index), `test_plugins.py` (the build) | Any change |
| The plugins match the skills | run | `python3 devtools/build_plugins.py --check`, exits 0 | `skills/`, `agents/`, `plugins/` | Plan-mandated; shows that no plugin file changes | A change under `skills/` or `agents/` |
| The component index is current | run | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py write`, then the same with `--check --strict`, exit 0 each | `devtools/sync.py`, `.devtools/components/` | `.devtools/project.md`, "Gates" | Any change to `sync.py` |
| The index against the phase's changes | run | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base 811b4a3 --strict`, exits 0 | The phase's diff | process-phase step 6 | Any change |
| The by-hand run (below) | run | The three commands under "By hand" | A scratch copy of the T1 state | Plan section 9 and the brief: the owner reads real lines | A change to what `apply` or `check` print |

No broader lane exists: the suite is the repository's only test command.

**By hand** (r1 F6). A scratch copy of the T1 state, built outside the repository by the
same steps, in `$SCRATCH` (the session's scratch folder): `$SCRATCH/source` is the
two-commit source, and `$SCRATCH/project` the project applied from its first commit.
From the repository root:

```bash
python3 devtools/sync.py apply --project "$SCRATCH/project" --source "$SCRATCH/source" --dry-run
python3 devtools/sync.py check --project "$SCRATCH/project" --source "$SCRATCH/source"
python3 devtools/sync.py check --project "$SCRATCH/project" --source "$SCRATCH/source" --strict
```

Expected exits 0, 0 and 5. The exact lines and exits go into the phase record and into
the new capture of `docs/adopt.html`.

## Owner gate

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/sync-reports/notes/phase-1-spec.md (the bytes of the
      commit that adds this block; its SHA-256 is in the phase 1 record)
    date: 2026-11-23
    authorization: the owner's "Milestone, auto=true" for sync-reports (001-plan.md)
    instrument: this prose (section 11); no review over the spec bytes beyond plan-r1
    decisions: S1 to S5 as proposed
    implementability sweep: each test row walked against section 6 and its fixtures, by
      the agent, 2026-11-23; the r1 findings F1 to F4 were the rows that failed it before
      the repair

## 9. Out of scope for this phase

- Any `git fetch`, and reading another commit than the checkout's (phase 2).
- `--as-is` (phase 2).
- Whether a named unit is delivered beside the file that names it, and a unit taken for
  one skills folder only (plan Q1, Q2).
- `compare`: it shows files, and gains nothing in this phase.
- Renaming or reordering anything `survey` prints today.

## 10. Size

Estimate at write time: `devtools/sync.py` about 170 lines added; `tests/test_sync.py`
about 330; the pages, the examples and the skill about 70. Measured at record time.

## 11. Approval instrument

This prose. There is no fixture corpus.

## Implementation findings, recorded as they were found

1. **"Not current" counted a hand-edited file** (2026-11-23, while checking the site's
   captures). `pending` as written in section 6 counts `plan`'s actions, and `plan` calls
   a file edited in the project an `update` (needing `--force`), so a project with drift
   and an unchanged source read as behind. Amended (o, delegated): an action counts only
   where the source differs from what the receipt records. Test T25. The prior wording
   of section 6, kept: "Counts `plan`'s actions; `keep` and `forget` are not counted."
2. **The commit wording.** Section 6 wrote `(synced from dev-tools c9648dd; this source
   is 811b4a3)` and an unknown commit as `an unknown commit`, which reads "synced from
   dev-tools an unknown commit". Amended (o, delegated): `synced from dev-tools at
   <commit>; this source is at <commit>`. S1 ruled the wording replaceable at no cost to
   an exit.
3. **`default_source` takes the folder as an argument** (`default_source(root=SOURCE_ROOT)`),
   so T16 can call it on an empty folder. Section 6 showed it with no argument.
4. **The site's first-sync frame now shows a unit report.** Run with the config the page
   shows, the phase workflow's `process-phase` names `dev-handoff`, `dev-takeover`,
   `phase-tests` and `agents`, none of which that config takes. The frame was retaken
   from that run; the hand-edit frame was retaken from a project that declines the four.
5. **The adopt walk-through frames of `docs/adopt.html`** (the `compare`, `apply --adopt`,
   `check` and `survey` run on the demo project `shelf`) cannot be retaken: the demo
   project is not in the repository, and those frames were already older than the
   current output (`dev-tools ships 8 unit(s)`). Left as they are; an open question for
   the close.
6. **Review round 1** (`notes/reviews/phase-1-r1`): five findings, four reproduced as
   failing tests and fixed (a config of the wrong shape, a machine with no git, a file
   already as shipped counted as behind, a receipt with no files), one a caption.
