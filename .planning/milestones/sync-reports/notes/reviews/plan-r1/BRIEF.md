# Review brief: the milestone plan

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can each phase of this plan be implemented and tested as written, and would a project that syncs see the behaviour section 2 describes?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The baseline in plan section 3 describes what devtools/sync.py prints at 811b4a3 for a project with that config.
- C2. Under the phase 1 design, a caller that passes no new option gets every line and exit that apply and check produce on main, with new lines only after the summary line.
- C3. The named rule of the phase 1 spec reports skills/milestone/review-pr for the baseline's config, and reports nothing for either example config as the spec changes them.
- C4. The normative order in section 6 of the phase 1 spec gives every unit exactly one outcome, and each step has a test in section 8 that fails when the step is wrong.
- C5. No existing test of tests/test_sync.py needs an edit under the design, plan decision D5 included.
- C6. The table of phase 2 in plan section 2 gives one outcome for every state a git checkout can be in, and none of them changes the checkout.
- C7. Every completion predicate C1 to C7 has a gate or ruling that can fail it, and every gate command in plan section 9 can run as written from the repository root.

## The change under review

The files below, as they stand at `632c8337a889`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/sync-reports/notes/sync-reports-plan.md` | `d25a141852307716eb358b66d97fd4731a3abd148025a6f940c1f04c44886d1e` |
| `.planning/milestones/sync-reports/notes/phase-1-spec.md` | `b69a3e79763368c20a6d7c5f41692f1f09e5f69447c56a4fb7e79f0bf15c4d02` |
| `devtools/sync.py` | `1637af6f38ec3472e42da7ea3207445ba7b0fd25a0e3e73bba46b140e8da06f6` |
| `tests/test_sync.py` | `83923df083064d0833c81f037008344642c70ee2987b7a3311df0799ad63c2fa` |
| `examples/milestone-project.devtools.toml` | `6cb9f40fca5c929df1c07c5734b6e476522a5c24a48656f5520cc5bed7ee82b5` |
| `examples/phase-project.devtools.toml` | `af7c9ba367e74745fbe582fdd4d2788ca85b46aebd8ff512b638d6aadbedeae1` |
| `.devtools/project.md` | `1e485b868fde627032c65f9bf311899d4cb18d8a5a0ba91c8ffec8b9de54ff3e` |
| `.planning/PROJECT.md` | `d6b274e2937a8e44fa652ba46e4fdf1260460a8fb1a2a28dd37d67eea591df08` |
| `AGENTS.md` | `2aa20beafc95d7fda49583f5c852b8091f40ff64e1d21c5c0ee0c1c3c9730e60` |
| `CONTRIBUTING.md` | `21f65706f46e6c6677d7202170dbc5f834e75832c88926324fbc611acc19d64f` |
| `README.md` | `18ff55e0a7cadc3ce46ec668699ae83a768742eff82b7e7282359c07fc90462d` |
| `skills/adopt-devtools/SKILL.md` | `42f1e199c9d99bda2db3f985c4a3df9ed7f7a078c735e99b63ed06da4eed1022` |
| `docs/adopt.html` | `82fbf18d3138cee2acecc760218b02dd5ec97fb8dc326b85da4e1f932bbe2e37` |

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
