# Component index review, 2026-11-21, reread 2026-11-22

Scope: the whole index, at its first build (phase 3 of the component-index milestone).
Code read at commit `f25d3a5`: 12 components and 3 subsystems after the build (none
before), 2 modules read in full and 10 in part. On 2026-11-22 the 10 were reread in full at
`3963a46` by four readers, one file per module in
`.planning/milestones/component-index/notes/phase-3-reading/`, and their entries rewritten
from those files; no entry is `checked: partial` now. These are suggestions; neither
reading changed code.

## What was repaired in the index

Nothing: this is the first build. Recorded on the way:

- `sync.copies`: `duplicates: devtools/from_gsd.py`, for `other_plans` and `OTHER_PLANS`
  (suggestion 1).
- `migrate.from_gsd`: `distinct_from: plugins.release, plugins.build`. Its `Stop` and `git`
  are its own, and its `build` makes a conversion plan, not plugins.

## What the reread repaired in the index

- Every `does` that named part of a command list now names all of it (`phase.state` 8 of
  15, `components.index` without `init` and `list`), and `components.index` no longer says
  it generates the catalog: the catalog is hand-written, `write` fills its generated lines.
- `subsystem.rule_check`'s flow was `components.rules -> components.index -> phase.state`;
  `components_index.py` never runs `phase_tool.py`. It is now the order of `check --phase`.
- `subsystem.release` named only `bump`: `release_plugins.py` loads `build_plugins.py` when
  imported, and every command uses it. `subsystem.phase_status`: the track cap only warns.
- `handoff.notes` said "take one over": `takeover` checks and reports, it switches nothing.
- Notes now give each script's exit codes where they differ from its docstring.

## Suggested code changes

| # | Kind | What | Where | Size | Checked how |
|---|---|---|---|---|---|
| 1 | Duplicate | `OTHER_PLANS` is the same list in both, and `other_plans` the same loop; `sync.py`'s also flags a planning folder in a format the phase tool does not read | devtools/sync.py:454 and :459, devtools/from_gsd.py:46 and :489 | small | read both functions; `diff` of the two lists printed nothing |
| 2 | No tests | No test in `tests/` runs the pytest plugin | skills/phase/pytest/phase_selection.py | small | `grep -l phase_selection tests/*.py` printed nothing |
| 3 | Split | The three largest modules each hold several jobs behind one command line | skills/phase/process-phase/scripts/phase_tool.py (2,051 lines), skills/components/scripts/components_index.py (1,664), devtools/from_gsd.py (1,410) | large | line counts, and the command lists in their docstrings |
| 4 | Defect | dvt-milestone ships `rules_check.py` but not `phase_tool.py`, which its default `phase_script` names, so `check --phase` exits 2 there | skills/components/scripts/rules_check.py:256; plugins/dvt-milestone/skills/ | small | `find plugins -name phase_tool.py` lists only dvt-phase's |
| 5 | Gap | `review`'s same-named-definition leads look only under `package_dir`, not the folders `count_extra_dirs` counts | skills/components/scripts/components_index.py:1317 | small | read; for dev-tools no module under `skills/` is examined |
| 6 | Docstring | Exit codes and claims a docstring gets wrong: `phase_tool.py status` always exits 0; `review_tool.py` exits 1 on bad settings (says 2); `from_gsd.py` says it never calls git (it reads with git); `coder_pool.py` says the pool becomes Claude Code's coder (only when `claude` is on PATH) | the four modules | small | runs on temp copies by the readers, and the cited lines |

### 1. One list of other planning tools

Both `devtools/` scripts carry the same `OTHER_PLANS` and the same search over it. They
both run from a dev-tools checkout and are not shipped to projects, so they could share
one module. A change to the list now has to be made twice. What could break:
`from_gsd.py`'s output shape (`{"tool", "sign"}`) differs from `sync.py`'s
(`(sign, tool)`), and each has its own callers.

### 2. A test for phase selection

`phase_selection.py` is a pytest plugin that a project uses as its root `conftest.py`. A
test would run pytest on a small project with acceptance tests of a complete and of an
open phase, and check what `--phase NN` selects.

### 3. Large modules

Each is one tool with one command line, and the skill's rule is one file under one
entry. Splitting would let the index give each job its own entry. For the scripts under
`skills/` that has a cost: R0.1 of the milestone plan says a shipped script stands alone,
so a split must still ship each command as one file, or teach the sync to copy several.

## Not confirmed

- Six scripts under `skills/` each define `plugin_root`, `checkout_root` and
  `load_settings` (R0.1: a synced or plugin copy imports nothing from another). Settled on
  2026-11-22: `plugin_root` and `checkout_root` are the same code in all six; `load_settings`
  is the same only in `phase_tool.py` and `coder_pool.py`, since each tool checks its own
  settings. Suggestion 1 holds for the list and the loop only: the two return different
  shapes, and `sync.py`'s also flags a planning folder the phase tool cannot read.
- Whether a GND older than 0.3.1 accepts the value lists `rules_check.py` adds to its model
  (rules_check.py:365) was not checked.

## Searches tried

- "copy the skills into my project" -> `sync.copies`
- "move my planning folder off GSD" -> `migrate.from_gsd`
- "bump the plugin version and tag a release" -> `plugins.release`
- "regenerate the plugins folder" -> `plugins.build`
- "does the project already have a function for this" -> `components.index`
- "enforce which areas may import which" -> `components.rules`
- "continue this branch on another machine" -> `handoff.notes`
- "get an independent review of a phase diff" -> `review.rounds`
- "which phase is next and can it advance" -> `phase.state`
- "deploy to kubernetes" -> `no component matched`
