# Phase 3 spec: starter rules that pass where they are written, and scripts that exit as they say

## 1. Status

Owner-decided (2026-11-23), by delegated approval (auto=true); recorded below, under
"Owner gate". Phase 2 is recorded (`003-phase-2.md`). Implementation may begin.

## 2. Provenance

- Derives from `notes/issue-sweep-plan.md`, approved at SHA-256 `309c6e55…81a4`
  (`001-plan.md`): section 2 ("Phase 3"), section 4 (P3.1 to P3.6, P3.4b), sections 5, 6
  (K7, K9) and 9; the owner's rulings D9, D10 and D11.
- Plan review r1 F1 added D11 and P3.4b, and r1 F2 added P3.6; those repairs are
  unreviewed.
- Issues 33 and 43, as kept in `notes/issues-2026-11-23.md`.
- The code at `a981377`, phase 2's head.
- No review round has read this spec.

Tags: `(o)` an owner ruling, `(d)` a delegated ruling (auto=true), `(rN)` review round N.

## 3. Obligations

| # | Obligation (source) | Discharged in |
|---|---|---|
| O1 | For each plugin, `rules_check.py init` then `test` in a new project exits 0 and prints `0 wrong` (issue 33; C5; P3.1) | 6.1; T1 |
| O2 | Where there is no phase tool, `test` leaves out a rule about plans, says so in one `skip:` line, and leaves it out of what `gnd synth` is given (plan section 2; D9) | 6.1; T2 |
| O3 | A rule that names an unknown fact type and is not about plans is still `wrong` (P3.2) | T3 |
| O4 | With the phase tool present, `test` prints what it prints today (P3.3, S0.1) | T4 and the existing tests |
| O5 | A test that would catch issue 33 again (issue 33, "What would fix it") | T1 |
| O6 | A settings file a script cannot use exits 2, with the message on standard error, in every script under `skills/` that reads one (D10; P3.4) | 6.2; T5 to T8 |
| O7 | `phase_tool.py`: one JSON envelope with `"ok": false` under `--format json`, exit 2, for every command, `status` too (D11; P3.4b) | 6.3; T9 |
| O8 | The four docstrings say what the code does, each checked against a run (issue 43; P3.5) | 6.4; section 8, "By hand" |
| O9 | `rules_check.py`, `review_tool.py` and `handoff.py`, and their plugin copies, stay clean under the linter of pull request 34 (P3.6) | Section 8, gate G-lint |
| O10 | K7: every reader of each script's exit is listed before the exit changes | 6.2, "Readers" |
| O11 | The skill and the page say what `test` now does and what a broken settings file does (plan section 5) | 6.5 |
| O12 | The plugins are rebuilt under 0.1.7 (D4 of the plan: one version for the milestone) | 6.6 |
| O13 | The index entries whose notes quote the wrong docstrings are corrected (plan section 4) | 6.6 |

Inherited from `003-phase-2.md`: A3 of phase 2 was written "non-zero" so this phase could
change the exit without editing it; it stays as it is.

## 4. The standing rules, bound to this phase

**The plan's rules.**

- **S0.1 With default settings, today's lines and exits stay.** Where the phase tool is
  there, `test` is unchanged (T4, and the existing `rules_check.py test` tests, unedited).
  The exit for a settings file a script cannot use changes from 1 to 2: D10 of the plan
  names it. No line a working settings file reaches changes.
- **S0.2 A shipped script stands alone.** Each of the five scripts gets its own few lines;
  none imports another.
- **S0.3 A new test is seen to fail.** Every test of section 8 is run before its code.
- **S0.4 An issue is closed by the owner's merge.** The record lists 33 and 43. Nothing is
  posted.

**The project's standing design rules.**

- **A script change comes with a test.** `rules_check.py` (`test`, `load_settings`),
  `components_index.py` (`load_settings`), `review_tool.py` (`load_settings`),
  `handoff.py` (`load_settings`), `phase_tool.py` (`load_settings`, its checks, `main`),
  and the docstrings of those and of `coder_pool.py` and `devtools/from_gsd.py`. Section 8
  maps each code change to a test that fails without it.
