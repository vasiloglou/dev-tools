# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff do what the phase 3 spec says for issues 33 and 43, does a working settings file see the lines and exits it saw before, and can each new test fail when the behaviour it names is wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. P3.1. In a new project, rules_check.py init then test exits 0 and prints 0 wrong with the copy of either plugin; with dvt-milestone's it prints one skip: line naming the rule about plans.
- C2. P3.2. A rule that names a fact type nobody has and is not about plans is still wrong, with or without the phase tool.
- C3. P3.3. With the phase tool present, rules_check.py test prints and exits exactly as before this diff, and gnd synth is given the same rules.
- C4. P3.4. A settings file that rules_check.py, components_index.py, review_tool.py or handoff.py cannot use, for any command, exits 2 with the reason on standard error and no traceback; a working settings file changes nothing.
- C5. P3.4b. phase_tool.py with such a file prints exactly one envelope with ok false and error code SETTINGS, exit 2, for every command including status, and the module can still be loaded by a caller that reads its tables.
- C6. P3.5. Each changed docstring sentence says what the code does.
- C7. P3.6. rules_check.py, review_tool.py and handoff.py and their copies under plugins/ have no finding under ruff 0.16.2 with the configuration pull request 34 names.
- C8. coder_pool.py is left at exit 1 for a settings file, and the spec's reason for that (D1) is true of its code and docstring.

## The change under review

The work from `a247f4d` to the working tree at `6c2ada571c8a`. Its diff is `.planning/milestones/issue-sweep/notes/reviews/phase-3-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/issue-sweep/notes/reviews/phase-3-r1/diff.patch` | `a18f64b4cc2c0a01d567b7b6ab1fd91bc8a927ee2bc808d3c30f26e2908bb658` |
| `.devtools/components/COMPONENTS.md` | `7a1192f316ac3663cd1238046cc2de3b244ab5a96ff9a0935427f76a601ba805` |
| `.devtools/components/modules/_root.md` | `fbebb4ca441f4e8548a615fd9426fdcae3ecf2ff0366ffb0a52ca899ee889664` |
| `.devtools/components/modules/skills.md` | `5388364738e740bf67bc23c5613e7e8233cd024d462ff5c76958ee97e4c95867` |
| `.planning/milestones/issue-sweep/notes/phase-3-spec.md` | `8b62d2e510f0ce2b0b2e4c585030229f8d71686978a033fb136b5979a7f015b3` |
| `devtools/from_gsd.py` | `fcb719f18739b87ab41b2b88478bf75db98c4e57347073849896facdb7ebc2cb` |
| `docs/rules.html` | `a9c7d68d9747f5543b7959c177384f1f027dcc54803f1a20a7905a34767a9069` |
| `plugins/dvt-milestone/skills/components/SKILL.md` | `5e9816ec30b83458eb145d4efceace78ab122e1309b9d9321b0cefd69a6a4c6c` |
| `plugins/dvt-milestone/skills/components/references/rules.md` | `6821b54cb1c189cd3ae95c0678f4531dee186fb06b47fe782234a9490fc82efb` |
| `plugins/dvt-milestone/skills/components/scripts/components_index.py` | `5419276cad7033df23a600b10e236edd488e3c4d55b80309622584c4a24f51e7` |
| `plugins/dvt-milestone/skills/components/scripts/rules_check.py` | `141c8d6dffb3e12910aa6a698821db11c6c78f1e203f2d3c2bd878a6552c1396` |
| `plugins/dvt-milestone/skills/dev-handoff/scripts/handoff.py` | `7779a0c7ab109a1856b643f85b4d28840c0732957951f356b542ec731787a9a2` |
| `plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py` | `5fade2fcb3ce3b7ba4089c8e0ef038829c6c7fca078e5a061170fee6b3cbe4c5` |
| `plugins/dvt-phase/skills/components/SKILL.md` | `801608a3fedb56830e6213f3b6cab70bbd7a5346d5b50d847c3806bff8b51fa8` |
| `plugins/dvt-phase/skills/components/references/rules.md` | `6821b54cb1c189cd3ae95c0678f4531dee186fb06b47fe782234a9490fc82efb` |
| `plugins/dvt-phase/skills/components/scripts/components_index.py` | `5419276cad7033df23a600b10e236edd488e3c4d55b80309622584c4a24f51e7` |
| `plugins/dvt-phase/skills/components/scripts/rules_check.py` | `141c8d6dffb3e12910aa6a698821db11c6c78f1e203f2d3c2bd878a6552c1396` |
| `plugins/dvt-phase/skills/dev-handoff/scripts/handoff.py` | `7779a0c7ab109a1856b643f85b4d28840c0732957951f356b542ec731787a9a2` |
| `plugins/dvt-phase/skills/process-phase/scripts/coder_pool.py` | `3f23de0f51ca2d96df305c550c50ff839ab93b48fb1a46611bf6183abd99f585` |
| `plugins/dvt-phase/skills/process-phase/scripts/phase_tool.py` | `7714ffc3c3bddc7e95b60204f55ea354f745d415efb8523610b19bfb1efae10a` |
| `skills/components/SKILL.md` | `a973c10a32f2a83ff88096a1d2bdd5882db39bf17a034d58784ba044fe25dbcc` |
| `skills/components/references/rules.md` | `ef9f5fbc1a5334f27ac06c9c65cb151b70e2cf9c2b9c9e404c691777deaade3d` |
| `skills/components/scripts/components_index.py` | `5419276cad7033df23a600b10e236edd488e3c4d55b80309622584c4a24f51e7` |
| `skills/components/scripts/rules_check.py` | `141c8d6dffb3e12910aa6a698821db11c6c78f1e203f2d3c2bd878a6552c1396` |
| `skills/dev-handoff/scripts/handoff.py` | `7779a0c7ab109a1856b643f85b4d28840c0732957951f356b542ec731787a9a2` |
| `skills/milestone/process-phase/scripts/review_tool.py` | `5fade2fcb3ce3b7ba4089c8e0ef038829c6c7fca078e5a061170fee6b3cbe4c5` |
| `skills/phase/process-phase/scripts/coder_pool.py` | `3f23de0f51ca2d96df305c550c50ff839ab93b48fb1a46611bf6183abd99f585` |
| `skills/phase/process-phase/scripts/phase_tool.py` | `7714ffc3c3bddc7e95b60204f55ea354f745d415efb8523610b19bfb1efae10a` |
| `tests/test_handoff.py` | `2dab9b61a1d8c8447fcf9453ef06a90551e669fb0554b2d5947e71d4b199ff84` |
| `tests/test_plugins.py` | `e2e0ba102658956ca00137be472d44d07f130801e1a68a4760604c3d2740a936` |
| `tests/test_review_tool.py` | `c061ad86eee63048d58e8e412b6b5402451411e2b7b1c06f46a81d8c8fd2475c` |
| `tests/test_tools.py` | `1f17a02ab780c0f227abe1fbe097a527d8422f155afa4482f8db307c4ce115f5` |
| `.planning/milestones/issue-sweep/notes/issue-sweep-plan.md` | `309c6e556ac85f24e71f3c63f79356421392e570cdf143472b02f1acd90481a4` |
| `.planning/milestones/issue-sweep/notes/issues-2026-11-23.md` | `7584fec3d861c1113450fa58207fbc671f1ad9e77f2db673d6b1df1f575dc84c` |

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
