# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this index do what notes/phase-3-spec.md requires of it, and where does an entry say something the code does not do, or leave out something a searcher would need? Where can the claims below be shown false?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Each entry's does, verbs, modules and tests are true of the code it names: no entry claims a command, option or behaviour the module does not have.
- C2. The three subsystems name every place where one of the 12 scripts runs or loads another, and their notes state each such run-time load truly.
- C3. Every entry not marked checked: partial was read in full.
- C4. REVIEW.md's suggestions and its 'Not confirmed' list are true of the code at f25d3a5.
- C5. Each query in search-cases.md is a fair newcomer's query, not one tuned to the entry's wording, and its expected component is the right one.
- C6. The settings file, run through plugins/dvt-milestone/skills/components/scripts/components_index.py from the repository root, counts exactly the 12 shipped modules and nothing under plugins/, tests/ or .claude/.

## The change under review

The work from `f25d3a5` to the working tree at `2e48abfc3e4b`. Its diff is `.planning/milestones/component-index/notes/reviews/phase-3-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-3-r1/diff.patch` | `719d569fb1f6d13e25518adb41da362e42714f296a89615c253b3161c6498762` |
| `.devtools/components/COMPONENTS.md` | `dd45618a5709776abdb969dd52ad06ea7e1d348e6693982c39727a0009b2d97d` |
| `.devtools/components/REVIEW.md` | `507255a5ecfb25380cd6a6c2626baf285c47ebfffa7b04b73e71184882593c09` |
| `.devtools/components/graph.md` | `3d3df2e0ad8132479eee1a84bff3f96280856e5fd9a61f8477914c64591a49b5` |
| `.devtools/components/modules/_root.md` | `a37b3a8d191d88feb586df3d33450981e6db68e2b6970cba9b5d5548aab1b9db` |
| `.devtools/components/modules/skills.md` | `da944750555d7f475ad63363950f00d9645eb75cdc92ec09f3c8f195b1a48f0f` |
| `.devtools/components/search-cases.md` | `876fab2dc57cca4dca143346783934556b2caadaf0b3d4415aa1caab616a5453` |
| `.devtools/components_index.settings.json` | `56717af02b363be6354f9fc760ea2a8e56151821c33bfa58342296d1adad6893` |
| `.planning/milestones/component-index/notes/phase-3-spec.md` | `bd9470e3f60b6792333b501cd009e5af265bfecf2d93ae5adc86c7f18d3a5cf9` |
| `.planning/milestones/component-index/notes/component-index-plan.md` | `3cc5eb4924e69fb5584fd2613a0246718a27b5b3dd9e58f34afebabb97b886a9` |
| `.devtools/project.md` | `e2f5561d5449bd9136880b6fa1bf696322bc70bdd98d583bdaa2a15a2ce25a7a` |
| `skills/components/SKILL.md` | `1232e277b0b9b116325956b0084027963491aa02065d441392698eb5013d1e10` |
| `skills/components/references/build.md` | `f01ae0b3865c4f5028a2075b988a3a84ec4665436d2120a7df97a1c82562fb32` |
| `devtools/build_plugins.py` | `a98b0d93ef4df6286c4c72d74986464d2f80c4b9c7d4b80eb09fc3e0b04ca674` |
| `devtools/release_plugins.py` | `eedc3a907803df084a8941aa9bf0a511c3679156cf904ebfa8cc693037e1be59` |
| `devtools/sync.py` | `1637af6f38ec3472e42da7ea3207445ba7b0fd25a0e3e73bba46b140e8da06f6` |
| `devtools/from_gsd.py` | `7865f45e952703de6d59793e016714a417e35056a6ba4ef8f14f2ea15dcf209a` |
| `skills/components/scripts/components_index.py` | `3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14` |
| `skills/components/scripts/rules_check.py` | `69dd596107826bdf3fc551db810097ae8e292e61c257977cef6b5cde8dbb772b` |
| `skills/dev-handoff/scripts/handoff.py` | `dbab0519e8689154579ec06bc0894125d08b5244ea738d547b66947537d16a6a` |
| `skills/milestone/process-phase/scripts/review_tool.py` | `12dc9800f55dc9f409dadf8466b39591c6b58f2210195478cb4ce39e985a38ff` |
| `skills/phase/process-phase/scripts/phase_tool.py` | `08dadf9fc68e96320f9c3bdaf6ae3483ed330a8d8608bf2c321232f4bf73be8e` |
| `skills/phase/process-phase/scripts/coder_pool.py` | `f657307c1e0f1f5c377aa3fcdd69e85daf7be81de91689ecc503c17e9ceb7b1d` |
| `skills/phase/process-phase/scripts/codex_gate.py` | `66f9cfeae96b82e6a4b3a757da94278c95a08dba2d8b2ccadcbc1524bae3e698` |
| `skills/phase/pytest/phase_selection.py` | `0d8f6ebf67e585ed573975d4e6fe31760592fa64f357091e589504bcc8dc9227` |

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