- **The plugins are rebuilt, and released under a new version.** Skills change; the
  version is already 0.1.7, unreleased, from phase 2 (D4 of the plan): `build_plugins.py`
  rebuilds, and the gate is `build_plugins.py --check`.
- **A wording change says what prompted it.** 6.5 lists each changed sentence with its
  issue.
- **Shared skills stay general.** The sentences describe the scripts, for any project.
- **Both agents read the same file.** `references/rules.md` and the components `SKILL.md`
  change; they name commands and exits, no path that differs between the tools. Checked by
  `build_plugins.py --check` and `tests/test_plugins.py`.
- **Captures on the site are real output.** `docs/rules.html` shows no capture of `test`;
  a sentence is added, no capture.
- **The page that describes it is updated too.** `docs/rules.html`: 6.5.

## 5. Goal

After this phase: in a new project, `rules_check.py init` then `rules_check.py test`
exits 0 and prints `0 wrong` with the copy of either plugin, and with dvt-milestone's it
prints one `skip:` line naming the rule about plans. A settings file that
`rules_check.py`, `components_index.py`, `review_tool.py` or `handoff.py` cannot use
(an unknown key, a wrong value, text that is not a JSON object) makes it exit 2 with the
message on standard error and no traceback; `phase_tool.py` prints one envelope with
`"ok": false` and exits 2, for `status` too. The docstrings of issue 43 say what the code
does. The gates of section 8 exit 0.

## 6. Design

**Reuse.**

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Know whether the phase tool is here | `search starter rules file`; `git grep -n phase_script skills/components` | `rules_check.vocabulary` and `read_plan_facts` already test `(root / SETTINGS['phase_script']).is_file()` | **reuse** that test |
| Read a settings file | `search read a settings file`; `git grep -n "def load_settings" skills` | Six copies of `load_settings`, one per script; same first lines, each its own checks | **adapt** each in place (S0.2) |
| Report an error as an envelope | `search one JSON envelope`; `git grep -n "error={" skills/phase` | `phase_tool.main` builds every envelope, `ToolError` carries code and hint | **adapt** `main` |
| A command that could not run | `git grep -n "class Stop" skills` | `review_tool.Stop`, caught in `main` as exit 2 | **reuse** in `review_tool.py` |

### 6.1 `rules_check.py test` without the phase tool (issue 33)

About 15 lines in `test`.

- `plans_here = (root / SETTINGS['phase_script']).is_file()`.
- When it is false, the rules with `"about": "plans"` are left out of the loop over the
  examples and out of what `generated` gives `gnd synth`. For each, before the other
  results:

      skip: <rule id>: a rule about plans, and <phase_script> is not here (it is judged where the phase tool is installed)

- The summary counts the rules judged, and when any were left out adds
  `; <N> rule(s) about plans skipped`. With `--format json` the results carry the same
  `skip` rows, with `"level": "skip"`.
- When it is true, nothing changes.
- `init` is unchanged: it writes the rule about plans in every project (D9).

| Branch | Phase tool | Rule | `test` | Case |
|---|---|---|---|---|
| a | absent | about plans | one `skip:` line, not judged, not given to `gnd synth` | T1, T2 |
| b | absent | not about plans, names a fact type of the plans | `wrong:`, as today | T3 |
| c | present | about plans | judged, as today | T4 |
| d | absent | not about plans, fine | judged, as today | T1, T2 |

### 6.2 A settings file a script cannot use (issue 43, D10)

Each of `rules_check.py`, `components_index.py`, `handoff.py`: `load_settings` ends the
script through one helper of its own,

```python
def settings_error(message: str) -> NoReturn:
    """A settings file this script cannot use: say why on standard error and exit 2, the code for a command
    that could not run."""
    print(message, file=sys.stderr)
    raise SystemExit(2)
```

