# Working on dev-tools

dev-tools is developed with dev-tools. Work on this repository runs under the milestone
workflow, from the released `dvt-milestone` plugin, and is described in that workflow's
words.

Read before you start:

- `.devtools/project.md`: this project's rules for the skills (lanes, gates, review
  instrument, standing design rules, what needs the owner).
- `.planning/PROJECT.md`: what the project is.
- `CONTRIBUTING.md`: how a change reaches `main`.

## The product and the project's own use of it

| Path | What it is |
|---|---|
| `skills/`, `agents/`, `devtools/`, `examples/`, `docs/` | The product: what other projects take. |
| `plugins/`, `.claude-plugin/` | Generated from the product by `devtools/build_plugins.py`. Never edited by hand. |
| `.devtools/`, `.planning/`, `AGENTS.md`, `CLAUDE.md` | This project's own use of the product. |

A rule that is true of dev-tools only goes in `.devtools/project.md`, never in `skills/`.

## Words

Use these words, in plans, records, commits, pull requests and conversation.

| Word | What it means here |
|---|---|
| owner | The maintainer. The person who rules at a gate and the only one who merges. |
| milestone | A named stretch of work with its own plan, phases and close: `.planning/milestones/<milestone>/`. Planned with `start-milestone`, run with `process-milestone`. |
| milestone plan | `notes/<milestone>-plan.md` in the milestone's folder, in the plan's sections 0 to 10. |
| plan gate | The owner's ruling on the plan, after the plan review. |
| phase | One numbered part of a milestone, `phase-N`, run with `process-phase`: harvest, spec, owner gate, implement and verify, review of the diff, refactoring review, record and commit. |
| spec | `notes/phase-N-spec.md`. Approved at the owner gate before any code is written. |
| owner gate | A stop where the owner approves or amends. With `auto=true` the ruling is a delegated approval and is recorded as one. |
| gate | A command and its exit code. A record says "exited 0", not "passed". |
| record | `NNN-<scope>.md` in the milestone's folder: one per material event, numbered, never edited after its commit. |
| close | The end of a milestone: the close review, the question sweep and the close record. |
| review round | One independent review by the other tool: `phase-N-rK` or `pr-N-rK`, holding the brief, the review word for word and the findings ledger. |
| finding | A row of the findings ledger. Reproduced before it is believed; classed blocking, hardening or completeness; disposed fixed, deferred, rejected or open. |
| fast lane, evidence lane | Routine work with no record, and work whose risk earns a record. |
| standing design rule | A rule every spec discharges by name. Listed in `.devtools/project.md`. |
| obligation, carryover, residual | What a source assigns to a phase; what an earlier milestone left for this one; what a close accepts as not done. |
| refuted premise, open question | A belief a run disproved, and a question a run raised. Both are sections of a record. |
| component, component index | A unit of what the code already does, and the searchable map of them. |
| hand-off, takeover | Moving unfinished work on a branch to another assistant or machine, and continuing from its note. |
| release | A plugin version, tagged `plugins-vX.Y.Z`. Not a milestone. |

Words to leave behind: "the next version" for a stretch of planned work (it is a
milestone), "task" or "step" for a part of one (a phase), "sign-off" (an owner gate or a
ruling), "another pass" (a review round), "the fix list" (the findings ledger).

## Names

- `dev-tools`: the project and the repository, in prose.
- `devtools`: in file and folder names (`devtools/`, `.devtools.toml`, `.devtools/`,
  `adopt-devtools`).
- `dvt`: the marketplace, and the prefix of the plugins (`dvt-phase`, `dvt-milestone`).

## Commands

```bash
uv run --no-project --with pytest python -m pytest tests -q
```

```bash
python3 devtools/build_plugins.py --check
```

After changing a skill or an agent, `python3 devtools/release_plugins.py bump` raises the
plugin version and rebuilds `plugins/`; commit both with the change.

Before writing a module or a function, search the component index
(`.devtools/components/`) for what already exists:

```bash
python3 plugins/dvt-milestone/skills/components/scripts/components_index.py search <words>
```

## Before you finish

- Commit, push, merge, tag or post to GitHub only when the owner asks.
- `main` takes changes only through a pull request.
