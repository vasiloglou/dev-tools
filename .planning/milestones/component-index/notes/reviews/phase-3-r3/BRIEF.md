# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 3. Do the repairs of round 2 (notes/reviews/phase-3-r2/FINDINGS.md, repaired at 27ca753) hold, and where can the claims below be shown false, by the code, a command or a search?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Every statement the repair added or changed in COMPONENTS.md is true of its module at this commit.
- C2. The handoff reading's addendum lists every definition handoff.py has that its table lacks, and says truly what each does.
- C3. The nine search cases of search-cases.md still put their component first, and 'normative document ownership' finds phase.state.

## The change under review

The work from `0b95fbb` to the working tree at `21491549a980`. Its diff is `.planning/milestones/component-index/notes/reviews/phase-3-r3/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-3-r3/diff.patch` | `773e451793f2a1405a744a14716c6b98334f8d90eb425dbd8a8fa9dea49a26cc` |
| `.devtools/components/COMPONENTS.md` | `925a71b720971e4bb0645b2a219ee20c76a48024753c4c0155f3fa305acfa251` |
| `.planning/milestones/component-index/notes/phase-3-reading/handoff.md` | `db4b38baff1254c2b551b0c12f784271644fb6c2c90852680a7d165df6c5ea91` |
| `.planning/milestones/component-index/notes/reviews/phase-3-r2/BRIEF.md` | `901ac741a94b73ee97e07e7a29f9320a21bad5175ac706818dfe5ebb48368752` |
| `.planning/milestones/component-index/notes/reviews/phase-3-r2/FINDINGS.md` | `3d8b4824d94a55cc7e75bff6ebf273baf378c4a92319d760e978b54a07072ca9` |
| `.planning/milestones/component-index/notes/reviews/phase-3-r2/brief.json` | `2b9c82835b11a19d2847d993ce664e68d94c269a2ff945122e7b3bcf3bc6c1d4` |
| `.planning/milestones/component-index/notes/reviews/phase-3-r2/diff.patch` | `7a84e2b18fbfa7412895a24db3176330ddf059064cf766bd50fa32100a1b3ef8` |
| `.planning/milestones/component-index/notes/reviews/phase-3-r2/review.md` | `5fa535009cd6026706ecab2586c0996fe84343ca08db6431b5a7efeff4c2aa8c` |
| `.planning/milestones/component-index/notes/reviews/phase-3-r2/run.json` | `ae83c6a9ae8435b827570f5b29ec996feb09ee745f237d6ea7c7f3af4748bec4` |
| `skills/dev-handoff/scripts/handoff.py` | `74de4ada6271fc728c3929a7bce68dc3f3de11a1d460c76bbaa6b534d2162285` |
| `skills/phase/process-phase/scripts/coder_pool.py` | `f657307c1e0f1f5c377aa3fcdd69e85daf7be81de91689ecc503c17e9ceb7b1d` |
| `skills/phase/process-phase/scripts/phase_tool.py` | `08dadf9fc68e96320f9c3bdaf6ae3483ed330a8d8608bf2c321232f4bf73be8e` |
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