for each refusal it has today, and for three it does not have: a value whose type is not
its default's, or a list that holds anything but strings (`<path>: <key> must be a string`,
`true or false`, `a whole number`, `a list of strings`; *added 2026-11-23, r1 F1 and F2*),
text that is not JSON
(`<path>: not valid JSON: <the parser's message>`) and JSON that is not an object
(`<path>: the settings must be a JSON object`). Today the first ends in a traceback.

`review_tool.py`: `load_settings` raises its own `Stop` with the same messages; `main`
already prints `error: <message>` on standard error and returns 2.

`coder_pool.py` is **not** changed (D1). Its docstring already says "1 a settings or
configuration file cannot be used, 2 usage error", and its pool's TOML files share that
code; moving the settings file alone to 2 would split one documented code in two.

**Readers** of each exit (K7), found by `git grep` over `skills/`, `devtools/`, `tests/`
and `docs/`:

| Script | Readers of its exit | Effect |
|---|---|---|
| `components_index.py` | `rules_check.read_facts` (any non-zero is "could not run"); the gate rows of `.devtools/project.md`; `tests/test_tools.py` (`!= 0`) | none: every reader treats any non-zero as a failure |
| `rules_check.py` | the components skill (`2 when the check did not run`); `tests/test_tools.py` | the skill's sentence becomes true for this case |
| `review_tool.py` | `tests/test_review_tool.py:367` (`== 1`); `tests/test_plugins.py:140` (`!= 0`) | the first test changes to 2 |
| `handoff.py` | `tests/test_handoff.py:457` (`!= 0`) | none |
| `phase_tool.py` | `tests/test_tools.py:482` (`== 1`); `rules_check.vocabulary` (catches `SystemExit` at import) | the test changes to 2; the import no longer exits (6.3) |

### 6.3 `phase_tool.py`'s envelope (D11)

About 20 lines. The settings are read when the module is loaded; today a bad file ends the
load with `SystemExit`, before `main` can print anything.

- `load_settings` and the three checks that follow it (`skill_check`, `shared_files`,
  `gated_from`) raise `ValueError(<message>)` in place of `SystemExit`, and a text that is
  not a JSON object gets the two messages of 6.2.
- At load: `SETTINGS_ERROR = ''`; on `ValueError` the module keeps `DEFAULT_SETTINGS` and
  sets `SETTINGS_ERROR` to the message, so every constant derived from the settings is
  defined and a caller that only imports the module (the rule check reads its fact types)
  is not stopped.
- `main`: *corrected 2026-11-23 (r1 F3): after parsing, so the format and the command are
  the parser's; prior wording: "before parsing"*, when `SETTINGS_ERROR` is set, the envelope is
  `{"ok": false, "tool": "phase_tool.<command>", "version": …, "data": {}, "error":
  {"code": "SETTINGS", "message": <the message>, "hint": "fix or remove the settings
  file"}}`, printed once in the format asked for, and the exit is 2, for `status` too.
- The docstring's two sentences become true and are kept: every command prints one
  envelope; and `status` exits 0 unless the settings file cannot be used (6.4).

### 6.4 The docstrings (issue 43)

| File | Today | After |
|---|---|---|
| `skills/phase/process-phase/scripts/phase_tool.py` | "Exit codes: 0 ok, 1 domain failure, 2 usage error. ``status`` always exits 0." | "Exit codes: 0 ok, 1 domain failure, 2 usage error or a settings file it cannot use. ``status`` exits 0 unless the settings file cannot be used." The envelope sentence stands, now true |
| `skills/milestone/process-phase/scripts/review_tool.py` | "2 the command could not run (usage, no brief, no git)" | "(usage, no brief, no git, a settings file it cannot use)" |
| `devtools/from_gsd.py` | "It never calls git." | "It never calls git to change anything: every git command it runs only reads." |
| `skills/phase/process-phase/scripts/coder_pool.py` | "and with none left the pool is the Claude Code coder." | "and with none left the pool is the Claude Code coder when ``claude`` is on PATH, and empty otherwise (read the warnings)." |
| `skills/dev-handoff/scripts/handoff.py` | "2 usage error." | "2 usage error or a settings file it cannot use." (not in the issue; the same defect, D10) |

