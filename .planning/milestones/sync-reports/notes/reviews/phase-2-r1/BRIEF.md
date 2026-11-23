# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Where does this code, its tests or its pages not do what the phase 2 spec and the phase 1 repairs say, or do something to a dev-tools checkout or a synced project that its user would not expect?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. P2.1: a checkout only behind its upstream delivers the upstream's files, the receipt records the upstream commit, and the checkout's HEAD, branch and git status are unchanged.
- C2. P2.2: a checkout behind with commits or uncommitted changes of its own under skills, agents, devtools or examples is delivered as it is, and the warning is printed before anything is written.
- C3. P2.3 and P2.3b: level, ahead only, detached, no upstream, not a checkout, and an upstream configured with no ref each deliver the checkout, with no new line except the one warning for the missing upstream.
- C4. P2.4 and P2.5: a fetch that fails or times out is a warning with exit 0; --as-is starts no git fetch.
- C5. P2.6 and P2.7: compare reads the same files as apply; a source folder inside another repository is never fetched.
- C6. S0.2: no command this phase adds changes the dev-tools checkout except git fetch, and no temporary folder is left behind.
- C7. The phase 1 repairs (2120090) do what the phase-1-r1 ledger says, and standard output and exit codes of apply and check are as phase 1 left them.

## The change under review

The work from `e49b052` to the working tree at `acc9ee38e47e`. Its diff is `.planning/milestones/sync-reports/notes/reviews/phase-2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/sync-reports/notes/reviews/phase-2-r1/diff.patch` | `34fcd3a61c3a14c1e241758de3a11b969da3b864941b5020b1679ff4961fea8d` |
| `.devtools/components/COMPONENTS.md` | `ef998ad19c7fba7b97c4a32e04088decd201618909bd2d679dd8344158dacd2f` |
| `.devtools/components/modules/_root.md` | `ca5a9930c796aae12f87f1e4138a9668014a6c72838fb37bfb094394066f2da6` |
| `.planning/milestones/sync-reports/002-phase-1.md` | `481261f9099b2fb27bc838f3bbaabf654e57059421fe3ed04edb34b5438cc42f` |
| `.planning/milestones/sync-reports/README.md` | `196f8c6c3385a73e9cdb827853650974eb0e84e76f282c782b9adac5f10c8d5e` |
| `.planning/milestones/sync-reports/notes/phase-1-spec.md` | `778a2dcb124adee54e08847fdeed55bbea1bc7ae121de80ab656843f97dad41f` |
| `.planning/milestones/sync-reports/notes/phase-2-spec.md` | `859c8b41486945b764ddfdc16120cd82548ecd5a9300580f1e7c3277f5e406c0` |
| `.planning/milestones/sync-reports/notes/reviews/phase-1-r1/BRIEF.md` | `15e25faae48491b3c1accddc937363594c3c444cf65737f5e89d1be1d0148355` |
| `.planning/milestones/sync-reports/notes/reviews/phase-1-r1/FINDINGS.md` | `01f6aae49ba7804db9430a2b49cba2d28eb7aa93f8e66f8af1a541a58743f29f` |
| `.planning/milestones/sync-reports/notes/reviews/phase-1-r1/brief.json` | `a071f432433d01892c6b47bfe4155efea508048c7ccdaa9fbe23e7b1e7cace22` |
| `.planning/milestones/sync-reports/notes/reviews/phase-1-r1/diff.patch` | `0250dceb8ab9c29b2be278c1e66214f939b73c0078939af0ee0a40616f215a7e` |
| `.planning/milestones/sync-reports/notes/reviews/phase-1-r1/review.md` | `0d0aa0b73f57e97c878d0ef4d7c6c871003a6a6cd7f3313a0480951fc991386a` |
| `.planning/milestones/sync-reports/notes/reviews/phase-1-r1/run.json` | `134fa9b4d65ad8fbaead63b44e9faabac32da696cf5253ab5cf70129d3426eaf` |
| `README.md` | `db3ed84d9df6e4f55082d868dfcab297228c21c2ad22d4cd0aad7cd32acb5208` |
| `devtools/sync.py` | `6801d9da145223ef2f5c6c83288ffe6d265deacaa8a2ffa5e848a460f9e67e48` |
| `docs/adopt.html` | `077343d19932a2bce664d4d06cda22e493343ea956801090656d31415629485f` |
| `skills/adopt-devtools/SKILL.md` | `8c735a4db21040d31ab223d78ad47592b8ce3aa0321835cc460e995b50edba09` |
| `tests/test_sync.py` | `dd5a42819a7ffac0dab8ca637d097edc8db65a7bda439cd5b9b50d83ff70af7e` |
| `.planning/milestones/sync-reports/notes/sync-reports-plan.md` | `cb58b4996b218d241290fbb89a02941327b3ef2c399220b9025401248362b967` |

You may read anything else in the repository that helps you answer.

## A standing check: code fitted to its examples

Whatever the question above, also look in the code this change adds or changes for a
solution that handles the examples in its tests and fixtures, and not the whole class of
input it is given:

- a regular expression, string split, slice or index over structured text (JSON, YAML,
  TOML, source code, paths, command lines) that a parser or an existing reader in this
  repository already reads;
- a pattern over output this project renders itself (a report, a table, a log line), where
  the code could have been handed the data instead;
- a pattern fitted to the fixtures: it matches every committed example and fails on a
  legal input with other whitespace, quoting, casing, nesting, Unicode or a line break;
- a branch on one literal name, file or message, added to make one case pass;
- a second matcher for something an existing helper already does.

A regular expression is not a finding in itself: one that states the whole grammar of a
flat token (an identifier, a version number, a hex digest) is the right tool. For each
suspect, build a legal input that the tests and fixtures lack and run the code on it.
Report a finding only with that input: what the code returned and what it should have
returned. A suspicion with no breaking input is style: label it so. In your list of what
you checked, name each matcher you tried and the input you tried it with.

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
