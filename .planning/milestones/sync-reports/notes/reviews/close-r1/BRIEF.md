# Review brief: the milestone close

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the milestone's evidence establish each completion predicate C1 to C7 of the plan, and what does a project that syncs from this branch see that the records do not say?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. C1: the observed case is a test with its own fixture, and the records show apply --dry-run exit 0 naming review-pr, check exit 0 with the count, check --strict exit 5.
- C2. C2: no test of tests/test_sync.py as on main at 811b4a3 was edited, and each exits as there.
- C3. C3: check --receipt-only prints the lines check printed on main, reads no source and starts no git process.
- C4. C4: a checkout behind its upstream delivers the upstream's files and stays unchanged; own work is delivered as it is with a warning; a failed fetch is a warning with exit 0.
- C5. C6: the README, docs/adopt.html, the examples and the adopt skill describe what the code does, and each changed capture is real output.
- C6. The records' boundaries name every limit a reader needs: what was not reviewed, not run, or not covered.

## The change under review

The files below, as they stand at `ff97d1050a34` with uncommitted changes.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/sync-reports/notes/sync-reports-plan.md` | `8dc8f11e9aa1df8e9aa909cff1fbab17f57afb09eea67e4e4c4d41fcedd532fb` |
| `.planning/milestones/sync-reports/001-plan.md` | `e6fc8c03f5e86b35af37fb6fe587afb90bcb2e44ec727399e8a5592eafdb5375` |
| `.planning/milestones/sync-reports/002-phase-1.md` | `481261f9099b2fb27bc838f3bbaabf654e57059421fe3ed04edb34b5438cc42f` |
| `.planning/milestones/sync-reports/003-phase-2.md` | `b8cd5012a85b25d8c155a70fa8aefabc58702e21b88e54e2b65da30533a08f1a` |
| `.planning/milestones/sync-reports/notes/phase-1-spec.md` | `778a2dcb124adee54e08847fdeed55bbea1bc7ae121de80ab656843f97dad41f` |
| `.planning/milestones/sync-reports/notes/phase-2-spec.md` | `5672de6274c77e8a0b2194f0b74e22c96a880a92ac27d1e7257c249ecda4a77a` |
| `devtools/sync.py` | `56759e3a89f25fea1f72bf41eef46577baee0636e7ca82c05599a5acebd872d0` |
| `tests/test_sync.py` | `668c3b0d1ad71400c011cf6a67d15623633cdcfe46ba66e741e6222f57d285a8` |
| `README.md` | `db3ed84d9df6e4f55082d868dfcab297228c21c2ad22d4cd0aad7cd32acb5208` |
| `docs/adopt.html` | `077343d19932a2bce664d4d06cda22e493343ea956801090656d31415629485f` |
| `skills/adopt-devtools/SKILL.md` | `8c735a4db21040d31ab223d78ad47592b8ce3aa0321835cc460e995b50edba09` |
| `examples/milestone-project.devtools.toml` | `7221089d737f9e94711e1da7eed26a1140d4e5e50d41b139e376f5351945a2e3` |
| `examples/phase-project.devtools.toml` | `71caa4a90c9d365c5a9e77dde8267fa6a74a962ca9c085bc82074b58647b8769` |

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
