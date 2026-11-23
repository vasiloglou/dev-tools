# Milestone plan: sync-reports

**Goal.** A project learns from its ordinary `sync.py apply` and `sync.py check` runs that
it lacks a unit its own synced files name, that dev-tools has added a unit since its last
sync, and that it is behind dev-tools. An `apply` run from a dev-tools checkout that is only
behind its upstream delivers the upstream's files, not the old ones.

**Status.** Approved, 2026-11-23, by delegated approval (auto=true): `001-plan.md`.
Written with `start-milestone` (the installed dvt-milestone 0.1.3; the scripts run are
the built copies under `plugins/`, at 0.1.5).
- **One owner ruling so far (o).** 2026-11-23, in this session, to "Should `apply` fetch and
  deliver the latest dev-tools by default?": "Yes, by default". It is D8, and phase 2
  exists because of it.
- **Lane ruled, 2026-11-23 (o).** The owner chose "Milestone, auto=true", relayed to this
  session by the session that started it. D1 is ruled by it, and the plan, spec and close
  rulings of this milestone are delegated (auto=true). Not delegated: pushing, opening the
  pull request, merging, tagging and releasing.
- **Plan review, round 1 (r1).** `notes/reviews/plan-r1`, run 2026-11-23 with the review
  helper and `--subject plan`; reviewer Codex, read-only, its default model at effort
  `high`; brief SHA-256
  `742e3a0cbb0de4e28fb85eef22d2db713888793bd832488e2e6446932858740c`. `VERDICT:
  CHANGES_REQUESTED`, with 6 findings: 3 blocking (all in the phase 1 spec's tests and
  error handling) and 3 completeness. All 6 were reproduced and repaired, marked
  `(r1 Fn)` at each site. **The repaired bytes carry no review opinion.**
- **Review budget** (declared before r1, section 8): at most r1 and r2.

  | Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
  |---|---|---|---|---|---|---|
  | r1 | 1 (Codex) | 6 | 0 / 6 (first round) | 3 / 6 | blocking | CHANGES_REQUESTED |

  Round 2 is not run. The three blocking findings were test rows and an error path of the
  phase 1 spec, where the discharge is a test that runs, not more prose
  (`review-convergence.md`, "Specify decisions, discover facts"); the design of section 2
  drew none. Phase 1's diff review reads the code that implements those rows.
- **Plan gate: delegated approval (auto=true), 2026-11-23.** Recorded in `001-plan.md`,
  which binds these bytes by SHA-256. D2 to D7 and D9 to D13 are ruled as proposed. The r1
  repairs are unreviewed (above).

**Done when** (the completion predicates; each is a gate with an exit code, or a ruling):

- C1. The observed case, as a test with its own fixture (a config without `review-pr`, a
  delivered `process-phase` that names it, a receipt older than the source): `apply
  --dry-run` exits 0 and prints the unit with the file that names it; `check` exits 0 and
  prints how many files an apply would change; `check --strict` exits 5 (D6).
- C2. Every test of `tests/test_sync.py` as it is on main at `811b4a3` exits as it does
  there, with no edit to any of them (section 3; section 6, K3).
- C3. `check --receipt-only` prints the lines `check` prints on main, reads no dev-tools
  source and starts no `git` process.
- C4. With a fixture checkout that is behind its upstream: `apply` delivers the upstream's
  files and leaves the checkout's `HEAD`, branch and files as they were; a checkout with
  commits of its own, or uncommitted changes, is delivered as it is, with a warning; a
  fetch that fails is a warning and the exit is 0.
- C5. `uv run --no-project --with pytest python -m pytest tests -q` exits 0,
  `python3 devtools/build_plugins.py --check` exits 0, and
  `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict`
  exits 0.
- C6. `README.md`, `docs/adopt.html`, `examples/*.devtools.toml` and
  `skills/adopt-devtools/SKILL.md` describe the new behaviour, and every capture that
  shows a changed command is from a real run.
- C7. A close record, after the close review.

## 0. Binding design rules

Every spec discharges each rule below by name, or argues in one sentence that it does not
apply. The rules are the project's seven standing design rules (`.devtools/project.md`,
"Standing design rules") and the five that follow.

- **S0.1 Today's lines and exits stay.** Every line `apply` and `check` print on main is
  printed unchanged for the same input, and exits 0 to 4 keep their meaning. A new line
  comes after the command's own summary line, and only when there is something to say.
  - *Prevents:* a project's script or CI that reads today's output or exit breaking on an
    update of dev-tools.
  - *Discharged by:* naming each existing line the phase's code path can reach, and the
    test that compares it with main's.
