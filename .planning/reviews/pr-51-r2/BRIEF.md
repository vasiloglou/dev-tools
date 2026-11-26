# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this pull request do what its description says for parts 1 to 4 of issue 50 and for the five findings of review pr-51-r1, and what does it break for a project that installs or syncs the dev-tools plugins and gates on changed --strict?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Since the review round (0c3e0b3): none of the four lines does, verbs, flow and reread, deleted or left empty, answers a change, and the line then says so, (reread removed); review no longer dates an entry from an empty line.
- C2. Since the review round (0c3e0b3): a component's code counts as changed when a file it holds now, or held at the base, differs, so a deleted module, both names of a renamed one, and an edited module moved to another component each ask the component that had it.
- C3. Since the owner's ruling (c6d55ca): a component's code also counts as changed when its modules line took a file in or gave one up, whether or not the file was edited. Both components are asked. The same files named another way ask nothing.
- C4. Since c6d55ca, changed --strict also exits 1 on a change that only regroups modules: lines, moving a module from one component to another without editing it, until both entries are answered; the plain changed still exits 0.
- C5. Part 4 (c6d55ca): a component's reread: line ends with what to look for, 'new public names not in does or verbs: ...' and 'removed public names still in does or verbs: ...'. The names are the public top-level classes and functions of the listed .py files, at the base against now. A name that moved between two files of one component is in neither list. Private names and methods are left out. Eight are shown, then +N more.
- C6. A name is 'in does or verbs' when each of its words is there, read as search reads prose (lower case, plural endings dropped, stopwords left out), with underscores and capital humps as word breaks.
- C7. The lead about names is a lead and fails nothing. A subsystem's line has none, and an entry that was answered has no line.
- C8. F3 (c6d55ca): the field reader is as it was. The lines of an entry that are no field (a key such as owner2 or audit-owner, or no key), up to the next heading, are kept beside its fields, and an edit to them reads 'only other lines edited'. The skill's table of fields now says a field's key is lower-case letters and underscores.
- C9. F4 (c6d55ca): the changed row of the command table now says a subsystem's line is for a subsystem with a member whose code changed while none of the subsystem's own four lines was edited, whether or not that member's entry was answered. The site's Reread bullet names the advisory line.
- C10. F5 (c6d55ca): entry_commits reads a commit id of 40 or 64 digits, so review dates entries in a repository made with git init --object-format=sha256.
- C11. Every page that describes the changed behaviour is updated in this pull request: skills/components/SKILL.md (the changed row of the command table, the table of fields, Before a PR), the two process-phase texts, examples/components-check.yml, docs/components.html and the --strict help string.
- C12. plugins/ is what devtools/build_plugins.py generates from the product, at version 0.1.8, which is not released.
- C13. Twelve of the tests of 0c3e0b3 fail on 8475b62's script, and fifteen of the tests of c6d55ca fail on 2b22500's script; all of them pass at the head.
- C14. The records 002-pr-51-r1.md and 003-rulings.md in .planning/milestones/reread-answers/ claim no plan, spec, review or close that did not happen, every gate they cite is one a reader can rerun at the commit named, and the findings ledger of pr-51-r1 gives each finding's disposition with the commit and the regression test.

## The change under review

Pull request #51, https://github.com/vasiloglou/dev-tools/pull/51, at head `6751dbd37629ea780d1c79c371ffc3447a4ba091` (base `31249da46556d06e611f8590d1d0cd05f6f29660`). Its diff is `.planning/reviews/pr-51-r2/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/reviews/pr-51-r2/diff.patch` | `75637cb1573fd846e49248025981dd3f09e8a1f4df383bbe0c8f87363eecae1d` |
| `.planning/milestones/reread-answers/notes/issue-50.md` | `b9e52bbfa75d714c492d8d082eb8dae109d92a4cd393c56e33690b8b7c944bea` |
| `.planning/reviews/pr-51-r1/review.md` | `ed61c285253c1d56e6b9cc83ce96e14353be14f4cd603968d65a4b91f49fe390` |
| `.planning/reviews/pr-51-r1/FINDINGS.md` | `1fe8e39151fd27601e90f77eae01e70fc9358698999753af59aee917688a4a13` |

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
