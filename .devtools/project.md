# dev-tools' own rules for the dev-tools skills

The skills of the `dvt-milestone` plugin read this file first when they run in this
repository. It holds what is true of dev-tools only. Anything that would hold in every
project belongs in the shared skill under `skills/`, not here.

## What runs here

- **Workflow.** The milestone workflow, from the `dvt-milestone` plugin, which
  `.claude/settings.json` turns on. Codex installs the same plugin with
  `codex plugin add dvt-milestone@dvt`.
- **The released version runs, not the branch.** A phase that changes a skill is still
  run by the released text of that skill. To try the changed text, build the plugins
  (`python3 devtools/build_plugins.py`) and start `claude --plugin-dir plugins/dvt-milestone`.
- **Planning folder.** `.planning`. Its scaffold is `.planning/PROJECT.md`, written on
  2026-11-21 when the project took the workflow. Nothing else is scaffolded: a milestone
  adds its own folder under `.planning/milestones/`. If `PROJECT.md` is missing, restore
  it from git; no skill writes it again.
- **Component index.** In `.devtools/components/`, with its settings in
  `.devtools/components_index.settings.json`. It has a component for every module of
  `devtools/` and `skills/`. (`docs/` is the public site, so the default folder
  `docs/components` was not free to use.)
  - A phase runs the three component steps with the copy of the script in `plugins/`,
    from the repository root:
    `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py`.
  - Not the copy under `skills/`: it reads its settings from beside itself, inside the
    product.
  - Not an installed plugin older than 0.1.7: it refuses the settings file with
    `unknown setting(s): allow_baseline` (older than 0.1.5: `count_extra_dirs`).
  - After a change to a module of `devtools/` or `skills/`: rebuild the plugins, run that
    script's `write`, and commit `.devtools/components/` with the change. The generated
    pages hold each definition's line number, so most changes to a module move them.
- **Workflow skills of its own.** None. `adopt-devtools` and `move-from-gsd` are part of
  the product; they do not own work in this repository.

## Which lane a piece of work takes

The owner says which. Where the owner has not said, propose one of these and wait:

- **Fast lane.** A fix, a wording change, a page of the site, a contributor's pull
  request: branch, test, pull request, as `CONTRIBUTING.md` says. No milestone and no
  record. `review-pr` runs when the owner asks for a review.
- **Evidence lane, as a milestone.** A new skill, script or subcommand; a change to a
  format that a project's files depend on (`.devtools.toml`, the receipt, the planning
  files, the record format, a hand-off note); a change to what a gate refuses.

A milestone is named for what it delivers (`component-index`), not for a plugin version.
A plugin version (`0.1.3`, tagged `plugins-v0.1.3`) is a release, and one milestone can
ship in several.

## Gates

Run from the repository root, with Python 3.11 or newer.

| Gate | Command |
|---|---|
| All tests | `uv run --no-project --with pytest python -m pytest tests -q` |
| One test file (a focused gate) | `uv run --no-project --with pytest python -m pytest tests/<file>.py -q` |
| The plugins match the skills | `python3 devtools/build_plugins.py --check` |
| Whether a release is due | `python3 devtools/release_plugins.py status` |
| The component index is current, and no baseline is kept (`allow_baseline` is false here; when a phase closes; `tests/test_own_index.py` runs it too) | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict` |
| The index against what a change touched (before a pull request, after `git fetch origin`) | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main` |

There is no lint command and no CI: the tests run on the machine that makes the change.

## Review instrument

- **Instrument.** process-phase's review helper (`review_tool.py`), with its defaults:
  the reviewer is the other tool (Codex when Claude Code drives, Claude Code when Codex
  drives). There is no `.devtools/review_tool.settings.json`.
- **Plan-review bar.** The default: one independent reviewer in a different tool, for the
  milestone plan and for the milestone close.
- **Where rounds are kept.** A phase's rounds in its milestone's `notes/reviews/`; a pull
  request's rounds in `.planning/reviews/pr-<number>-r<round>/`.
- **Posting.** A review is posted to a pull request only with the owner's approval for
  that pull request.

## Standing design rules

The rules are the seven under "What makes a change easy to accept" in `CONTRIBUTING.md`,
which is where they are stated. A spec discharges each one by name, or says in one
sentence why it does not apply.

| Rule (its heading in `CONTRIBUTING.md`) | Prevents | A spec discharges it by naming |
|---|---|---|
| A script change comes with a test | A script that passes here and fails in a project | Each script and function the phase changes, and the test in `tests/` that fails without the change |
| The plugins are rebuilt, and released under a new version | A project that keeps the old skill because the version did not change | Whether a skill or agent changes; if so, `release_plugins.py bump` and the `build_plugins.py --check` gate |
| A wording change says what prompted it | Prose changed for no reason anyone can check | The run or the misreading behind each changed sentence of a skill |
| Shared skills stay general | One project's rule shipped to every project | Each rule the phase adds to a skill, and why it holds outside this repository |
| Both agents read the same file | A skill that is right in one tool and wrong in the other | Each changed skill, and what was checked for Claude Code and for Codex (paths, `${CLAUDE_PLUGIN_ROOT}`, how a skill is invoked) |
| Captures on the site are real output | A capture that shows what no command prints | Each capture the phase replaces, and the run the new one came from |
| The page that describes it is updated too | A site that describes what the skills used to do | Each page of `docs/` that describes the changed behaviour, changed in the same pull request |

## What needs the owner each time

The owner is the maintainer. `auto=true` covers the plan, spec and close rulings of the
milestone it names, and none of these:

- merging a pull request into `main`;
- `python3 devtools/release_plugins.py tag`, which tags and publishes a release;
- posting to GitHub: a comment, a review, a label, a new issue, a close.

## Record fields

None beyond the shipped record format.