- **S0.2 The checkout is read, never changed.** The sync runs `git fetch` and commands that
  read. It never merges, pulls, checks out, resets or writes a file in the dev-tools
  checkout. In the project it writes what `apply` writes today.
  - *Prevents:* a sync that moves the branch or the files of a checkout someone is working
    in.
  - *Discharged by:* naming every `git` command the phase adds, and the test that compares
    `HEAD`, the branch and `git status` before and after.
- **S0.3 A report is rows before it is lines.** The code that decides what to report
  returns data; one function prints it. No code reads back what the sync printed, and a
  test checks the rows as well as the lines.
  - *Prevents:* code fitted to its own output (`standing-rules.md`, "Code fitted to its
    examples").
  - *Discharged by:* naming the function that returns the rows and the one that prints.
- **S0.4 A test brings its own upstream.** No test reaches the network, and no test's
  result depends on the branch or the age of the checkout it runs in. A test that needs
  an upstream builds one with `git init` under `tmp_path`. In the suite the repository's
  own checkout is never an implicit source for `check`, and is always read as it is: one
  autouse fixture in `tests/test_sync.py` sees to both, and the tests of those two
  defaults call the real functions with folders of their own.
  - *Prevents:* a suite that exits 0 on a branch and 1 on a `main` that is behind, and a
    test of the repository's files that silently reads another commit's.
  - *Discharged by:* naming each test that runs `git`, and where its repository comes
    from.
- **S0.5 `sync.py` stays one file on the standard library.** It is run from a checkout
  by a project that installed nothing.
  - *Prevents:* a sync that needs an install step.
  - *Discharged by:* naming every import the phase adds.

## 1. Scope, sources and authority

**Scope:**

- what `apply`, `check` and `survey` say about units the project does not take;
- one new key in `.devtools.toml`, `declined`, and one new field in the receipt,
  `shipped`;
- `check` against a dev-tools source, and `check --strict`;
- which commit of dev-tools `apply`, `check`, `compare` and `survey` read (phase 2);
- the pages, examples and the one skill that describe these.

**Sources** (read for this plan):

| Source | What it gives |
|---|---|
| The brief of 2026-11-23 from the session that started this one, written after the owner chose to fix the tool | The three silences, what the tool should do, and what done looks like. The design was left to this plan, with each decision to be stated with its reason |
| Owner, 2026-11-23, this session | "shouldn't the sync skill run an install of the latest dev-tools?", then "Yes, by default" (D8) |
| `.devtools/project.md`, "Which lane a piece of work takes" | A change to a format a project's files depend on (`.devtools.toml`, the receipt), or to what a gate refuses, takes the evidence lane as a milestone. Where the owner has not said which lane, propose one and wait |
| `.planning/PROJECT.md` | "A project that synced takes no dependency on this repository"; "A script a project runs is tested here" |
| `CONTRIBUTING.md`, "What makes a change easy to accept" | The standing design rules |
| `devtools/sync.py`, `tests/test_sync.py`, `examples/`, `README.md`, `docs/adopt.html`, `skills/adopt-devtools/SKILL.md` at main `811b4a3` | What the tool does and what is written about it today (section 3, "Baseline") |
| `.devtools/components/`, searched five times with the built `components_index.py` | What exists: the component `sync.copies`, and in it `shipped_units`, `source_identity`, `survey`, `plan` |

**Authority.** This plan is a proposal written by the agent. Nothing in it is approved
until the plan gate is recorded. The brief named no lane and the owner has not ruled one,
so no code is written before the gate. A merge, a release tag and anything posted to
GitHub need the owner each time (`.devtools/project.md`, "What needs the owner each time").

## 2. Contract proposal and product behaviour

Words used below. A **unit** is what `shipped_units` returns today: each skill folder, the
`agents` folder, and each script under `skills/` that stands alone. The config **takes** a
unit when a `[[sync]]` entry's `source` is the unit, lies inside it, or contains it.

### Phase 1: what the sync says about units, and `check` against a source

**A unit is reported in one of three ways, or not at all.**

| The unit is | `apply`, `apply --dry-run`, `check` | `survey` |
|---|---|---|
| taken | nothing | as today |
| covered by `declined` | nothing | listed, marked declined |
| under a workflow folder (`skills/<workflow>/`) the config takes nothing from (D3) | nothing | listed, as today |
| not taken, and **named** by a file this config delivers | reported on every run, with the first file that names it and how many more do | listed, marked with that file |
| not taken, and **new**: absent from the receipt's `shipped` list | reported until the next `apply` writes a receipt | listed, as today |
| not taken, none of the above | nothing | listed, as today |

- **Named** (D2). A delivered file names a unit when its text holds one of the unit's
  names between backticks (`` `review-pr` ``) or as a folder in a relative path
  (`../review-pr/`). A skill's name is its folder's; the `agents` unit has one name per
  file, without the extension; a script's name is its file name. The text read is what
  the config delivers, so a file under `exclude` names nothing. A name is satisfied when
  any taken unit has it: the two workflows each ship a `process-phase`, and a project has
  one.
- **New.** `apply` writes the sorted sources of every unit of the source it read into the
  receipt, as `shipped`. On the next run a unit that is not in that list is new. A receipt
  written before this change has no `shipped`: on that one run every unit that is not
  taken, not declined and not under an untaken workflow folder is listed once, with a
  line saying why (D7). Without a receipt nothing is new.
- **`declined`.** A top-level key of `.devtools.toml`: a list of paths in dev-tools.

  ```toml
  declined = ["skills/milestone/review-pr", "agents"]
  ```

  An entry covers the unit at that path and every unit under it. Exit 2, as for any
  configuration error, when it is not a list of relative paths, or when it covers a unit
  the config also takes. An entry that covers no unit dev-tools ships is a warning on
  standard error and changes no exit: dev-tools may have retired the unit.

**`check` reads the dev-tools source when it has one** (D5). The receipt comparison runs
first, exactly as today. Then, when `sync.py` sits in a dev-tools checkout or `--source`
names one, `check` reads `.devtools.toml` and prints, each only when it applies:

- one line when an `apply` from that source would change files: the receipt's commit, the
  source's commit, and how many files would be created, updated and deleted;
- the unit report above.

`check --receipt-only` does the receipt comparison alone, as `check` does today, and so
does a `sync.py` that is not in a checkout. If the config cannot be read or is invalid,
the receipt verdict stands and one warning says the comparison was not made.

**Exits.**

| Command | Exit | Meaning |
|---|---|---|
| `apply`, `apply --dry-run` | 0, 2, 3, 4 | As today. A unit report never changes the exit |
| `check` | 0, 1, 2 | As today. The new lines are notes |
| `check --strict` | 1 | Drift, as today. It wins over 5 |
| `check --strict` | 5 | No drift, and at least one of: an `apply` would change a file; a named unit is not taken; a unit is new; the comparison with the source could not be made (D6, D13) |

**What it prints** (a sketch: the spec fixes the wording, and the record pastes real
output):

```
$ sync.py check --project .
60 managed file(s), 0 problem(s)
behind: synced from dev-tools c9648dd, this source is 811b4a3: an apply would update 22 file(s)
not taken, and named by a file this project has:
  skills/milestone/review-pr
      named by .claude/skills/handle-issue/SKILL.md and 3 more file(s)
to take a unit, add a [[sync]] entry; to stop hearing of it, add its path to `declined` in .devtools.toml
```

### Phase 2: the sync reads the latest dev-tools

`apply`, `compare`, `survey` and `check` (when it reads a source) decide once, in one
function, which files to read. `compare` must read what `apply` would, or it shows
another update than the one that arrives.

| The source is | What is read | What is said |
|---|---|---|
| not a git checkout of its own (a copy, a folder inside another repository) | the folder | nothing, as today |
| on a detached `HEAD`, or a branch with no upstream | the checkout | nothing: a tag checked out on purpose is how a project pins dev-tools |
| a branch whose upstream is configured but has no ref after the fetch (the remote branch was deleted, or never fetched) (r1 F5) | the checkout | one warning: the upstream is named and was not found, so the checkout is delivered as it is |
| level with its upstream after the fetch, or only ahead of it | the checkout | nothing |
| behind its upstream, with no commit of its own and nothing uncommitted | the upstream commit, read from git's tree (`ls-tree`, `cat-file`) into a temporary folder that is removed at exit (D9). *Repaired at the close, 2026-11-23, from `003-phase-2.md` (phase 2 r1 F1, F3): `git archive` drops `export-ignore` paths and applies `tar.umask`. Prior wording: "read with `git archive` into a temporary folder that is removed at exit (D9)".* | one line: how far behind, which commit is read, and that the checkout is not changed |
| behind its upstream, with commits of its own or uncommitted changes | the checkout | a warning before anything is written: how far behind, and that it is delivered as it is |

- **The fetch.** `git fetch <the upstream's remote>`, with no prompt for credentials and a
  time limit. If it fails, one warning says so and the rule above is applied to the refs
  the checkout already has.
- **`--as-is`** (D10) reads the checkout as it is and starts no fetch. If the refs already
  fetched show it behind, the warning is still printed.
- **The receipt** records the commit that was read.
- **The tool itself.** When the upstream commit's `devtools/sync.py` differs from the one
  running, one line says that the tool is older than the files it read and that `git
  pull` in the checkout updates it.

## 3. Dependencies and artifact homes

### Baseline, observed on 2026-11-23

Observed evidence, from a scratch project outside the repository. Its config takes
`skills/components`, `skills/dev-handoff`, `skills/dev-takeover`, `skills/handle-issue`,
`skills/milestone/process-milestone`, `skills/milestone/process-phase` and
`skills/milestone/start-milestone`, each to `.claude/skills` and `.codex/skills`. It was
applied from a clone of dev-tools at `c9648dd`, then read with `devtools/sync.py` at
`811b4a3`.

| Command, at `811b4a3` | Printed | What is wrong |
|---|---|---|
| `check --project .` | `60 managed file(s), 0 problem(s)`, exit 0 | The project is 22 files behind and reads as clean |
| `apply --project . --dry-run` | 22 `update:` lines, then `dry run: {"keep": 38, "update": 22}`, exit 0 | Nothing names `skills/milestone/review-pr`, which the config does not take |
| `grep -rl review-pr .claude` | `handle-issue/SKILL.md`, `process-phase/references/review-tool.md` | Two delivered files name a skill the project does not have |
| `survey --project .` | Under "Shipped, with no counterpart here": `skills/milestone/review-pr`, `skills/phase/phase-tests`, `skills/phase/process-phase`, `agents`, `skills/phase/pytest/phase_selection.py` | The one unit the project lacks is listed with four it is right not to take |

A prototype of the "named" rule, run over the same config and over both example configs
at `811b4a3` (not committed; phase 1 writes it with tests):

| Config | What the rule reports |
|---|---|
| The scratch project | `skills/milestone/review-pr`, named by 4 files (2 in each skills folder). Nothing else |
| `examples/milestone-project.devtools.toml` | `skills/components`, named by 3 files. Nothing else (D11) |
| `examples/phase-project.devtools.toml` | Nothing. Three milestone skills are named by `handle-issue` and `dev-handoff`, and all three are under a workflow folder the config takes nothing from (D3) |

Inherited claims, not observed here: the brief's "62 managed file(s)" and "21 files to
update" for the real project, and that the owner's main checkout was 54 commits behind
`origin/main`.

**What `sync.py` does today.** `apply` and `compare` read the working tree of the folder
`--source` names (default: the checkout that holds `sync.py`). `source_identity` records
`git rev-parse HEAD` and whether the taken paths have uncommitted changes. Nothing
fetches, and nothing compares `HEAD` with an upstream. `check` takes no `--source` and
reads only the receipt. `survey` is the only command that lists units not taken.

**Five tests sync from the real checkout**, with no `--source`: they write an example
from the repository as the project's config and run `apply` (one also `survey`, one also
`check`):

