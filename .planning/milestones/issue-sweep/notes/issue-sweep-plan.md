# Milestone plan: issue-sweep

**Goal.** Eight of the ten open issues are fixed, each with a test that fails without the
fix: the suite tests what it claims (31, 42), one list serves two scripts (41), the
component index tool closes three gaps its own milestone found (44, 45, 46), and the
shipped scripts do what their starter rules and docstrings say (33, 43). The other two
(39, 40) are each left for a milestone of its own, with the reason written down.

**Status.** Closed, 2026-11-23, by delegated approval (auto=true): `006-close.md`, after the
close review (`notes/reviews/close-r1`), with one earlier record corrected in
`005-phase-3-correction.md`. Repaired at the close where the phase records refuted it, each
repair marked `(c1)`. Approved by the owner at the plan gate, 2026-11-23,
with D3 to D11 as proposed (o): `001-plan.md`. Run with `process-milestone issue-sweep
auto`, from 2026-11-23: phases 1 to 3 are recorded in `002-phase-1.md`, `003-phase-2.md`
and `004-phase-3.md`.

- Written with `start-milestone` (the installed dvt-milestone 0.1.3; the scripts run are
  the built copies under `plugins/`, at 0.1.6), on branch
  `claude/open-issues-milestone-43c5a0` at `cecebc6`, which is `origin/main`.
- **Two owner rulings so far (o).** 2026-11-23, the request that started this plan: "plan a
  small milestone to address the open issues", which rules the lane (D2). 2026-11-23, to
  "Rule the plan's scope (D1): eight issues in, with 39 and 40 left for their own
  milestones?": "Yes, eight", which rules D1.
- **Plan gate ruled (o).** 2026-11-23, to "Approve the plan at the plan gate, with D3 to
  D11 as proposed?", offered beside "Run round 2 first": "Approve as proposed". It
  approves the plan and rules D3 to D11 as the table of section 10 proposes. It does not
  rule the phase 1 spec's own decisions, start a phase, or cover a commit, a push, the
  pull request, a merge, a tag or anything posted to GitHub.
- **Plan review, round 1 (r1).** `notes/reviews/plan-r1`, run 2026-11-23 with the review
  helper and `--subject plan`; reviewer Codex, read-only, its default model at effort
  `high`; brief SHA-256
  `80d522f4ec9daa46d0f3b7d39efce53f5cb37a2bbc114e1c03ca14d714120c62`, over 22 files.
  `VERDICT: CHANGES_REQUESTED`, with 5 findings. All 5 were reproduced and repaired,
  marked `(r1 Fn)` at each site: the ledger is `notes/reviews/plan-r1/FINDINGS.md`. **The
  repaired bytes carry no review opinion.** One reviewer is one reviewer.
- **Review budget** (declared before any round, section 8): at most r1 and r2.

  | Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
  |---|---|---|---|---|---|---|
  | r1 | 1 (Codex) | 5 | 0 / 5 (first round) | 3 / 5 | blocking | CHANGES_REQUESTED |

  Round 2 was not run. It was put to the owner with the plan gate, and the owner approved
  the plan instead (above). The repairs are one new decision row (D11), three criteria,
  one gate and two corrected facts; they and the rulings below are unreviewed.
- **A premise of issue 42 is refuted in part (r1 F5).** A test already runs the pytest
  plugin: `tests/test_tools.py::test_plain_pytest_leaves_out_phases_that_are_not_complete`,
  which reaches it through the sync and never names the file, so the issue's `grep` and
  this plan's first draft both missed it. What is left of the issue is in section 2.

**Done when** (the completion predicates; each is a gate with an exit code, or a ruling):

- C1. `tests/test_tools.py::test_suggestions_and_generated_cases_with_newer_gnd` is
  skipped, not failed, when GND refuses `synth --guarded-cases` for want of its `synth`
  extra, and still runs and exits as today when GND has the extra. A test with a fake
  `gnd` that lists the flag and exits 5 holds the guard (issue 31).
- C2. The index entry of the pytest plugin lists the test that already runs it, and
  `tests/test_phase_selection.py` holds the branches that test does not reach and exits 0;
  `components_index.py review` prints `## Components with no tests listed (0)` (issue 42)
  (r1 F5).
- C3. A change to `sync.OTHER_PLANS` changes what `sync.py` and `from_gsd.py` both report,
  shown by a test; every test of `tests/test_from_gsd.py` and `tests/test_sync.py` as it is
  at `cecebc6` exits as it does there, unedited (issue 41).
- C4. The index tool, each with a test: a project can make `--check --strict` fail on a
  baseline file, and the default is as today (issue 46); `changed` does not judge against
  a local base that is behind its remote-tracking branch without saying so (issue 45,
  part 1); an entry marked as reread is not listed under "Descriptions older than their
  code" until its modules change again (issue 45, part 2); with `count_extra_dirs`,
  `review`'s same-name group reads the counted modules (issue 44).
- C5. For each plugin, `rules_check.py init` then `rules_check.py test` in a new project
  exits 0 and prints `0 wrong` (issue 33).
- C6. The four docstrings of issue 43 say what their code does, and a settings file that
  cannot be used exits as D10 rules and, for `phase_tool.py`, prints what D11 rules, with a
  test per script. The three scripts that are clean under the linter of pull request 34
  stay clean (P3.6) (r1 F1, F2).
