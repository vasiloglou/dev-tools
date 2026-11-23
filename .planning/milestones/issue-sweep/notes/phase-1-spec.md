# Phase 1 spec: the suite tests what it claims, and one list of other planning tools

## 1. Status

Owner-decided (2026-11-23), by delegated approval (auto=true); recorded below, under
"Owner gate". The plan gate is recorded (`001-plan.md`). Implementation may begin.

## 2. Provenance

- Derives from `notes/issue-sweep-plan.md` (draft of 2026-11-23): sections 2 and 4,
  "Phase 1", criteria P1.1 to P1.6, predicates C1 to C3, rules S0.1 to S0.4.
- Issues 31, 41 and 42 of vasiloglou/dev-tools, read on 2026-11-23. None has a comment.
- The code at `cecebc6` (`origin/main`).
- No prior phase record: this is the milestone's first phase.
- **Plan review round 1** (`notes/reviews/plan-r1`, Codex, 2026-11-23) read this spec at
  SHA-256 `9a83000e6048c974…` as one of 22 files, and returned two findings about it, F4
  and F5. Both were reproduced and are repaired here, marked `(r1 F4)` and `(r1 F5)`.
  **The current bytes are not the bytes that round read, and carry no review opinion.**

Tags used when the spec is amended: `(o)` an owner ruling, `(d)` a delegated ruling
(auto=true), `(rN)` review round N.

## 3. Obligations

| # | Obligation | Source | Discharged in |
|---|---|---|---|
| O1 | The guard asks whether `synth --guarded-cases` can run, and skips when GND refuses for want of its extra | Issue 31, "Asked for" | Section 6.1; T1, T3 |
| O2 | A test for the guard, with a fake `gnd` that lists the flag and exits 5 | Issue 31 | T1 |
| O3 | The guard skips for that refusal only | Plan P1.2, K1 | T2 |
| O4 | A test that makes a project with the plugin as its `conftest.py` and checks what is collected: plain `pytest`, `pytest --phase NN`, a named acceptance path | Issue 42 | Section 6.2: one test does this already for the three cases (r1 F5); S1 to S4 check the sets |
| O5 | Each branch of the plugin has a case | Plan P1.3; `standing-rules.md`, "A declared branch with no case that can fail it" | The branch table of section 6.2; S1 to S9 |
| O6 | One list of other planning tools, in one place | Issue 41 | Section 6.3; G1 |
| O7 | The callers of the two `other_plans` functions are looked at first: they return different shapes | Issue 41, "What could break" | Section 6.3, "Callers"; G2 |
| O8 | Every existing test of `tests/test_from_gsd.py` and `tests/test_sync.py` exits as at `cecebc6`, unedited | Plan C3 | Section 8, the focused gate |
| O9 | `review` prints 0 for components with no tests and for same public names | Plan P1.5 | Section 6.4; section 8, gate G-review |
| O10 | No file under `plugins/` changes | Plan P1.6 | Section 4, "The plugins are rebuilt"; section 8 |
| O11 | Each new test is seen to fail | Plan S0.3 | Section 8, "Seen to fail" |
| O12 | The index is current when the phase closes | `.devtools/project.md`, "Gates" | Section 6.4; section 8 |

## 4. The standing rules, bound to this phase

**The plan's rules.**

- **S0.1 With default settings, today's lines and exits stay.** No command a project runs
  changes. `from_gsd.py survey` and `convert` print what they print today: held by the
  existing tests of `tests/test_from_gsd.py`, unedited, and by G2.
- **S0.2 A shipped script stands alone.** No script under `skills/` is edited. The one
  load added is in `devtools/from_gsd.py`, of `devtools/sync.py`, by path. `sync.py` gains
  no import and stays one file.
- **S0.3 A new test is seen to fail.** Section 8, "Seen to fail", names the run for each.
- **S0.4 An issue is closed by the owner's merge.** The record lists 31, 41 and 42 as
  fixed by this phase's commits. Nothing is posted.

**The project's standing design rules.**

- **A script change comes with a test.** `devtools/from_gsd.py`, `other_plans`: G1, which
  fails without the change. No other script changes.
