# Phase 3 spec: dev-tools' own component index

## 1. Status

Draft, 2026-11-21, written with `process-phase` (dvt-milestone 0.1.3) under
`process-milestone component-index auto`. Its gate is a delegated approval (auto=true),
recorded in section 12. No review has run over these bytes.

Phase 2 is not merged (vasiloglou/dev-tools#30, stacked on #29). By plan amendment a3,
this phase's branch, `claude/component-index-phase-3`, is cut from phase 2's tip
(`a7bc35c`), and its pull request will name phase 2's branch as its base. The tool this
phase runs is the built 0.1.5 copy on that branch (R0.3).

## 2. Provenance

- **Plan.** `notes/component-index-plan.md` at SHA-256 `3cc5eb49…a9`: phase 3 in section 4,
  C1 and C2, the baseline and artifact homes in section 3, R0.1 to R0.3 in section 0, D1 and
  D4 in section 10.
- **Code read for this spec.** The 12 modules' docstrings and command lists; the run-time
  calls between them (`git grep` for `subprocess`, `importlib`, `runpy` and the script
  names); the test files that name each script.
- **Tool run.** On this branch, with the settings of section 6:
  `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py write` exited 0
  and wrote the starter catalog; `stats` printed
  `coverage: 0/12 devtools, skills modules assigned to components; external: none`.
- **GND.** Since 2026-11-21 this machine's GND is installed with its `synth` extra
  (`get-nick-done[synth]==0.4.0`), and the known red R5 passes: `1 passed` for that test
  alone. The full suite is expected to exit 0 (section 8, G7). The skip guard that let R5
  fail instead of skip is vasiloglou/dev-tools#31, out of scope here.

## 3. Obligations (step 0 harvest)

| # | Obligation | Source | Discharged in |
|---|---|---|---|
| O1 | Every module of `devtools/` and `skills/` has a component, with no baseline file | Plan C1 | Section 6, components; G2, G3 |
| O2 | 8 to 10 search cases put their component first; one negative case | Plan C2; phase 3 deliverables | `search-cases.md`; G5 |
| O3 | `write`, then `--check --strict`, exit 0 | P3.1 | G1, G2 |
| O4 | `review` reports no components that import each other, and no flow step no earlier step imports apart from run-time loads stated in `notes:` | P3.2 | Section 6, subsystems; G4 |
| O5 | Every entry is read from the code; a `checked: partial` entry is listed in the record | P3.3 | Section 6, reading; the record |
| O6 | `REVIEW.md`: files worth splitting, names shared across scripts (R0.1), code with no tests; suggestions only | Phase 3 deliverables | Section 6, `REVIEW.md` |
| O7 | Gates run the built copy from the repository root, never `skills/…/components_index.py` | R0.3 | Section 8, every gate |
| O8 | Shared helper names are left alone and recorded with `distinct_from` | Plan D4 | Section 6, `distinct_from` |
| O9 | The index lives in `.devtools/components/`, with its settings in `.devtools/components_index.settings.json` | Plan D1; section 3, artifact homes | Section 6, settings |

## 4. The standing rules, bound to this phase

| Rule | Bound here to |
|---|---|
| A script change comes with a test | Does not apply: no script changes. The catalog is data. Phase 4 adds the test that keeps it current |
| The plugins are rebuilt, and released under a new version | Does not apply: nothing under `skills/` or `agents/` changes, so there is no bump. G6 checks `plugins/` is still what the build makes |
| A wording change says what prompted it | Does not apply: no skill wording changes |
| Shared skills stay general | Nothing of the index goes into `skills/`. It is dev-tools' own, under `.devtools/` (R0.2) |
| Both agents read the same file | The catalog is read by the script, and by an agent through `search`, the same way under Claude Code and Codex |
| Captures on the site are real output | Does not apply: no page changes in this phase (phase 4 adds the pointer) |
| The page that describes it is updated too | Does not apply in this phase; phase 4 owns the pages |
| R0.1 A shipped script stands alone | Recorded, not changed: the helpers several scripts define for themselves (`plugin_root`, `checkout_root`, `load_settings`, `git`) are listed in `REVIEW.md` and marked `distinct_from` (O8) |
| R0.2 The index is the project's | Only `.devtools/` files are written |
| R0.3 The released plugin runs | Every gate in section 8 names `plugins/dvt-milestone/skills/components/scripts/components_index.py` |

## 5. Goal

Run from the repository root, the built copy's `write` and `--check --strict` exit 0
with `coverage: 12/12 devtools, skills modules assigned`. No
`unassigned-baseline.txt` exists. Each search case in `search-cases.md` puts its
expected component first among the components. `review` prints
`## Components that import each other (0)`.

## 6. Design

**Settings** (`.devtools/components_index.settings.json`):

```json
{"package_dir": "devtools", "import_prefix": "devtools", "extra_source_dirs": ["skills"],
 "count_extra_dirs": true, "docs_dir": ".devtools/components",
 "script_path": "plugins/dvt-milestone/skills/components/scripts/components_index.py"}
```

`script_path` is how the generated files and messages name the script (D1).

**Components** (D2): one entry per module, since each module is one tool with its own
command line, and a file goes under one entry only (`build.md`, section 3). The ids use
the project's words:

| Id | Module |
|---|---|
| `plugins.build` | `devtools/build_plugins.py` |
| `plugins.release` | `devtools/release_plugins.py` |
| `sync.copies` | `devtools/sync.py` |
| `migrate.from_gsd` | `devtools/from_gsd.py` |
| `components.index` | `skills/components/scripts/components_index.py` |
| `components.rules` | `skills/components/scripts/rules_check.py` |
| `handoff.notes` | `skills/dev-handoff/scripts/handoff.py` |
| `review.rounds` | `skills/milestone/process-phase/scripts/review_tool.py` |
| `phase.state` | `skills/phase/process-phase/scripts/phase_tool.py` |
| `phase.coder_pool` | `skills/phase/process-phase/scripts/coder_pool.py` |
| `phase.codex_gate` | `skills/phase/process-phase/scripts/codex_gate.py` |
| `phase.test_selection` | `skills/phase/pytest/phase_selection.py` |

Each entry has `does`, `verbs` (ten to twenty phrases, with the script's subcommands),
`status: canonical`, `modules`, and `tests` (the files that run the script; see
section 2).

**Subsystems** (D3): the paths through the code where one script runs another. The
scripts import nothing from each other, so every such step is a run-time load, and each
subsystem's `notes:` states it.

| Id | Flow | The run-time load `notes:` states |
|---|---|---|
| `subsystem.release` | `plugins.release -> plugins.build` | `release_plugins.py` loads `build_plugins.py` with `importlib` |
| `subsystem.rule_check` | `components.rules -> components.index -> phase.state` | `rules_check.py` runs `components_index.py facts`, and `phase_tool.py facts` for `check --phase`, as subprocesses; it also loads `phase_tool.py` with `importlib` for its fact types |
| `subsystem.phase_status` | `phase.state -> phase.coder_pool` | `phase_tool.py` runs `coder_pool.py show --json` for the track cap |

The skills' own workflows (process-phase's steps, a hand-off) are agent procedures written
in Markdown, not code paths, and are not subsystems.

**Reading** (D4): for each module, read its module docstring, its command-line parser and
dispatcher, and every public function's signature and docstring (the generated
`modules/` pages). Open a function's body wherever `does` or `verbs` claims more than the
docstring says. An entry is `checked: partial` unless its whole module was read; the
partial list goes in the record (O5).