- C7. `uv run --no-project --with pytest python -m pytest tests -q` exits 0,
  `python3 devtools/build_plugins.py --check` exits 0, and
  `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict`
  exits 0.
- C8. Every page and skill that describes a changed behaviour says the new one
  (section 5), and dev-tools' own "no baseline" gate is one command.
- C9. A close record, after the close review, that names for each of the ten issues what
  became of it.

## 0. Binding design rules

Every spec discharges each rule below by name, or argues in one sentence that it does not
apply. The rules are the project's seven standing design rules (`.devtools/project.md`,
"Standing design rules") and the four that follow.

- **S0.1 With default settings, today's lines and exits stay.** A project that changes no
  setting and passes no new option sees the lines and the exit it sees at `cecebc6`,
  except where a decision of section 10 says otherwise and names the line.
  - *Prevents:* a project's gate changing its verdict on an update of dev-tools.
  - *Discharged by:* naming, for each changed command, the test that runs it with the
    default settings and compares its exit and lines.
- **S0.2 A shipped script stands alone.** No script under `skills/` imports another. A fix
  that six scripts need is made in each. (`devtools/` scripts run from a checkout and may
  load one another by path; `sync.py` itself stays one file on the standard library.)
  - *Prevents:* a synced copy that fails for want of a file the project did not take.
  - *Discharged by:* naming every import or load the phase adds, and where it is.