### 6.5 The skill and the page

| File | Change | Prompted by |
|---|---|---|
| `skills/components/references/rules.md`, the `test` paragraph | "Where the phase tool is not installed, a rule about plans is left out with a `skip:` line." | issue 33 |
| same, the settings row | "A settings file the script cannot use stops it with exit 2." | issue 43 |
| `skills/components/SKILL.md`, the settings paragraph | the same sentence for `components_index.settings.json` | issue 43 |
| `docs/rules.html`, the paragraph on examples | one sentence, as in `rules.md` | issue 33 |

### 6.6 The plugins and the index

- `python3 devtools/build_plugins.py`; the version stays 0.1.7.
- `.devtools/components/COMPONENTS.md`: `migrate.from_gsd`'s note "the module docstring's
  'never calls git' is wrong" and any note that quotes the other docstrings are corrected;
  each entry whose code changes is read beside the diff and edited or marked `reread:`.

## 7. Decisions

Ruled 2026-11-23 by delegated approval (auto=true), each as proposed (d). See "Owner gate".

| # | Question | Readings and their cost | Proposed |
|---|---|---|---|
| D1 | `coder_pool.py` under the plan's D10 ("exit 2 in every script under `skills/` that reads one") | **Leave it at 1, and amend D10 for it:** D10's reason ("the code each docstring already gives to 'could not run'") is false here: this docstring gives 1 to settings and configuration alike. **Move it to 2:** its TOML errors stay 1, or move too, which changes the exit of a configuration error the issue does not name | Ruled: leave it at 1 (d). An amendment of the plan's D10, for the close; prior wording kept there |
| D2 | Text that is not JSON, and JSON that is not an object | **Within the same rule, exit 2 with a message:** today each is a traceback, which is the defect class of the issue. **Leave them:** two of the most likely broken files stay a traceback | Ruled: within the rule (d) |
| D3 | What `phase_tool.py` uses when its settings cannot be used | **The defaults, kept for the constants only; every command still refuses with the envelope:** importing the module (the rule check does) never stops. **No defaults:** constants undefined, and the module cannot be imported | Ruled: the defaults (d) |
| D4 | The summary of `test` when rules were skipped | **Count the rules judged, and say how many were skipped:** `0 wrong` stays true and the skip is visible in the last line too. **Count all rules:** the count would include a rule that was not judged | Ruled: as the first reading (d) |

## 8. Tests

Expected exit of every pytest command: 0.

