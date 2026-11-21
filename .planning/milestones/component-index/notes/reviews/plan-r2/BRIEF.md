# Review brief: the milestone plan

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can each phase of this milestone plan be implemented and tested as written, against the code it cites at main c9648dd, and do the plan and its two draft phase specs agree with each other, with the code, and with the project's rules in .devtools/project.md? Sites marked (r1 Fn) were changed after round 1 (notes/reviews/plan-r1); judge them as you judge the rest.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The baseline in plan section 3 describes what components_index.py and handoff.py do at c9648dd.
- C2. Phase 1's design leaves the note of any hand-off with 25 or fewer ignored paths exactly as main writes it.
- C3. Phase 1's design makes takeover report not ready whenever an ignored path the note was written with, other than a key file, is absent, for new and older notes.
- C4. Phase 2's design, with count_extra_dirs absent or false, leaves every output and exit of components_index.py unchanged, ordering included.
- C5. Phase 2's list of sites covers every place that decides whether a module has a component, or which modules an entry details.
- C6. No phase needs an input that only a later phase produces, and every completion predicate C1 to C6 has a gate or ruling that can fail it.
- C7. Every gate command in plan section 9 can run as written from the repository root.
- C8. Each test in the two specs, run against the fixture it names, can produce the exit and output the spec expects.

## The change under review

The files below, as they stand at `ada0d1ab3d54` with uncommitted changes.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/component-index-plan.md` | `b139ce1b257ecde2c33fb8496f5eba7413f2c5ea93c8454f533cac176d3f5be4` |
| `.planning/milestones/component-index/notes/phase-1-spec.md` | `ecbb1ca6e0ac35cb2d0faf1d0c6568eee0ed2f05b29517a6534b833f83269373` |
| `.planning/milestones/component-index/notes/phase-2-spec.md` | `a6f148bd662b314ad0b8ae434f58ecf009b5177575cd007c4987182499b93f46` |
| `.planning/milestones/component-index/notes/reviews/plan-r1/review.md` | `92bea45cd4deedbb3510f07938d545d33f441291d1ccb6a1547ce6f8705f2d21` |
| `.planning/milestones/component-index/notes/reviews/plan-r1/FINDINGS.md` | `a4a7cf69afb0f8f13c78e1aec681da7d14ad23592084a761816b9483d4cb8049` |
| `.devtools/project.md` | `e2f5561d5449bd9136880b6fa1bf696322bc70bdd98d583bdaa2a15a2ce25a7a` |
| `.planning/PROJECT.md` | `d6b274e2937a8e44fa652ba46e4fdf1260460a8fb1a2a28dd37d67eea591df08` |
| `AGENTS.md` | `d79796d25b4a68e2145bcc01fab07eb058361bbf77c737ebfb99d9abb20a5c20` |
| `.gitignore` | `5b0d7f0ad8bc998c48ee905c533a5dfe728bbb1dc7fb318e1f7e7ab1456c085a` |
| `skills/components/scripts/components_index.py` | `13105bfbee8587baf491e757c47e2f6da7b1594bb99bb89b006773577fe95793` |
| `skills/dev-handoff/scripts/handoff.py` | `8cf8cb2bccc255a0318d1aa922ecc062bcdd89cd02a5bd6b772322ca27f2cc18` |
| `skills/components/references/build.md` | `8b74ccda535b97bcc4fdcf1b911dc246d6a7a18c6033ef555456076d25efb263` |
| `skills/dev-handoff/references/handoff.md` | `fd4a0ee50d5bded553a17d1ba3320515a442c94390eca97f11b4caf0b9fa3327` |
| `tests/test_handoff.py` | `59f1d71ecee62cdbc8ee8a6244b78e28c606f036e53605d177a2f4505b6cb364` |
| `docs/handoff.html` | `7e35d850d584c7b2d7887f1ccf8868479fd300dddd2953c90628605e56a66c4f` |
| `docs/adopt.html` | `bc4081fcfa9bf43433c83f2198f523e43fabcaf6406566db915cd7de7f00631c` |

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
