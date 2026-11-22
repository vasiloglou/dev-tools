# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 3. Do the repairs of round 2 (notes/reviews/phase-1-r2/FINDINGS.md, repaired at 4903752) hold, and where can the claims below be shown false, by a note, an input or a checkout state? Rounds 1 and 2 are notes/reviews/phase-1-r1 and phase-1-r2.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. A note written with 25 or fewer ignored paths is byte-for-byte the note main writes.
- C2. takeover reports ready only if every ignored path the note was written with, other than a key file, exists in the checkout, wherever it sits in the list and whatever characters it holds.
- C3. A note from 0.1.3 or older whose list was cut, and any ignored-rest line that is damaged, short, long, nested or not a list of path and kind items, gives ready false and never raises.
- C4. A path holding a newline or other control character cannot make a note read as ready while that path is missing.
- C5. A commit subject, file name or other text shaped like the ignored-files heading does not move where takeover reads the ignored section.
- C6. A missing key file, listed or after the 25th, is reported in missing_keys and does not block.
- C7. plugins/ is rebuilt from skills/ at 0.1.4.

## The change under review

The work from `1a5f14c` to the working tree at `24b2d83f215b`. Its diff is `.planning/milestones/component-index/notes/reviews/phase-1-r3/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-1-r3/diff.patch` | `ca730330b4c9b3edc9f29c41b5c67158588ca68ce244f7f49209d4c78a42855e` |
| `.planning/milestones/component-index/002-phase-1.md` | `c522ddb42eccb62b94f19480211ea46a821e1fd3190e76858b5b112f47bfcf03` |
| `.planning/milestones/component-index/README.md` | `9cbacfb141622964e7da6a0ea7d8c210043957d1ed31f20f33f7979ca1d42b59` |
| `.planning/milestones/component-index/notes/phase-1-spec.md` | `77f589b5f47729bcb47626ba93591c111fc305866c699fad838963969f409a9f` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r1/BRIEF.md` | `c8f50889fbda5c75a7ba7f41479bca4b4c38a5b34686c796bf45ee554364c490` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r1/FINDINGS.md` | `c8faf63ce3990e8513863547309370a116da852a8b6462d8c03d50403079aa5a` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r1/brief.json` | `029a22ca25be177587a4461cba525adc41730c28bb83aeeeaaa5f24b05405969` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r1/diff.patch` | `f732528b2037cb53a3ec99be06595dbafd567ddadb6332db83c228f37d32fa76` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r1/review.md` | `c6c5f22687c7b3f76fb95d8bc8cfa6bf37f6ca2878b98e5e36a9c1c6991150f6` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r1/run.json` | `c9ddc86587382b2622be48174dc17c7086dc53a73f0d17e79bf6dbd168620938` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r2/BRIEF.md` | `d0f50d879392cbf653f072c064ae6133a377ef259cb82e4093120c948ebabc02` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r2/FINDINGS.md` | `dec990ecb3676568f6df6a81514e91f1d84f72a170f6d11c73b52591ed175fba` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r2/brief.json` | `5fc31cc533c599a96a7bfabbf32d539f96edea7fe55ad5b106e034561e48321b` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r2/diff.patch` | `c387a3db863a527a4b5e2cc68922d6912788feec76ff91d32e783d27c3ae2736` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r2/review.md` | `cc5044b05a9c187b3dbcd12af8955a5fc55408ecff436badcb0772f77d03bdc5` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r2/run.json` | `b61f0f276f3f40c8ba1924a4571e9365d2d27f995dae396a5410b013cb299441` |
| `devtools/PLUGIN_VERSION` | `8a3dad16d348c163566a456fcf650d85d7aeeda5e53d01ee1fa8dc15212915a7` |
| `docs/handoff.html` | `33880b4fac821bf766c802d81ef25158470d36747b192f02fa410981db24b6a7` |
| `plugins/dvt-milestone/.claude-plugin/plugin.json` | `492ae4c62c4fe4706eeec04e118af8c2d4ea264235122aa15443c8e4c7294599` |
| `plugins/dvt-milestone/skills/dev-handoff/references/handoff.md` | `2cc54f1e8f3f1d626baeeb1c4818878cac82a079f3897f560b3fa6ce68abcb9b` |
| `plugins/dvt-milestone/skills/dev-handoff/scripts/handoff.py` | `dbab0519e8689154579ec06bc0894125d08b5244ea738d547b66947537d16a6a` |
| `plugins/dvt-phase/.claude-plugin/plugin.json` | `f3a7e2a54161de4145830a96c41ec780a6bce3fa8cd8f33c1a5f6351a62e03b1` |
| `plugins/dvt-phase/skills/dev-handoff/references/handoff.md` | `2cc54f1e8f3f1d626baeeb1c4818878cac82a079f3897f560b3fa6ce68abcb9b` |
| `plugins/dvt-phase/skills/dev-handoff/scripts/handoff.py` | `dbab0519e8689154579ec06bc0894125d08b5244ea738d547b66947537d16a6a` |
| `skills/dev-handoff/references/handoff.md` | `81ce6d44aa595922f59d8b6d4f5151978d6538b2cd0f64ba5f06bd65c481a4b3` |
| `skills/dev-handoff/scripts/handoff.py` | `dbab0519e8689154579ec06bc0894125d08b5244ea738d547b66947537d16a6a` |
| `tests/test_handoff.py` | `b1c98487f83ee8b84f6e6757329172a538786e359bb3e3233655c863cc138b67` |
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
