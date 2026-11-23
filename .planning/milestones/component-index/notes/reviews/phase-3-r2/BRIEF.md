# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 2. Does each entry and subsystem of .devtools/components/COMPONENTS.md say truly what its modules do at this commit, and where can the claims below be shown false, by the code, a command or a search? Round 1 is notes/reviews/phase-3-r1; the reread's method is notes/phase-3-reading/README.md.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Every statement in each entry's does and notes is true of its modules at this commit, cited or not.
- C2. Each entry's does names every command of its module's command line.
- C3. Each subsystem's flow and notes state every run-time call one shipped script makes to another, and no call that does not happen.
- C4. A capability of a module that someone new would search for is named in its entry's does or verbs.
- C5. No entry is checked: partial, and each reading file's definitions table has one row for every function, method and class of its module.
- C6. REVIEW.md's suggestions 4 to 6 and its settled 'Not confirmed' points are true at the lines they cite.
- C7. The round 1 repairs (phase-3-r1/FINDINGS.md) still hold.

## The change under review

The work from `caffae7` to the working tree at `0b95fbb88536`. Its diff is `.planning/milestones/component-index/notes/reviews/phase-3-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-3-r2/diff.patch` | `7a84e2b18fbfa7412895a24db3176330ddf059064cf766bd50fa32100a1b3ef8` |
| `.devtools/components/COMPONENTS.md` | `0726280a469314440090fa2682c2e6b81da031ef82f0846ec80f389d5124e0cf` |
| `.devtools/components/REVIEW.md` | `821c841181d8bd82b95cfc4019e461381d03c5589a12cf53f012f09cf6d390e7` |
| `.devtools/components/modules/skills.md` | `6f20216aecde910a8c1cd16b5f406c11588fc3a75b71ee72a6264ec4fdae20db` |
| `.planning/milestones/component-index/notes/phase-3-reading/README.md` | `043adaf210b1b37c4add163371ccba7ae73810cd9d8df299ae66663046b44e51` |
| `.planning/milestones/component-index/notes/phase-3-reading/build_plugins.md` | `65fa2273b832525094a4e1d848563eff45b713b1af882bfee0035b7c96a62e80` |
| `.planning/milestones/component-index/notes/phase-3-reading/coder_pool.md` | `1e4099538f1dd3f0f51a69cb2ce83914abc4bc7f84f75675292373232ebd2cf2` |
| `.planning/milestones/component-index/notes/phase-3-reading/components_index.md` | `3da959f140348e732ae0c24a3bce0e9334a18201d15d232ff734d31d2ed287d9` |
| `.planning/milestones/component-index/notes/phase-3-reading/from_gsd.md` | `fd0772a29a8b8ad75d85dc9565c50cdda5d54a0859fd43a281810651a8a039ab` |
| `.planning/milestones/component-index/notes/phase-3-reading/handoff.md` | `43d14b773c9617e08475f82e2ec77aaf8d4b136fd291f4b6ec963cff0f9315d6` |
| `.planning/milestones/component-index/notes/phase-3-reading/phase_tool.md` | `23c0708919370fb2eadaff044348727e71dedf6759fdbdee00fcc3fa757bffe3` |
| `.planning/milestones/component-index/notes/phase-3-reading/release_plugins.md` | `ee8106bb557676a40de5d4b77f73bb651995c4c620193fe148df2d3c6e89e985` |
| `.planning/milestones/component-index/notes/phase-3-reading/review_tool.md` | `0cf73612adb5145c7bf6cc2365de9f943f3c263e70015ab46a2aa72c730c1cf4` |
| `.planning/milestones/component-index/notes/phase-3-reading/rules_check.md` | `41d16ca6c72595492db94b9e3ae29e09dcc459e389104c1230ef56a4848a09a0` |
| `.planning/milestones/component-index/notes/phase-3-reading/sync.md` | `e518515c6ead1ff021947d1a278294b09f5fb66721ad2a7ddd3a55a205c487d4` |
| `devtools/build_plugins.py` | `a98b0d93ef4df6286c4c72d74986464d2f80c4b9c7d4b80eb09fc3e0b04ca674` |
| `devtools/release_plugins.py` | `eedc3a907803df084a8941aa9bf0a511c3679156cf904ebfa8cc693037e1be59` |
| `devtools/sync.py` | `1637af6f38ec3472e42da7ea3207445ba7b0fd25a0e3e73bba46b140e8da06f6` |
| `devtools/from_gsd.py` | `7865f45e952703de6d59793e016714a417e35056a6ba4ef8f14f2ea15dcf209a` |
| `skills/components/scripts/components_index.py` | `3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14` |
| `skills/components/scripts/rules_check.py` | `69dd596107826bdf3fc551db810097ae8e292e61c257977cef6b5cde8dbb772b` |
| `skills/dev-handoff/scripts/handoff.py` | `74de4ada6271fc728c3929a7bce68dc3f3de11a1d460c76bbaa6b534d2162285` |
| `skills/milestone/process-phase/scripts/review_tool.py` | `12dc9800f55dc9f409dadf8466b39591c6b58f2210195478cb4ce39e985a38ff` |
| `skills/phase/process-phase/scripts/phase_tool.py` | `08dadf9fc68e96320f9c3bdaf6ae3483ed330a8d8608bf2c321232f4bf73be8e` |
| `skills/phase/process-phase/scripts/coder_pool.py` | `f657307c1e0f1f5c377aa3fcdd69e85daf7be81de91689ecc503c17e9ceb7b1d` |
| `.planning/milestones/component-index/notes/phase-3-spec.md` | `cb2825bc1b2da14c15859b9834766d0b8d22105c33742c9313556d78b5cf6e7a` |
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
