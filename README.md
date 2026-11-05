# dev-tools

A development process for coding agents (Claude Code and Codex), kept in one place and
copied into each project that uses it.

**Documentation: <https://vasiloglou.github.io/dev-tools/>**

![The dev-tools documentation site](docs/assets/shots/home.png)

Status: prototype.

## What it gives an agent

- **Phase workflow.** One roadmap phase at a time, in seven steps: Orient, Discuss (with
  a timeboxed prototype), Specify (acceptance tests, locked before code is written),
  Plan, Implement, Verify, Close. You approve at four of them.
- **Milestone workflow.** A reviewed plan, a spec you approve before any code, an
  independent review of each change, and numbered records that are never edited.
- **Component index.** A searchable map of what the code already does, so existing code
  is reused instead of written again.

A project picks the workflow that fits it. Both use the component index.

## How a project takes it

This repository is the canonical source. A project lists what it wants in a
`.devtools.toml` file, and the sync command copies those skills and scripts into the
project, where they are committed. The project takes no dependency on this repository.

```bash
python3 path/to/dev-tools/devtools/sync.py apply --project .
```

```bash
python3 path/to/dev-tools/devtools/sync.py check --project .
```

- `apply` copies the files and records each one in `.devtools-receipt.json`. It writes
  nothing unless every file can be written: a file the project edited by hand needs
  `--force`, and an existing file it does not manage yet needs `--adopt`.
- `check` compares the managed files with the receipt. It needs only the project.

Rules that belong to one project go in a file that project owns,
`references/project.md` beside the synced skill. The sync never touches it.

See `examples/phase-project.devtools.toml` for a complete project file. A new project follows
the first sync with `python3 .claude/skills/process-phase/scripts/phase_tool.py setup`.

The sync command and the component index need Python 3.11 or newer; the phase state tool
runs on 3.9.

## What is here

| Path | What |
|---|---|
| `skills/phase/process-phase/` | The phase workflow. `scripts/phase_tool.py` owns the status transitions and checks, and `phase_tool.py setup` writes a new project's starter planning files. |
| `skills/phase/phase-tests/` | How a phase's acceptance tests are written and locked. |
| `skills/phase/pytest/phase_selection.py` | A pytest plugin: `pytest --phase NN` runs one phase's acceptance tests, and plain `pytest` leaves out phases that are not complete. |
| `agents/` | Helper agents the phase steps hand work to (test writer, researcher, implementer, verifier, code reviewer). |
| `skills/milestone/` | The milestone workflow: `start-milestone`, `process-milestone`, `process-phase`. |
| `skills/components/` | The component index: the skill, and `scripts/components_index.py`, which generates, checks and searches it. |
| `devtools/sync.py` | The sync command. |
| `docs/` | The documentation site (plain HTML, served by GitHub Pages). |
| `tests/` | Tests for the sync command and for the scripts a project runs after a sync. |

## Tests

```bash
uv run --no-project --with pytest python -m pytest tests -q
```
