# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this pull request do what its description says for each of the eight issues it closes, and what does it break for a project that installs or syncs the dev-tools plugins?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. 31: the test of generated cases skips, rather than fails, when GND refuses synth --guarded-cases for want of its synth extra, and only then.
- C2. 42: tests/test_phase_selection.py runs the pytest plugin as a project's conftest.py and checks which tests are kept.
- C3. 41: from_gsd.py reads sync.py's list of other planning tools.
- C4. 46: with allow_baseline false, --check --strict fails while unassigned-baseline.txt exists, and stats --write-baseline refuses to write one; the default is true.
- C5. 45: changed and facts --base compare with the upstream of a local branch that is strictly behind it, and say so in a note: line; nothing fetches. An entry may carry a reread: line, which dates it as an edit of does or verbs would.
- C6. 44: with count_extra_dirs, review's groups read from the modules themselves cover the extra folders.
- C7. 33: where the phase tool is not installed, rules_check.py test skips a rule about plans with one skip: line; a dvt-milestone install prints 0 wrong on its own starter rules.
- C8. 43: a settings file that rules_check.py, components_index.py, review_tool.py or handoff.py cannot use (an unknown key, a value of the wrong type, text that is not a JSON object) exits 2 with the reason; phase_tool.py reports it in one JSON envelope with exit 2, status too; coder_pool.py keeps its documented exit 1.
- C9. With default settings, every line and exit is as before, except: a local base behind its upstream is now compared through the upstream (with a note: line); a tie in commit time within one second is settled by history; and a bad settings file exits 2 instead of 1.
- C10. plugins/ is what devtools/build_plugins.py generates from the product, at version 0.1.7.

## The change under review

Pull request #48, https://github.com/vasiloglou/dev-tools/pull/48, at head `f77923ab67cea701e8ed4d649a48805498e1c36c` (base `cecebc6f5612531b539ced10c47b3a0d05cc3636`). Its diff is `.planning/reviews/pr-48-r1/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/reviews/pr-48-r1/diff.patch` | `b7dd93a451a6e02c536574ba3cf225297c8bbc4bda40bede54b0d9f050d266b2` |
| `.planning/milestones/issue-sweep/notes/issues-2026-11-23.md` | `7584fec3d861c1113450fa58207fbc671f1ad9e77f2db673d6b1df1f575dc84c` |
| `.planning/milestones/issue-sweep/notes/issue-sweep-plan.md` | `21da842fc08caa6b9e3294a8c61c21616ae2ac7b440913e3f01953feeed9aadc` |
| `.planning/milestones/issue-sweep/006-close.md` | `f56b78052d40e5a2ea5db5a50024497faa9ca1c3d08c67a638b8f13ad4897a51` |

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
