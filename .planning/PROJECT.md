# dev-tools

The one-page statement of the project, read before any milestone is planned or run. The
reasoning at length is in `README.md` ("Why") and on the site (`docs/why.html`).

## The problem

A coding agent writes code faster than anyone can read it. What is left to settle is
whether the code does what was asked, whether it rebuilt something that already existed,
and whether the next session can carry on from it.

## What dev-tools is

A development process for coding agents (Claude Code and Codex), kept in this repository
and taken by each project that uses it: skills, the scripts they run, and helper agents.
A project takes them with the sync command (`devtools/sync.py`) or as a plugin
(`dvt-phase` or `dvt-milestone`).

They make an agent agree on the goal, write the tests first, reuse what exists, stop for
the owner's approval and leave a record. Each of those is held by a check that can
refuse, not by a sentence in a prompt.

## Who it is for

- The owner of a project, who approves at the gates and reads the records.
- The agents that work in that project, in either tool. A skill is one file that both
  read, byte for byte.

## What a change here has to keep true

- The skill text is the product. A changed sentence changes how an agent behaves in
  every project that takes the next update.
- Shared skills stay general. A rule for one project goes in that project's own
  `project.md`.
- A project that synced takes no dependency on this repository.
- A script a project runs is tested here, in `tests/`.
- The site in `docs/` describes what the skills do today, with captures from real runs.

## How it is developed

With itself, since 2026-11-21: the milestone workflow, from the released `dvt-milestone`
plugin. The project's rules for the skills are in `.devtools/project.md`, the words the
work uses are in `AGENTS.md`, and each milestone is a folder under
`.planning/milestones/`.

## Status

Prototype. Public, under the Apache License 2.0. The maintainer is the owner at every
gate and the only person who merges.