- **The plugins are rebuilt, and released under a new version.** No skill or agent
  changes, so no bump: `build_plugins.py --check` exits 0 and `release_plugins.py status`
  prints the baseline's lines. If S1 to S9 find a defect in `phase_selection.py`, D3 rules
  what happens.
- **A wording change says what prompted it.** No skill sentence changes. Three index
  entries change (section 6.4), each because the code or the tests beside it changed.
- **Shared skills stay general.** Does not apply: no skill is edited.
- **Both agents read the same file.** Does not apply: no skill is edited.
- **Captures on the site are real output.** Does not apply: no command prints anything
  new.
- **The page that describes it is updated too.** Does not apply: no page describes the
  guard, the plugin's tests or where the list is kept.

## 5. Goal

After this phase, `uv run --no-project --with pytest python -m pytest tests -q` exits 0
on a machine whose GND lacks its `synth` extra, reporting one test skipped where it
reported one failed; it exits 0 with no test skipped for that reason where GND has the
extra. `tests/test_phase_selection.py` exits 0 and exits 1 against a copy of the plugin
with any one of its branches broken. `from_gsd.py` holds no list of other planning tools
of its own, and a test that changes `sync.py`'s list sees both scripts follow it.
`components_index.py --check --strict` and `build_plugins.py --check` exit 0.

## 6. Design

**Reuse.**

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Skip a test when GND cannot do what it lists | `search skip a test when an optional dependency is missing`; `search read a settings file`; `git grep -n skipif tests/` | Nothing in the index (tests are not indexed). In `tests/test_tools.py`: `REAL_GND`, `NEWER_GND`, `offered` (`:1333`), `fake_gnd` (`:895`) | **adapt** `fake_gnd`; the guard is **new**, since `offered` reads `--help` and the refusal comes only when the command runs |
| Run a script in a new project under `tmp_path` | `search copy a plugin and run its scripts in a new project`; `git grep -n "def installed" tests/` | `tests/test_plugins.py`, `installed` and `run`. Missed by these searches and found by the plan review (r1 F5): `tests/test_tools.py:1879`, which runs the plugin in the synced `project` fixture | **keep** the existing test; **reuse the shape**, as issue 42 says. The fixture is **new**: a pytest project, not a plugin install |
| The list of other planning tools, and the walk over it | `search signs of other planning tools`; `git grep -n OTHER_PLANS` | `devtools.sync.other_plans` (`:850`) and `devtools.from_gsd.other_plans` (`:489`), in components `sync.copies` and `migrate.from_gsd` | **reuse** `sync.py`'s; `from_gsd.py`'s becomes an adapter over it |
| One `devtools/` script loading another | `git grep -n spec_from_file_location devtools/` | `devtools/release_plugins.py:35` loads `build_plugins.py` by path | **reuse** that way of loading |

### 6.1 The guard for a GND without its `synth` extra (issue 31)

`tests/test_tools.py`, about 25 lines changed or added, and about 45 of tests.

`rules_check.py` is not changed. When `gnd synth --guarded-cases` writes no manifest,
`generated` (`rules_check.py:804`) already returns one note:

    note: gnd synth --guarded-cases built no cases (exit <N>): <the first 300 characters GND printed>

The guard reads that note in what `rules_check.py test` printed (D1):

```python
SYNTH_EXTRA = "needs the optional 'synth' extra"


def without_synth_extra(out: str) -> bool:
    """Whether `rules_check.py test` reported that GND built no cases for want of its synth extra."""
    return any(line.startswith("note: gnd synth --guarded-cases built no cases (exit 5): ") and SYNTH_EXTRA in line
               for line in out.splitlines())


def skip_without_synth_extra(out: str) -> None:
    if without_synth_extra(out):
        pytest.skip("this GND lacks its synth extra: uv tool install --force 'get-nick-done[synth]'")
```

