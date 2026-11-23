# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the fixes of the pull request's review round 1 do what its ledger says, and what do they break that worked before them?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. A local change to any path the project's config takes, inside or outside skills, agents, devtools and examples, keeps a behind checkout delivered as it is, with a warning.
- C2. A dev-tools source that is not a folder is a configuration error: check reports it as not compared (exit 0, or 5 with --strict) and apply exits 2.
- C3. No other output or exit of apply, check, survey or compare changed with these fixes.

## The change under review

Pull request #47, https://github.com/vasiloglou/dev-tools/pull/47, at head `fc7bd2883ddc3fa743ad5ed360db5fa9c805c4e0` (base `a8d6f42ffb2929d38afd8512e0f07d3f27f2f966`). Its diff is `.planning/reviews/pr-47-r2/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/reviews/pr-47-r2/diff.patch` | `ebda09c180be204f9bfa93dde27b966b1cadd464aa6d2552eabe32eb35470fe2` |
| `.planning/reviews/pr-47-r1/FINDINGS.md` | `bef9fea26011073b01ffe47e058a1bdd9985cad33505bc172360aea92d8898ab` |
| `.planning/milestones/sync-reports/005-pr-47-r1.md` | `8186ddb43f81b9560e655d874588325755b68a83d60760dabe56a2f9b1523dac` |

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