- **S0.3 A new test is seen to fail.** A test of a fix is run against the code before the
  fix and its failure is pasted into the record. A test of code that does not change
  (issue 42) is run against a scratch copy with one line broken, once per branch it
  claims to hold.
  - *Prevents:* a test that cannot fail (`standing-rules.md`, "A declared branch with no
    case that can fail it").
  - *Discharged by:* naming, for each new test, the run that showed it red.
- **S0.4 An issue is closed by the owner's merge.** The pull request's description names
  the issues it closes. No comment, label or close is posted for this milestone without
  the owner's word for it.
  - *Prevents:* an issue closed before its fix is on `main`, or by nobody the project
    answers to.
  - *Discharged by:* the record listing the issues the phase's commits fix, and saying
    that nothing was posted.

## 1. Scope, sources and authority

**Scope:** issues 31, 33, 41, 42, 43, 44, 45 and 46 of vasiloglou/dev-tools, as open on
2026-11-23. Issues 39 and 40 are read, and left out (section 7; D1, ruled).

**Sources** (read for this plan):

| Source | What it gives |
|---|---|
| Owner, 2026-11-23, this session | "plan a small milestone to address the open issues": the lane, and "small" |
| The ten open issues, read with `gh issue view` on 2026-11-23 (31, 33, 39 to 46) and kept as read in `notes/issues-2026-11-23.md`; none has a comment | What is wrong, what is asked for, and for 43, 45 and 46 the readings to choose between |
| `.planning/milestones/component-index/007-close.md`, "The open-questions sweep" and "Proposed issues" | Issues 39 to 46 are its P1 to P8, in order (Q1, Q3, Q7, Q10, Q12 to Q15). Issue 33 is its Q9. P2 is called "a milestone, not a fix"; P3, P4 and P5 "fast-lane fixes" |
| `.planning/milestones/sync-reports/004-close.md`, question sweep | Q1 to Q4 are residuals or deferred to the owner. No issue carries them, and this plan takes none |
| `.devtools/project.md` | Lanes, gates, the review instrument, the standing rules, what needs the owner |
| `.planning/PROJECT.md`, `AGENTS.md`, `CONTRIBUTING.md` | What a change has to keep true; the words; how a change reaches `main` |
| The code at `cecebc6`: `skills/components/scripts/components_index.py` and `rules_check.py`, `devtools/sync.py` and `from_gsd.py`, `skills/phase/pytest/phase_selection.py`, the four scripts of issue 43, `tests/test_tools.py`, `tests/test_plugins.py`, `tests/test_own_index.py` | Whether each issue still holds, and what a fix touches (section 3, "Baseline") |
| `.devtools/components/`, searched seven times and reviewed once with the built `components_index.py` | What exists (section 3, "What the index says") |

**Authority.** This plan is a proposal written by the agent. The owner asked for a
milestone, which rules the lane, ruled which issues are in (D1), and approved the plan
with D3 to D11 as proposed (the plan gate, 2026-11-23). No code is written before the
phase's owner gate. Committing, pushing, the pull request, a merge, a release
tag and anything posted to GitHub need the owner each time.

## 2. Contract proposal and product behaviour

What each issue's fix does, as proposed. A phase's spec fixes the wording and the exact
surface; the decisions are in section 10.

### Phase 1: no product behaviour changes

| Issue | Today | After |
|---|---|---|
| 31 | The test is skipped only when `gnd synth --help` lacks `--guarded-cases`. A GND without the `synth` extra lists the flag and refuses at run time, and the test fails | The test also skips when `rules_check.py test` reports that refusal: exit 5 and the sentence that names the extra. Any other failure of `synth` still fails the test |
| 42 | One test runs the plugin, through the sync: plain `pytest`, `--phase 2` and one named file, each judged by the count in pytest's last line. No file under `tests/` names the plugin, and its index entry lists no test and says none runs it (r1 F5; prior wording: "No test names `phase_selection.py`") | The entry lists that test. A new test file holds the branches it does not reach (an inserted phase, a named folder and node id, the two configuration options, no `STATE.md`, the plugin beside a `conftest.py`) and checks which tests are kept, not how many (phase 1 spec, D5) |
| 41 | `OTHER_PLANS` and the walk over it are written out in `sync.py` and in `from_gsd.py` | `from_gsd.py` loads `sync.py` and uses its list and its walk. What either script prints is unchanged |

### Phase 2: the component index tool

| Issue | Today | After |
|---|---|---|
| 46 | `--check --strict` excuses every module a baseline file names, always | A setting, `allow_baseline` (default `true`). With `false`, `--check --strict` prints one line naming the baseline file and exits 1 while it exists, and `stats --write-baseline` refuses to write one (D5) |
| 45, part 1 | `changed --base main` uses the local `main` when there is one, however old | When the base names a local branch that is strictly behind its remote-tracking branch, `changed` compares with that branch and says so in one line. A base that is level, ahead or diverged, a commit, and a branch with no upstream are read as today (D6). `facts --base` resolves its base with the same function, and `rules_check.py check --base` reads those facts, so both follow the same rule: `facts` still writes one JSON document and nothing else on standard output, and its line goes to standard error (r1 F3) |
| 45, part 2 | An entry is dated by the last edit of its `does`, `verbs` or `flow` line | An optional line, `- reread: <text>`, is dated the same way: by the commit that last changed it. Editing it brings the entry's date forward and changes nothing the entry says (D7) |
| 44 | With `count_extra_dirs`, `review`'s same-name group still reads `package_dir` alone | With the setting on, the groups that do not come from the import graph read `counted_modules`: the same name in two or three components, modules with no docstring, components over 12 modules, and the summary's module count. With it off, as today (D8) |

### Phase 3: scripts that do what they say

| Issue | Today | After |
|---|---|---|
| 33 | Where the phase tool is not installed, `rules_check.py test` calls the starter rule about plans `wrong` twice, and exits 1 | `test` leaves out a rule marked `"about": "plans"` when the phase tool is not there, prints one `skip:` line that names the rule and the reason, and judges the rest. The rule is also left out of what `gnd synth` is given. `init` writes what it writes today (D9) |
| 43 | A settings file a script cannot use ends it with the message on standard error and exit 1, the code each docstring gives to "a check found something" or "domain failure" | The message is the same and the exit is 2, in every script under `skills/` that reads a settings file (D10), except `coder_pool.py` (c1, below). The four docstrings say what the code does: `phase_tool.py` (what it prints then is D11's to rule: proposed, one JSON envelope with `"ok": false` under `--format json`, for `status` too, and the docstring says `status` exits 0 unless the settings file cannot be used) (r1 F1; prior wording: "the envelope and `status` hold once the settings are read"), `review_tool.py`, `from_gsd.py` ("it never calls git to change anything"), `coder_pool.py` ("when `claude` is on PATH") |

## 3. Dependencies and artifact homes

### Baseline, observed on 2026-11-23 at `cecebc6`

Observed on this machine (macOS, Python 3.14.4, GND 0.4.0 with its `synth` extra).

| Issue | Command | Observed |
|---|---|---|
| all | `uv run --no-project --with pytest python -m pytest tests -q` | `447 passed in 196.83s (0:03:16)`, exit 0. The output lives outside history |
| all | `python3 devtools/build_plugins.py --check` | exit 0 |
| all | `python3 devtools/release_plugins.py status` | `version in the tree: 0.1.6`, `released: 0.1.2`, `0.1.6 is ready`, exit 1 |
| 31 | the suite above | The test passes here, because this GND has the extra. **Not reproduced**: the failure is the issue's claim, for a GND installed without `[synth]` |
| 33 | `components_index.py init`, `rules_check.py init`, `rules_check.py test`, with each plugin's copy, in a new project | dvt-milestone: `2 wrong`, exit 1, and a second symptom the issue does not name: `note: gnd synth --guarded-cases built no cases (exit 3): ERROR: model validation failed: … undeclared fact type 'task_touches_component'`. dvt-phase: `0 wrong`, exit 0 |
| 41 | both scripts loaded, `sync.OTHER_PLANS == from_gsd.OTHER_PLANS` | `True`, 8 entries |
| 42 | `sed -n 1879,1894p tests/test_tools.py`, after r1 F5 | `test_plain_pytest_leaves_out_phases_that_are_not_complete` runs pytest in a project the sync gave the plugin as `conftest.py` (`examples/phase-project.devtools.toml:70`), and asserts `2 passed, 1 deselected`, then `1 passed, 2 deselected` for `--phase 2`, then `1 passed` for a named file |
| 42 | the plugin as `conftest.py` of a scratch project with a complete phase 1, an open phase 2, an inserted phase 6.1 and a unit test, under pytest 9.2.0 | Eight runs, each as the docstring says: plain, `--phase 02`, `--phase 1`, `--phase 6.1`, a named file of the open phase, `tests`, `tests/acceptance`, `tests/unit --phase 02`. No defect seen |
| 43 | a settings file with an unknown key, then `review_tool.py status .`, `phase_tool.py --format json status`, `components_index.py --check` | Each prints `…: unknown setting(s): nope` and exits 1. The third is not one of the issue's four |
| 44 | `components_index.py review` | `## The same public name in two or three components (a duplicate?) (0)`, and the summary says `4 module(s)` of the 12 |
| 45, part 1 | `changed --base main`, then `changed --base origin/main`, in this worktree, whose local `main` is 99 commits behind | `changed against main (b685e82): 263 file(s) differ`, then `changed against origin/main (cecebc6): 0 file(s) differ`, before this milestone's files existed |
| 45, part 1 | `facts --base main`, then `facts --base origin/main`, after r1 F3 | revision `b685e82` with 0 rows of `component_has_status`, then `cecebc6` with 12: the stale base gives `rules_check.py check --base` an empty catalog to compare with |
| 43 | `uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml` on `rules_check.py`, `review_tool.py` and `handoff.py`, the three scripts pull request 34 made clean; then on each other script under `skills/`, after r1 F2 | The three: `All checks passed!`, exit 0. `components_index.py`, `phase_tool.py`, `coder_pool.py`, `codex_gate.py` and `phase_selection.py`: exit 1 each. They were never clean and are not held |
| 43 | `grep -l settings.json` over the scripts under `skills/` | Six read a settings file: `rules_check.py`, `components_index.py`, `review_tool.py`, `handoff.py`, `coder_pool.py`, `phase_tool.py` |
| 45, part 2 | `components_index.py review` | Three entries under "Descriptions older than their code": `sync.copies` (5 commits), `handoff.notes` (4), `components.rules` (1) |
| 46 | not run | Read in the code: `write_or_check` reads the baseline whenever the file exists (`components_index.py:961`). The issue's three steps are its claim |

Inherited claims, not observed: issue 31's failure; issue 46's reproduction; issue 44's
"six scripts each define `plugin_root`, `checkout_root` and `load_settings`".

**A premise to check in phase 2.** `review` leaves out a name defined in four or more
modules and only counts it in the group's title. If six scripts define those three names,
the fix for 44 will not list them: it will raise the count in the title. The spec says
which the tests expect.

### What the index says

- Searches (the words, and what came first): "signs of other planning tools":
  `devtools.from_gsd.other_plans` and `devtools.sync.other_plans`; "select acceptance
  tests by phase": `phase.test_selection`; "baseline of unassigned modules":
  `components.index`, `counted_modules`; "files changed since the merge base":
  `components_index.changed` and `base_snapshot`, and also `phase_tool.merge_base`, which
  resolves a base by its own rule, was not read for this plan and is not changed; "starter rules file":
  `rules_check.places`, `vocabulary`; "read a settings file" and "skip a test when an
  optional dependency is missing": nothing that fits (tests are not indexed; `git grep`
  finds `offered`, `REAL_GND` and `fake_gnd` in `tests/test_tools.py`).
- Nothing the milestone builds in a script exists already under another name: every fix
  adapts the function the issue names. One thing did exist and the searches missed it,
  because the index does not hold tests: a test of the pytest plugin (r1 F5; prior
  wording: "Nothing the milestone builds exists already under another name. Every fix
  adapts the function the issue names.").
- **The index is partly stale.** `review` lists 3 of 12 entries as older than their code.
  `sync.copies` was edited by `sync-reports`; the other two were reread at the
  `component-index` close and stayed listed, which is issue 45, part 2. A review of the
  index (the components skill's Review mode) is offered and is the owner's to accept;
  this plan relies on the code it read, not on those three entries.

### What the code depends on

The standard library, `git`, and for `rules_check.py` an installed GND, as today. Phase 1
adds one load by path, of `sync.py` from `from_gsd.py`. No phase adds a dependency.

### Artifact homes

| Artifact | Home |
|---|---|
| Plan, specs, review rounds | `.planning/milestones/issue-sweep/notes/` |
| Records | `.planning/milestones/issue-sweep/NNN-<scope>.md` |
| Tests | `tests/test_tools.py`, `tests/test_from_gsd.py`, `tests/test_plugins.py`, `tests/test_own_index.py`, and one new file, `tests/test_phase_selection.py` |
| The component entries | `.devtools/components/`, edited and regenerated with `write` in each phase |
| Pages and skills | Section 5 |

### Phase dependencies

| Phase | Depends on |
|---|---|
| 1 (tests, one list) | the plan gate |
| 2 (the index tool) | phase 1 recorded: both edit `.devtools/components/COMPONENTS.md` and regenerate its pages |
| 3 (starter rules, docstrings, settings exits) | phase 2 recorded: both rebuild `plugins/` and regenerate the index pages, and phase 3 changes `components_index.py`'s settings exit after phase 2 changed its settings |
| Close | phase 3 |

No phase needs another's code. The order keeps two phases from rewriting the same
generated files at once.

## 4. Phases, deliverables, named criteria and inherited residuals

### Phase 1: the suite tests what it claims, and one list of other planning tools

*Issues:* 31, 42, 41. *Outcome:* three gaps in the tests and in `devtools/` are closed,
and nothing a project runs behaves differently.

*Deliverables:*

- `tests/test_tools.py`: the guard, the fake `gnd` able to refuse `synth`, and the tests
  of the guard;
- `tests/test_phase_selection.py`, new;
- `devtools/from_gsd.py`: its own list and walk replaced by `sync.py`'s; a test in
  `tests/test_from_gsd.py`;
- `.devtools/components/`: `phase.test_selection` lists its test; `sync.copies` and
  `migrate.from_gsd` say how they are related; regenerated.

*Criteria:*

- P1.1. With a fake `gnd` that lists `--guarded-cases` and exits 5 naming the extra,
  `rules_check.py test` exits 0 with its `note:` line, and the guard skips (C1).
- P1.2. The guard does not skip for any other failure of `synth`.
- P1.3. The plugin's branches each have a case, in the existing test or the new file:
  plain, `--phase NN`, an inserted phase, a named path, the two configuration options, no
  `STATE.md` (C2).
- P1.4. One list (C3).
- P1.5. `review` prints 0 for "Components with no tests listed" and for "The same public
  name in two or three components".
- P1.6. No file under `plugins/` changes: `build_plugins.py --check` exits 0 and
  `release_plugins.py status` prints what it prints in the baseline.

*Spec:* `notes/phase-1-spec.md` (draft).

### Phase 2: the index tool can refuse a baseline, name a stale base, mark a reread, and review every counted module

*Issues:* 46, 45, 44. *Outcome:* dev-tools' own gates stop working around its own tool.

*Deliverables:*

- `skills/components/scripts/components_index.py`: the setting `allow_baseline`; the base
  resolution of `base_snapshot` (which `changed` and `facts --base` share); `reread` among
  the fields `entry_commits` dates and among the fields that may appear once; the groups
  of `review` that read `counted_modules`;
- tests in `tests/test_tools.py`, where the index tool's tests are, and
  `tests/test_own_index.py` using the setting instead of testing for the file;
- `.devtools/components_index.settings.json`: `allow_baseline: false`;
  `.devtools/project.md`: the gate rows and the plugin version its note names;
- `skills/components/SKILL.md`, `references/build.md`, `references/review.md` and
  `docs/components.html`: the setting, the line `changed` prints, the `reread:` line;
- the plugins rebuilt under a new version (D4), and the index regenerated.

*Criteria:*

- P2.1. `allow_baseline: false` and a baseline file: `--check --strict` exits 1 and names
  the file; `stats --write-baseline` writes nothing and exits 1. Without the setting, a
  project with a baseline exits as today. *Repaired at the close, 2026-11-23 (c1), from
  `003-phase-2.md` (phase 2 spec D1: the script exits 1 for every refusal). Prior wording:
  "writes nothing and exits 2".*
- P2.2. A local base strictly behind its remote-tracking branch: the summary line names
  the remote-tracking branch and its commit, and one line before it says why. Level,
  ahead, diverged, no upstream, and a commit given as the base: today's lines.
- P2.2b. With the same stale local base, `facts --base main` writes the document that
  `facts --base origin/main` writes, its standard output parses as JSON with nothing
  before or after it, and `rules_check.py check --base main` judges against that base
  (r1 F3).
- P2.3. Nothing fetches: no `git fetch` is started by any command.
- P2.4. An entry whose `reread:` line was committed after the last commit to its modules
  is not listed as older than its code; after a later commit to a module it is listed
  again. A `reread:` line written twice in one entry is refused, as `does` is.
- P2.5. With `count_extra_dirs` on and two components in an extra folder that define one
  name, the same-name group lists it; with the setting off it does not.
- P2.6. dev-tools' own check for "no baseline" is `--check --strict` alone, and
  `tests/test_own_index.py` holds it through the setting.

*Spec:* written when phase 1 is recorded (an outline until then).

### Phase 3: starter rules that pass where they are written, and scripts that exit as they say

*Issues:* 33, 43. *Outcome:* a dvt-milestone project's first `rules_check.py test` exits
0, and a broken settings file is told apart from a finding by its exit.

*Deliverables:*

- `skills/components/scripts/rules_check.py`: `test` and what it gives `gnd synth` leave
  out a plan rule when the phase tool is absent, and say so;
- a test in `tests/test_plugins.py` that runs `init` then `test` with each plugin's copy;
- the settings exit in each script under `skills/` that reads a settings file (the spec
  lists them; three are observed in section 3), with one test per script;
- the four docstrings of issue 43, and `devtools/from_gsd.py`'s;
- `docs/rules.html` and `skills/components/references/rules.md` where they describe
  `test`; any skill sentence that gives exit 1 a meaning a settings error had;
- the plugins rebuilt, the index regenerated, and the entries' `notes:` that quote the
  wrong docstrings corrected.

*Criteria:*

- P3.1. For each plugin: `init`, then `test`, exits 0 with `0 wrong` (C5). In
  dvt-milestone the `skip:` line names `plan_names_the_components_it_touches`.
- P3.2. A rule that names an unknown fact type and is not marked as about plans is still
  `wrong`.
- P3.3. With the phase tool present, `test` prints what it prints today.
- P3.4. For each script with a settings file: an unknown key exits as D10 rules, with the
  message on standard error, for every command including `phase_tool.py status`.
- P3.4b. `phase_tool.py --format json status` with such a settings file prints what D11
  rules. As proposed: exactly one JSON object on standard output, with `"ok": false` and a
  message that names the file, and exit 2 (r1 F1).
- P3.5. Each corrected docstring sentence is checked against a run, pasted in the record.
- P3.6. `rules_check.py`, `review_tool.py` and `handoff.py`, and their copies under
  `plugins/`, exit 0 under `uvx ruff@0.16.2 check` with the configuration of pull request
  34, as they do at `cecebc6` (section 9) (r1 F2).

*Spec:* written when phase 2 is recorded (an outline until then).

### Close

The close review (the review helper with `--subject close`), the question sweep, plan
repairs and the close record (C9), which says for each of the ten issues: fixed by which
commit, or left open and why.

**Inherited residuals.** None is assigned to this milestone except through the eight
issues. The residuals the `component-index` close accepted, and Q1 to Q4 of
`sync-reports`, stay where those closes left them.

## 5. Documentation, skill and compatibility surfaces

| Surface | Phase | Note |
|---|---|---|
| `components_index.settings.json`: `allow_baseline` | 2 | New and optional. A `components_index.py` older than this change refuses the key with `unknown setting(s): allow_baseline`: loud, not silent, as `count_extra_dirs` was |
| `COMPONENTS.md` entries: `reread:` | 2 | New and optional. An older script ignores an unknown field |
| `changed`'s base, and the base of `facts --base` and `rules_check.py check --base` (r1 F3) | 2 | One new line, and another base, only when the local base is strictly behind its remote-tracking branch (S0.1 names this exception through D6). The facts document keeps its format, `devtools-facts/1`; its `revision` is the commit that was used |
| `review`'s groups | 2 | More leads for a project with `count_extra_dirs` on. `review` always exits 0 |
| `rules_check.py test` | 3 | One new `skip:` line where the phase tool is absent; exit 0 where it was 1 |
| The exit for a settings file a script cannot use | 3 | 2 where it was 1 (D10). A caller that reads 1 as "the check found something" is what this corrects |
| `skills/components/SKILL.md` and its references, `docs/components.html`, `docs/rules.html` | 2, 3 | Each sentence that describes a changed behaviour; a capture is replaced only by a real run |
| `.devtools/project.md` | 2 | The gate table, and "not an installed plugin older than 0.1.5" becomes the version that has `allow_baseline` |
| The plugins | 2, 3 | Rebuilt; one new version for the milestone (D4). Phase 1 changes no plugin file |
| Both agents | 2, 3 | The changed skills name commands and settings, with `${CLAUDE_PLUGIN_ROOT}` paths as they have today; each spec says what was checked for Claude Code and for Codex |

## 6. Risks and required controls

| Risk | Control |
|---|---|
| K1. The guard for issue 31 skips a real failure | It skips on exit 5 with the sentence naming the extra, and on nothing else (P1.2). The `suggest` half of the test runs before the guard |
| K2. The test of the pytest plugin runs pytest inside pytest and inherits the outer run's options, plugins or cache | Each run is a subprocess in a project under `tmp_path`, with `PYTEST_ADDOPTS` removed and the cache plugin off |
| K3. A test of unchanged code that cannot fail | S0.3: each branch is broken once in a scratch copy and the failing test named in the record |
| K4. `from_gsd.py` loading `sync.py` makes an edge the index cannot see (issue 39) | The two entries say it in `notes:` and stay marked as settled, so `review` raises no same-name lead (P1.5) |
| K5. Preferring the remote-tracking branch changes a verdict of `changed`, and of `rules_check.py check --base` through `facts --base` (r1 F3) | Only when the local base is strictly behind it, where the remote-tracking branch holds everything the local one does. The line says which was used. An explicit commit is never replaced |
| K6. dev-tools' own settings file takes a key the installed plugin refuses | The gates already run the built copy under `plugins/` (`.devtools/project.md`); the note there is updated in the same phase |
| K7. Exit 2 for a settings error breaks a caller that expects 1 | The spec greps the skills and the tests for each script's exit codes before the change and lists every reader |
| K8. `main` moves while the milestone runs (a tag of 0.1.6, another merge) | `main` is merged into the branch, never rebased; the gates are run again; `release_plugins.py bump` already takes the higher of the tree and the last tag |
| K9. A phase finds a defect outside its issues (the pytest plugin, a seventh settings reader) | It is written into the record as a finding. A fix of one function goes in with a test; anything larger is a draft issue for the owner (S0.4) |

## 7. Out of scope

- **Issue 39** (the index cannot see one script running another). It adds a kind of edge
  to the graph, to `uses` and `used_by`, to the flow check and to the facts `rules_check.py`
  reads: a format other tools depend on, with a design to settle first. A milestone of its
  own, or the first phase of the next.
- **Issue 40** (a hand-off note's ignored paths in a form `takeover` can parse). It changes
  the note's format, which branches of other projects hold, and its own text names the
  question to settle first: whether a hand-edited inventory line is trusted or checked
  against a digest. A milestone of its own, as the `component-index` close said.
- The residuals of earlier closes (section 4).
- Splitting the three largest scripts (`REVIEW.md`, suggestion 3): S0.2.
- Tagging 0.1.6 or any release; CI; GND itself.

## 8. Execution, approval and review protocol

- **Workflow.** `process-milestone issue-sweep`, phase by phase with `process-phase`.
  `auto=false` unless the owner says otherwise: the plan gate, each spec's owner gate and
  the close stop for the owner.
- **Branch and pull request** (D3). One branch, `claude/open-issues-milestone-43c5a0`,
  where this plan is, and one pull request for the milestone, opened when the owner asks.
  Its description names the issues it closes (S0.4).
- **Reviews.** The review helper (`review_tool.py`), with Codex as reviewer:
  `--subject plan` before the plan gate, `--subject phase` over each phase's diff,
  `--subject close` at the close. Rounds follow `review-convergence.md`. A repaired file
  is unreviewed until a later round reads it.
- **Review budget for this plan.** At most two rounds (r1, r2), declared here before
  either has run. The stop rule of `review-convergence.md` ends it earlier.
- **Records.** `001-plan.md` at the plan gate, one per phase, and the close record.
- **Owner actions no delegation covers.** Committing and pushing are asked for each time
  unless the owner says otherwise; merging; a release tag; anything posted to GitHub.

## 9. Per-phase verification story, expected results and affected consumers

Commands run from the repository root.

| Phase | Gate command | Expected | Affected consumers |
|---|---|---|---|
| 1 | `uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_phase_selection.py tests/test_from_gsd.py tests/test_sync.py -q` | exits 0 | Contributors, who run the suite |
| 1 | `uv run --no-project --with pytest python -m pytest tests -q` | exits 0 | Same |
| 1 | `python3 devtools/build_plugins.py --check` | exits 0, and no file under `plugins/` differs from `cecebc6` | Plugin users: no change |
| 1 | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict` | exits 0 | dev-tools' own sessions |
| 1 | By hand, if D4 of the phase 1 spec is ruled so: the suite with a GND installed without its extra. *Repaired at the close (c1), from `002-phase-1.md` (spec I2): the command is `GND_COMMAND="uvx -q --isolated --from get-nick-done==0.4.0 gnd"`; without `--isolated`, `uvx` reused the installed GND, extra included, and tested nothing. Prior wording named no command; the phase 1 spec's D4 named the one without `--isolated`* | the one test reported as skipped, with the guard's reason; exit 0 | A contributor whose GND has no extra |
| 2 | The focused gate over `tests/test_tools.py` and `tests/test_own_index.py`, then the three gates of phase 1 | exit 0 each | Every project that keeps an index: a new setting, a new field, and one new line from `changed` in the stale-base case |
| 2 | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base main`, in a worktree whose local `main` is behind | The line that names `origin/main`, and the count that `--base origin/main` gives | dev-tools' own sessions in worktrees |
| 3 | The focused gate over `tests/test_plugins.py` and `tests/test_tools.py`, then the three gates of phase 1 | exit 0 each | dvt-milestone projects that write rules; every caller that reads a script's exit |
| 3 | `uvx ruff@0.16.2 check --config <a gnd-public checkout>/pyproject.toml skills/components/scripts/rules_check.py skills/milestone/process-phase/scripts/review_tool.py skills/dev-handoff/scripts/handoff.py`, and the same over their copies under `plugins/` (r1 F2). The configuration is another repository's file: on this machine `~/github-repos/gnd-public/pyproject.toml`. Where there is no such checkout the gate is recorded as not run, not as exited 0 | exit 0, `All checks passed!` | A project that lints its synced copies, as gnd-public does |
| 3 | By hand: the three commands of issue 33 with each built plugin, in a new project | `0 wrong`, exit 0, twice | Same |

## 10. Owner decisions and open questions

### Decisions for the plan gate (ruled 2026-11-23: D1 to D11 by the owner; D3 to D11 each as proposed)

| # | Question | Readings and their cost | Proposed |
|---|---|---|---|
| D1 | Which issues are in (ruled by the owner, 2026-11-23: "Yes, eight") (o) | **Eight (31, 33, 41 to 46):** three phases, each a few dozen lines of code and its tests; 39 and 40 stay open with their reason. **All ten:** two more phases, each with a format change and a design to settle before its spec (section 7); the milestone is no longer small, and 40's question would hold up the eight. **Fewer** (only the three of phase 1, the ones the `component-index` close called fast-lane): one phase, no plugin release, five issues left | Ruled: eight |
| D2 | The lane (ruled by the owner, 2026-11-23: "plan a small milestone") | **A milestone:** a plan, three specs, records and review rounds. Phase 1's three issues would be fast-lane fixes by `.devtools/project.md` and ride along; phases 2 and 3 add a setting, an entry field and an exit code, which the same file puts in the evidence lane | Ruled |
| D3 | Pull requests | **One for the milestone:** one merge, one release, and a diff of a few hundred lines. **One per phase:** three smaller reviews, three merges, and phases 2 and 3 each wait for the one before | Ruled: one (o) |
| D4 | The plugin version | **One new version for the milestone**, taken with `release_plugins.py bump` in phase 2; phase 3 rebuilds under it. The tree's 0.1.6 is not tagged, so the bump gives 0.1.7 and the owner may tag once. **A version per phase:** 0.1.7 and 0.1.8, neither released on its own under D3 | Ruled: one (o) |
| D5 | How a project refuses a baseline (issue 46) | **A setting, `allow_baseline: false`:** the project's gate command stays `--check --strict`, and the choice is in the project's files. **An option, `--no-baseline`:** nothing new in the settings, and every gate row, skill sentence and test that runs the check has to carry it. **Both:** two ways to say one thing | Ruled: the setting (o) |
| D6 | A local base behind its remote-tracking branch (issue 45, part 1) | **Use the remote-tracking branch and say so:** the first run is right; the verdict can differ from today's for the same checkout, only in that case. **Only say so, and name the command:** today's verdict stays, and the run has to be repeated by hand. Either reading holds for `facts --base` and `rules_check.py check --base` too, which share the function (r1 F3) | Ruled: use it and say so (o) |
| D7 | Marking an entry as reread (issue 45, part 2) | **A `reread:` line, dated by its own last edit:** nothing to parse or validate, and what the entry says is untouched; one more optional field. **Count an edit to `notes:`:** no new field, and any edit of a note for another reason marks the entry as reread | Ruled: the `reread:` line (o) |
| D8 | Which groups of `review` follow `count_extra_dirs` (issue 44) | **Every group not built from the import graph** (same name, no docstring, over 12 modules, the summary's count): one rule a reader can state. **The same-name group alone**, as the issue asks: the summary would still say `4 module(s)` beside leads about 12 | Ruled: every such group (o) |
| D9 | The starter rule about plans where there is no phase tool (issue 33) | **`test` leaves the rule out and says so:** also right for a rules file written under one install and read under another. **`init` leaves the rule out:** quiet, and a project that later takes the phase workflow never gets the rule. **dvt-milestone ships `phase_tool.py`:** a milestone project carries a 2000-line script for one rule | Ruled: `test` leaves it out (o) |
| D10 | The exit for a settings file a script cannot use (issue 43) | **Exit 2, in every script under `skills/` that reads one:** it is the code each docstring already gives to "could not run"; several scripts change by a few lines each. **Exit 2 in the issue's two only:** `components_index.py --check` keeps exit 1 for a broken settings file, the code that means "stale". **Leave the exit and correct the docstrings:** no caller changes, and a broken file still reads as a finding | Ruled: exit 2, in every one (o). *Amended at the close, 2026-11-23 (c1), by delegated approval, from `004-phase-3.md` (phase 3 spec D1; a refuted premise there): except `coder_pool.py`, which keeps exit 1, since its docstring gives 1 to "a settings or configuration file cannot be used" and its pool's TOML files share that code, so "the code each docstring already gives to 'could not run'" is false for it. Prior ruling: "exit 2, in every one"* |
| D11 | What `phase_tool.py` prints for a settings file it cannot use (issue 43; r1 F1) | **One JSON envelope with `"ok": false` under `--format json`, exit 2, for every command:** the issue's own pairing ("exit 2, with an envelope"); a caller that parses the output always gets JSON; `status` no longer "always exits 0", and the docstring says when it does not; the settings are checked when the script is loaded, so the spec has to move the report into `main`. **Plain text on standard error, exit 2, and the docstring says the envelope holds once the settings are read:** a few lines fewer, and a caller that parses standard output gets nothing to parse | Ruled: the envelope (o) |

### Open questions (carried to the close sweep)

- Q1. Which of 39 and 40 comes next, and whether 39 is a milestone or a phase of one.
- Q2. Issue 31's failure was not reproduced here. Whether a GND without its extra is
  installed for one by-hand run (phase 1 spec, D4) or the fake `gnd` is the evidence.
- Q3. Whether the index review offered in section 3 is taken before phase 2, which adds
  the field that would record it.

### Obligation-to-phase map

| Obligation (source) | Phase and gate |
|---|---|
| The guard asks whether `synth --guarded-cases` can run, and skips on the refusal (issue 31) | 1: P1.1, P1.2 |
| A test for the guard with a fake `gnd` that lists the flag and exits 5 (issue 31) | 1: P1.1 |
| A test that runs the plugin as a `conftest.py`: plain, `--phase NN`, a named path (issue 42) | 1: P1.3. One exists already for these three (r1 F5); the entry lists it and the new file adds the rest |
| One list, in one place; the callers looked at first (issue 41) | 1: P1.4 |
| `--check --strict` can refuse a baseline; the default stays (issue 46) | 2: P2.1, D5 |
| Say when the base is behind, or prefer the remote-tracking branch; nothing fetches (issue 45) | 2: P2.2, P2.2b, P2.3, D6 |
| Record that an entry was read without changing what it says; `changed`'s `reread:` lines follow (issue 45) | 2: P2.4, D7. `changed` already treats any edited authored field as an edited entry; the spec pins it with a test |
| The same-name group over `counted_modules` when the setting is on (issue 44) | 2: P2.5, D8 |
| `init` then `test` passes in each plugin; a test that would catch it again (issue 33) | 3: P3.1 to P3.3, D9 |
| Correct two sentences; choose for the other two, with an envelope for `phase_tool.py` if the exit becomes 2 (issue 43) | 3: P3.4, P3.4b, P3.5, D10, D11 (r1 F1) |
| `review_tool.py` stays clean under the linter pull request 34 names (issue 43) | 3: P3.6 and its gate in section 9 (r1 F2; prior mapping: "P3.4, P3.5, D10", none of which runs a linter) |
| Issues 39 and 40 (their own texts; `007-close.md`, P1 and P2) | Not in this milestone: section 7, D1, Q1 |
| A script change comes with a test (standing rule) | 1 to 3: each fix's test, seen to fail first (S0.3) |
| Rebuild and release under a new version (standing rule) | 2, 3: D4. Phase 1: no plugin file changes (P1.6) |
| A wording change says what prompted it (standing rule) | 2, 3: the issue and the baseline row behind each changed sentence |
| Shared skills stay general (standing rule) | 2, 3: each added sentence describes a setting or a line of the tool, for any project |
| Both agents read the same file (standing rule) | Section 5, last row |
| Captures on the site are real output (standing rule) | 2, 3: section 5 |
| The page that describes it is updated too (standing rule) | 2, 3: C8 |
| The component index stays current (`.devtools/project.md`, "Gates") | 1 to 3: C7 |