| # | File | Case | Asserts | Branch |
|---|---|---|---|---|
| T1 | `tests/test_plugins.py` | `test_starter_rules_pass_their_own_test_in_each_plugin` (one per plugin; skipped when GND is not installed) | A copy of the plugin, a new project with `src/app/__init__.py`: `components_index.py init`, `rules_check.py init`, `rules_check.py test` exit 0, 0, 0; the last prints `0 wrong`; with dvt-milestone also `skip: plan_names_the_components_it_touches: a rule about plans`, with dvt-phase no `skip:` line | 6.1 a, c, d |
| T2 | `tests/test_tools.py` | `test_a_rule_about_plans_is_skipped_where_the_phase_tool_is_not` | The synced project, the phase tool removed, the stand-in `gnd` with a manifest: the `skip:` line, exit 0, `rule_ids` of the model given to `gnd synth` equal `STARTER_IDS` (no plan rule), the summary ends `; 1 rule(s) about plans skipped`; with `--format json` a result with `"level": "skip"` | 6.1 a, d |
| T3 | `tests/test_tools.py` | `test_a_rule_that_is_not_about_plans_still_names_only_known_facts` | Same project without the phase tool, a rule not about plans whose example names `task_in_plan`: `wrong: … names task_in_plan, which no fact type of this project is`, exit 1 | 6.1 b |
| T4 | `tests/test_tools.py`, existing | `test_rules_are_tested_on_their_own_examples_with_real_gnd` and the test of generated cases (`rule_ids … == STARTER_IDS + [PLAN_RULE]`) | unedited, exit as today | 6.1 c; S0.1 |
| T5 | `tests/test_tools.py` | `test_a_settings_file_the_script_cannot_use_exits_2`, three scripts (`components_index.py`, `rules_check.py`, and `phase_tool.py` in md format) times three files (an unknown key; `{` ; `[]`) | exit 2; the message names the settings file; no `Traceback` | 6.2, 6.3 |
| T6 | `tests/test_review_tool.py` | the existing assertion at line 367, `code == 1`, becomes `code == 2`; a new case with `{` | exit 2, `error: …: not valid JSON` | 6.2 |
| T7 | `tests/test_handoff.py` | the existing assertion at line 457, `!= 0`, becomes `== 2`; a new case with `[]` | exit 2 | 6.2 |
| T8 | `tests/test_tools.py`, existing at line 482 (`shared_files`) | `code == 1` becomes `code == 2` | exit 2 and the message | 6.3 |
| T9 | `tests/test_tools.py` | `test_phase_tool_reports_a_bad_settings_file_in_one_envelope`, for `status`, `check` and `roadmap list` | `--format json`: standard output is one JSON object with `"ok": false`, `error.code == "SETTINGS"` and the file in `error.message`; exit 2 for each, `status` included | 6.3 |
| T10 | `tests/test_tools.py` | `test_the_phase_tool_can_be_loaded_with_a_bad_settings_file` | Loading the module with `importlib` in a project with an unknown key raises nothing, and `FACT_TYPES` is there | 6.3; D3 |
| T11 | `tests/test_tools.py`, existing at line 1932 (`coder_pool.settings.json`) | unedited: `code == 1` | D1 |

**Seen to fail** (S0.3): T1 (with dvt-milestone: `2 wrong`, exit 1), T2, T3 (its exit
and line hold today too: a pin), T5, T6, T7, T8, T9 and T10, each before its code.

**By hand** (P3.5; each pasted into the record):

- `phase_tool.py --format json status` with an unknown key: one envelope, exit 2.
- `review_tool.py status .` with an unknown key: `error: …`, exit 2.
- `coder_pool.py show --json` with a `PATH` that has no `claude`, `codex` or `gemini`:
  `"pool": []`, `"effective_tracks": 0`, exit 0.
- `git grep -n subprocess devtools/from_gsd.py` and each git command it builds: only
  `rev-parse`, `symbolic-ref`, `ls-files`, `check-ignore`.

**Gates.**

| Gate | Command | Expected |
|---|---|---|
| Focused | `uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_plugins.py tests/test_review_tool.py tests/test_handoff.py tests/test_from_gsd.py tests/test_sync.py -q` | exit 0 |
| All tests | `uv run --no-project --with pytest python -m pytest tests -q` | exit 0 |
| Plugins | `python3 devtools/build_plugins.py --check` | exit 0 |
| Release status | `python3 devtools/release_plugins.py status` | `0.1.7 is ready`, exit 1 |
| Index | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict` | exit 0 |
| Index against the base | `… changed --base <this spec's commit> --strict` | exit 0; each `reread:` line answered |
| By hand, issue 33 | the three commands of the issue, with each built plugin, in a new project | `0 wrong`, exit 0, twice |
| G-lint | `uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml` over `rules_check.py`, `review_tool.py`, `handoff.py` and their copies under `plugins/` | exit 0, `All checks passed!` |

**Verification selection.** Plan-mandated: the gates above. Direct: the five test files
the phase edits. Impact closure: `tests/test_sync.py` and `tests/test_from_gsd.py` load
`phase_tool.py` and `from_gsd.py`. The full suite runs: it is the only broad lane and the
plan names it.

## 9. Out of scope for this phase

- `coder_pool.py`'s exits (D1), and the exits of its TOML files.
- `rules_check.py check --phase` without the phase tool: it already refuses with exit 2
  and a sentence that says why (issue 33 calls that intended).