**`distinct_from`** (O8): the helpers that several scripts define for themselves under one
name (`plugin_root`, `checkout_root`, `load_settings`, `git`, `Stop`). They are copies by
design (R0.1). `review` reports same-named definitions as places to look, and
`distinct_from` on the entries that share them records that they are separate on purpose.

**Search cases** (`search-cases.md`, hand-written; the tool ignores it). Nine capabilities
in a newcomer's words, each with its expected component, and one negative case:

1. copy the skills into my project → `sync.copies`
2. move my planning folder off GSD → `migrate.from_gsd`
3. bump the plugin version and tag a release → `plugins.release`
4. regenerate the plugins folder → `plugins.build`
5. does the project already have a function for this → `components.index`
6. enforce which areas may import which → `components.rules`
7. continue this branch on another machine → `handoff.notes`
8. get an independent review of a phase diff → `review.rounds`
9. which phase is next and can it advance → `phase.state`

Negative: "deploy to kubernetes" → `no component matched`, or no component hit matching
more than one word.

**`REVIEW.md`** (O6): the groups `review` prints, then what the reading noticed. These are
suggestions, not acted on.

## 7. Decisions

| # | Question | Readings, and what each costs | Proposed |
|---|---|---|---|
| D1 | `script_path` | **(A)** The built copy's path, so every message names a command that runs here (R0.3). **(B)** Leave it out: a plugin install names `${CLAUDE_PLUGIN_ROOT}/…`, which no shell here expands | (A) |
| D2 | How many components | **(A)** One per module, 12. **(B)** Group `plugins.build` and `plugins.release` as one: they are one release step, but each has its own command and its own tests | (A) |
| D3 | Which subsystems | **(A)** The three paths where one script runs another, above. **(B)** Also the skills' workflows: those are agent procedures, which the import graph and `review` cannot check | (A) |
| D4 | How deep the reading goes | **(A)** As in section 6, with `checked: partial` where a body was not read. **(B)** Every line of the 12 modules, about 10,500, before writing: the plan's estimate, but more than one reading turn holds | (A) |

