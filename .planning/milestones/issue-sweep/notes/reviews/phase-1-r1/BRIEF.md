# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff do what the phase 1 spec says for issues 31, 42 and 41, and can each new test fail when the behaviour it names is wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. P1.1. With a stand-in gnd that lists --guarded-cases and exits 5 naming the synth extra, rules_check.py test exits 0 with its note line, and the guard skips.
- C2. P1.2. The guard does not skip for any other failure of gnd synth, or for anything else rules_check.py test can print.
- C3. P1.3. Every branch of the plugin in the spec's table of section 6.2 (B1 to B18) has a case in tests/test_phase_selection.py or in the existing test of tests/test_tools.py that fails when that branch is wrong.
- C4. P1.4. from_gsd.py holds no list of other planning tools of its own; a change to sync.OTHER_PLANS changes what both scripts report; and from_gsd.py survey and convert print what they printed before the change for every project.
- C5. P1.5. After this diff, components_index.py review prints 0 for components with no tests listed and for the same public name in two or three components.
- C6. P1.6. No file under plugins/ changes, and nothing a project runs behaves differently.
- C7. The implementation findings I1 to I6 at the end of the spec describe what the diff does and what was run.

## The change under review

The work from `dd0e7a1` to the working tree at `2921a3bbf35d`. Its diff is `.planning/milestones/issue-sweep/notes/reviews/phase-1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/issue-sweep/notes/reviews/phase-1-r1/diff.patch` | `e474234961d434bfc2e565b97dbc49db152f42fe056d5e6f56ea0b714c64f3c1` |
| `.devtools/components/COMPONENTS.md` | `7f3378c223ac8d40576a8db5c9827ca2dd9df8bca4bcfbed07578664128776fe` |
| `.devtools/components/modules/_root.md` | `d603e2622c30e848ae895c51b06d094e12c5ecdbd4f765c3a3bbb064973700ac` |
| `.planning/milestones/issue-sweep/notes/phase-1-spec.md` | `319fe086febaf88f483592e1e0560475b31fc6dfc4470b5c1a8151a8a8b0b913` |
| `devtools/from_gsd.py` | `67983517b29c9c62a687772c616cd39d40c003259b11d36e05df8a15fee273a8` |
| `tests/test_from_gsd.py` | `9b3c4a12fca5be70278e70a07e424abc533841bb17b174c52fd99b993af2d4cf` |
| `tests/test_phase_selection.py` | `37e1b6a6e6a203228122c91a305a8a1a4699cdf3f2c7ba32a786b6ec89ea7071` |
| `tests/test_tools.py` | `4c5ab1785091022f9a754595921b9bfef8099d2e9b495262823c0ddb06a4f99b` |
| `.planning/milestones/issue-sweep/notes/issue-sweep-plan.md` | `309c6e556ac85f24e71f3c63f79356421392e570cdf143472b02f1acd90481a4` |
| `.planning/milestones/issue-sweep/notes/issues-2026-11-23.md` | `7584fec3d861c1113450fa58207fbc671f1ad9e77f2db673d6b1df1f575dc84c` |
| `skills/phase/pytest/phase_selection.py` | `0d8f6ebf67e585ed573975d4e6fe31760592fa64f357091e589504bcc8dc9227` |
| `devtools/sync.py` | `c3632fc092eb44208e20e04a3124e2a109c3a6031b6c6a0b58b3fc85160d27fd` |
| `skills/components/scripts/rules_check.py` | `7e2e49cb065942aa7868a7f615c3b06bef8a603bb82f6edcd5ec60d76b9779ec` |

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