- `test_the_gsd_history_line_says_whether_the_milestone_skills_are_synced_and_where_records_go`;
- `test_the_milestone_example_applies_as_it_is`;
- `test_review_pr_finds_process_phase_beside_it_in_the_milestone_example`;
- `test_both_examples_deliver_handle_issue_and_it_passes_the_skill_check` (once per
  example);
- `test_both_examples_deliver_the_handoff_skills_with_the_script_they_share` (once per
  example).

Phase 2 would make these fetch, and read another commit on a `main` that is behind.
Every other test passes `apply` a source built under `tmp_path`, which is not a git
checkout, but the file runs plain `check` in 10 places, which under D5 would read the repository's
own checkout as its source. The autouse fixture of S0.4 keeps both away from every
existing test without editing one (section 6, K3).

**The suite on this machine**, at `811b4a3`, before any change:
`uv run --no-project --with pytest python -m pytest tests -q` printed
`350 passed in 147.44s (0:02:27)` and exited 0. `python3 devtools/build_plugins.py
--check` exited 0. The output lives outside history.

### What the code depends on

The standard library and the `git` command, as today. *Repaired at the close,
2026-11-23, from `003-phase-2.md`: phase 2 adds `shutil` and reads the upstream's tree
with `git ls-tree` and `git cat-file --batch`. Prior wording: "Phase 2 adds `tarfile`
and `tempfile` (already imported) to read `git archive` output."*

