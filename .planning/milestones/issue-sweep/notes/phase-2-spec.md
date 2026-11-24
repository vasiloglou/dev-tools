# Phase 2 spec: the index tool can refuse a baseline, name a stale base, mark a reread, and review every counted module

## 1. Status

Owner-decided (2026-11-23), by delegated approval (auto=true); recorded below, under
"Owner gate". Phase 1 is recorded (`002-phase-1.md`). Implementation may begin.

## 2. Provenance

- Derives from `notes/issue-sweep-plan.md`, approved at SHA-256 `309c6e55…81a4`
  (`001-plan.md`): section 2 ("Phase 2"), section 4 (P2.1 to P2.6, P2.2b), sections 5, 6
  (K5, K6, K8) and 9; the owner's rulings D4 to D8.
- Plan review r1 F3 added `facts --base` and P2.2b; that repair is unreviewed.
- Issues 44, 45 and 46, as kept in `notes/issues-2026-11-23.md`.
- The code at `a8e4182`, phase 1's head.
- No review round has read this spec.

Tags: `(o)` an owner ruling, `(d)` a delegated ruling (auto=true), `(rN)` review round N.

## 3. Obligations

| # | Obligation (source) | Discharged in |
|---|---|---|
| O1 | A project can make `--check --strict` fail on a baseline file; the default stays (issue 46; P2.1; D5 of the plan: a setting) | 6.1; A1, A4 |
| O2 | With the setting, `stats --write-baseline` writes nothing (P2.1) | 6.1; A2; D1 |
| O3 | A local base strictly behind its remote-tracking branch: that branch is used, and one line says so (issue 45; P2.2; D6 of the plan) | 6.2; B1 |
| O4 | Level, ahead, diverged, no upstream, a commit: today's lines (P2.2, S0.1) | 6.2; B2 |
| O5 | Nothing fetches (issue 45; P2.3) | 6.2; B3 |
| O6 | `facts --base` follows the same rule and still writes one JSON document on standard output; `rules_check.py check --base` judges against that base (P2.2b; r1 F3) | 6.2; B4, B5 |
| O7 | An entry marked as reread is not listed as older than its code until its modules change again; the line may appear once (issue 45; P2.4; D7 of the plan) | 6.3; C1, C2 |
| O8 | `changed`'s `reread:` lines follow the same rule (issue 45; the plan's map) | 6.3; C3 |
| O9 | With `count_extra_dirs`, the groups of `review` not built from the import graph read the counted modules; with it off, as today (issue 44; P2.5; D8 of the plan) | 6.4; D1 to D3 |
| O10 | The premise to check: six scripts define `plugin_root`, `checkout_root` and `load_settings`, so the fix may raise the title's count and list nothing (plan, section 3) | 6.4; section 8, "By hand" |
| O11 | dev-tools' own "no baseline" check is `--check --strict` alone (P2.6, C8) | 6.5; E1, E2 |
| O12 | The skill, its references, the page and `.devtools/project.md` say the new behaviour (plan section 5, C8) | 6.6 |
| O13 | One new plugin version for the milestone, taken here (D4 of the plan) | 6.7 |
| O14 | `rules_check.py` stays clean under the linter of pull request 34 if this phase edits it (P3.6's reason, met early) | Section 8, gate G-lint |
| O15 | K5: the verdict changes only in the stale case; K6: the settings key and older installs | 6.2; 6.5 |
| O16 | The index is current when the phase closes | Section 8 |

Inherited from `002-phase-1.md`: nothing this phase discharges. Its open question about
the `--isolated` command is a plan repair for the close.

## 4. The standing rules, bound to this phase

**The plan's rules.**

- **S0.1 With default settings, today's lines and exits stay.** `allow_baseline` defaults
  to `true`: A4 names the two existing baseline tests that run unedited. An entry with no
  `reread:` line is dated and described as today: C1's first half asserts today's
  sentence, except a tie within one second, now settled by history (6.3; r1 F2), pinned
  by `test_a_tie_in_commit_time_is_settled_by_history_without_a_reread_line`. `count_extra_dirs` off: D1's second half. The one exception is D6 of the
  plan, the stale base, and B2 holds every other state to today's summary line.
- **S0.2 A shipped script stands alone.** No import is added to either script.
  `rules_check.py` already runs `components_index.py facts` as a subprocess; it now also
  reads that process's standard error.
- **S0.3 A new test is seen to fail.** Every test of section 8 is written before the
  code it tests and run red; the record pastes the failures.
- **S0.4 An issue is closed by the owner's merge.** The record lists 44, 45 and 46 as
  fixed by this phase's commits. Nothing is posted.

**The project's standing design rules.**

- **A script change comes with a test.** `components_index.py`: `load_settings`,
  `write_or_check`, `main` (`stats`, `changed`, `facts`), `base_snapshot`, the new
  `resolve_base`, `entry_commits`, `review`; `rules_check.py`: `read_facts`. Section 8
  maps each to a test that fails without the change.
- **The plugins are rebuilt, and released under a new version.** `skills/components/`
  changes: `python3 devtools/release_plugins.py bump` (0.1.6 to 0.1.7), and the gate
  `build_plugins.py --check`.
- **A wording change says what prompted it.** Each changed sentence of the skill is
  listed in 6.6 with its issue.
- **Shared skills stay general.** Every added sentence describes a setting, a field or a
  line of the tool, for any project. What is true of dev-tools only (its settings file,
  its gate row) goes in `.devtools/`.
- **Both agents read the same file.** The changed files are `SKILL.md`, `build.md` and
  `review.md` of the components skill. They name commands and settings; no sentence adds
  a path, and the script paths keep the form they have (`scripts/components_index.py`,
  which the plugin build rewrites to `${CLAUDE_PLUGIN_ROOT}` for both tools). Checked by
  `build_plugins.py --check` and `tests/test_plugins.py`.
- **Captures on the site are real output.** The captures of `docs/components.html` show
  `changed` and `review` in states this phase does not change (a base that is not
  behind; entries with no `reread:` line). None is retaken; the record says which were
  compared.
- **The page that describes it is updated too.** `docs/components.html`: 6.6.

## 5. Goal

After this phase: with `"allow_baseline": false`, `components_index.py --check --strict`
exits 1 and names the baseline file while one exists, and `stats --write-baseline` exits
1 and writes nothing; without the setting both exit as today. `changed --base <branch>`
and `facts --base <branch>` compare with the branch's remote-tracking branch when the
local one is strictly behind it, say so in one line, and start no fetch. `review` does
not list an entry whose `reread:` line is newer than the last commit to its modules.
With `count_extra_dirs`, `review`'s same-name, no-docstring and over-12-modules groups
and its summary read the counted modules. The gates of section 8 exit 0.

## 6. Design

**Reuse.**

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Refuse a baseline | `search baseline of unassigned modules`; `git grep -n unassigned-baseline` | `components.index`: `write_or_check` (`:951`), `stats` in `main` (`:1611`) | **adapt** both |
| A boolean setting | `search read a settings file`; `git grep -n count_extra_dirs skills/components` | `load_settings` (`:79`), which already checks `count_extra_dirs` | **adapt** |
| Resolve the base of a comparison | `search files changed since the merge base`; `git grep -n "origin/" skills/` | `base_snapshot` (`:1079`), used by `changed` and `facts`. `phase_tool.merge_base` answers for the phase workflow's own base branch, in another script | **adapt** `base_snapshot`; one **new** helper beside it, since a shipped script stands alone (S0.2) |
| Date an entry | `search descriptions older than their code`; `git grep -n entry_commits` | `entry_commits` (`:1256`), read by `review` only | **adapt** |
| The modules a project counts | `search modules every component must cover` | `counted_modules` (`:240`) | **reuse** in `review` |

### 6.1 `allow_baseline` (issue 46)

`skills/components/scripts/components_index.py`, about 20 lines.

- `DEFAULT_SETTINGS` gains `'allow_baseline': True`, with a comment. `load_settings`
  refuses a value that is not a boolean: `<path>: allow_baseline must be true or false`,
  the wording `count_extra_dirs` has.
- `write_or_check`, under `--check --strict` only: when the setting is `false` and
  `<docs_dir>/unassigned-baseline.txt` exists, it prints

      baseline refused: <docs_dir>/unassigned-baseline.txt exists and allow_baseline is false (give its modules a component, then delete the file)

  excuses nothing the file names (so each such module also gets its `no component:`
  line), and exits 1.
- `stats --write-baseline` with the setting `false`: raises the tool's refusal, standard
  error `allow_baseline is false: this project keeps no baseline; give each module a
  component`, exit 1 (D1), and no file is written. Plain `stats` is unchanged.
- `--check` without `--strict`, `changed`, `draft` and `review` do not read the setting:
  none of them reads the baseline today.

| Branch | Setting | Baseline file | `--check --strict` | Case |
|---|---|---|---|---|
| a | absent or `true` | absent | as today | A4 (existing tests) |
| b | absent or `true` | present | excuses its modules, as today | A4, A1 (first half) |
| c | `false` | absent | as today | A1 (last step) |
| d | `false` | present | the line above, a `no component:` line per uncovered module, exit 1 | A1 |
| e | `false` | present, and `--check` without `--strict` | exit 0, no line | A1 |
| f | `false` | `stats --write-baseline` | exit 1, nothing written | A2 |
| g | not a boolean | any command | the settings error | A3 |

### 6.2 The base of `changed` and `facts --base` (issue 45, part 1)

`components_index.py`, about 35 lines; `rules_check.py`, about 4.

```python
def resolve_base(root: Path, base: str) -> tuple[str, str]:
    """The ref to compare with for `base`, and a line to print when it is not the one asked for ('' otherwise)."""
```

Normative order, and this docstring's function is its one home:

1. `base` does not name a commit: `origin/<base>` when that does, else the error of
   today (`no branch or commit named <base>: …`). No line.
2. `base` names a local branch that has an upstream configured. *Corrected 2026-11-23
   (r1 F1): "names a local branch" means git itself reads the name as one
   (`git rev-parse --symbolic-full-name <base>` prints `refs/heads/…`), so a tag of the
   same name wins, as it does in git, and a branch given in full (`refs/heads/main`) is
   read like its short name. Prior wording: "(`refs/heads/<base>` resolves)", which took a
   same-named branch even when git read the name as a tag.* The branch is one (`git rev-parse --abbrev-ref <base>@{upstream}` answers, and that ref
   resolves), and the local branch is **strictly behind** it: the two commits differ and
   the merge base of the two is the local one. The upstream is used, and the line is

       <base> (<7 hex>) is <N> commit(s) behind <upstream> (<7 hex>): comparing with <upstream>

3. Anything else: `base`, as given. No line. That covers a local branch level with,
   ahead of or diverged from its upstream, one with no upstream, a remote-tracking
   branch, a tag and a commit id.

Only the branch's own configured upstream counts (D3). Every git command reads:
`rev-parse`, `merge-base`, `rev-list --count`. Nothing fetches.

- `base_snapshot` calls it and returns the line as a sixth item.
- `changed` prints `note: <the line>` immediately before its summary line, whose
  `changed against <ref> (<commit>)` already names the ref used. Its exit is decided as
  today, from what it found against that ref.
- `facts(root, base='', modules=False, notes=None)`: when `notes` is a list, the line is
  appended to it. `main` prints each as `note: <the line>` on **standard error**, so
  standard output stays the one JSON document, and `--out FILE` holds only the document.
  The document's `revision` is the merge base that was used, as today.
- `rules_check.py`, `read_facts`: after a run of the index script that exited 0, each
  line of its standard error that starts with `note: ` is written to this script's
  standard error. `check --base` then judges against the base the index script used,
  which is all it ever did.

| Branch | State of `<base>` | Ref used | Line | Case |
|---|---|---|---|---|
| a | local branch, strictly behind its upstream | the upstream | yes | B1 |
| b | local branch, level with its upstream | the branch | no | B2 |
| c | local branch, ahead of its upstream | the branch | no | B2 |
| d | local branch, diverged from its upstream | the branch | no | B2 |
| e | local branch, no upstream configured, a remote branch of the same name ahead | the branch | no | B2 |
| f | a commit id | the commit | no | B2 |
| g | `origin/<name>` given | as given | no | B2 |
| h | no such name, `origin/<base>` exists | `origin/<base>`, as today | no | existing behaviour; B2 |
| i | no such name at all | the error of today | -- | existing test, unedited |
| j | `facts --base` in state a | the upstream; the line on standard error | yes | B4 |
| k | `rules_check.py check --base` in state a | the upstream; the line relayed | yes | B5 |

### 6.3 The `reread:` line (issue 45, part 2)

`components_index.py`, about 12 lines.

- An entry may carry `- reread: <text>`. The text is the author's: the date, the commit
  read against, and "still accurate". The script does not read it.
- `entry_commits` dates an entry by the newest of its `does`, `verbs`, `flow` **and
  `reread`** lines, by the commit that last changed the line (git blame, as today), and
  returns which kind of line that was. An uncommitted line counts as edited now, as
  today.
- `review`'s lead keeps today's sentence when the newest line is `does`, `verbs` or
  `flow`: `… since <commit> (<day>), when its does and verbs were last edited`.
- *Added 2026-11-23 (J10; r1 F2):* lines committed in the same second are ordered by
  history: the commit that has the other in its history is newer. This applies to the
  `does`, `verbs` and `flow` lines too, so it is an exception to S0.1: an entry whose
  `does` or `verbs` was edited in the same commit as its code, within one second of the
  entry's other lines, was listed before (the blame order decided) and is not now. When it
  is the `reread` line: `… since <commit> (<day>), when it was last marked as reread`.
- `reread` joins `CHECKED`: written twice in one entry it is refused, as `does` is.
- `changed` already compares every hand-written field of an entry with the base, so an
  entry whose `reread:` line was added or edited in the change gets no `reread:` line
  from `changed`. No code changes for that; C3 pins it.

| Branch | Case |
|---|---|
| a. no `reread:` line: dated as today, today's sentence | C1 (first step) |
| b. a `reread:` line committed after the last commit to the modules: not listed | C1 |
| c. a later commit to a module: listed again, with the new sentence | C1 |
| d. a `reread:` line not committed yet: not listed | C1 |
| e. two `reread:` lines: refused | C2 |
| f. `changed`: an edited `reread:` line counts as an edited entry | C3 |
| g. `write` and `--check` keep the line and stay current | C1 |

### 6.4 `review` over the counted modules (issue 44)

`components_index.py`, `review`, about 12 lines changed.

`package` stays what it is, the modules of `package_dir`: the import graph is built from
it. A second list, `counted = counted_modules(root)`, is what these read:

- the owners table (which components hold a module);
- the loop that collects each module's public names, whether it has a docstring, and
  whether it defines `main`;
- the pairs settled by `duplicates:`;
- "The same public name in two or three components";
- "Modules with no docstring";
- "Components that cover more than 12 modules";
- the `(defines main)` label of "Components nothing in the package imports" (D5): the
  label is read from the module, though the group is built from the graph;
- the summary's `<N> module(s)`.

Unchanged, and still read from `package`: components that import each other, loops,
"Modules nothing in the package imports, inside a component that is used", the test
files group, flow steps. With `count_extra_dirs` off, `counted` is `package`, and every
line is today's.

The rule that a name defined in four or more modules is a convention, counted in the
title and not listed, is unchanged (O10).

### 6.5 dev-tools' own files

- `.devtools/components_index.settings.json`: `"allow_baseline": false`.
- `tests/test_own_index.py`: `problems` no longer looks for the file itself;
  `test_a_baseline_is_refused` writes a baseline by hand and expects the tool's line;
  one new test, that `stats --write-baseline` is refused here.
- `.devtools/project.md`: the gate row says the strict check also refuses a baseline;
  the note about installed plugins names 0.1.7 and `allow_baseline`.
- `.devtools/components/COMPONENTS.md`: `components.index` (its `does` and `verbs` gain
  the setting, the stale base and the `reread:` line), and `components.rules`, which this
  phase edits and whose entry `review` lists as older than its code: it is read beside
  this phase's diff and the one commit `review` names, and gets a `reread:` line or an
  edit, whichever is true (D6).

### 6.6 The skill, its references and the page

Each change, and what prompted it:

| File | Sentence | Change | Prompted by |
|---|---|---|---|
| `skills/components/SKILL.md` | the settings list | adds `allow_baseline` (true or false, default true; from plugin 0.1.7) and what `false` does | issue 46 |
| same | `--check` row | with `allow_baseline` false, `--strict` fails while a baseline file exists | issue 46 |
| same | `stats` row | `--write-baseline` is refused when `allow_baseline` is false | issue 46 |
| same | `changed` row | which ref is used when the base is a local branch behind its remote-tracking branch, the `note:` line, and that nothing fetches | issue 45 |
| same | `review` row | the first group counts from the entry's `does`, `verbs` or `reread` line; which groups read the folders `count_extra_dirs` counts | issues 45, 44 |
| same | the field table | a `reread` row | issue 45 |
| same | "Before a PR", the `reread:` bullet | when the entry is still accurate: add or update its `reread:` line, where it said only to say so in the PR body | issue 45 |
| `references/review.md` | "Descriptions older than their code" row | a `reread:` line also resets the lead; when to write one | issue 45 |
| same | "The same public name…" row | reads the counted folders when the setting is on | issue 44 |
| `references/build.md` | step 5 | a project that has reached full coverage sets `allow_baseline` to false | issue 46 |
| `docs/components.html` | the paragraph on the strict check, and the one on review | one sentence each: a project can refuse a baseline; an entry reread and found true is marked, not edited | issues 46, 45 |

### 6.7 The plugins

`python3 devtools/release_plugins.py bump`: `devtools/PLUGIN_VERSION` from 0.1.6 to
0.1.7, `plugins/` rebuilt. Run again with `python3 devtools/build_plugins.py` after any
later edit of a skill file in this phase; the version stays 0.1.7.

## 7. Decisions

Ruled 2026-11-23 by delegated approval (auto=true), each as proposed (d). See "Owner gate".

| # | Question | Readings and their cost | Proposed |
|---|---|---|---|
| D1 | The exit of a refused `stats --write-baseline` | **1:** the code this script gives every refusal (`main` turns `ValueError` into exit 1, as for a baseline that would grow); the plan's P2.1 said 2, which this script uses for nothing. **2:** as the plan wrote; one command of the script would then exit by another rule than the rest | Ruled: 1 (d). A plan repair for the close |
| D2 | Where the stale-base line goes | **`changed`: standard output, as `note:`, before the summary; `facts`: standard error; `rules_check.py` relays it to standard error:** the JSON of `facts` and of `rules_check.py --format json` stays clean. **Standard output everywhere:** breaks both JSON outputs | Ruled: as the first reading (d) |
| D3 | What "its remote-tracking branch" is | **The branch's configured upstream:** what git itself calls it; a branch with none is read as today. **Also `origin/<name>` when no upstream is set:** catches more stale bases, and guesses a remote the branch may not track | Ruled: the configured upstream (d) |
| D4 | The lead's sentence for an entry dated by its `reread:` line | **A sentence of its own ("when it was last marked as reread"):** the reader knows the entry was not edited. **Today's sentence for both:** it would say `does` and `verbs` were edited when they were not | Ruled: its own sentence (d) |
| D5 | The `(defines main)` label | **Read from the counted modules too:** a script in a counted folder that defines `main` is labelled an entry point, which it is. **From `package_dir` only:** every script of `skills/` reads as possibly unused | Ruled: the counted modules (d) |
| D6 | dev-tools' entries that `review` lists as older than their code | **Reread the entry of each script this phase edits, and mark it:** uses the field on real entries. **Mark all three listed now:** would mark `sync.copies` and `handoff.notes` without reading them beside their commits, which is what the field must never record | Ruled: only what this phase rereads (d) |

## 8. Tests

Expected exit of every pytest command: 0. All in `tests/test_tools.py` unless said; each
works in the synced `project` fixture, with the settings file beside the script.

| # | Case | Asserts | Branch |
|---|---|---|---|
| A1 | `test_strict_check_refuses_a_baseline_when_the_setting_says_so` | An uncovered module and `stats --write-baseline`: `--check --strict` exits 0 (today). Then `allow_baseline: false`: exit 1, the `baseline refused:` line and `no component: <path>`; `--check` alone exits 0 with neither line. Then the module is given a component and the file deleted: exit 0 | 6.1 b, d, e, c |
| A2 | `test_no_baseline_is_written_when_the_setting_refuses_one` | `allow_baseline: false`, an uncovered module: `stats --write-baseline` exits 1 with the message, and no file exists; `stats` exits 0 | 6.1 f |
| A3 | `test_allow_baseline_must_be_a_boolean` | `"allow_baseline": "no"`: non-zero, `allow_baseline must be true or false` | 6.1 g |
| A4 | `test_the_baseline_can_hold_a_module_of_a_counted_extra_folder`, `test_the_baseline_cannot_take_a_new_module_in_exchange_for_an_old_one`, existing | unedited, exit as today | 6.1 a, b; S0.1 |
| B1 | `test_changed_compares_with_the_upstream_of_a_base_that_is_behind` | A project with a remote under `tmp_path`, `main` tracking `origin/main`, the local `main` one commit behind it, and the work on a branch cut from `origin/main`: `changed --base main` prints `note: main (<a>) is 1 commit(s) behind origin/main (<b>): comparing with origin/main` and then `changed against origin/main (<b>): <N> file(s) differ…`, the summary `changed --base origin/main` prints | 6.2 a |
| B2 | `test_changed_reads_every_other_base_as_it_is`, parameters: level, ahead, diverged, no upstream, a commit id, `origin/main` given, a name only the remote has | No `note:` line; the summary names the ref today's code names (`main`, the commit id, `origin/main`) | 6.2 b to h |
| B3 | `test_no_command_of_the_index_fetches` | With a `git` first on `PATH` that records its arguments and runs the real one: after `changed --base main` and `facts --base main` in state a, no recorded command is `fetch`, `pull` or `remote` | O5 |
| B4 | `test_facts_follow_the_same_base_and_stay_one_json_document` | In state a: standard output of `facts --base main` parses as JSON and equals that of `facts --base origin/main`; standard error holds the `note:` line; with `--out FILE` the file holds the document and nothing else | 6.2 j |
| B5 | `test_the_rule_check_says_which_base_it_judged_against` | In state a, with the stand-in `gnd`: `rules_check.py check --base main` writes the `note:` line to standard error, and its standard output is what `check --base origin/main` prints | 6.2 k |
| C1 | `test_a_reread_line_brings_an_entrys_date_forward` | An entry and its module committed; a commit to the module: `review` lists the entry with today's sentence. A `reread:` line added: not listed while uncommitted, and not after it is committed; `--check` exits 0. A later commit to the module: listed, with `when it was last marked as reread` | 6.3 a, b, c, d, g |
| C2 | `test_a_reread_line_written_twice_is_refused` | Two `reread:` lines in one entry: `--check` exits 1 and names the repeated field | 6.3 e |
| C3 | `test_changed_takes_a_reread_line_as_an_edit_of_the_entry` | A module changed since the base: `changed` prints `reread: <id>`. With a `reread:` line added to the entry: it does not. A pin: no code changes for it | 6.3 f |
| D1 | `test_review_reads_the_counted_folders_for_names_and_docstrings` | `count_extra_dirs` on; `tools/report.py` and a package module, in two components, both define `report`; a second module of `tools/` has no docstring: the same-name group lists `report` with both paths, the no-docstring group lists the module, the summary counts the modules of both folders. With the setting off and the same files: the same-name group is `(0)` and the summary counts the package alone | 6.4; S0.1 |
| D2 | `test_review_sizes_a_component_by_its_counted_modules` | 13 modules under `tools/` in one component: listed under "more than 12 modules" with the setting on, not with it off | 6.4 |
| D3 | `test_review_labels_an_entry_point_in_a_counted_folder` | A module of `tools/` that defines `main`: its component is listed with `(defines main)` with the setting on, without the label with it off | 6.4; D5 |
| E1 | `tests/test_own_index.py::test_a_baseline_is_refused`, rewritten | A baseline written by hand in the copy: `--check --strict` exits 1 with `baseline refused:`; `problems` reports it from the tool's own line | 6.5; P2.6 |
| E2 | `tests/test_own_index.py::test_no_baseline_can_be_written_here`, new | `stats --write-baseline` in the copy exits 1 and leaves no file | 6.5 |

**Seen to fail** (S0.3): each of A1 to A3, B1, B3 to B5, C1, C2, D1 to D3, E1 and E2 is
run before its code exists, and the failure pasted into the record. B2 and C3 hold
today's behaviour and pass before and after; B2 is also run against a build in which
rule 2 ignores "strictly behind", to see its ahead and diverged cases fail.

**By hand** (O10, and plan section 9):

- `components_index.py review` in dev-tools before and after: the same-name group's
  title and rows, and the summary's module count. What the six scripts' shared names do
  to it is recorded as found.
- In this worktree, whose local `main` is behind `origin/main`:
  `components_index.py changed --base main`, expecting the `note:` line and the count
  that `--base origin/main` gives.

**Gates.**

| Gate | Command | Expected |
|---|---|---|
| Focused | `uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_own_index.py tests/test_plugins.py tests/test_index_cache.py -q` | exit 0 |
| All tests | `uv run --no-project --with pytest python -m pytest tests -q` | exit 0 |
| Plugins | `python3 devtools/build_plugins.py --check` | exit 0 |
| Release status | `python3 devtools/release_plugins.py status` | `0.1.7 is ready`, exit 1 |
| Index | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict` | exit 0, with `allow_baseline` false |
| Index against the base | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base <this spec's commit> --strict` | exit 0; each `reread:` line answered in the record |
| G-lint | `uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml skills/components/scripts/rules_check.py plugins/dvt-phase/skills/components/scripts/rules_check.py plugins/dvt-milestone/skills/components/scripts/rules_check.py` | exit 0, `All checks passed!` |

**Verification selection.** Plan-mandated: the gates above. Direct: `tests/test_tools.py`
and `tests/test_own_index.py`. Impact closure: `tests/test_plugins.py` (the plugin copies
of both scripts) and `tests/test_index_cache.py` (it loads the index script). The full
suite is the repository's only broad lane and the plan names it for this phase.

## 9. Out of scope for this phase

- The import graph and every group of `review` built from it. Issue 39.
- Preferring a remote-tracking branch for a base that is ahead or diverged, or guessing
  one for a branch with no upstream.
- `phase_tool.py`'s own base resolution.
- A date or a commit the script would parse out of a `reread:` line.
- Rereading `sync.copies` and `handoff.notes` (D6).
- The exit of a settings file a script cannot use: issue 43, phase 3. A3's "non-zero"
  is written so that phase 3 can change the code without editing the test.
- Retaking captures of `docs/components.html`.

## 10. Size

Estimate at write time: about 85 lines of source (`components_index.py` 80,
`rules_check.py` 5), about 260 lines of tests, about 25 changed lines across the skill,
its references and the page, and the generated files (`plugins/`, the index pages).

## 11. Approval instrument

This prose. The phase adds an exit and a setting's validation, for which
`review-convergence.md` makes a corpus the default. Prose is chosen because the expected
lines and exits are written out literally in 6.1 to 6.3 and section 8, and every test is
written and seen red before its code: the red tests are the corpus, in the test file
where the suite keeps running them.

## Owner gate

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/issue-sweep/notes/phase-2-spec.md
    sha256: in the phase record, 003-phase-2.md (a file cannot hold its own digest)
    date: 2026-11-23
    authorization: the owner's "process-milestone issue-sweep auto", for the milestone
      issue-sweep only
    scope: this spec and its amendments; the phase's commits over the files it names
    not covered: pushing, the pull request, merging, tagging, releasing, and anything
      posted to GitHub
    instrument: this prose
    decisions: D1 to D6, each as proposed
    spec review: none; omitted unless a concrete uncertainty needs one
    phase review: review_tool.py, --subject phase, reviewer Codex; at most two rounds
      (r1, r2), declared here before either has run

This is an agent's ruling under the owner's delegation. It is not the owner's own
reading of the spec.

**Implementability sweep.**

| Requirement | Answer |
|---|---|
| `--check --strict` reads the setting (6.1) | Yes: `write_or_check` already reads the baseline file there, and `SETTINGS` is module-level |
| "Strictly behind" from read-only git (6.2) | Yes: `git merge-base <a> <b>` printing `<a>`'s commit while the two differ. The script's `git` helper returns no exit code when `check` is off, so the rule is written on outputs |
| A branch's upstream without a fetch | Yes: `git rev-parse --abbrev-ref main@{upstream}` answered `origin/main` in this worktree on 2026-11-23 |
| The line on standard error for `facts` | Yes: `main` owns the printing; `facts` returns the document |
| `rules_check.py` relays it | Yes: `run` captures the index script's standard error already |
| An entry dated by a new line (6.3) | Yes: `entry_commits` reads blame line by line and already filters by field name |
| B1's fixture: a local `main` behind its upstream | Yes: a bare clone under `tmp_path` as `origin`, a commit pushed, and `git branch -f main <the commit before>` from another branch |
| B3 can fail | Yes: a build that fetched would add a `fetch` line to the recording |
| D1 with the setting off | An entry may name a module outside `package_dir` today (`module_graph` takes it), so the two components exist in both runs |
| E1 without `stats --write-baseline` | Yes: the baseline is a text file of paths; the test writes it |

## Implementation findings, recorded as they were found

All on 2026-11-23, on the phase's base `361b2cc`.

- **J1. Red first (S0.3).** Before any code: 11 of the new tests failed, each for the
  reason it names (the missing `baseline refused:` line; the missing refusal message; the
  missing settings error; `changed against main (…): 2 file(s) differ` with no `note:`;
  two different `facts` documents; no `note:` on the rule check's standard error; the
  entry still listed after its `reread:` line; no `reread appears twice`; and the three
  `review` groups at `(0)` or without the label). The rest passed before, as pins: B2's
  seven cases, C3, and the `count_extra_dirs: false` half of D1 to D3.
- **J2. B3 cannot fail before the change, and the spec said it would.** Today's code
  fetches nothing, so the test of "nothing fetches" passes on the base. Section 8 listed
  it among the tests seen red; that was wrong. It is held instead by a negative control:
  a build whose `resolve_base` runs `git fetch` made B3 fail (`assert not ['-C … fetch
  --quiet']`). B2 likewise: a build that took any upstream that differs, ignoring
  "strictly behind", failed its `ahead` and `diverged` cases. Both builds were the
  script with one line changed, restored byte for byte after (same SHA-256).
- **J3. A defect of this phase's own, caught by B2.** `base_snapshot` named the stale-base
  line `line`; the loop over `git diff` lines below it reuses that name, so on any base
  with a differing file the line printed as `note: A	src/widget/later.py`. Renamed
  `said`. B1 had passed, because nothing differed in its state.
- **J4. B5's expectation was wrong.** `rules_check.py check --base main` prints its
  summary as `rules against main (<commit>)`: it names the base as given, and the commit
  the facts were read at, which is origin/main's. The spec expected standard output equal
  to that of `--base origin/main`, which names `origin/main`. The test now asserts the
  note on standard error, the commit in the summary, and that the outputs differ only in
  that name. Making `rules_check.py` print the resolved name would mean parsing its
  sibling's message; not done. An open question for the close.
- **J5. D1's expected module count was wrong.** The fixture has four counted modules, not
  five; a counting error in the test, corrected.
- **J6. dev-tools' own tests needed the rebuild first (K6, as the plan foresaw).** With
  `allow_baseline` in `.devtools/components_index.settings.json`, the built copy under
  `plugins/` still refused the key until `release_plugins.py bump` rebuilt it (0.1.7).
- **J7. What `review` says in dev-tools now (O10).** The same-name group went from
  `(0)` over 4 modules to `(13)` over 12, and its title says `4 name(s) defined in four
  or more modules are left out`: the three names issue 44 named, and a fourth, are
  conventions, counted and not listed, as the plan's premise said. The 13 listed are
  leads for a review of the index (`cell`, `find_root`, `read_json`, `Stop`, …), not
  failures; this phase settles none of them. `review` exits 0.
- **J8. Entries reread (D6).** `components.rules` and `subsystem.rule_check`, whose code
  this phase changed, and `migrate.from_gsd`, which `review` listed after phase 1's
  change: each read beside the commits concerned, each still true, each given a
  `reread:` line. `components.index` was edited instead (its `does` and `verbs` gained
  the three behaviours). `sync.copies` and `handoff.notes` stay listed: not reread here.
- **J9. The by-hand gate.** In this worktree, whose local `main` is 99 commits behind:
  `changed --base main` printed `note: main (b685e82) is 99 commit(s) behind origin/main
  (cecebc6): comparing with origin/main` and `changed against origin/main (cecebc6): 36
  file(s) differ`, the count `--base origin/main` gives. Before the change it judged 263
  files.
- **J10. A defect of this phase's own, found by the full suite.** The first full run
  after the work printed `1 failed, 494 passed`: C1 failed about two runs in three. The
  dating compares commit times with a strict `>`, and a `reread:` line committed in the
  same second as the entry's `does` line lost the tie, so the entry stayed listed. The
  commit `ed88315` was first made with a message that said the suite had passed; that
  message was written before the output was read, and was corrected before anything
  else was built on the commit. Repaired: `entry_commits` breaks a tie by history (the
  commit that has the other in its history is newer). Regression test:
  `test_a_reread_line_committed_in_the_same_second_still_counts`, which fixes every
  commit's time to one second and failed on three of three runs before the repair.
  Rule 3 of the order of `entry_commits` is now: newest by commit time, ties settled by
  ancestry.

## Phase review round 1 (r1)

`notes/reviews/phase-2-r1`, 2026-11-23: the review helper with `--subject phase --base
361b2cc`, reviewer Codex, read-only, effort `high`, over the diff and 29 files; brief
SHA-256 `eb7a86756fa77ee04171505dbf662a701a9ff59653519463ed1a92385f8231d6`. `VERDICT:
CHANGES_REQUESTED`, 2 findings. One reviewer is one reviewer. It ran no test (read-only;
pytest was not in its environment) and could not repeat the negative controls.

- **F1 (blocking), reproduced.** With a tag `main` and a local branch `main` behind its
  upstream, git reads `main` as the tag, and `resolve_base` substituted `origin/main` with
  a note. Reproduced in a scratch repository (`git rev-parse main` gave the tag's commit
  with `refname 'main' is ambiguous`) and by the new case "a tag of the same name" of B2,
  red before the repair. Repaired: rule 2 reads the name through `git rev-parse
  --symbolic-full-name`, which refuses an ambiguous name. The reviewer also noted that
  `refs/heads/main` was not read as the branch; that is now held by
  `test_changed_reads_a_branch_named_in_full_like_its_short_name`, also red before. B2
  gained "a tag" as well.
- **F2 (hardening), reproduced.** The tie rule of J10 also orders `does` and `verbs`, so a
  default-settings output changed: an entry whose `verbs` was edited with its code within
  one second of being written was listed before and is not now. Reproduced with every
  commit's time fixed to one second: listed on the code before the tie rule, not after.
  The behaviour is kept, because the earlier answer depended on the order of blame lines;
  the spec now names it as an exception to S0.1 (4, 6.3), and
  `test_a_tie_in_commit_time_is_settled_by_history_without_a_reread_line` pins it.

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 | 1 (Codex) | 2 | 0 / 2 (first round) | 1 / 2 | blocking | CHANGES_REQUESTED |

Round 2 is not run. F1's repair is one rule of one function, held by two cases seen red;
F2 changed no code. The repaired bytes carry no review opinion.

