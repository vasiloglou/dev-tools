# Phase 2 spec: an index can count more than one source folder

## 1. Status

Draft, 2026-11-21. Written as phase 1 and renumbered phase 2 the same day, when the owner
added issue 28 as the new phase 1 (o). **Implementable once the plan gate is recorded,
phase 1 is merged, and this spec's owner gate rules D1 to D3.** No code has been written. No review has run over these bytes.

## 2. Provenance

- **Plan.** `notes/component-index-plan.md`, a draft written on 2026-11-21: phase 2 in
  section 4, the baseline in section 3, and rules R0.1 to R0.3 in section 0. The plan is
  unreviewed and has no plan gate yet. A change at the plan gate can change this spec.
- **Code read.** `skills/components/scripts/components_index.py`, `devtools/sync.py`
  (`survey --toml`'s settings block), `tests/test_tools.py` (the `project` fixture) and
  `tests/test_plugins.py`, all at main `c9648dd`.
- **Written with.** `start-milestone`, dvt-milestone 0.1.3. This spec has not been run
  through `process-phase` and has no owner gate yet.
- **Review rounds.** `reviews/plan-r1` (Codex, 2026-11-21) read the bytes with the
  SHA-256 listed in its `BRIEF.md`. Its F3, F4 and F5 were repaired here, marked
  `(r1 F3)` to `(r1 F5)`. `reviews/plan-r2` (Codex, 2026-11-21) read the repaired bytes;
  its F1 was repaired here, marked `(r2 F1)`. **The bytes repaired after round 2 carry no
  review opinion.**

## 3. Obligations (step 0 harvest)

| # | Obligation | Source | Discharged in |
|---|---|---|---|
| O1 | With the setting on, `stats`, `--check --strict`, `draft`, `changed` and `review` name a module in an extra folder that has no component, and `show` prints one that has (r1 F5) | Plan section 4, P2.1 | Design, "Sites"; tests T2 to T6, T9 |
| O2 | With the setting off or absent, every existing test exits as it does on main | Plan section 4, P2.2; risk R1 | Design, "Default"; T1 and the full suite |
| O3 | `draft` gives a stub for a module in an extra folder and does not raise an error | Plan section 4, P2.3; section 3 (`relative_to(PACKAGE_DIR)`) | Design, `draft()`; T3 |
| O4 | `build_plugins.py --check` exits 0 after the bump | Plan section 4, P2.4; standing rule "plugins are rebuilt" | Design, "Release"; gate G3 |
| O5 | The setting is described where the settings are described | Plan section 5; standing rule "the page that describes it" | Design, "Text" |
| O6 | An older plugin refuses the new key loudly, and the docs name the first version that accepts it | Plan section 5, "Settings compatibility" | Design, "Text"; T7 |
| O7 | A capture whose output the change alters is retaken from a real run | Standing rule "captures are real output"; `docs/adopt.html` lines 241 to 244 | D2 |
| O8 | A gate never runs the branch's script against this repository | Plan R0.3 | Section 4, row R0.3 |

## 4. The standing rules, bound to this phase

| Rule | Bound here to |
|---|---|
| A script change comes with a test | `components_index.py`: `load_settings`, the new `counted_modules`, `coverage`, `draft`, `changed` and `review`. Tests T1 to T7 in `tests/test_tools.py`; each of T2 to T7 fails on main |
| The plugins are rebuilt, and released under a new version | `release_plugins.py bump` to the next patch version (0.1.5 if phase 1 released 0.1.4), then gate G3. The owner tags after the merge |
| A wording change says what prompted it | The SKILL.md and build.md sentences are prompted by plan section 3's baseline: `extra_source_dirs` are listed but never counted |
| Shared skills stay general | The setting is for any project whose code sits in several folders (for example `src/` and `tools/`), and it is off by default. Nothing in it names dev-tools |
| Both agents read the same file | The SKILL.md settings line and build.md step 1 are read the same way by Claude Code and Codex. The setting is read by the script, not by the agent, so the two tools see no difference |
| Captures on the site are real output | The `docs/adopt.html` capture of `survey --toml` changes (D2) |
| The page that describes it is updated too | `skills/components/SKILL.md` (settings line), `references/build.md` (step 1), `docs/components.html` (where its settings are named), and the commented line in `examples/phase-project.devtools.toml` |
| R0.1 A shipped script stands alone | Does not apply: no script gains an import |
| R0.2 The index is the project's | The only product files changed are those above, and each holds outside this repository. No dev-tools path is in them |
| R0.3 The released plugin runs | Gates G1 to G3 run pytest and the build check. None runs `components_index.py` against this repository |

## 5. Goal

With `count_extra_dirs` set to true, a module under one of `extra_source_dirs` that no
component covers makes `--check --strict` and `changed` exit 1 with a
`no component: <path>` line. It is also listed by `stats` and by `review`'s "Modules with
no component", and stubbed by `draft`, which exits 0. With the setting absent or false,
`uv run --no-project --with pytest python -m pytest tests -q` gives the same result as on
main: every test passes apart from the GND `synth` case (plan, R5).

## 6. Design

**Reuse.** This project has no component index, so there is nothing to search; the plan
builds one in phase 3. `git grep -n "EXTRA_DIRS\|PACKAGE_DIR" skills/components/scripts/`
was searched instead. Every counted set is built inline, from
`sources(root, PACKAGE_DIR)`; no helper gives the counted modules. Decision: **new**
function `counted_modules`, used at each site, and **adapt** the sites.

**Module.** `skills/components/scripts/components_index.py`. The estimate is about 25
changed source lines.

- **Setting.** Add `'count_extra_dirs': False` to `DEFAULT_SETTINGS`, after
  `extra_source_dirs`, with a comment:
  `# Whether coverage, --check --strict, draft, changed and review count the modules of extra_source_dirs too.`
  `load_settings` refuses a value that is not a boolean, with
  `SystemExit(f'{path}: count_extra_dirs must be true or false')`.
- **One function.**

  ```python
  def counted_modules(root: Path) -> list[str]:
      """The repo-relative paths every module must have a component for: the package, and
      with count_extra_dirs the extra source folders too. Sorted, each once."""
  ```

  The result is the package's modules, in the order `sources(root, PACKAGE_DIR)` gives
  them today: `sources()` sorts `Path` objects, so `src/widget/a/z.py` comes before
  `src/widget/a.py`. When `SETTINGS['count_extra_dirs']` is true, the modules of each `d`
  in `EXTRA_DIRS` follow, in the order of `EXTRA_DIRS`, each folder in `sources()` order.
  A path already in the list is skipped. Each path is made relative with `as_posix()`.
  There is no re-sort of the strings. With the setting false, the list is exactly
  today's list in today's order (r1 F3; the earlier wording sorted the strings, which
  changes the order of `stats`, `draft` and the baseline file).
- **Sites.** These now call `counted_modules`. Each currently builds the set inline:
  - `coverage()` (line 237);
  - `changed()`, the `package` set used for the new-file check (line 1091);
  - `review`, the `package` list behind "Modules with no component" (line 1295);
  - `show`, the `package` list that decides which of the entry's modules get a section
    with their symbols (line 1476, used at the loop
    `for path in [p for p in package if covers(entry, p)]`) (r1 F5). Its import lines
    stay package-only, so a module in an extra folder shows no imports.
- **Sites that stay as they are.** These build the import graph, which stays inside
  `package_dir` (plan section 7): `package_imports()`, `module_graph()`, `changed()`'s
  `existed` set, and `show`'s `imports` and `outside_importers`.
- **The coverage line.** `coverage: <a>/<n> <dirs> modules assigned to components; …`.
  `<dirs>` is `PACKAGE_DIR` today. With the setting on it is `PACKAGE_DIR` and the extra
  folders, joined by `, `: `coverage: 0/12 devtools, skills modules assigned …`.
- **`draft()`.** For a path not under `PACKAGE_DIR`, the id is computed relative to the
  extra folder that holds it, and the area is that folder's last name. So `tools/report.py`
  under extra folder `tools` gets `tools.report`. Today `relative_to(PACKAGE_DIR)` raises
  `ValueError` for such a path. A deeper path, `skills/components/scripts/rules_check.py`
  under `skills`, gets area `components` and name `scripts_rules_check`. The ids are
  placeholders, as all draft ids are.
- **Default.** With `count_extra_dirs` false, `counted_modules` returns exactly the paths
  the inline code returns today. Every output and exit is therefore unchanged (O2).

**Text** (O5, O6):

- `skills/components/SKILL.md`, line 23: add `count_extra_dirs` to the list of settings,
  and one sentence: "`count_extra_dirs` (true or false, default false; from plugin
  0.1.5) makes the modules of `extra_source_dirs` count like the package's, for a project
  whose code sits in more than one folder."
