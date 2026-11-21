# Milestone plan: component-index

**Goal.** dev-tools has a component index of its own code, searchable by capability.
Every module of the shipped code has a component, and a change that adds a module without
one is refused by a gate this repository runs. On the way, the milestone fixes issue 28:
`dev-takeover` reports ready while an ignored path that the note did not list is missing.

**Status.** Draft, 2026-11-21, written with `start-milestone` (dvt-milestone 0.1.3).

- **Amended the same day (o).** The owner asked for issue 28 to be fixed in this
  milestone. It is now phase 1, and the phases first written as 1 to 3 are now 2 to 4.
  Nothing had been approved or reviewed before the change.
- **Plan review, round 1 (r1).** `notes/reviews/plan-r1`, run 2026-11-21 with the review
  helper and `--subject plan`.
  - *Reviewer:* Codex, read-only, its default model at effort `high`.
  - *What it read:* this plan, both specs and 10 context files (brief SHA-256
    `b64a960e46ad450113a22d40af7d55c78c95145054d9b71cc550e723b1ea06e4`).
  - *Result:* `VERDICT: CHANGES_REQUESTED`, with 8 findings: 3 blocking, 2 hardening and
    3 completeness. All 8 were reproduced and repaired in the working tree, marked
    `(r1 Fn)` at each site.
  - **The repaired bytes carry no review opinion.** The repairs were committed at
    `ada0d1a`, and the ledger rows are `fixed` at that commit.
- **Review budget, declared before round 2.** At most two more rounds over these
  artifacts (r2, r3). The stop rule of `review-convergence.md` ends the loop earlier, and
  a round whose findings are mostly completeness ends it too.

  | Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
  |---|---|---|---|---|---|---|
  | r1 | 1 (Codex) | 8 | 0 / 8 (first round) | 3 / 8 | blocking | CHANGES_REQUESTED |
  | r2 | 1 (Codex) | 3 | 1 / 3 (F3 attacks a2) | 1 / 3 | blocking | CHANGES_REQUESTED |

  | r3 | 1 (Codex) | 1 | 1 / 1 (F1 attacks the r2 F2 repair) | 0 / 1 | hardening | CHANGES_REQUESTED |

  After r2 the stop rule did not fire: 1/3 is not above one half, and the count fell
  from 8 to 3. After r3 it fires (1/1 is above one half), and the budget is spent. The
  next instrument is the code: r3 F1 is repaired as a test row (phase 1 spec, T10), and
  phase 1's diff review reads it.
- **Plan review, round 2 (r2).** `notes/reviews/plan-r2`, run 2026-11-21 over the r1
  repairs and a2 (brief SHA-256
  `fc912dc8da465b01c6895b59f577fb595ea2ed7bfddb892062761b5f89078b1e`). `VERDICT:
  CHANGES_REQUESTED`, with 3 findings: 1 blocking (a phase 2 test that cannot give its
  exits), 1 hardening (a path holding a backtick is never checked) and 1 completeness
  (section 8 said `auto=false`). All 3 were reproduced and repaired, marked `(r2 Fn)`.
- **Plan review, round 3 (r3).** `notes/reviews/plan-r3` (brief SHA-256
  `92d7eadd722d588543504414dddc6401e5c215361d880cb0d5ed70cad48449f2`). `VERDICT:
  CHANGES_REQUESTED`, with 1 hardening finding: a path holding a newline is still
  skipped by the r2 bullet pattern. It was reproduced and repaired, marked `(r3 F1)`.
- **Amendment a2, 2026-11-21, before round 2.** The owner invoked
  `process-milestone component-index auto`, which delegates the plan, spec and close
  rulings of this milestone (`auto=true`). Before round 2, `git check-ignore` showed the
  milestone's `notes/` folder ignored by `.gitignore` line 7, so none of this plan could be
  committed. Phase 1 now also anchors that line (section 3, artifact homes; section 4,
  phase 1 deliverables).
- **Plan gate: delegated approval (auto=true), 2026-11-21.** Recorded in `001-plan.md`,
  which binds these bytes by SHA-256. D1 to D5 are ruled as proposed (section 10). The
  r3 F1 repair is unreviewed (above).
