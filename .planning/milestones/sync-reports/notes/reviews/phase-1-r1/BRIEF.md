# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Where does the phase 1 code, its tests or its pages not do what the phase 1 spec says, or do something a project that syncs would not expect?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. P1.1: on the observed case, apply --dry-run exits 0 and names skills/milestone/review-pr with the file that names it; check exits 0 and says how many files an apply would change; check --strict exits 5.
- C2. P1.2 and P1.3: a declined unit, and a unit under a workflow folder the config takes nothing from, appear in no report of apply or check.
- C3. P1.4 and P1.5: a unit added since the receipt is reported as new until the next apply, and a receipt without shipped gets a one-time list that the next apply ends.
- C4. P1.6 and S0.1: check --receipt-only prints what check printed on main and starts no process, and a caller that passes no new option gets every line and exit it got on main, with new lines only after the summary line.
- C5. P1.7: a declined value that is not a list of relative paths, or that covers a taken unit, exits 2 and writes nothing.
- C6. The named rule reports a unit only when a delivered file names it alone in backticks or as the folder after ../, and a name a taken unit has is never reported.
- C7. Every capture changed in docs/adopt.html is output a real run of the current code prints.

## The change under review

The work from `c85728d` to the working tree at `e49b05295569`. Its diff is `.planning/milestones/sync-reports/notes/reviews/phase-1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/sync-reports/notes/reviews/phase-1-r1/diff.patch` | `0250dceb8ab9c29b2be278c1e66214f939b73c0078939af0ee0a40616f215a7e` |
| `.devtools/components/COMPONENTS.md` | `53528dfe833f8cf820e64df525ebc2236bb7dd086f51bc17cf4623eb4a2213a5` |
| `.devtools/components/modules/_root.md` | `148c4e83c705be772732ff2c181e3060b7c3a8229e82f41322586560ca2051a5` |
| `README.md` | `e33eb8757f2af0504d9de842ed20a5dae7e86d46428753272224f034e5444b69` |
| `devtools/sync.py` | `5c8894bd9e93c56f99278a3010c0eafdbc5e50e514234142d0e25dda07244c2e` |
| `docs/adopt.html` | `bd655711702f2e01e205c8da00691c30232ecf24d0c0851504ff94fdb6f1472a` |
| `examples/milestone-project.devtools.toml` | `7221089d737f9e94711e1da7eed26a1140d4e5e50d41b139e376f5351945a2e3` |
| `examples/phase-project.devtools.toml` | `71caa4a90c9d365c5a9e77dde8267fa6a74a962ca9c085bc82074b58647b8769` |
| `skills/adopt-devtools/SKILL.md` | `a3ca78aff2ec9615aa0dac40e7b6ab3c8835e2edc29aa5b20e58f7dcd201a111` |
| `tests/test_sync.py` | `fdc5fade34f64575ab2b6b64def2784d640dfa3d497d91a2f9aee0ebb0155181` |
| `.planning/milestones/sync-reports/notes/phase-1-spec.md` | `c27d0bc0aa51d879ebbc6d8fefd1d0d31c7249c1a28a90dc4734dcb34dc048a2` |
| `.planning/milestones/sync-reports/notes/sync-reports-plan.md` | `cb58b4996b218d241290fbb89a02941327b3ef2c399220b9025401248362b967` |

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