### Artifact homes

| Artifact | Home |
|---|---|
| Plan, specs, review rounds | `.planning/milestones/sync-reports/notes/` |
| Records | `.planning/milestones/sync-reports/NNN-<scope>.md` |
| The tool | `devtools/sync.py` |
| Its tests and their fixture projects | `tests/test_sync.py`, built under `tmp_path`. No test names or reads a real downstream project |
| The component entry | `.devtools/components/`, regenerated with `write` after each change to `sync.py` |
| Pages and examples | `README.md`, `docs/adopt.html`, `examples/milestone-project.devtools.toml`, `examples/phase-project.devtools.toml`, `skills/adopt-devtools/SKILL.md` |

### Phase dependencies

| Phase | Depends on |
|---|---|
| 1 (units, `check` against a source) | the plan gate |
| 2 (the latest dev-tools) | phase 1's code: `check` against a source is where "behind" is printed, and phase 2 changes which commit that source is |
| Close | phase 2 |

## 4. Phases, deliverables, named criteria and inherited residuals

### Phase 1: the sync names what a project has not taken, and `check` can say it is behind

*Outcome:* the three silences of the baseline are closed for a checkout that is current.
No command reaches the network.

*Deliverables:*

- in `devtools/sync.py`: the unit report (rows, then lines), `declined`, the receipt's
  `shipped`, `check --source`, `check --receipt-only`, `check --strict`, and the marks in
  `survey`;