- Both parts must hold on one line: exit 5, and the sentence that names the extra. The
  sentence is GND's, quoted in the issue: `ERROR: the synthetic-value generator needs the
  optional 'synth' extra.`
- In `test_suggestions_and_generated_cases_with_newer_gnd`, one line is added after
  `code, out = tool(project, "test", script=RULES)` and before the two assertions that
  follow it: `skip_without_synth_extra(out)`. The `suggest` assertions above it run first,
  with or without the extra. The `skipif` on the two `--help` flags stays.
- `fake_gnd` gains two keyword arguments, `synth_exit=0` and `synth_stderr=""`. When
  `synth_exit` is not 0, the fake's `synth` branch writes `synth_stderr` to standard error
  and exits with that code, writing no manifest. With the defaults the fake does what it
  does today, so no existing test changes.

Branches of the guard:

| Branch | `out` holds | Guard | Case |
|---|---|---|---|
| A | the note, exit 5, the extra's sentence | skip | T1 |
| B | the note, another exit, the extra's sentence | run | T2 |
| C | the note, exit 5, another message | run | T2 |
| D | the note, another exit and message (a model GND refuses: exit 3) | run | T2 |
| E | no such note: cases were built | run | T2, and T3 on a machine with the extra |

### 6.2 A test of the pytest plugin (issue 42)

**What exists (r1 F5).** `tests/test_tools.py:1879`,
`test_plain_pytest_leaves_out_phases_that_are_not_complete`, already runs the plugin. Its
`project` fixture syncs `examples/phase-project.devtools.toml`, which delivers the plugin
as the project's `conftest.py` (`:70`); the test then runs pytest three times and reads
the last line: `2 passed, 1 deselected`; `1 passed, 2 deselected` for `--phase 2`; `1
passed` for a named file of the open phase. It holds B1 to B5 and B9 of the table below
by count. It never names `phase_selection.py`, which is why the issue's `grep` and this
spec's first draft missed it. It stays as it is: it is the one test of the plugin as the
sync delivers it.

**What is added** (D5). `tests/test_phase_selection.py`, new, about 130 lines, for the
branches that test does not reach, and for which tests are kept where it counts them.
`skills/phase/pytest/phase_selection.py` is not changed.

One fixture, `selection(tmp_path)`, makes a project and returns a function that runs
pytest in it:

- `conftest.py`: a copy of `ROOT / "skills/phase/pytest/phase_selection.py"`;
- `.planning/STATE.md`: `completed_phases: 1`;
- `tests/acceptance/p01_done/test_done.py`, `tests/acceptance/p02_open/test_open.py`,
  `tests/acceptance/p06_1_inserted/test_inserted.py`, `tests/unit/test_unit.py`, each with
  one test that passes;
- `collected(*args, cwd=project) -> set[str]`: runs
  `[sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "--collect-only", "-q", *args]`
  in `cwd`, with `PYTEST_ADDOPTS` removed from the environment, asserts exit 0 (or 5 when
  the caller expects nothing collected), and returns the node ids pytest printed.

A node id is listed only when the plugin kept it, so the set is what would run.

The plugin's branches (`pytest_collection_modifyitems`, `phase_id`, `completed_phases`):

| Branch | Case |
|---|---|
| B1. No `--phase`: a test outside the acceptance folder is kept | S1 |
| B2. No `--phase`: a test of a complete phase is kept | S1 |
| B3. No `--phase`: a test of a phase that is not complete is left out | S1 |
| B4. `--phase NN`: that phase's tests are kept, complete or not | S2 |
| B5. `--phase NN`: other phases' tests and tests outside the folder are left out | S2 |
| B6. `--phase` is normalised: `2`, `02` | S2 |
| B7. An inserted phase: `--phase 6.1` selects `p06_1_*` | S3 |
| B8. `completed_phases:` holds an inserted phase (`6.1`), and a number written `01` | S3 |
| B9. A file inside the acceptance folder named on the command line runs whatever its phase's state | S4 |
| B10. A folder inside the acceptance folder named on the command line: everything under it runs | S4 |
| B11. A named path with a `::` node id | S4 |
| B12. A named path runs although `--phase` names another phase | S4 |
| B13. The acceptance folder itself named (`tests/acceptance`) is not "inside" it: open phases stay left out | S5 |
| B14. No `STATE.md`, and a `STATE.md` with no `completed_phases:` line: no phase is complete | S6 |
| B15. `phase_planning_dir` and `phase_acceptance_dir` in the pytest configuration | S7 |
| B16. The plugin kept beside a `conftest.py` that holds `pytest_plugins = ["phase_selection"]` | S8 |
| B17. Nothing to leave out: pytest reports no deselected test | S9 |
| B18. A run that is not `--collect-only`: the kept tests run and pass, the rest are counted as deselected | S9 |

Observed on 2026-11-23 with pytest 9.2.0 (plan, section 3): B1 to B7, B9 and B13 behave
as the plugin's docstring says. B8, B10 to B12 and B14 to B18 were not tried.

### 6.3 One list of other planning tools (issue 41)

`devtools/from_gsd.py`: about 8 lines added, 9 removed. `devtools/sync.py`: not changed.

`from_gsd.py` loads `sync.py` by path, as `release_plugins.py` loads `build_plugins.py`.
It gains one import, `importlib.util` (standard library), and these lines after its
imports:

```python
# The list of other planning tools is sync.py's (OTHER_PLANS): one list, read by both scripts.
_SYNC = importlib.util.spec_from_file_location("sync", Path(__file__).resolve().with_name("sync.py"))
sync = importlib.util.module_from_spec(_SYNC)
_SYNC.loader.exec_module(sync)
```

`OTHER_PLANS` and its comment (`from_gsd.py:45-48`) are deleted. `other_plans` keeps its
signature and what it returns:

```python
def other_plans(project: Path) -> list:
    """Other planning tools whose files are in the project. The move does not read them."""
    return [{"tool": tool, "sign": sign} for sign, tool in sync.other_plans(project)]