## 8. Tests and gates

No test file changes in this phase. The gates, each run from the repository root, with
`C=plugins/dvt-milestone/skills/components/scripts/components_index.py`:

- G1: `python3 $C write` exits 0.
- G2: `python3 $C --check --strict` exits 0.
- G3: `test ! -e .devtools/components/unassigned-baseline.txt` exits 0.
- G4: `python3 $C review` exits 0 and prints `## Components that import each other (0)`.
  Its flow group lists only the steps section 6 states as run-time loads.
- G5: `python3 $C search --explain <case>` for each case of `search-cases.md`: the
  expected component is the first `component` line. For the negative case, no component
  line matches more than one query word.
- G6: `python3 devtools/build_plugins.py --check` exits 0.
- G7: `uv run --no-project --with pytest python -m pytest tests -q` exits 0 (R5 now
  passes on this machine, section 2).

## 9. Out of scope for this phase

- `tests/test_own_index.py`, the gates in `.devtools/project.md`, `AGENTS.md`, and the
  pages (phase 4).
- Any code change `REVIEW.md` suggests.
- The R5 skip guard (vasiloglou/dev-tools#31).

## 10. Size

- `COMPONENTS.md`: 12 components and 3 subsystems, about 180 lines;
- the generated `modules/` pages and `graph.md`;
- `search-cases.md`, about 25 lines, and `REVIEW.md`, about 40;
- the settings file.

## 11. Approval instrument

This prose, with the search cases as the corpus: they are written before the entries,
in section 6, and G5 runs them as they stand.

## 12. Owner gate: delegated approval (auto=true), 2026-11-21

- **Authorization.** The owner's invocation `/dvt-milestone:process-milestone auto` for
  component-index, and the owner's "go on" after phase 2's pull request was opened. That
  covers this spec's ruling. It does not cover merging, tagging or posting to GitHub.
- **D1 to D4: as proposed.**
- **Refuted premise.** Plan section 3, "Three load another script at run time", lists
  three of five. `rules_check.py` also runs `components_index.py facts`, and `phase_tool.py`
  runs `coder_pool.py`. Section 6 states all five; the plan's wording is repaired at the
  close.
- **Unreviewed.** No review round reads this spec before the code. The phase's diff
  review (`--subject phase`) reads both.

## 13. Implementation findings

- **IF1 (phase-3-r1 F2), 2026-11-21.** Section 6's `subsystem.rule_check` row said
  `rules_check.py` "runs `components_index.py facts`, and `phase_tool.py facts` for
  `check --phase`, as subprocesses; it also loads `phase_tool.py` with `importlib` for its
  fact types". That wording is kept above. The code (`rules_check.py`, `check_phase` and
  `vocabulary`) does this instead: `check` and `test` run `components_index.py facts`,
  and `test` then loads `phase_tool.py` with `importlib`; `check --phase` runs
  `phase_tool.py facts` first, then `components_index.py facts`. The entry's `notes:`
  says so; its `flow:` keeps the order of `check` and `test`.