- the tests in `tests/test_sync.py`, with the observed case as one of them;
- `examples/milestone-project.devtools.toml` and `examples/phase-project.devtools.toml`:
  `declined`, shown and explained (D11);
- `README.md`, `docs/adopt.html` and `skills/adopt-devtools/SKILL.md`: what `apply` and
  `check` now say, the key, the option and exit 5;
- `.devtools/components/`, regenerated.

*Criteria:*

- P1.1. The observed case (C1).
- P1.2. A unit covered by `declined` is in no report of `apply` or `check`, and `check
  --strict` exits 0 when it was the only thing to report.
- P1.3. A unit under a workflow folder the config takes nothing from is in no report,
  though a delivered file names it.
- P1.4. A unit added to the source after the receipt was written is reported as new by
  `apply --dry-run` and `check`, and by no run after the next `apply`.
- P1.5. A receipt without `shipped` gets the one-time list, and the receipt `apply` then
  writes ends it.
- P1.6. `check --receipt-only` (C3), and every existing test (C2).
- P1.7. A `declined` entry that covers a taken unit exits 2 and writes nothing.
- P1.8. Both examples apply as they are, and `apply` on each prints no unit report.

*Spec:* `notes/phase-1-spec.md` (draft).

### Phase 2: the sync reads the latest dev-tools

*Outcome:* an `apply` from a checkout that is only behind delivers the upstream's files,
and every other state of the checkout is either delivered as it is or said aloud.

*Deliverables:*

- in `devtools/sync.py`: one function that resolves the source for `apply`, `compare`,
  `survey` and `check`; the fetch; the read of the upstream commit; `--as-is`; the lines
  of section 2;
- the tests, each with an upstream built under `tmp_path`, and the autouse fixture of
  S0.4 extended so the repository's own checkout is read as it is;
- `README.md`, `docs/adopt.html` ("Updates that respect your changes") and
  `skills/adopt-devtools/SKILL.md` (its step that names the dev-tools commit): the sync
  fetches, what it reads when the checkout is behind, and `--as-is`;
- `.devtools/components/`, regenerated.

*Criteria:*

- P2.1. Behind only: the upstream's files are delivered, the receipt holds the upstream
  commit, and the checkout's `HEAD`, branch and `git status` are as before (C4, S0.2).
- P2.2. Behind with a commit of its own, and behind with an uncommitted change: the
  checkout is delivered as it is, and the warning is printed before any file is written.
- P2.3. Level, ahead only, detached, no upstream, and not a checkout: delivered as today,
  with no new line.
- P2.3b. An upstream that is configured and has no ref: delivered as it is, with the one
  warning, exit 0 (r1 F5).
- P2.4. A fetch that fails: one warning, exit 0, and the rule applied to the refs already
  there.
- P2.5. `--as-is`: no `git fetch` is started, and a checkout that is behind is delivered
  as it is.
- P2.6. `compare` and `apply --dry-run` name the same files for the same checkout state.
- P2.7. The source folder inside another repository is not fetched.

*Spec:* written when phase 1 is recorded (an outline until then).

### Close

The close review (the review helper with `--subject close`), the question sweep, plan
repairs and the close record (C7).

**Inherited residuals:** none. `component-index`, the project's other milestone, assigns
nothing to this one. It is not closed yet (its close record is still to be written), and
this milestone changes none of its files except `.devtools/components/`, which its phase 4
test requires to be current after any change to `sync.py`.

## 5. Documentation, skill and compatibility surfaces