```

**Callers.**

| Function | Returns | Callers | Changed |
|---|---|---|---|
| `sync.other_plans(project, planning=None)` | `[(sign, tool)]`, one per tool, in the order of the list; with `planning`, also a row for a planning folder the phase tool did not write | `sync.py:1011`, in `survey` | no |
| `from_gsd.other_plans(project)` | `[{"tool", "sign"}]`, one per tool, in the order of the list | `from_gsd.py:920`, as the model's `"elsewhere"`, printed at `:1336` | its body |

`from_gsd.py` calls `sync.other_plans` with no `planning`, so the extra row is never made.
The two walks are the same six lines today (`sync.py:853-857`, `from_gsd.py:491-495`), so
the rows and their order do not change.

`sync.py` runs nothing when loaded: its top level holds constants, a `tomllib` import
guard and the `if __name__ == "__main__"` line. It uses no dataclass, so it needs no
entry in `sys.modules`. The tests load both scripts the same way (`tests/test_from_gsd.py:15`).

### 6.4 The index entries

`.devtools/components/COMPONENTS.md`, three entries, then `write`.

| Entry | Change | Why |
|---|---|---|
| `phase.test_selection` | Add `- tests: tests/test_tools.py, tests/test_phase_selection.py`; replace "No test in tests/ runs it (REVIEW.md)." in `notes:` with "tests/test_tools.py runs it as the sync delivers it (test_plain_pytest_leaves_out_phases_that_are_not_complete); tests/test_phase_selection.py holds its other branches." (r1 F5; prior wording: "Add `- tests: tests/test_phase_selection.py`; drop the sentence") | A test ran it all along, and the note said none did |
| `sync.copies` | Replace `- duplicates: devtools/from_gsd.py` with `- distinct_from: migrate.from_gsd` | The list is no longer written twice. `other_plans` is still defined in both modules, one as an adapter over the other, and the index cannot see the load (issue 39), so without `distinct_from` `review` would raise it as a same-name lead |
| `migrate.from_gsd` | Add to `notes:` "Loads sync.py by path for its list of other planning tools (OTHER_PLANS, other_plans)." | The load is invisible to the index and is stated by hand, as the three subsystems state theirs |

If `review` then lists another name the two modules share, the spec is wrong about what
`duplicates:` was settling: it is recorded as a finding, and settled by reading the two
definitions, not by widening the entry.

## 7. Decisions

Ruled 2026-11-23 by delegated approval (auto=true), each as proposed (d). See "Owner gate".

| # | Question | Readings and their cost | Proposed |
|---|---|---|---|
| D1 | How the guard learns GND cannot build cases | **From the note in what `rules_check.py test` printed, inside the test:** no model to build in the test file, the `suggest` half always runs, and the note's wording is pinned by T1. A change of GND's sentence makes the test fail again, loudly. **By running `gnd synth` once at collection**, as the issue's example says: the test file needs a model GND accepts (a second copy of what `rules_check.model` builds), every collection pays for a GND run, and the whole test is skipped | Ruled: from the note (d) |
| D2 | Where the one list lives | **In `sync.py`, loaded by `from_gsd.py`:** `sync.py` stays one file; `from_gsd.py` depends on the file beside it, which it already does for the templates. **In a third file both load:** `sync.py` is no longer one file. **In `from_gsd.py`, loaded by `sync.py`:** the script every project runs depends on the one few do | Ruled: in `sync.py` (d) |
| D3 | If S1 to S9 show a defect in `phase_selection.py` | **Fix it here when the fix is within one function**, with the failing case as its test; that changes a plugin file, so the milestone's bump (plan D4) moves to this phase. **Record it and draft an issue:** the phase changes no product file, and the test that found it is committed marked as an expected failure | Ruled: fix it here (d) |
| D4 | Whether issue 31's failure is reproduced with a real GND | **One by-hand run** with a GND installed without the extra (`GND_COMMAND="uvx --from get-nick-done==0.4.0 gnd"`, which fetches the package from PyPI): the record shows the skip on the real refusal. **The fake only:** nothing is fetched, and the sentence GND prints stays an inherited claim from the issue | Ruled: one by-hand run (d) |
| D5 | What issue 42 still needs, now that a test of the plugin is known to exist (r1 F5) | **The entry lists the existing test, and a new file holds the other branches** (S1 to S9): about 130 lines of tests, and every branch of the plugin has a case that names the tests kept. **Extend the existing test in `tests/test_tools.py`:** one place, but each case pays for the `project` fixture's full sync, and that file is 1894 lines already. **List the existing test in the entry and add nothing:** a few lines; B6 to B8 and B10 to B18 stay without a case, and the issue is answered more than fixed | Ruled: the entry and a new file (d) |

## 8. Tests

Expected exit of every pytest command below: 0.

**`tests/test_tools.py`**

| # | Case | Asserts | Branch |
|---|---|---|---|
| T1 | `test_a_gnd_without_its_synth_extra_is_a_note_and_the_guard_skips` | With `fake_gnd(project, cases={}, synth_exit=5, synth_stderr="ERROR: the synthetic-value generator needs the optional 'synth' extra.\n")`: `rules_check.py test` exits 0; its output has the `note:` line with `(exit 5)`; `without_synth_extra(out)` is true; `skip_without_synth_extra(out)` raises `pytest.skip.Exception` | A; O1, O2 |
| T2 | `test_the_guard_skips_for_the_missing_extra_only`, four parameters | (exit 3, the extra's sentence), (exit 5, `ERROR: no solver`), (exit 3, `ERROR: model validation failed`), and cases built (`cases={"schema_version": …, "rules": []}`, exit 0): `without_synth_extra(out)` is false and `skip_without_synth_extra(out)` returns | B, C, D, E; O3 |
| T3 | `test_suggestions_and_generated_cases_with_newer_gnd`, existing | Its assertions are unchanged. With the extra it passes; without it, it is reported as skipped with the guard's reason | E here; A by hand (D4) |

**`tests/test_phase_selection.py`** (new)

| # | Case | Asserts (the set `collected` returns) | Branches |
|---|---|---|---|
| S1 | `test_plain_pytest_leaves_out_the_phases_that_are_not_complete` | `test_done` and `test_unit`; not `test_open`, not `test_inserted` | B1, B2, B3 |
| S2 | `test_phase_option_runs_that_phase_only`, parameters `02`, `2`, `01` | `02` and `2`: `test_open` alone. `01`: `test_done` alone | B4, B5, B6 |
| S3 | `test_an_inserted_phase` | `--phase 6.1`: `test_inserted` alone. With `completed_phases: 01, 6.1`: plain pytest collects exactly `test_done`, `test_inserted` and `test_unit` (r1 F4; prior wording: "keeps `test_done` and `test_inserted`, not `test_open`", which left out the unit test a plain run always keeps) | B7, B8 |
| S4 | `test_a_named_acceptance_path_always_runs`, four parameters | The open phase's file; its folder; its file with `::test_open`; its file with `--phase 01`: each collects `test_open` (the last one alone) | B9 to B12 |
| S5 | `test_naming_the_acceptance_folder_itself_keeps_the_selection` | `tests/acceptance`: `test_done` alone | B13 |
| S6 | `test_no_state_means_no_phase_is_complete`, two parameters | `STATE.md` removed; `STATE.md` without the line: `test_unit` alone | B14 |
| S7 | `test_the_two_folders_can_be_configured` | With a `pytest.ini` naming `phase_planning_dir = plan` and `phase_acceptance_dir = checks`, and the folders moved: as S1 | B15 |
| S8 | `test_the_plugin_beside_a_conftest_that_names_it` | The plugin as `phase_selection.py` and a `conftest.py` with `pytest_plugins = ["phase_selection"]`: as S1 | B16 |
| S9 | `test_a_real_run_counts_what_it_left_out` | Without `--collect-only`: exit 0 and `2 passed, 2 deselected`. With every phase complete: `4 passed` and no `deselected` | B17, B18 |

**`tests/test_from_gsd.py`**

| # | Case | Asserts | Obligation |
|---|---|---|---|
| G1 | `test_one_list_of_other_planning_tools_serves_both_scripts` | With `monkeypatch.setattr(gsd.sync, "OTHER_PLANS", [(".newtool", "New Tool")])` and a folder `.newtool/` in the project: `gsd.other_plans(project) == [{"tool": "New Tool", "sign": ".newtool/"}]` and `gsd.sync.other_plans(project) == [(".newtool/", "New Tool")]` | O6 |
| G2 | `test_other_plans_keeps_its_rows_and_their_order` | With `.specify/`, `specs/a/spec.md`, `openspec/` and `.taskmaster/`: exactly `[{"tool": "Spec Kit", "sign": ".specify/"}, {"tool": "OpenSpec", "sign": "openspec/"}, {"tool": "Task Master", "sign": ".taskmaster/"}]`. A pin: it passes before the change too | O7 |
| -- | every existing test of the file, and of `tests/test_sync.py`, unedited | exits as at `cecebc6` | O8 |

**Seen to fail** (S0.3; each pasted into the record):

- T1 and T2, before `fake_gnd` and the guard are written: `TypeError` for `synth_exit`, or
  `NameError` for the guard.
- G1, before `from_gsd.py` changes: `AttributeError: module 'from_gsd' has no attribute 'sync'`.
- S1 to S9, each against a scratch copy of the plugin with one line broken, the copy
  named by an environment variable the fixture reads only for this check. Five breaks
  cover the branches: `phase in done` made always true (S1, S3, S6); `phase == wanted`
  made always true (S2); the `named` list emptied (S4); the `startswith(acceptance + "/")`
  filter dropped (S5); `completed_phases` made to return an empty set (S3, S9). The
  configuration and the `pytest_plugins` cases (S7, S8) fail when the plugin is absent.
  The breaks are not committed.
- G2 is a pin and is not expected to fail.

**Gates.**

| Gate | Command | Expected |
|---|---|---|
| Focused | `uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_phase_selection.py tests/test_from_gsd.py tests/test_sync.py -q` | exit 0 |
| All tests | `uv run --no-project --with pytest python -m pytest tests -q` | exit 0; 447 tests at the baseline, plus this phase's |
| Plugins | `python3 devtools/build_plugins.py --check` | exit 0 |
| Release status | `python3 devtools/release_plugins.py status` | the baseline's four lines, exit 1 (`0.1.6 is ready`) |
| Index | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict` | exit 0 |
| G-review | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py review` | `## Components with no tests listed (0)` and `## The same public name in two or three components (a duplicate?) (0)` |
| By hand (D4) | `GND_COMMAND="uvx --from get-nick-done==0.4.0 gnd" uv run --no-project --with pytest python -m pytest tests/test_tools.py -q -rs` | exit 0; one `SKIPPED` line with the guard's reason |

