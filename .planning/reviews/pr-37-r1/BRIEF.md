# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

This pull request closes the component-index milestone with a close record, an amended plan and a close review round. Does it do what it sets out to do, and where is what it says untrue of the repository?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The pull request changes planning files only, under .planning/milestones/component-index/: no code, skill, page or plugin file.
- C2. On main at 811b4a3 the plan's five measurable completion predicates hold: the index check exits 0 at 12 of 12 modules, with no baseline file; each of the 9 search cases puts its component first, and the negative case matches nothing; the full suite exits 0 with 350 passed, and includes the test that fails while the index is out of date; .devtools/project.md and the pages that describe dev-tools' own use name the index; tests/test_handoff.py exits 0, and issue 28 is closed.
- C3. The sweep of the milestone's 15 open questions: 6 closed, 8 carried to the owner, 1 partly closed. Two of the carried ones are #33, already filed.
- C4. notes/component-index-plan.md, repaired at ten sites as amendment c1. Each repair keeps the earlier wording beside it and names the record that showed it wrong.
- C5. Codex reviewed the close, read-only: 18 files, among them handoff.py with the round 4 fixes (22d6258) that no earlier round had read. It approved with no findings. It did not run pytest; the test counts are the author's runs. The record's Review and Close ruling sections were written after that review read the record, so they are unreviewed.

## The change under review

Pull request #37, https://github.com/vasiloglou/dev-tools/pull/37, at head `6650e455e1ad2d37acddd51e12e8374573c08d46` (base `811b4a3ef993aa7a9b7a9ff108a3b56c43a1440d`). Its diff is `.planning/reviews/pr-37-r1/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/reviews/pr-37-r1/diff.patch` | `872d35908704e7900fe224639fcfb1b9d29fa5c3ec2287ee1780915aafa5a55d` |
| `.planning/milestones/component-index/001-plan.md` | `5efa7b890a4036186851c8a7e32a51dd3a4e17f816eddc06567dedf20b7c0b74` |
| `.planning/milestones/component-index/002-phase-1.md` | `c522ddb42eccb62b94f19480211ea46a821e1fd3190e76858b5b112f47bfcf03` |
| `.planning/milestones/component-index/003-phase-2.md` | `b8aa7fba44e8a384390ebd06329fec6b99409d5cd48c28dba030bce83acedf19` |
| `.planning/milestones/component-index/004-phase-3.md` | `fc7445dd41398c3d6e21e139669fd7d7a156aa87b6f30b652bb487fb5d11f9c0` |
| `.planning/milestones/component-index/005-phase-3-reread.md` | `f2e6b7c0c7f39760a5969ce5f5044c4715b938e010d1f8514bc3a3639bf4c9ad` |
| `.planning/milestones/component-index/006-phase-4.md` | `66f696e67adb095ff06b9bbccf0055ce6ce946de238404fd59b60331a617aa75` |
| `.devtools/project.md` | `1e485b868fde627032c65f9bf311899d4cb18d8a5a0ba91c8ffec8b9de54ff3e` |

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