| Surface | Phase | Note |
|---|---|---|
| `.devtools.toml`: `declined` | 1 | New and optional. A `sync.py` older than this change refuses the key with `unknown top-level keys: ['declined']`, exit 2: loud, not silent. The pages say which change added it |
| The receipt: `shipped` | 1 | New. An older `sync.py` reads only `files` and `source` and ignores it. A receipt without it is read as section 2 says |
| `check`'s output | 1 | Run from a checkout, it can print more lines than today, after the summary line (S0.1). `--receipt-only` gives today's output |
| Exit 5 | 1 | Only with `--strict`, which no caller passes today |
| `apply`, `compare`, `survey` from a checkout that is behind | 2 | They read the upstream commit, where today they read the old files. This is the change the owner ruled (D8) |
| `README.md`, "How a project takes it" | 1, 2 | `check` "needs only the project" becomes true of `--receipt-only`; the fetch |
| `docs/adopt.html` | 1, 2 | The table "What the sync does" gains rows; new captures come from real runs on a scratch project. The existing captures show commands whose lines do not change (S0.1), and each is checked against a real run before it is left as it is |
| `skills/adopt-devtools/SKILL.md` | 1, 2 | The command table and the step that names the dev-tools commit. The skill is read from the checkout and is in no plugin, so `build_plugins.py --check` and the plugin version are unaffected. If `release_plugins.py status` reports a changed plugin file, the phase bumps |
| `examples/*.devtools.toml` | 1 | `declined`. Both must still apply as they are (P1.8) |
| Both agents | 1, 2 | The one skill changed is read the same way by Claude Code and Codex: it names commands, no plugin path |

## 6. Risks and required controls

| Risk | Control |
|---|---|
| K1. The "named" rule reports a unit that prose mentions in passing, and the report becomes a list nobody reads | The rule is tried on both examples and the scratch project before the gate (section 3): one report in each case where a decision is owed, none elsewhere. `declined` ends a report for good. The phase review's standing check tries inputs the fixtures lack |
| K2. The "named" rule misses a unit named some other way (without backticks, or by a plugin name) | Stated as a boundary in the phase record: the rule finds the two forms the shipped skills use today, counted in section 3. The new-unit report does not depend on it |
| K3. Existing tests start reading the repository's own checkout through plain `check`, fetching it, or reading another commit of it | S0.4: the autouse fixture, written in phase 1 (no implicit source for `check`) and extended in phase 2 (the repository's checkout is read as it is, and a `git fetch` against it fails the test). The defaults themselves are tested by calling the real functions on folders under `tmp_path` |
| K4. A fetch hangs on a credential prompt or a dead network | No prompt (`GIT_TERMINAL_PROMPT=0`), a time limit, and P2.4 |
| K5. The sync changes a checkout someone is working in | S0.2 and P2.1: only `git fetch` writes, and only remote-tracking refs |
| K6. The tool that runs is older than the files it reads, and misreads them | The line of section 2 says so. A config key the old tool does not know is refused with exit 2 |
| K7. A project's CI that runs `check` from a checkout now reaches the network | `--receipt-only` reads no source; `--as-is` reads it without a fetch; a failed fetch is a warning. `check` without `--strict` never changes its exit for any of this |
| K8. `source` inside another repository: `git -C` answers for the outer repository, and a fetch would fetch that one | P2.7: the checkout's top level must be the source folder |
| K9. A capture on the site goes stale without anyone noticing | Section 5: each capture of `apply`, `check` and `survey` is compared with a real run in the phase that could change it, and the record lists which were retaken |

## 7. Out of scope

- Whether a named unit is delivered **beside** the file that names it (a skill taken into
  `.codex/skills` while the file that needs it is in `.claude/skills`). Q1.
- A unit taken for one skills folder and not for another. Q2.
- Running the fetched `sync.py` in place of the one in the checkout. Q3.
- Changing the checkout: a fast-forward, a pull. The owner pulls.
- The plugins: `claude plugin update` already installs the latest release.
- A check of the sync in CI for dev-tools itself. There is no CI.
- `from_gsd.py` and the scripts under `skills/`.

## 8. Execution, approval and review protocol

- **Workflow.** `process-milestone sync-reports`, phase by phase with `process-phase`.
  *Amended 2026-11-23 (o):* with `auto=true`, by the owner's lane ruling: the plan gate,
  each spec's owner gate and the close ruling are delegated approvals, recorded as such.
  The prior wording, kept: "`auto=false` unless the owner says otherwise: the plan gate,
  each spec's owner gate and the close stop for the owner."