- **Amendment a3, 2026-11-21: delegated approval (auto=true).** Phase 1's pull request
  (vasiloglou/dev-tools#29) is open and not merged. The owner said to go on. Phase 2
  needs nothing phase 1 produces (section 3, phase dependencies), so its branch is cut
  from phase 1's branch tip, and its pull request names phase 1's branch as its base
  (section 8, "Branches"). The phases still run one at a time and release one version
  each. Recorded in `003-phase-2.md`. The amended bytes are not reviewed.

**Done when** (the completion predicates; each is a gate with an exit code, or a ruling):

- C1. The built plugin's `components_index.py --check --strict`, run from the repository
  root with `.devtools/components_index.settings.json`, exits 0, and
  `test ! -e .devtools/components/unassigned-baseline.txt` exits 0. `--check --strict`
  excuses any module the baseline names, so the second command is what shows there is
  none (r1 F6). Together they mean every module of `devtools/` and of `skills/` has a
  component.
- C2. Each search case in `.devtools/components/search-cases.md` puts its expected
  component first among the components. The negative case returns `no component matched`,
  or no hit that matches more than one word.
- C3. `uv run --no-project --with pytest python -m pytest tests -q` exits 0, except for
  the known GND `synth` case (section 6, R5). The suite includes a test that fails while
  the index is stale.
- C4. `.devtools/project.md` names the index, its folder and its two gates. The
  documentation that describes dev-tools' own use names the index.
- C5. `handoff.takeover` returns `ready: false` when any ignored path the note was written
  with, other than a key file, is absent, including one after the 25th. A missing key file
  is reported in `missing_keys` and does not block, as today (r1 F1). The tests T1 to T10 of
  `notes/phase-1-spec.md` exit as that spec lists, and the pull request says
  `Fixes #28`.
- C6. A close record, after the close review.

## 0. Binding design rules

Every spec discharges each rule below by name, or argues in one sentence that it does not
apply. The rules are the project's seven standing design rules (`.devtools/project.md`,
"Standing design rules") and the three that follow.

- **R0.1 A shipped script stands alone.** The sync copies each script into a project by
  itself, so the scripts import nothing from each other. A helper written in several
  scripts (`git` in seven, `load_settings` in five) is not a defect, and the index does
  not mark it `duplicate-of`. Where `review` reports a shared name, the entries record it
  under `distinct_from:`, with the reason in `notes:`.
  - *Prevents:* a consolidation that makes one script depend on another and breaks a
    synced project.
  - *Discharged by:* naming every `distinct_from` pair the phase writes and the reason it
    gives, and every import the phase adds.
- **R0.2 The index is the project's, not the product's.** Every file of dev-tools' own
  index lives under `.devtools/`. Nothing under `skills/`, `agents/`, `plugins/` or
  `docs/` is written to serve it. A change to the product made for this index is a change
  any project could use, and it is documented as one.
  - *Prevents:* the shipped skills carrying dev-tools-only settings or paths.
  - *Discharged by:* naming each product file the phase changes and why it holds outside
    this repository.
- **R0.3 The released plugin runs; the branch is tested.** A gate that uses the index tool
  runs the built copy, `plugins/dvt-milestone/skills/components/scripts/components_index.py`,
  from the repository root. That copy reads `.devtools/`, as a plugin install does.
  `skills/components/scripts/components_index.py` is never run directly against this
  repository: it would read its settings from beside itself, inside the product.
  - *Prevents:* a settings file written into `skills/`, and a gate that tests other code
    than the plugin ships.
  - *Discharged by:* writing the exact command of every gate.

## 1. Scope, sources and authority

**Scope:**

- the component index of dev-tools' own code, built with the `components` skill's Build
  mode;
- the one change to the index tool needed so it can cover that code;
- the gates that keep the index current;
- the fix of issue 28 in `handoff.py`.

**Sources** (read for this plan):

