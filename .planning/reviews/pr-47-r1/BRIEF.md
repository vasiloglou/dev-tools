# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this pull request do what its description says, and what does it break for a project that syncs dev-tools or for the dev-tools checkout it reads from?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. A shipped unit the config does not take, named by a synced file, is reported by apply and check, with the file that names it.
- C2. A unit added to dev-tools since the last sync is reported until the next apply.
- C3. declined in .devtools.toml silences a unit for good; a workflow folder the project takes nothing from is never reported.
- C4. check run from a dev-tools checkout, or with --source, says how many files an apply would update; check --receipt-only is the old check.
- C5. Every new line is a note with exit 0; check --strict exits 5 when there is anything to report; drift still exits 1; exits 0 to 4 keep their meaning, and no existing test was edited.
- C6. A checkout only behind its upstream delivers the upstream commit's files and is not changed; one with work of its own, a detached HEAD or tag, or no upstream is delivered as it is; --as-is skips the fetch; these lines go to standard error only.

## The change under review

Pull request #47, https://github.com/vasiloglou/dev-tools/pull/47, at head `fe1c2c2bf4f7efe3842bd08e473e047e7fa49d07` (base `a8d6f42ffb2929d38afd8512e0f07d3f27f2f966`). Its diff is `.planning/reviews/pr-47-r1/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/reviews/pr-47-r1/diff.patch` | `bcd1e55d378350bd2b04e86122401c9ff59a03f86b4a0671c19c40acf66603a8` |
| `.planning/milestones/sync-reports/notes/sync-reports-plan.md` | `d89a7175429c521932aba262848aff0989044355590c50f80d7a5f52a1936ad9` |
| `.planning/milestones/sync-reports/004-close.md` | `baf7b4f263ac6332e3739e2c33e92cb2e7221ca7ed0ba59ed9837ada28fec5d8` |

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
