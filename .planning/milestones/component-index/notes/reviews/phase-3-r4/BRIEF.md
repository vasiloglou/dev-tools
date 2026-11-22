# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 4. Does the repair of round 3 (notes/reviews/phase-3-r3, repaired at b471ff5) say truly what takeover checks, and where can the claims below be shown false, by the code or a command?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Every statement in the handoff.notes entry of .devtools/components/COMPONENTS.md is true of skills/dev-handoff/scripts/handoff.py at this commit.
- C2. components_index.py --check --strict exits 0, and the search case 'continue this branch on another machine' still puts handoff.notes first.

## The change under review

The work from `2149154` to the working tree at `b471ff515c4c`. Its diff is `.planning/milestones/component-index/notes/reviews/phase-3-r4/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-3-r4/diff.patch` | `47bda5110b5e3f84af7026aebdc4adf06344077bfc96d49be21b8e313c6cc513` |
| `.devtools/components/COMPONENTS.md` | `4c1713a7dd55ef0751caecb92f1476a2a0cc91490fb0e04547abfaf8e065c07e` |
| `skills/dev-handoff/scripts/handoff.py` | `74de4ada6271fc728c3929a7bce68dc3f3de11a1d460c76bbaa6b534d2162285` |
| `.devtools/project.md` | `e2f5561d5449bd9136880b6fa1bf696322bc70bdd98d583bdaa2a15a2ce25a7a` |

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
