# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Phase 4 of the component-index milestone adds a test that is meant to fail while dev-tools' own component index is out of date, and names the index in the project's rules and pages. Does the work do what notes/phase-4-spec.md says, and where can the claims below be shown false, by the code or a command?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. tests/test_own_index.py::test_the_index_is_current fails in every state of this repository in which the built copy's --check --strict exits non-zero or .devtools/components/unassigned-baseline.txt exists, and passes otherwise. There is no way to leave the index out of date that this test passes.
- C2. Each of the six other tests can fail: none passes for a reason other than the line it asserts on, and each line problems() can return has a test that fails without it.
- C3. The tests read and write nothing outside the checkout and pytest's tmp_path, and give the same result under Python 3.11, 3.12, 3.13 and 3.14.
- C4. Every sentence this change adds to .devtools/project.md, AGENTS.md, CONTRIBUTING.md, README.md, docs/milestone.html, docs/components.html and docs/contribute.html is true of the repository at this commit, and every command it names runs as written from the repository root.
- C5. Each obligation O1 to O13 of notes/phase-4-spec.md is discharged where its row says, and the spec's implementation findings IF1 to IF3 say what the code and the commands show.

## The change under review

The work from `827e766` to the working tree at `d49bdf472416`. Its diff is `.planning/milestones/component-index/notes/reviews/phase-4-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-4-r1/diff.patch` | `9aedbef2083e887a9af62fe4506d2c5e2860cdc416f66853665e2bcba0eeb215` |
| `.devtools/project.md` | `1e485b868fde627032c65f9bf311899d4cb18d8a5a0ba91c8ffec8b9de54ff3e` |
| `.planning/milestones/component-index/notes/phase-4-spec.md` | `4cedcc74777378ccb315a396e9d252550e30fd9cc016de2cca640fc5edda8a05` |
| `AGENTS.md` | `2aa20beafc95d7fda49583f5c852b8091f40ff64e1d21c5c0ee0c1c3c9730e60` |
| `CONTRIBUTING.md` | `21f65706f46e6c6677d7202170dbc5f834e75832c88926324fbc611acc19d64f` |
| `README.md` | `18ff55e0a7cadc3ce46ec668699ae83a768742eff82b7e7282359c07fc90462d` |
| `docs/components.html` | `c19c726f27e2d62245acd14ed3f5ef7673cca36ee802a784eda203531bbf3d03` |
| `docs/contribute.html` | `376da66c13656492193418b236ea674b3c29e690326c3003b2bc100f6d3f05c5` |
| `docs/milestone.html` | `ae396d9aa8b15fe00afd6c5f7309d65ae0f5d8add1e43839e95e42c1e9ab0522` |
| `tests/test_own_index.py` | `ef4183f2aac2de78800e2193851e16fd66c5c12bd3ad7b7d2be22c53570511df` |
| `plugins/dvt-milestone/skills/components/scripts/components_index.py` | `3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14` |
| `.planning/milestones/component-index/notes/component-index-plan.md` | `3cc5eb4924e69fb5584fd2613a0246718a27b5b3dd9e58f34afebabb97b886a9` |

You may read anything else in the repository that helps you answer.

## Rules

- Read only. Do not edit, create, stage, commit, push or post anything.
- Do not open `.env` files, keys, tokens, `auth.json` or any other credential file, and do
  not print environment variables. If you need one, name it and go on without it.
- A finding names its file and line and the consequence someone would observe. Run what
  you can to show it; where you only read, say so.

## What to return

1. Findings, each with an id (F1, F2, ...), file and line, what is wrong, the observable
   consequence, and how to reproduce it. A finding with no observable consequence is
   style: label it so.
2. What you checked and found true.
3. What you could not check, and why.
4. A last line: `VERDICT: APPROVE` or `VERDICT: CHANGES_REQUESTED`.