- **Branches** (D12). Phase 1 on `claude/sync-report-untaken-and-stale-32f991`, where this
  plan is; phase 2 on a branch cut from phase 1's tip, its pull request based on phase
  1's branch until that merges. One pull request per phase. The plan and the milestone's
  planning files go in with phase 1's.
- **Reviews.** The review helper (`review_tool.py`), with Codex as reviewer:
  `--subject plan` before the plan gate, `--subject phase` over each phase's diff,
  `--subject close` at the close. Rounds follow `review-convergence.md`. A repaired file
  is unreviewed until a later round reads it.
- **Review budget for this plan.** At most two rounds (r1, r2), declared here before
  either has run. The stop rule of `review-convergence.md` ends it earlier.
- **Records.** `001-plan.md` at the plan gate, one per phase, and the close record.
- **Owner actions no delegation covers.** Merging each pull request; a release tag;
  anything posted to GitHub.

## 9. Per-phase verification story, expected results and affected consumers

Commands run from the repository root.

| Phase | Gate command | Expected | Affected consumers |
|---|---|---|---|
| 1 | `uv run --no-project --with pytest python -m pytest tests/test_sync.py -q` | exits 0 | Every project that syncs. `apply` and `check` can print lines they did not; no exit changes without `--strict` |
| 1 | `uv run --no-project --with pytest python -m pytest tests -q` | exits 0 | Same |
| 1 | `python3 devtools/build_plugins.py --check` | exits 0 | Plugin users: no change |
| 1 | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict` | exits 0 | dev-tools' own sessions |
| 1 | By hand, on a scratch copy of the observed-case fixture: the three commands of the phase 1 spec, section 8, "By hand" (`python3 devtools/sync.py apply --project "$SCRATCH/project" --source "$SCRATCH/source" --dry-run`, then `check` and `check --strict` with the same two options) (r1 F6) | The lines of section 2, pasted into the record with their exits (0, 0, 5) | The owner, who reads them |
| 2 | The four commands of phase 1 | exit 0 each | Every project that syncs from a checkout on a branch |
| 2 | By hand, with `$SCRATCH/upstream` a scratch repository and `$SCRATCH/clone` a clone of it one commit behind: `python3 "$SCRATCH/clone/devtools/sync.py" apply --project "$SCRATCH/project" --dry-run`, then `git -C "$SCRATCH/clone" status --short` and `git -C "$SCRATCH/clone" rev-parse HEAD` before and after (r1 F6) | The line that names the commit read; the status and `HEAD` the same before and after | Same |

## 10. Owner decisions and open questions

### Decisions for the plan gate (ruled 2026-11-23: D1 and D8 by the owner, the rest by delegated approval (auto=true), each as proposed)

| # | Question | Readings and their cost | Proposed |
|---|---|---|---|
| D1 | The lane (ruled by the owner, 2026-11-23: "Milestone, auto=true") | **Evidence lane, this milestone:** a plan, specs, records and review rounds for a change of roughly 400 lines of code and tests. **Fast lane:** one tested pull request; `.devtools/project.md` reserves that for changes that touch no format and no gate, and this one adds a config key, a receipt field and an exit | Evidence lane |
| D2 | How the sync knows a file names a unit | **From the delivered text** (backticked name, or a folder in a relative path): nothing to maintain, the report can name the file, and it follows `exclude`; it can miss a name written another way and report a passing mention (K1, K2). **A hand-kept table** in dev-tools of which unit uses which: exact, but it goes stale silently, and cannot name the file | From the text |
| D3 | A workflow folder the config takes nothing from | **Silent in `apply` and `check`:** a milestone project never hears of the phase workflow, and `survey` still lists it. **Reported:** every phase project is told of three milestone skills that `handle-issue` and `dev-handoff` name | Silent |
| D4 | The shape of the opt-out | **`declined`, a top-level list of paths, a folder covering what is under it:** one place, and `declined = ["skills/phase"]` covers units added there later. **A key per `[[sync]]` entry:** there is no entry for a unit that is not taken | The top-level list |
| D5 | Whether plain `check` reads the source | **By default when `sync.py` is in a checkout, with `--receipt-only` to turn it off:** the ordinary `check` says "behind", which is the silence this milestone exists for; callers see extra lines after the summary, never another exit. **Only with `--source`:** today's output for everyone, and the ordinary run stays silent unless every page and skill changes its command. In this session the owner was told plain `check` would stay receipt-only; this proposal differs, so it is put here to be ruled | By default |
| D6 | `--strict`, and its exit | **One option that makes every note fail, exit 5:** a project's CI can tell "a synced file was edited" (1) from "behind, or a unit to decide" (5). **Exit 1 for both:** one fewer code, and CI cannot tell them apart. **No option:** notes can never fail a build | `--strict`, exit 5 |
| D7 | A receipt written before `shipped` existed | **List every unit not taken once:** needs no git, and ends with the next `apply`. **Read the unit list at the receipt's commit from git history:** exact, but fails when the checkout lacks that commit or is not a checkout | List once |
| D8 | Whether `apply` fetches and reads the latest by default | Ruled by the owner on 2026-11-23: "Yes, by default" (o) | Ruled |
| D9 | What "the latest" is read with | **The running tool reads the upstream commit's files:** no fetched code is run, and the checkout is not touched; the tool can be older than the files (K6). **Run the fetched `sync.py`:** always the newest tool, at the cost of running code no one pulled. **Fast-forward the checkout:** updates the tool too, and moves a branch in someone's working checkout | The running tool reads the files |
| D10 | The opt-out of the fetch | **`--as-is`:** no fetch, and the checkout is delivered whatever its upstream says. **`--offline`:** no fetch, but a checkout the old refs show behind still reads the upstream commit, so there is no way to say "exactly these files" | `--as-is` |
| D11 | `examples/milestone-project.devtools.toml` and `skills/components`, which three of its files name | **Decline it in the example, with a comment that says how to take it:** the example delivers what it does today. **Take it:** the example grows a script and its settings | Decline, with the comment |
| D12 | Pull requests | **One per phase, the second based on the first:** two smaller reviews; the fix reaches `main` in two merges. **One for both:** one merge, a larger diff | One per phase |
| D13 | `check --strict` when the config cannot be read | **Exit 5:** a strict check that could not check does not read as clean. **Exit 0 with a warning:** the receipt verdict alone decides | Exit 5 |

### Open questions (carried to the close sweep)

- Q1. A named unit that is taken, but into another folder than the file that names it by
  relative path. The check needs to know which taken unit the path means when two
  workflows ship the same folder name.
- Q2. A unit taken for `.claude/skills` and not for `.codex/skills`: a choice, or an
  omission?
- Q3. Should a checkout that is behind run the fetched tool? It would close K6, and it
  runs code the owner has not pulled.
- Q4 (raised in `002-phase-1.md`). The adopt walk-through frames of `docs/adopt.html`
  come from the demo project `shelf`, which is not in the repository, and were older than
  main's output before this milestone. Retaking them needs the demo project rebuilt.

### Obligation-to-phase map

| Obligation (source) | Phase and gate |
|---|---|
| A unit the config does not take is named on `apply` and `check` (brief) | 1: P1.1 |
| A named unit is reported with the file that names it (brief) | 1: P1.1 |
| A unit the project does not use does not nag; one way to decline in `.devtools.toml` (brief) | 1: P1.2, D4 |
| Decide whether an untaken workflow is reported at all (brief) | 1: P1.3, D3 |
| Units added since the last receipt are called out as new (brief) | 1: P1.4, P1.5 |
| `check` can say the project is behind, given a source; decide option or default (brief) | 1: P1.1, D5 |
| A receipt-only check stays possible (brief) | 1: P1.6, C3 |
| A stale source is visible before anything is written (brief; the brief's "do not reach the network" is replaced by D8) | 2: P2.2, P2.4 |
| `apply` fetches and delivers the latest by default (owner, 2026-11-23) | 2: P2.1 |
| Decide notes, failures and `--strict`; today's exits keep working (brief) | 1: D6, D13, C2 |
| Update the examples, the README, the pages and the adopt skill (brief) | 1 and 2: C6 |
| Tests with their own fixture projects; no real downstream project named (brief) | 1 and 2: section 3, "Artifact homes" |
| A test that reproduces the observed case (brief) | 1: P1.1, C1 |
| The new `apply --dry-run` and `check` run on a scratch copy, their lines pasted (brief) | 1: section 9, by hand |
| A script change comes with a test (standing rule) | 1, 2: `tests/test_sync.py` |
| Rebuild and release under a new version (standing rule) | 1, 2: no plugin file changes; `build_plugins.py --check` exits 0 |
| A wording change says what prompted it (standing rule) | 1, 2: the baseline of section 3 |
| Shared skills stay general (standing rule) | 1, 2: `adopt-devtools` names no project |
| Both agents read the same file (standing rule) | Section 5, last row |
| Captures on the site are real output (standing rule) | 1, 2: K9 |
| The page that describes it is updated too (standing rule) | 1, 2: C6 |
| The component index stays current (`.devtools/project.md`, "Gates") | 1, 2: C5 |
