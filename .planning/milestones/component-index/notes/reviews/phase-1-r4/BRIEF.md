# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 4. Do the repairs of round 3 (notes/reviews/phase-1-r3/FINDINGS.md, repaired at e2b2762) hold, and where can the claims below be shown false, by a note, an input, a file name or a checkout state?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. takeover reports ready only if every ignored path the note was written with, other than a key file, exists in the checkout, whatever characters the path holds, including every character str.splitlines() breaks a line at.
- C2. A bullet or ignored-rest path that is empty, absolute, or has an empty, '.' or '..' part withholds ready and is never checked as a path.
- C3. No text in the snapshot (a commit subject, a tracked or uncommitted file name) can end the snapshot before its ignored-files section or hide that section, so as to make a note with a missing ignored path read as ready.
- C4. takeover never raises on a path the file system refuses to look up, on any Python the scripts support.
- C5. write and check find the snapshot's end where takeover does, and a second write keeps the note's filled sections and leaves exactly one snapshot.
- C6. Every note main writes for a checkout with ordinary paths reads as it did at 24b2d83: the same ready, missing and unlisted results.
- C7. plugins/ is rebuilt from skills/ and nothing under plugins/ was edited by hand.

## The change under review

The work from `24b2d83` to the working tree at `d58436228c03`. Its diff is `.planning/milestones/component-index/notes/reviews/phase-1-r4/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-1-r4/diff.patch` | `5290f8f5bad0312908a67255b3ebb4a5ab93f8d214408f0dd568787ff6619965` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r3/BRIEF.md` | `d21cf1e9daaba5e8ddd727f681084f1b2c73c6ce949a10429ca862967ad72775` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r3/FINDINGS.md` | `6a560e53be153c5111fa3f2db12c09076d6ef78a4f5e616b1c727ccdf4b6a09c` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r3/brief.json` | `865bdb12cae1ff9766433068425b0eb1488e4a738892fc9a088eaf8eae66d23f` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r3/diff.patch` | `ca730330b4c9b3edc9f29c41b5c67158588ca68ce244f7f49209d4c78a42855e` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r3/review.md` | `ba874a6a20b1cefe5f6f3a59cdf44fef1844a3d4de73e0addf1a87079378258b` |
| `.planning/milestones/component-index/notes/reviews/phase-1-r3/run.json` | `3c47909c9c808ae5dcc0b9b155b2f3ff104a4e9bc42d5e681eacc30f073fe4e2` |
| `plugins/dvt-milestone/skills/dev-handoff/references/handoff.md` | `3ab0aa28718fe1a11e388c20a38b7b214f885502865583328600557e3f72aee9` |
| `plugins/dvt-milestone/skills/dev-handoff/scripts/handoff.py` | `74de4ada6271fc728c3929a7bce68dc3f3de11a1d460c76bbaa6b534d2162285` |
| `plugins/dvt-phase/skills/dev-handoff/references/handoff.md` | `3ab0aa28718fe1a11e388c20a38b7b214f885502865583328600557e3f72aee9` |
| `plugins/dvt-phase/skills/dev-handoff/scripts/handoff.py` | `74de4ada6271fc728c3929a7bce68dc3f3de11a1d460c76bbaa6b534d2162285` |
| `skills/dev-handoff/references/handoff.md` | `28024500a082ff229f4cb1a97e7f5a03bc6205692a1115aa62453b477cf04780` |
| `skills/dev-handoff/scripts/handoff.py` | `74de4ada6271fc728c3929a7bce68dc3f3de11a1d460c76bbaa6b534d2162285` |
| `tests/test_handoff.py` | `2cf051c9f5dc3a89187319f6d0c81cfbcd72a4f382a72a52ae538503bdb8613d` |
| `.planning/milestones/component-index/notes/phase-1-spec.md` | `77f589b5f47729bcb47626ba93591c111fc305866c699fad838963969f409a9f` |
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
