# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the repairs of phase 2 review round 1 do what its ledger says, and where do they break a case that worked before them?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. read_commit writes every blob of the commit with mode 0644 or 0755 as the tree records it, ignoring export-ignore, tar.umask and any other local git setting.
- C2. No temporary folder outlives resolve_source unless it is returned with its cleanup.
- C3. A behind checkout with any tracked or untracked change under skills, agents, devtools or examples is delivered as it is, whatever git status is configured to show.

## The change under review

The work from `acc9ee3` to the working tree at `f65f66a6e2a3`. Its diff is `.planning/milestones/sync-reports/notes/reviews/phase-2-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/sync-reports/notes/reviews/phase-2-r2/diff.patch` | `78e031cd49adfc454acb4701cb050759ab80ea25dc1182212d6fbd6bb7ff6569` |
| `.devtools/components/modules/_root.md` | `a6d3c83ff71cf097683b65c19239b1b191206560cbe1d3662285c3216eb69901` |
| `.planning/milestones/sync-reports/notes/phase-2-spec.md` | `1fc1da308928ec041c95d37c82d5c05ca22c64f184f31ddfded7c1a2698f7f2d` |
| `.planning/milestones/sync-reports/notes/reviews/phase-2-r1/BRIEF.md` | `d0fc386ddc1769ceb5e38fa0e228b41392283558cd0c96c7bfbbad937faf37af` |
| `.planning/milestones/sync-reports/notes/reviews/phase-2-r1/FINDINGS.md` | `7370d96610c1448571ccf3767860583ca2de7e52e6005c344fb023ccfffcbade` |
| `.planning/milestones/sync-reports/notes/reviews/phase-2-r1/brief.json` | `e95b45e1c5fb8a0d41ba5c858658da85f422a8d6bf4355838f064c1b53dee855` |
| `.planning/milestones/sync-reports/notes/reviews/phase-2-r1/diff.patch` | `34fcd3a61c3a14c1e241758de3a11b969da3b864941b5020b1679ff4961fea8d` |
| `.planning/milestones/sync-reports/notes/reviews/phase-2-r1/review.md` | `9cc2bd90e1d25b144b1c945ae88dd975130e4ed361dd6d754687ad6d22f8de7a` |
| `.planning/milestones/sync-reports/notes/reviews/phase-2-r1/run.json` | `62c9fd0e29eadf3d34357697c29884bd6ca319d1d2c2913397ea2416682e17c8` |
| `devtools/sync.py` | `2d68dbc9b2c4a38c42b4a6b14f476f8dfaf322882827da2dfdf486398495e3d1` |
| `tests/test_sync.py` | `945eb81ad376773bd2deb627a89e0edf6bb9f572db0f9a04d10e4a7fc1e1ea54` |

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
