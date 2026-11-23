# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

This pull request changes how a hand-off note is written, so that no value it prints can add a line of the note's own. Does it do what it sets out to do, and what does it break?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The note is now kept to one line per generated line at the two places it is put together (the header and the snapshot), whatever a value holds.
- C2. After this change, takeover does not report a checkout ready while an ignored path is missing, for any note written by handoff.py write, whatever the git remote, the base, --from, the project's setup_command or any other value the note prints.
- C3. A note with no control character in any value is written byte for byte as before.
- C4. test_t22 puts a forged section into every string of the snapshot and of the header in turn, found by walking the data, not from a list of field names, and into the setup command, once for each of the 8 line breaks Python splits lines at. Before the fix it failed for all 8.
- C5. The plugins are released as 0.1.6 (devtools/PLUGIN_VERSION, plugins/ rebuilt), and dev-tools' own component index is regenerated, with the handoff.notes entry updated.

## The change under review

Pull request #38, https://github.com/vasiloglou/dev-tools/pull/38, at head `17e63c61231fc8020d7e2a467778a593b61abf97` (base `811b4a3ef993aa7a9b7a9ff108a3b56c43a1440d`). Its diff is `.planning/reviews/pr-38-r1/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/reviews/pr-38-r1/diff.patch` | `b8784d328310b939a4281abe0889e09f90ec76258e42008254eee72cfdbfea65` |
| `skills/dev-handoff/references/handoff.md` | `4ab09c9621c60c1f7afdef00aa1eba4d4626d6490cf39fa8bc3222ec55a85629` |
| `.planning/reviews/pr-37-r1/review.md` | `1aeec1217056d7aabaf1138ee94bc782b654201602c09019c82a9645c24e87d1` |

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
