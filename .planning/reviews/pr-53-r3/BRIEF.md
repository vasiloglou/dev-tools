# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this change do what it sets out to do for every input of the classes it names, and what does it break?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. changed --strict asks both components when a file moves between them by a modules edit: a tracked file of any kind, a link without its target included, or a file git ignores that any modules line names or that is a counted module
- C2. git's -z listings and the base-blob requests are handled as bytes, so a carriage return, a line break or bytes that are not UTF-8 in a file's name or in the project's folder name no longer stop changed, write or --check, and such a file is still the file of its component
- C3. every file name changed and --check print is one line, its unprintable characters escaped, and every command, --help included, escapes output its stream cannot encode instead of stopping
- C4. the tests added fail on main and pass on this head; nothing else changes behaviour

## The change under review

Pull request #53, https://github.com/vasiloglou/dev-tools/pull/53, at head `c60b38fa91a5e43d511fb9b4c48d28d8952fce28` (base `d82c87ed449c2d66aa3e723855a33c42d37f3437`). Its diff is `.planning/reviews/pr-53-r3/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/reviews/pr-53-r3/diff.patch` | `9b6125ca8aab44275ec15f8fa82d3c49a847b7c460bc8ff98037e488c847b92d` |
| `.planning/reviews/pr-53-r1/FINDINGS.md` | `c3f8f0490a2df132c29f10d3661c15c4d6973049991ca5943f27054b61110fb4` |
| `.planning/reviews/pr-53-r2/FINDINGS.md` | `4ffe6de87b58c105df9a8b5b9560cd03b99bef6035fd6871c91dc58dc2b6990d` |

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
