# dev-tools

Development-process skills for agentic coding (Claude Code and Codex), kept in one place
and copied into each project that uses them.

Status: prototype.

## How it works

This repository is the canonical source. A project lists what it wants in a
`.devtools.toml` file, and `devtools/sync.py` copies those skills and scripts into the
project, where they are committed. The project takes no dependency on this repository:
the scripts are ordinary files, run with the project's own Python.

Each script reads its project-specific values (directories, package name, branch prefix)
from a settings file beside it, which the sync writes from `.devtools.toml`.

```bash
python3 path/to/dev-tools/devtools/sync.py apply --project .
python3 path/to/dev-tools/devtools/sync.py check --project .
```

- `apply` copies the files and records each one in `.devtools-receipt.json`. It writes
  nothing unless every file can be written: a file the project edited by hand needs
  `--force`, and an existing file it does not manage yet needs `--adopt`.
- `check` compares the managed files with the receipt. It needs only the project.

See `examples/phase-project.devtools.toml` for a complete project file.

## What is here

| Path | What |
|---|---|
| `skills/phase/process-phase/` | Run one roadmap phase test-first: Orient, Discuss (with a timeboxed prototype), Specify (locked acceptance tests), Plan, Implement, Verify, Close. `scripts/phase_tool.py` owns the status transitions and checks. |
| `skills/components/scripts/components_index.py` | Generate and search an index of a project's code by capability, so existing code is found before new code is written. |
| `devtools/sync.py` | The sync command. |
| `tests/` | Tests for the sync command. |

## Tests

```bash
uv run --no-project --with pytest python -m pytest tests -q
```