- `init` writing a different set of starter rules per plugin (D9 of the plan).
- The linter's findings in the scripts pull request 34 did not clean (plan, section 3).
- Issue 39 (the index cannot see the load of `phase_tool.py` by `rules_check.py`).

## 10. Size

Estimate at write time: about 70 lines of source across six scripts (15 in
`rules_check.py`, 20 in `phase_tool.py`, about 8 in each of the other three, 4 lines of
docstrings), about 170 lines of tests, about 6 changed lines of the skill and the page,
and the generated files.

## 11. Approval instrument

This prose. The phase changes an exit code, for which `review-convergence.md` makes a
corpus the default; prose is chosen because each expected exit and line is written out in
6.1 to 6.3 and section 8, and every test is written and seen red before its code.

## Owner gate

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/issue-sweep/notes/phase-3-spec.md
    sha256: in the phase record, 004-phase-3.md (a file cannot hold its own digest)
    date: 2026-11-23
    authorization: the owner's "process-milestone issue-sweep auto", for the milestone
      issue-sweep only
    scope: this spec and its amendments; the phase's commits over the files it names
    not covered: pushing, the pull request, merging, tagging, releasing, and anything
      posted to GitHub
    instrument: this prose
    decisions: D1 to D4, each as proposed. D1 amends the plan's D10 for coder_pool.py;
      the plan is repaired at the close with the prior wording kept
    spec review: none; omitted unless a concrete uncertainty needs one
    phase review: review_tool.py, --subject phase, reviewer Codex; at most two rounds
      (r1, r2), declared here before either has run

This is an agent's ruling under the owner's delegation. It is not the owner's own
reading of the spec.

**Implementability sweep.**

| Requirement | Answer |
|---|---|
| `test` knows the phase tool is absent (6.1) | Yes: the same file test `vocabulary` makes |
| The plan rule is kept out of `gnd synth` | Yes: `generated` takes the list of rules it is given |
| Exit 2 at import time (6.2) | Yes: `SystemExit(2)` at import exits 2, as `SystemExit(<text>)` exits 1 today |
| `phase_tool.py` prints an envelope for a load-time error (6.3) | Yes, once the load records the error instead of exiting; `main` already computes the format from `argv` before parsing |
| T1 without GND | Skipped, as the other real-GND tests are; with GND 0.4.0 installed here it runs |
| T9 for `status` | Yes: `main` sets `code = 0` for `status` after the command runs; the settings branch returns before that |

## Implementation findings, recorded as they were found

All on 2026-11-23, on the phase's base `a247f4d`.