## 9. Out of scope for this phase

- Any change to `rules_check.py`: issue 31 says it is right, and issue 33 is phase 3.
- Any change to `phase_selection.py`, unless D3 applies.
- `sync.py`'s `other_plans`, its foreign-planning row, and what `survey` prints.
- Letting the index see the load `from_gsd.py` now makes: issue 39, out of the milestone.
- The docstring of `from_gsd.py` ("It never calls git"): issue 43, phase 3.
- Issues 44, 45 and 46: phase 2.

## 10. Size

Estimate at write time: about 35 lines of source changed (`tests/test_tools.py` helpers
and `fake_gnd`, `devtools/from_gsd.py`), about 215 lines of tests (45 in
`tests/test_tools.py`, 130 in the new file, 40 in `tests/test_from_gsd.py`), and three
index entries. The measurement goes in the record.

## 11. Approval instrument

This prose. There is no fixture corpus: the phase adds no serialized format, no exit
code and no validation predicate, so the corpus-first default of `review-convergence.md`
does not apply.

## Owner gate

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/issue-sweep/notes/phase-1-spec.md
    sha256: in the phase record, 002-phase-1.md (a file cannot hold its own digest)
    date: 2026-11-23
    authorization: the owner's "process-milestone issue-sweep auto", given in the
      session that wrote the plan, after the plan gate; for the milestone issue-sweep
      only
    scope: this spec and its amendments; the phase's commits over the files it names
    not covered: pushing, the pull request, merging, tagging, releasing, and anything
      posted to GitHub
    instrument: this prose
    decisions: D1 to D5, each as proposed
    spec review: none. The plan review read this spec (r1); its two findings are
      repaired above. An optional review of a spec is omitted unless a concrete
      uncertainty needs one, and the uncertainties here are facts a test settles.
    phase review: review_tool.py, --subject phase, reviewer Codex; at most two rounds
      (r1, r2), declared here before either has run

