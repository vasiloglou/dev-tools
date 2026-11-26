# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this pull request do what its description says for parts 1, 2 and 3 of issue 50, and what does it break for a project that installs or syncs the dev-tools plugins and gates on changed --strict?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The process-phase skill text (skills/milestone/process-phase/SKILL.md) and skills/phase/process-phase/references/close.md now say, for each reread: line, to edit does or verbs, or to add or update the entry's reread: line, and to name the entries in the record too; no shipped text still sends the answer only to the record or the commit body.
- C2. changed and review read one rule: both now read one set, DATING, in components_index.py.
- C3. An entry whose code changed with only notes, tests, modules (or any other field) edited now gets its reread: line, and the line names what was edited; with nothing edited it still reads (entry not edited), so the capture on the site is unchanged.
- C4. An entry with does, verbs or flow edited, or a reread: line added or updated, gets none. A reread: line that was already there at the base, unchanged, does not answer a new change.
- C5. An entry absent at the base is still 'written in this change'.
- C6. A subsystem whose member changed follows the same rule for whether its line is printed: an edit to its components or notes alone does not answer it.
- C7. From plugin 0.1.8, changed --strict exits 1 while a component's reread: line is left. A subsystem's reread: line is advice: it is printed and never fails, with or without --strict. The plain changed is unchanged in what it exits with: it prints the lines and exits 0.
- C8. The note: line appears only when a line that fails is left, and the summary says how many of the lines are subsystems; with none it reads as it did before.
- C9. Every page that describes the changed behaviour is updated in this pull request (skills/components/SKILL.md, the two process-phase texts, examples/components-check.yml, docs/components.html, the --strict help string), and skills/components/references/review.md needed no change.
- C10. plugins/ is what devtools/build_plugins.py generates from the product, at version 0.1.8.
- C11. Ten of the first commit's tests fail on main (31249da) for the reasons the issue gives. Five of the second commit's fail on the first commit's script.
- C12. The record .planning/milestones/reread-answers/001-issue-50.md was written after the code and says so; it claims no plan, plan review, spec gate, review round or close that did not happen, and every gate it cites is one a reader can rerun at the commit it names.

## The change under review

Pull request #51, https://github.com/vasiloglou/dev-tools/pull/51, at head `8475b62dcc3c90b323a5855e7348e6f2d01e7ee5` (base `31249da46556d06e611f8590d1d0cd05f6f29660`). Its diff is `.planning/reviews/pr-51-r1/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/reviews/pr-51-r1/diff.patch` | `476fecf8e934b1c1d8b9227195ef2c0463b8ad071f7d91c5530fb8ba2b8b864f` |
| `.planning/milestones/reread-answers/notes/issue-50.md` | `b9e52bbfa75d714c492d8d082eb8dae109d92a4cd393c56e33690b8b7c944bea` |

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
