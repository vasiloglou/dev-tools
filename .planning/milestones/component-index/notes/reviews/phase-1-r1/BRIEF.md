# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff do what notes/phase-1-spec.md requires of it, and where can its claims below be shown false, by an input, a note or a checkout state?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. A note written with 25 or fewer ignored paths is byte-for-byte the note main writes.
- C2. takeover reports ready only if every ignored path the note was written with, other than a key file, exists in the checkout, wherever it sits in the list and whatever characters it holds.
- C3. A note from 0.1.3 or older whose list was cut, and any ignored-rest line that is damaged, short, long or not a list of path and kind items, gives ready false.
- C4. A missing key file, listed or after the 25th, is reported in missing_keys and does not block.
- C5. The JSON report always carries unlisted_ignored, and the text report prints its line only when it is above 0.
- C6. Each of the tests T1 to T11 fails without the change to handoff.py, except T5, which pins unchanged behaviour.
- C7. plugins/ is rebuilt from skills/ at 0.1.4 and nothing under plugins/ was edited by hand.

## The change under review

The work from `1a5f14c` to the working tree at `1a5f14c534df` with uncommitted changes. Its diff is `.planning/milestones/component-index/notes/reviews/phase-1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-1-r1/diff.patch` | `f732528b2037cb53a3ec99be06595dbafd567ddadb6332db83c228f37d32fa76` |
| `devtools/PLUGIN_VERSION` | `8a3dad16d348c163566a456fcf650d85d7aeeda5e53d01ee1fa8dc15212915a7` |
| `docs/handoff.html` | `33880b4fac821bf766c802d81ef25158470d36747b192f02fa410981db24b6a7` |
| `plugins/dvt-milestone/.claude-plugin/plugin.json` | `492ae4c62c4fe4706eeec04e118af8c2d4ea264235122aa15443c8e4c7294599` |
| `plugins/dvt-milestone/skills/dev-handoff/references/handoff.md` | `2cc54f1e8f3f1d626baeeb1c4818878cac82a079f3897f560b3fa6ce68abcb9b` |
| `plugins/dvt-milestone/skills/dev-handoff/scripts/handoff.py` | `d0d3ac3fa6d25d0d2b7bfcdc434a11bac5b259a837e6d486b914a524851b499b` |
| `plugins/dvt-phase/.claude-plugin/plugin.json` | `f3a7e2a54161de4145830a96c41ec780a6bce3fa8cd8f33c1a5f6351a62e03b1` |
| `plugins/dvt-phase/skills/dev-handoff/references/handoff.md` | `2cc54f1e8f3f1d626baeeb1c4818878cac82a079f3897f560b3fa6ce68abcb9b` |
| `plugins/dvt-phase/skills/dev-handoff/scripts/handoff.py` | `d0d3ac3fa6d25d0d2b7bfcdc434a11bac5b259a837e6d486b914a524851b499b` |
| `skills/dev-handoff/references/handoff.md` | `81ce6d44aa595922f59d8b6d4f5151978d6538b2cd0f64ba5f06bd65c481a4b3` |
| `skills/dev-handoff/scripts/handoff.py` | `d0d3ac3fa6d25d0d2b7bfcdc434a11bac5b259a837e6d486b914a524851b499b` |
| `tests/test_handoff.py` | `f1d5759606a7805fff389272e2f44896212e4eb94342c3944272f4d4d009bd11` |
| `.planning/milestones/component-index/notes/phase-1-spec.md` | `6b292fbfd2b3fc758faa5b49bbacd36e16200e3244343d275daf9ee9055f433b` |
| `.planning/milestones/component-index/notes/component-index-plan.md` | `42ac8f116b426ad9589c6f9224b99a188d34ae03e75f2a1cceac6d84bf0b460c` |
| `.devtools/project.md` | `e2f5561d5449bd9136880b6fa1bf696322bc70bdd98d583bdaa2a15a2ce25a7a` |

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
