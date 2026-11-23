# Review brief: the milestone close

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

The component-index milestone is at its close. 007-close.md is the draft close record; its Close ruling and Review sections are marked PENDING and are written after you answer. Is the milestone ready to close as that record says, and where can the claims below be shown false, by the files or a command?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Each completion predicate C1 to C5 of notes/component-index-plan.md holds at this commit, as 007-close.md measures it.
- C2. The open-questions sweep of 007-close.md misses no question that records 001 to 006 or plan section 10 raise, and each disposition is true: a row marked closed is closed by what it cites, and a row marked carried names who takes it.
- C3. Every refuted premise in records 001 to 006 that names a plan repair is repaired in the plan at a site marked (c1), the repair says what the cited record shows, and the earlier wording is kept beside it.
- C4. skills/dev-handoff/scripts/handoff.py at this commit: takeover never reports ready while an ignored path the note was written with, other than a key file, is missing from the checkout. Its last repairs (commit 22d6258: _one_line, checking each path before redaction, a rest line without its cut line, doctor not raising on an over-long name) were never reviewed.
- C5. Every statement in the sections Since record 006, Residuals the close accepts and Boundary of 007-close.md is true of the repository at this commit.

## The change under review

The files below, as they stand at `811b4a3ef993` with uncommitted changes.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/007-close.md` | `2207e2d76851c9c97cd9c5980870c821c5d1600268a8d1889041931630220103` |
| `.planning/milestones/component-index/notes/component-index-plan.md` | `9684c846e59bf116b706aa3c64dc5d4710486572a20f73cf581d11a188132f31` |
| `.planning/milestones/component-index/001-plan.md` | `5efa7b890a4036186851c8a7e32a51dd3a4e17f816eddc06567dedf20b7c0b74` |
| `.planning/milestones/component-index/002-phase-1.md` | `c522ddb42eccb62b94f19480211ea46a821e1fd3190e76858b5b112f47bfcf03` |
| `.planning/milestones/component-index/003-phase-2.md` | `b8aa7fba44e8a384390ebd06329fec6b99409d5cd48c28dba030bce83acedf19` |
| `.planning/milestones/component-index/004-phase-3.md` | `fc7445dd41398c3d6e21e139669fd7d7a156aa87b6f30b652bb487fb5d11f9c0` |
| `.planning/milestones/component-index/005-phase-3-reread.md` | `f2e6b7c0c7f39760a5969ce5f5044c4715b938e010d1f8514bc3a3639bf4c9ad` |
| `.planning/milestones/component-index/006-phase-4.md` | `66f696e67adb095ff06b9bbccf0055ce6ce946de238404fd59b60331a617aa75` |
| `.planning/milestones/component-index/README.md` | `b5930774a74c8054339c7e33ae299639a9576b7a27b338ff1178df7855e2d7bf` |
| `.planning/milestones/component-index/notes/phase-4-spec.md` | `a629877e7cb50f16ee231c243fa13932adb309ca832fcbb04310ba14515721f7` |
| `.devtools/project.md` | `1e485b868fde627032c65f9bf311899d4cb18d8a5a0ba91c8ffec8b9de54ff3e` |
| `.devtools/components/COMPONENTS.md` | `33b6da675aa123e43bb1ce610c583ddcc6c326e22bbade8aad8eb650a7e8a099` |
| `.devtools/components/search-cases.md` | `876fab2dc57cca4dca143346783934556b2caadaf0b3d4415aa1caab616a5453` |
| `.devtools/components/REVIEW.md` | `821c841181d8bd82b95cfc4019e461381d03c5589a12cf53f012f09cf6d390e7` |
| `skills/dev-handoff/scripts/handoff.py` | `e891bdb31f0a48089a9db0a117ed5aad12486d34d536dc3fa35f049dc3e16a35` |
| `skills/dev-handoff/references/handoff.md` | `4ab09c9621c60c1f7afdef00aa1eba4d4626d6490cf39fa8bc3222ec55a85629` |
| `tests/test_handoff.py` | `e8096c363a107043e284b4ed041870230c0ff3e340a2e4f2a67eb4121a98c5ab` |
| `tests/test_own_index.py` | `20eb2fa283b4ece497665e188eceecea50581193c7119b729fcc0b7b69e9f405` |

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