This is an agent's ruling under the owner's delegation. It is not the owner's own
reading of the spec.

**Implementability sweep**, before the ruling. For each requirement, can some
implementation meet it as written?

| Requirement | Answer |
|---|---|
| The guard reads the note of `rules_check.py test` (6.1) | Yes: `generated` returns that note whenever no manifest is written (`rules_check.py:818`), with GND's exit and its first 300 characters |
| A fake `gnd` that lists the flag and exits 5 (T1) | Yes: `fake_gnd` lists `--guarded-cases` when `cases` is not `None`, and its `synth` branch can exit before it writes the manifest |
| S1 to S9 expect what the plugin collects | Yes for S1, S2, S3 (first half), S4 (the file) and S5: run by hand on 2026-11-23 (plan, section 3). S3's second half was corrected by r1 F4. The rest are facts for the tests to settle; an expectation the plugin does not meet is a finding under D3, not a reason to bend the test |
| `from_gsd.py` loads `sync.py` by path (6.3) | Yes: the tests already load both that way, and `sync.py` runs nothing when loaded |
| G1 fails before the change and passes after | Yes: `from_gsd` has no attribute `sync` today |
| The by-hand gate of D4 | Depends on PyPI being reachable. If it is not, the gate is recorded as not run and Q2 of the plan stays open |
| `review` prints 0 for both groups after 6.4 | Simulated by the plan reviewer (r1, "checked and found true"); the gate G-review decides |

**Verification selection.** Plan-mandated: the five gates of section 8 and the by-hand
run. Direct: the three test files the phase edits or adds. Impact closure:
`tests/test_sync.py` (it shares `sync.py`'s list) and `tests/test_own_index.py` (the
index). The full suite is the repository's only broad lane and the plan's section 9
names it for this phase, so it runs.

## Implementation findings, recorded as they were found

(None yet.)
