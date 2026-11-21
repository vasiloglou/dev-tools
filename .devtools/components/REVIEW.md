# Component index review, 2026-11-21

Scope: the whole index, at its first build (phase 3 of the component-index milestone).
Code read at commit `f25d3a5`. 12 components and 3 subsystems after the build (none
before), 12 modules (2 read in full, 10 in part: their module docstrings, command lines and
documented functions). These are suggestions; the build changed no code.

## What was repaired in the index

Nothing: this is the first build. Recorded on the way:

- `sync.copies`: `duplicates: devtools/from_gsd.py`, for `other_plans` and `OTHER_PLANS`
  (suggestion 1).
- `migrate.from_gsd`: `distinct_from: plugins.release, plugins.build`. Its `Stop` and `git`
  are its own, and its `build` makes a conversion plan, not plugins.

## Suggested code changes

| # | Kind | What | Where | Size | Checked how |
|---|---|---|---|---|---|
| 1 | Duplicate | `OTHER_PLANS` is the same list in both, and `other_plans` the same loop; `sync.py`'s also flags a planning folder in a format the phase tool does not read | devtools/sync.py:454 and :459, devtools/from_gsd.py:46 and :489 | small | read both functions; `diff` of the two lists printed nothing |
| 2 | No tests | No test in `tests/` runs the pytest plugin | skills/phase/pytest/phase_selection.py | small | `grep -l phase_selection tests/*.py` printed nothing |
| 3 | Split | The three largest modules each hold several jobs behind one command line | skills/phase/process-phase/scripts/phase_tool.py (2,051 lines), skills/components/scripts/components_index.py (1,664), devtools/from_gsd.py (1,410) | large | line counts, and the command lists in their docstrings |

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
  `load_settings`. This is deliberate (R0.1: a synced or plugin copy imports nothing from
  another), and `review` does not list them, since they are in more than three components.
  Whether the copies have drifted apart was not checked; a `diff` of the six would settle it.
- The 10 entries marked `checked: partial` describe their modules from docstrings and
  command lines. A later review rereads their bodies, starting with the largest.

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