- `references/build.md`, step 1: one sentence after the `extra_source_dirs` one: when the
  extra folders hold code that should have components too, set `count_extra_dirs` to true.
- `docs/components.html`: the same sentence where the page names the settings.
- `examples/phase-project.devtools.toml`: a commented line after `extra_source_dirs`,
  `# count_extra_dirs = true   # count the extra folders' modules too (plugin 0.1.5 or newer)`.

**Release** (O4): run `python3 devtools/release_plugins.py bump`, which takes the version one patch up (0.1.4 to
0.1.5 if phase 1 went first) and rebuilds `plugins/`. Commit the result with the change.

## 7. Decisions

| # | Question | Readings, and what each costs | Proposed |
|---|---|---|---|
| D1 | The shape of the setting | **(A)** A new key, `count_extra_dirs: bool`. About 25 lines, and each site keeps one notion of "the package". It adds a line to `survey --toml`'s output (D2). **(B)** `package_dir` accepts a list. No new key, and the capture is unchanged. But every `PACKAGE_DIR` site, `PACKAGE`, `SOURCE_ROOT` and relative-import resolution must handle several roots: an estimated 80 lines or more, touching code every existing project runs. **(C)** Always count the extra folders. That changes the exit of `--check --strict` from 0 to 1 for any existing project with unassigned scripts in an extra folder | (A) |
| D2 | `docs/adopt.html`'s capture of `survey --toml` (`grep -n '= "TODO"'` printing one line, `26:verb_list …`) | With (A), the same commands print a second line for `count_extra_dirs`, so the capture no longer shows what the commands print. The demo project it came from (`demo/shelf`, per the maintainer's notes) no longer exists on this machine. **(a)** Re-make a demo project to the notes' description and retake that one terminal block from a real run. The caption says it was retaken, and when. **(b)** Retake the whole adopt-page sequence on a re-made demo: larger, and no other capture changes. **(c)** Leave the capture: this breaks the standing rule | (a) |
| D3 | Whether `count_extra_dirs` is written by `survey --toml` as `TODO`, like every setting the survey cannot read | That is today's behaviour for every key, and it is unchanged. Writing its default instead would special-case one key in `sync.py` | Leave as is |