| Source | What it gives |
|---|---|
| Owner, 2026-11-21, this session | "Should the component index be the first milestone, planned with `start-milestone`?", answered "yes"; then "can you also include the fix of a new issue that was just filed?" |
| Issue 28, opened 2026-11-21 | The defect, its suggested fixes, and the test it asks for. Reproduced on main `c9648dd` (`notes/phase-1-spec.md`, section 2) |
| `.devtools/project.md`, "What runs here" | "Component index. None yet … the folder is chosen when the index is built, set as `docs_dir` … and named here" |
| `.devtools/project.md`, "Which lane" | A change to what a gate refuses, or to a format a project depends on, takes the evidence lane. A hand-off note is named there as such a format |
| `.planning/PROJECT.md` | What a change must keep true: shared skills stay general, and a synced project takes no dependency on this repository |
| `skills/components/SKILL.md`, `references/build.md`, `references/review.md` (0.1.3) | The entry format, the Build procedure and its finish, the Review groups |
| `skills/components/scripts/components_index.py`, `skills/dev-handoff/scripts/handoff.py` (main `c9648dd`) | What the tools do today (section 3, "Baseline") |
| `CONTRIBUTING.md`, "What makes a change easy to accept" | The standing design rules |

**Authority.** This plan is a proposal written by the agent. Nothing in it is approved
until the plan gate is recorded. A merge, a release tag and anything posted to GitHub,
including the reply to issue 28, need the owner each time (`.devtools/project.md`, "What
needs the owner each time"). `auto=true` would not cover them.

## 2. Contract proposal and product behaviour

**For every project: hand-offs (phase 1).** `takeover` checks every ignored path the note
was written with:

- the 25 the note lists;
- the rest, which the note keeps in one comment line at the end of its snapshot, written
  only when the list is cut.

A note of 25 paths or fewer is written exactly as today. A note from an older version
whose list was cut reports `unlisted_ignored: N` and is not ready.

**For every project: the index (phase 2).** A project whose code sits in more than one
folder can have all of it counted. Today the modules of `extra_source_dirs` are listed and
searched, but not counted. The proposed setting `count_extra_dirs` makes these count them
too:

- the coverage line and `stats`;
- `--check --strict`;
- `draft`;
- `changed`;
- `review`'s "Modules with no component".

The default leaves every existing project as it is.

**For dev-tools (phase 3).** The index lives in `.devtools/components/` (D1). Its settings
are in `.devtools/components_index.settings.json`:

```json
{"package_dir": "devtools", "extra_source_dirs": ["skills"], "count_extra_dirs": true,
 "docs_dir": ".devtools/components"}
```

The setting's name and shape are ruled at phase 2's owner gate, and this block follows
that ruling.

**What the index will look like.** The code is 12 modules of about 10,800 lines: 4 in
`devtools/`, and 8 in `skills/*/scripts/` and `skills/phase/pytest/`. A file is listed
under exactly one entry (`build.md`, step 3). That gives about 12 components, each
covering one script, and about 8 subsystems:

- sync;
- the GSD move;
- the plugin build and release;
- the phase state tool;
- the coder pool;
- the review helper;
- the hand-off;
- the component index and its rules check.

Most of what a planner finds is found at the level of functions, in the symbol lines that
`search` prints under a module hit.

## 3. Dependencies and artifact homes

### Baseline, observed on 2026-11-21

This is observed evidence, not claims.

**The index tool**, run in a scratch clone of main:

| Settings tried | Coverage line | What is wrong |
|---|---|---|
| `package_dir: devtools`, `extra_source_dirs: [skills]` | `0/4 devtools modules` | The 8 skill scripts are listed but never counted |
| `package_dir: skills`, `extra_source_dirs: [devtools]` | `0/8 skills modules` | The 4 `devtools/` modules are never counted |
| `package_dir: .` | `0/23 . modules` | Counts the 11 generated copies under `plugins/`. In a real checkout it would also walk `.claude/worktrees/`, which are full copies of the repository, because `sources()` uses `rglob` with no exclude and no git check |

`components_index.py` builds the counted set from `package_dir` alone. It does so in the
three places that judge coverage (`coverage()`, `changed()` and `review`), and in `show`,
which uses the same list to decide which of an entry's modules it prints in detail (r1
F5). `draft()` drafts only what `coverage()` returns, so today it never sees a module in
an extra folder. It computes a module's id with `relative_to(PACKAGE_DIR)`, which would
raise an error for such a module once extra folders are counted (r1 F8; the earlier
wording said it raises today).

