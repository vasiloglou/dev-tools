# Review brief: the milestone plan

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can each phase of this plan be implemented and tested as written, and does each of the eight issues it takes get what the issue asks for?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. C1. Every row of the baseline table in plan section 3 that is marked observed describes what the code at these bytes does when the command in that row is run.
- C2. C2. Each thing an issue asks for, for the eight issues the plan takes (31, 33, 41 to 46 in notes/issues-2026-11-23.md), has a criterion in plan section 4 that would fail if it were not delivered, and no request is dropped or contradicted without a decision row that says so.
- C3. C3. Under the phase 1 spec, no command a project runs prints or exits differently, and every existing test of tests/test_from_gsd.py and tests/test_sync.py passes without an edit.
- C4. C4. Every branch in the two branch tables of the phase 1 spec (sections 6.1 and 6.2) has a test in section 8 that fails when that branch is wrong, and the sets the tests S1 to S9 expect are what the plugin at these bytes collects.
- C5. C5. The guard of the phase 1 spec, section 6.1, skips the test when GND refuses synth for want of its extra, and for nothing else that rules_check.py test can print.
- C6. C6. After the index changes of the phase 1 spec, section 6.4, components_index.py review prints 0 for the two groups the spec's gate G-review names, and --check --strict exits 0.
- C7. C7. Each behaviour plan section 2 proposes for phases 2 and 3 can be implemented in the function the plan names, without breaking the plan's rules S0.1 and S0.2.
- C8. C8. Every completion predicate C1 to C9 of the plan has a gate or a ruling that can fail it, and every gate command in plan section 9 runs as written from the repository root.

## The change under review

The files below, as they stand at `cecebc6f5612`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/issue-sweep/notes/issue-sweep-plan.md` | `5ae6fe45eeeddd8870193a3b352e2ec08441e6dbed7ca052d74258276a74d667` |
| `.planning/milestones/issue-sweep/notes/phase-1-spec.md` | `61f8177910722f273e255d6a98b8d752b9fcb6c0bf65559ac38d656b774e5864` |
| `.planning/milestones/issue-sweep/notes/issues-2026-11-23.md` | `7584fec3d861c1113450fa58207fbc671f1ad9e77f2db673d6b1df1f575dc84c` |
| `.planning/milestones/issue-sweep/README.md` | `0c40611ef0046ca22fd810c5f1d6209e9fea1454c75a7a9a6e2496b44e7a2488` |
| `skills/components/scripts/components_index.py` | `3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14` |
| `skills/components/scripts/rules_check.py` | `7e2e49cb065942aa7868a7f615c3b06bef8a603bb82f6edcd5ec60d76b9779ec` |
| `devtools/sync.py` | `c3632fc092eb44208e20e04a3124e2a109c3a6031b6c6a0b58b3fc85160d27fd` |
| `devtools/from_gsd.py` | `7865f45e952703de6d59793e016714a417e35056a6ba4ef8f14f2ea15dcf209a` |
| `skills/phase/pytest/phase_selection.py` | `0d8f6ebf67e585ed573975d4e6fe31760592fa64f357091e589504bcc8dc9227` |
| `skills/phase/process-phase/scripts/phase_tool.py` | `08dadf9fc68e96320f9c3bdaf6ae3483ed330a8d8608bf2c321232f4bf73be8e` |
| `skills/milestone/process-phase/scripts/review_tool.py` | `ef07d53fcf3649a13726ab82c0eba2a824d92c857e81030b3b2f3262895ed9be` |
| `skills/phase/process-phase/scripts/coder_pool.py` | `f657307c1e0f1f5c377aa3fcdd69e85daf7be81de91689ecc503c17e9ceb7b1d` |
| `tests/test_tools.py` | `8453af3f28b0c1fa31d35f563fa71b5e99409253488bee247d53fa574ef31df8` |
| `tests/test_from_gsd.py` | `87c07336d9463bb66d916460d425d95189119abf273f601dc8776a095218156e` |
| `tests/test_plugins.py` | `38d83cf8bca99051bad3e60541507350665f3791ff1c9df50c1a98f2b8e40c54` |
| `tests/test_own_index.py` | `20eb2fa283b4ece497665e188eceecea50581193c7119b729fcc0b7b69e9f405` |
| `.devtools/components/COMPONENTS.md` | `e851b62460cbf59d1d673a390ea0243ab59cbde902be7549c08c133453691634` |
| `.devtools/components_index.settings.json` | `56717af02b363be6354f9fc760ea2a8e56151821c33bfa58342296d1adad6893` |
| `.devtools/project.md` | `1e485b868fde627032c65f9bf311899d4cb18d8a5a0ba91c8ffec8b9de54ff3e` |
| `.planning/PROJECT.md` | `d6b274e2937a8e44fa652ba46e4fdf1260460a8fb1a2a28dd37d67eea591df08` |
| `AGENTS.md` | `2aa20beafc95d7fda49583f5c852b8091f40ff64e1d21c5c0ee0c1c3c9730e60` |
| `CONTRIBUTING.md` | `21f65706f46e6c6677d7202170dbc5f834e75832c88926324fbc611acc19d64f` |

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