## 8. Tests

All tests are in `tests/test_tools.py` and use the `project` fixture (a synced project; the
settings are at `scripts/components_index.settings.json`). The shared setup adds:

- an entry `core.package` covering `src/widget/__init__.py`, so the package itself is
  fully covered (r1 F4: without it, every strict check below also names `__init__.py`);
- a module `tools/report.py`, with a docstring and one function;
- `extra_source_dirs: ["tools"]`.

| Id | Case | Expected |
|---|---|---|
| T1 | Setting absent: `--check --strict`, `stats` | `--check --strict` exits 0; `stats` prints `coverage: 1/1 src/widget modules …` and does not name `tools/report.py` (as on main) |
| T2 | Setting true: `--check --strict` | exits 1; prints `no component: tools/report.py` |
| T2b | Setting true, with an entry whose `modules:` is `tools/report.py`: `write`, then `--check --strict` | both exit 0 |
| T3 | Setting true: `draft` | exits 0; prints a stub with id `tools.report` and the module's docstring summary. On main the stub is not printed |
| T4 | Run once with the setting true and once with it false. Each run: `write`, then commit everything on `main` (the fixture makes no commit). Then add `tools/new.py`, untracked, and run `write` again so that no generated page is stale. Then `changed --base main` | true: exits 1; prints `fail: no component: tools/new.py (new file; …)`. false: exits 0 and prints no such line (r2 F1: the earlier wording ran `changed` with no commit, which exits 1 on `no branch or commit named main`, and without the second `write`, which exits 1 on `stale or missing: docs/components/modules/tools.md` whatever the setting) |
| T5 | Setting true: `review` | exits 0; "Modules with no component (1)" lists `tools/report.py` |
| T6 | Setting true: `stats` | prints `coverage: 1/2 src/widget, tools modules …` and lists `tools/report.py` |
| T7 | Setting `"yes"`: `stats` | exits non-zero; prints `count_extra_dirs must be true or false` |
| T8 | Setting true, with `stats --write-baseline`, then `--check --strict` | the baseline holds `tools/report.py`, and `--check --strict` exits 0 |
| T9 | Setting true, with an entry whose `modules:` is `tools/report.py`: `show <that id>` | prints a module section for `tools/report.py` with its function. On main there is none (r1 F5) |
| T10 | Setting absent, with modules `src/widget/a.py` and `src/widget/a/z.py`, both unassigned: `stats` | lists `src/widget/a/z.py` before `src/widget/a.py`, as main does (r1 F3) |

Branch walk over the design:

- `counted_modules` has two branches (setting on: T2 to T6, T8 and T9; off: T1, T10, and
  T4's second half). The order of the off branch is pinned by T10.
- `show`'s module sections: in the package (existing tests) and in an extra folder (T9).
- `load_settings` has two (valid: all; invalid: T7).
- `draft`'s id has two (under `PACKAGE_DIR`: the existing `test_draft_gives_a_stub…`;
  under an extra folder: T3).
- The coverage line has two (T1, T6).

**Gates:**

- G1: `uv run --no-project --with pytest python -m pytest tests/test_tools.py -q` exits
  0, apart from the R5 case.
- G2: `uv run --no-project --with pytest python -m pytest tests -q` has 1 failure, the R5
  case.
- G3: `python3 devtools/build_plugins.py --check` exits 0.

## 9. Out of scope for this phase

- Import edges between modules of the extra folders, or between them and the package.
- Building dev-tools' own index or its settings file (phase 3).
- Any change to `sync.py`'s survey (D3).
- Tagging the release (an owner action after the merge).

## 10. Size

Estimated at write time:

- `components_index.py`: about 25 source lines;
- `tests/test_tools.py`: about 90 test lines;
- about 6 lines of skill and page text;
- the retaken capture block (D2);
- the rebuilt `plugins/` copies.

The measured figures go in the record.

## 11. Approval instrument

This prose. The phase's shape (settings, exit codes) is not one of the three for which
`review-convergence.md` makes corpus-first the default, so it is asked, not inherited.
Proposed: prose, with T1 to T8 as the corpus written first in step 3.