**The hand-off script**, run through `write_note` and `takeover` in a scratch folder: a
note written with 26 ignored folders lists 25, and ends with
`- and 1 smaller path (`handoff.py ignored`)`. A clone that lacks the 26th returns
`{"head": "ok", "missing_ignored": [], "blocking": [], "ready": true}`.

### What the shipped code depends on

The standard library only, so `external.toml` is not needed. The scripts import nothing
from each other statically. Three load another script at run time, which the import graph
cannot see:

- `release_plugins.py` loads `build_plugins.py`;
- `rules_check.py` loads `phase_tool.py`;
- `phase_tool.py` runs a project's generator script with `runpy`.

The subsystems' flows state these in `notes:`.

### Artifact homes

| Artifact | Home |
|---|---|
| Plan, specs, review rounds | `.planning/milestones/component-index/notes/`. On main, `.gitignore` line 7 (`notes/`) ignored every folder of that name, this one included; phase 1 anchors it to `/notes/`, which still ignores the root working notes it was written for (amendment a2) |
| Records | `.planning/milestones/component-index/NNN-<scope>.md` |
| The issue 28 fix | `skills/dev-handoff/scripts/handoff.py`, `tests/test_handoff.py` |
| The index tool change | `skills/components/scripts/components_index.py`, `tests/test_tools.py` |
| Index and its settings | `.devtools/components/`, `.devtools/components_index.settings.json` |
| Search cases | `.devtools/components/search-cases.md` (hand-written; the tool ignores it) |
| Stale-index test | `tests/test_own_index.py` (D3) |

### Phase dependencies

| Phase | Depends on |
|---|---|
| 1 (issue 28) | the plan gate only |
| 2 (the index tool) | the plan gate. It runs after phase 1 because the plan keeps one phase at a time and one release per phase. It needs nothing that phase 1 produces |
| 3 (build the index) | phase 2 merged. Its gates run the built copy on main (R0.3), so it does not wait for the release tag |
| 4 (keep it current) | phase 3 |
| Close | phase 4 |

## 4. Phases, deliverables, named criteria and inherited residuals

### Phase 1: takeover checks every ignored path the note was written with (issue 28)

*Outcome:* the defect in issue 28 is gone, and older notes cannot read as ready.

*Deliverables:*

- the change to `_snapshot_text` and `takeover` in `handoff.py`;
- the tests in `tests/test_handoff.py`;
- one sentence each in `skills/dev-handoff/references/handoff.md` and
  `docs/handoff.html`;
- `release_plugins.py bump`, to 0.1.4;
- `.gitignore` line 7 anchored to `/notes/`, so the milestone's planning files can be
  committed with it (a2);
- a pull request with `Fixes #28`.

*Criteria:*

- P1.1. A missing ignored path after the 25th, other than a key file, makes `ready` false
  (issue 28, reproduced). A missing key file is reported and does not block (r1 F1).
- P1.2. A note in the old format with a cut list makes `ready` false, with
  `unlisted_ignored` set to the number of unlisted paths.
- P1.3. A note of 25 paths or fewer is written exactly as on main.
- P1.4. `build_plugins.py --check` exits 0.

*Spec:* `notes/phase-1-spec.md` (draft).

### Phase 2: an index can count more than one source folder

*Outcome:* a project can have the modules of its `extra_source_dirs` counted like those of
its `package_dir`. The default is unchanged.

*Deliverables:*

- the setting, and one function `counted_modules` used by every site in section 3 that
  decides whether a module has a component, `show` included;
- the tests in `tests/test_tools.py`;
- the setting described in `skills/components/SKILL.md`, `references/build.md`,
  `docs/components.html` and `examples/phase-project.devtools.toml`;