- **K1. Red first (S0.3).** Before any code, 17 of the new or changed cases failed, each
  for the reason it names: with dvt-milestone `2 wrong` and exit 1 (with the `gnd synth`
  note about undeclared fact types the plan's baseline recorded); no `skip:` line;
  exit 1, not 2, for every settings case, and a traceback for `{` and `[]`; no envelope
  from `phase_tool.py`; `SystemExit` when loading it. T3 and the dvt-phase case of T1
  passed before, as pins.
- **K2. The lint gate caught this phase's own lines.** `ruff` 0.16.2 with the
  configuration of pull request 34 reported 9 findings over the three scripts and their
  plugin copies: an implicit string concatenation in a tuple (`ISC004`) in
  `rules_check.py`, and two `str.format` calls in `handoff.py` (`UP032`). Fixed in the
  sources and rebuilt; the gate then printed `All checks passed!`. Without P3.6 (plan
  review r1 F2) these would have reached the projects that lint their synced copies.
- **K3. The `skip:` line names the phase tool as the settings name it.** In a plugin
  install that is the absolute path of the plugin's own `phase_tool.py`, as `rules_check.py`
  computes it (`rules_check.py`, the plugin defaults); in a synced project it is the
  relative path. Kept: it says where the script looked.
- **K4. By hand** (P3.5), in scratch projects:
  - issue 33's three commands: dvt-milestone `rules test: 5 rule(s), 10 example(s); 0
    wrong; 1 rule(s) about plans skipped`, exit 0; dvt-phase `rules test: 6 rule(s), 12
    example(s); 0 wrong`, exit 0;
  - `phase_tool.py --format json status` with an unknown key: one envelope, `"code":
    "SETTINGS"`, exit 2;
  - `review_tool.py status .` with an unknown key: `error: …: unknown setting(s): nope`,
    exit 2;
  - `coder_pool.py show --json` with `PATH=/usr/bin:/bin`: `pool []`, `effective_tracks
    0`, the warning `no coder on PATH; ask the user before Implement`, exit 0;
  - `from_gsd.py` builds only `rev-parse`, `symbolic-ref`, `ls-files` and `check-ignore`.
- **K5. Index entries.** The notes of `migrate.from_gsd`, `review.rounds` and
  `phase.state` quoted the wrong docstrings or the old exit; corrected. Six entries whose
  module changed were read beside this phase's diff and given or updated a `reread:`
  line: `components.rules`, `components.index`, `review.rounds`, `phase.state`,
  `phase.coder_pool`, `migrate.from_gsd`. `handoff.notes` was not: it is listed as older
  than its code for four earlier commits this phase did not read, and a `reread:` line
  would claim otherwise.

## Phase review round 1 (r1)

`notes/reviews/phase-3-r1`, 2026-11-23: the review helper with `--subject phase --base
a247f4d`, reviewer Codex, read-only, effort `high`, over the diff and 34 files; brief
SHA-256 `a0dbaefcd587572ce521cb4b8b4d5d49f06b554e867476b6da34c6deeb95fe6b`. `VERDICT:
CHANGES_REQUESTED`, 3 findings. One reviewer is one reviewer. It ran no fresh-project
test and no suite (read-only).

- **F1 (blocking), reproduced.** `phase_tool.py` checked three of its values only:
  `{"package_prefix": 7}` and `{"process_skill": null}` ended the load in a `TypeError`,
  exit 1, no envelope. Reproduced on the built copy in a scratch project. Repaired: every
  value must have its default's type, and a list must hold strings; the load records the
  error and every command prints the envelope.
- **F2 (blocking), reproduced.** The same gap in the other four loaders: `verb_list: []`
  and `index_script: 7` ended in a `TypeError`, exit 1. `handoff.py list` with
  `planning_dir: 7` exited 0 here, because `list` does not read it; `write` does, and is
  the case the test uses. `review_tool.py` with `codex_model: 7` was not run by hand
  before the repair; its test was red. Repaired by the same rule in each loader.
- **F3 (hardening), reproduced.** The settings branch read the format and the command
  from raw tokens: `--for=json status` printed Markdown, and `--root status check`
  named `status`. Repaired: the branch runs after the parser, through `ToolError`, and
  `status`'s exit stays 2 for it.
- Regression tests, each red before its repair: the seven cases of
  `test_a_setting_of_the_wrong_type_exits_2`, the three of
  `test_the_settings_envelope_follows_the_parsed_command_line` (the second only once it
  used the reviewer's own command line), and the added assertions in
  `tests/test_handoff.py` and `tests/test_review_tool.py`.

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 | 1 (Codex) | 3 | 0 / 3 (first round) | 2 / 3 | blocking | CHANGES_REQUESTED |

Round 2 is not run. The repairs are one rule repeated in five loaders and a move of one
branch in `main`, each held by tests seen red. The repaired bytes carry no review
opinion.

- **K6. A defect of the repair, found by the full suite.** The first full run after the
  repairs printed `34 failed, 493 passed`. In `rules_check.py` and `components_index.py`
  the new type loop had been written one level out, after `if path.is_file():` instead of
  inside it, so either script with no settings file at all ended in `UnboundLocalError`.
  The focused selection had missed it: every case it ran wrote a settings file. Fixed;
  the five loaders were then checked by their syntax tree (each loop inside the file
  branch). The 34 tests that failed are its regression tests: among them 27 of
  `tests/test_tools.py` that run `rules_check.py` with no settings file and both cases of
  T1 in `tests/test_plugins.py`. The next full run printed `527 passed`, the same 527
  tests.