- the retaken `docs/adopt.html` capture (that spec's D2);
- `release_plugins.py bump`, to 0.1.5.

*Criteria:*

- P2.1. With the setting on, `stats`, `--check --strict`, `draft`, `changed` and `review`
  name a module in an extra folder that has no component, with the exits the spec lists.
- P2.2. With the setting off or absent, every existing test exits as on main.
- P2.3. `draft` gives a stub for a module in an extra folder and does not raise an error.
- P2.4. `build_plugins.py --check` exits 0.

*Spec:* `notes/phase-2-spec.md`. It is a draft, written before the amendment, and is kept
as the phase's starting text.

### Phase 3: build dev-tools' index

*Outcome:* `.devtools/components/` holds an index with a component for each of the 12
modules, the subsystems, and the generated pages.

*Deliverables:*

- the settings file and `COMPONENTS.md`;
- the generated `modules/` and `graph.md`;
- `search-cases.md`: 8 to 10 capabilities a newcomer would ask for, in their own words,
  and one negative case;
- `REVIEW.md`, with what the build noticed: files worth splitting, names shared across
  scripts (R0.1), code with no tests. These are suggestions, not acted on.

*Criteria:* C1 and C2, and:

- P3.1. `write` exits 0, then `--check --strict` exits 0.
- P3.2. `review` reports no "components that import each other", and no "flow step that no
  earlier step imports" apart from the run-time loads that `notes:` states.
- P3.3. Every entry is read from the code. An entry marked `checked: partial` is listed in
  the record.

*Reading:* about 10,800 lines, roughly one reader's share by `build.md`'s measure. The
driving agent reads it, and no readers are fanned out.

### Phase 4: keep it current

*Outcome:* a change that leaves the index stale is caught, by a test and a gate.

*Deliverables:*

- `tests/test_own_index.py`, which runs the built copy's `--check --strict` from the
  repository root (D3);
- `.devtools/project.md`: the index's folder in "What runs here", and two rows in "Gates"
  (`changed --base main` before a pull request, and `--check --strict` when a phase
  closes);
- one line in `AGENTS.md`: search the index before writing a module or a function;
- a row naming `.devtools/components/` in `README.md` and `docs/milestone.html#own-use`,
  and a pointer to it on `docs/components.html` as an example of a built index.

*Criteria:* C3 and C4, and:

- P4.1. The new test exits 0 on the phase's head.
- P4.2. With one entry's module path removed, the new test fails and names the module.
- P4.3. With an `unassigned-baseline.txt` present, the new test fails (r1 F6).

### Close

The close review (the review helper with `--subject close`), the question sweep, plan
repairs, and the close record (C6).

**Inherited residuals:** none. This is the project's first milestone.

## 5. Documentation, skill and compatibility surfaces

| Surface | Phase | Note |
|---|---|---|
| `skills/dev-handoff/references/handoff.md`, `docs/handoff.html` | 1 | What `takeover`'s ready checks |
| The hand-off note's snapshot | 1 | A format other projects' branches hold. The new line is written only when the list is cut, so every note of 25 paths or fewer, and the site's capture of one, is unchanged. An older plugin reading a new note ignores the comment line and behaves as 0.1.3 does today, which is the defect, not a new failure |
| `skills/components/SKILL.md` (the settings line), `references/build.md` (step 1) | 2 | Read the same way by Claude Code and Codex, from `${CLAUDE_PLUGIN_ROOT}` |
| `docs/components.html` | 2, 4 | The setting (2); dev-tools' index as an example (4) |
| `docs/adopt.html` capture of `survey --toml` | 2 | It gains a line for the new key and is retaken from a real run (phase 2 spec, D2) |
| `plugins/` | 1, 2 | Rebuilt by `release_plugins.py bump`; never edited by hand |
| `.devtools/project.md`, `AGENTS.md`, `README.md`, `docs/milestone.html` | 4 | The project's own use |
| Settings compatibility | 2 | `load_settings` refuses an unknown setting today. A project that writes the new key and runs an older plugin gets `unknown setting(s): count_extra_dirs`, which is loud, not silent. The docs name the first version that accepts the key |

## 6. Risks and required controls

| Risk | Control |
|---|---|
| R1. Counting extra folders changes the verdict for existing projects | Off by default; P2.2 keeps every existing test's exit |
| R2. One entry per file turns the 2,000-line scripts into vague entries | `does` names the main entry points and `verbs` carries the subcommands; the search cases (C2) test it |
| R3. The graph cannot see run-time loads, so a flow reads as wrong | The flows state the loads in `notes:`; P3.2 allows exactly those |
| R4. A gate runs the branch's script against the repository and writes settings into `skills/` | R0.3: every gate command names the built copy |
| R5. A test failure known on this machine (GND lacks its `synth` extra) is read as a regression | Every gate record names that case and its cause, and does not call the suite green |
| R6. Phase 3 merges before 0.1.5 is tagged, so a developer on an older plugin gets `unknown setting(s)` from their plugin | Phase 4's line in `.devtools/project.md` names the plugin version the index needs. The owner tags 0.1.4 and 0.1.5 after their merges (owner actions) |
| R7. The issue 28 fix makes notes with long lists unreadable to people | Only one comment line is added, and only for a cut list. The bullet list a reader sees is unchanged |

## 7. Out of scope

- Import resolution across several source folders: the graph stays within `package_dir`.
  The scripts have no static imports of each other, so it would show nothing here.
- Splitting or merging scripts, or consolidating shared helpers (R0.1). `REVIEW.md` lists
  them; nothing is done about them.
- How many ignored paths a note lists for a reader (the 25).
- The optional rules check (`rules_check.py`, `layers.toml`).
- CI. There is none, and adding it is a separate decision.
- Committing or deleting the PR 26 review rounds in `.planning/reviews/`.

## 8. Execution, approval and review protocol

- **Workflow.** `process-milestone component-index`, phase by phase with `process-phase`.
  The owner invoked it with `auto` on 2026-11-21 (a2), so the plan, spec and close rulings
  are delegated approvals (auto=true), recorded as such, and the walk does not stop at
  them. The owner actions below are not delegated (r2 F3: the earlier wording said
  `auto=false`, and that each spec stops at its owner gate).
- **Branches.** One topic branch and one pull request per phase,
  `claude/component-index-phase-N`, cut from main after the previous phase merges. The
  plan and the milestone's planning files go in with phase 1's pull request, unless the
  owner merges them first. *Amended a3, 2026-11-21:* while the previous phase's pull
  request is open, the next branch is cut from that branch's tip and its pull request
  names that branch as its base. Once the previous phase merges, the branch is rebased
  onto main and the base changed to main. The prior wording, above, stands for every
  other case.
- **Reviews.** The review helper (`review_tool.py`), with the other tool as reviewer:
  - `--subject plan` over this plan, before the plan gate (the project's plan-review bar);
  - `--subject phase` over each phase's diff (process-phase step 4);
  - `--subject close` at the close.

  Rounds follow `review-convergence.md`. A repaired file is unreviewed until a later round
  reads it.
- **Records.** One per material event, numbered, in the milestone's folder: `001-plan.md`
  at the plan gate, one per phase, and the close record.
- **Owner actions no delegation covers.** Each needs the owner every time:
  - merging each pull request;
  - tagging `plugins-v0.1.4` and `plugins-v0.1.5`;
  - posting anything to GitHub, including the reply to issue 28.

## 9. Per-phase verification story, expected results and affected consumers

Commands run from the repository root. `INDEX` below stands for exactly
`python3 plugins/dvt-milestone/skills/components/scripts/components_index.py`, the built
copy (R0.3). Each `INDEX …` row is run with those words in its place; nothing else is
abbreviated (r1 F7). In a search row, `<words>` is the query of one case of
`search-cases.md`, copied from that file, and the row is run once per case.

| Phase | Gate command | Expected | Affected consumers |
|---|---|---|---|
| 1 | `uv run --no-project --with pytest python -m pytest tests/test_handoff.py -q` | exits 0 | Every project that hands off work. A note of 25 paths or fewer is unchanged |
| 1 | `uv run --no-project --with pytest python -m pytest tests -q` | 1 failure, the R5 case | Same |
| 1 | `python3 devtools/build_plugins.py --check` | exits 0 | Plugin users after 0.1.4 |
| 2 | `uv run --no-project --with pytest python -m pytest tests/test_tools.py -q` | exits 0, apart from R5 | Every project with `extra_source_dirs`. With the default, nothing changes for them |
| 2 | `uv run --no-project --with pytest python -m pytest tests -q` | 1 failure, the R5 case | Same |
| 2 | `python3 devtools/build_plugins.py --check` | exits 0 | Plugin users after 0.1.5 |
| 3 | `INDEX write` | exits 0 | dev-tools' own sessions |
| 3 | `INDEX --check --strict` | exits 0 | Same |
| 3 | `INDEX stats` | prints the coverage line `12/12` | Same |
| 3 | `test ! -e .devtools/components/unassigned-baseline.txt` | exits 0 | Same |
| 3 | `INDEX search --explain <words>` | the expected component first among components | Same |
| 3 | `INDEX review` | exits 0 (it always does); its leads go into `REVIEW.md` | Same |
| 4 | `uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q` | exits 0; exits 1 with one module path removed (P4.2), and with a baseline present (P4.3) | Every contributor: the full suite now checks the index |
| 4 | `INDEX changed --base main` | exits 0 on the phase's head | Same |

`12/12` is the value expected at write time. If phase 2 changes which files count, phase
3's spec states the count, and C1 is judged by the exit code, not by the number.

## 10. Owner decisions and open questions

### Decisions for the plan gate (ruled 2026-11-21, delegated approval (auto=true): each as proposed)

| # | Question | Readings and their cost | Proposed |
|---|---|---|---|
| D1 | Where the index lives | `.devtools/components/`: beside the project's other files, and not published. `components/` at the root: visible, but a new top-level folder. `docs/components/`: published raw on the site, since `docs/.nojekyll` is there and nothing excludes it | `.devtools/components/` |
| D2 | Whether phase 2 is in the milestone | In: full coverage, and the product gains a setting any project can use. Out: phase 3 uses `package_dir: skills`, the 4 modules of `devtools/` stay uncounted, and C1 is weakened to `skills/` | In |
| D3 | How a stale index is caught | A test in `tests/`: the suite every contributor runs checks it, but then depends on `.devtools/`. A gate row in `.devtools/project.md` only: nothing runs it unless an agent does, and there is no CI | A test, and the gate rows |
| D4 | R0.1: shared helper names are recorded as `distinct_from` and left alone | As proposed. Or `duplicate-of`, which `review` would then report as consolidation work that R0.1 forbids | As proposed |
| D5 | The milestone's name, now that it also fixes issue 28 | Keep `component-index`: the issue is one phase, recorded here as an owner addition. Rename (for example `own-index`): every path in this plan changes, which costs nothing before the gate but does not describe the fix better | Keep |

### Open questions (carried to the close sweep)

- Q1. The graph cannot see run-time loads (section 3). Should the index tool read
  `spec_from_file_location` and `runpy.run_path` calls with literal paths? That would be a
  product change, for a later milestone.
- Q2. One entry per file (`build.md`, step 3) gives large scripts one entry each. Does
  search, through its symbol lines, find what planners ask for? C2 measures it, and the
  close says whether a finer grain is needed.

### Obligation-to-phase map

| Obligation (source) | Phase and gate |
|---|---|
| Fix issue 28 (owner, 2026-11-21; issue 28) | 1: P1.1 to P1.3, C5 |
| A test with more than 25 ignored paths (issue 28, "Suggested fix") | 1: the phase 1 spec, T1 |
| Reply to issue 28 saying where it went (`handle-issue`, step 3) | 1: the pull request's `Fixes #28`; the reply is posted on approval |
| Build the index (owner, 2026-11-21) | 3: C1, C2 |
| Choose the folder and name it in `.devtools/project.md` (`.devtools/project.md`, "What runs here") | D1; 4: C4 |
| Count every module of the shipped code (the goal; the section 3 baseline) | 2: P2.1 to P2.3; 3: C1 |
| A script change comes with a test (standing rule) | 1: `test_handoff.py`; 2: `test_tools.py`; 4: `test_own_index.py` |
| Rebuild and release under a new version (standing rule) | 1: 0.1.4, P1.4; 2: 0.1.5, P2.4; the owner tags |
| Shared skills stay general (standing rule; R0.2) | 1, 2: both changes hold for any project; 2's is off by default |
| Both agents read the same file (standing rule) | 1, 2: the section 5 rows |
| The page that describes it is updated (standing rule) | 1: `references/handoff.md`, `docs/handoff.html`; 2: `docs/components.html`; 4: the README and the milestone page |
| Captures are real output (standing rule) | 1: P1.3 keeps the snapshot capture true; 2: the `docs/adopt.html` capture is retaken |
| A wording change says what prompted it (standing rule) | 1: issue 28; 2: the section 3 baseline |
| Keep the index current (`build.md`, step 8.5) | 4: C3, C4 |
