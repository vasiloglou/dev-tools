---
milestone: component-index
station: "close"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: close
date: 2026-11-23
gates:
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
    output: "(no output)"
  - command: "test ! -e .devtools/components/unassigned-baseline.txt"
    exit: 0
    output: "(no output)"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py search --explain <each case of search-cases.md>"
    exit: 0
    output: "9 of 9 cases put the expected component first; the negative case printed 'no component matched'"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "350 passed in 167.71s (0:02:47)"
  - command: "uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q"
    exit: 0
    output: "8 passed in 2.88s"
  - command: "uv run --no-project --with pytest python -m pytest tests/test_handoff.py -q"
    exit: 0
    output: "103 passed in 44.70s"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
    output: "(no output)"
  - command: "review_tool.py run .planning/milestones/component-index/notes/reviews/close-r1 (the close review, Codex, read-only)"
    exit: 0
    output: "VERDICT: APPROVE; no findings"
  - command: "ruling: delegated (auto=true) approved the close of component-index, with the residuals this record lists"
    exit: "n/a -- ruling"
slow_cadence:
  command: "uv run --no-project --with pytest python -m pytest tests -q"
  trigger: "n/a -- the full suite is completion predicate C3, and it ran"
  reason: "this repository has no broader lane than the full suite"
evidence:
  - path: .planning/milestones/component-index/notes/component-index-plan.md
    sha256: 9684c846e59bf116b706aa3c64dc5d4710486572a20f73cf581d11a188132f31
  - path: .planning/milestones/component-index/notes/reviews/close-r1/BRIEF.md
    sha256: d83e92c4dd7d101a14c5df9ca2915afb060b6486b16c83b4ed08661e08f00d0e
  - path: .planning/milestones/component-index/notes/reviews/close-r1/review.md
    sha256: f9b5999d89f2cd75d18f581197057138dd3c161e9cb3b74621539d393e436695
  - path: .planning/milestones/component-index/notes/reviews/close-r1/FINDINGS.md
    sha256: c1b4b82e630e2ed6171e89f5011af1f8c0d4d3134396a8b86a3a1c6c25875fc5
  - path: .devtools/components/COMPONENTS.md
    sha256: 33b6da675aa123e43bb1ce610c583ddcc6c326e22bbade8aad8eb650a7e8a099
  - path: skills/dev-handoff/scripts/handoff.py
    sha256: e891bdb31f0a48089a9db0a117ed5aad12486d34d536dc3fa35f049dc3e16a35
  - path: tests/test_own_index.py
    sha256: 20eb2fa283b4ece497665e188eceecea50581193c7119b729fcc0b7b69e9f405
---

# Claim

On `main` at `811b4a3`, the five measurable completion predicates of the plan hold: the
index check exits 0 at 12 of 12 modules with no baseline (C1); each of the 9 search cases
puts its component first and the negative case matches nothing (C2); the full suite exits
0 with 350 passed, and it includes a test that fails while the index is stale (C3);
`.devtools/project.md` and the pages that describe dev-tools' own use name the index
(C4); and `tests/test_handoff.py` exits 0, with issue 28 closed by a pull request that
says `Fixes #28` (C5). This record is C6. Fifteen questions are swept below: six are
closed, eight carried to the owner and one partly closed. The plan is repaired at ten
sites (amendment c1).

## Close ruling (verbatim)

    ruling: delegated (auto=true) approved
    subject: the close of the component-index milestone
    date: 2026-11-23
    authorization: the owner's invocation "/dvt-milestone:process-milestone auto" of
      2026-11-21, which delegates the plan, spec and close rulings of this milestone, and
      the owner's "Yes, run the close" of 2026-11-23
    on: C1 to C5 measured at 811b4a3; the close review's APPROVE with no findings; the
      sweep of Q1 to Q15; plan amendment c1
    accepts: the five residuals of "Residuals the close accepts"
    carries: Q1, Q3, Q7, Q9, Q10, Q12, Q13, Q14 and the rest of Q15 to the owner

This is an agent's ruling under the owner's delegation, not the owner's own reading of
this record. It covers neither the merge of the pull request that carries the record, nor
a release tag, nor the filing of any proposed issue.

## What the milestone delivered

| Phase | What | Pull request | Record |
|---|---|---|---|
| Plan | The plan, three review rounds, the plan gate | in #29 | `001-plan.md` |
| 1 | `takeover` checks every ignored path a hand-off note was written with (issue 28) | vasiloglou/dev-tools#29, merged `2b5173a` | `002-phase-1.md`, `005-phase-3-reread.md` |
| 2 | An index can count the modules of extra source folders (`count_extra_dirs`) | vasiloglou/dev-tools#30, merged `938c4e6` | `003-phase-2.md` |
| 3 | dev-tools' own index: 12 components, 3 subsystems, 9 search cases, six suggested code changes | vasiloglou/dev-tools#32, merged `827e766` | `004-phase-3.md`, `005-phase-3-reread.md` |
| 4 | A test that fails while the index is stale; the gate rows; the pages | vasiloglou/dev-tools#36, merged `811b4a3` | `006-phase-4.md` |

Fifteen review rounds ran, all with Codex as the one reviewer: 3 over the plan and 12 over
phase diffs, with 40 findings in their ledgers: 19 classed blocking, 8 hardening and 13
completeness. All 40 were reproduced; 39 were fixed and 1 was rejected.

## Since record 006

- vasiloglou/dev-tools#35 (a standing check in review briefs for code fitted to its
  examples; plugins 0.1.5) was merged into `main` while phase 4 was being pushed. It
  changed `review_tool.py`, which the index covers.
- `main` was merged into phase 4 (`05abd23`). On that merge the new test exited 1 with
  `stale or missing: .devtools/components/modules/skills.md`: its first failure on a
  real change. The page was regenerated and the `review.rounds` entry, read beside #35's
  diff, gained the standing check in its `verbs` and `notes` (`181bde9`). The full suite
  then exited 0 with 350 passed, and the 9 search cases still held.
- The owner asked for vasiloglou/dev-tools#36 to be opened and then merged; the agent
  merged it with a merge commit (`811b4a3`). `main`'s tree is the tree of `090e3a0`.

## Completion predicates, measured

All on `main` at `811b4a3`, with a clean tree (`git diff HEAD | shasum -a 256` gave the
empty-input hash, `e3b0c442…`).

| Predicate | Measurement |
|---|---|
| C1 Every module of `devtools/` and `skills/` has a component, with no baseline | `--check --strict` exit 0; `stats`: `coverage: 12/12 devtools, skills modules assigned to components`; the `test ! -e` exit 0 |
| C2 Each search case puts its component first; the negative case matches nothing | 9 of 9; `no component matched` |
| C3 The suite exits 0 and includes a test that fails while the index is stale | `350 passed`, exit 0. `tests/test_own_index.py`: 8 passed; it exited 1 on the merge of #35 (above) and in the two gates of record 006 |
| C4 `.devtools/project.md` names the index, its folder and its two gates; the own-use documentation names it | `.devtools/project.md`, "What runs here" and "Gates"; `README.md`, `docs/milestone.html#own-use`, `docs/components.html`, `docs/contribute.html`, `AGENTS.md`, `CONTRIBUTING.md` |
| C5 `takeover` is not ready while an ignored path the note was written with, other than a key file, is absent; the phase 1 tests exit as their spec lists; the pull request says `Fixes #28` | `tests/test_handoff.py`: 103 passed, exit 0. #29's description opens `Fixes #28.`; issue 28 closed with its merge on 2026-11-23 |
| C6 A close record, after the close review | This record |

## Gate output (verbatim)

    $ C=plugins/dvt-milestone/skills/components/scripts/components_index.py
    $ python3 $C --check --strict                                 -> exit 0
    $ test ! -e .devtools/components/unassigned-baseline.txt      -> exit 0
    $ python3 $C stats | head -1
    coverage: 12/12 devtools, skills modules assigned to components; external: none
    $ python3 $C search --explain <each query of search-cases.md>
    9 of 9 cases put the expected component first
    $ python3 $C search --explain deploy to kubernetes
    no component matched: this is not proof that nothing exists; search modules/ and git grep
    $ uv run --no-project --with pytest python -m pytest tests/test_handoff.py -q
    103 passed in 44.70s                                          -> exit 0
    $ uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q
    8 passed in 2.88s                                             -> exit 0
    $ python3 devtools/build_plugins.py --check                   -> exit 0
    $ uv run --no-project --with pytest python -m pytest tests -q
    350 passed in 167.71s (0:02:47)                               -> exit 0

## Plan repairs (amendment c1)

The phase records deferred these to the close. Each is written into
`notes/component-index-plan.md` at its site, marked `(c1)`, with the earlier wording kept
and the record that raised it named. The amended plan's SHA-256 is in the evidence list.

| Site | Earlier wording | Repair | Raised in |
|---|---|---|---|
| C3; section 9 | "except for the known GND `synth` case" | The suite exits 0; that case was this machine's GND install | `004-phase-3.md` |
| C5 | "The tests T1 to T10" | The list grew to T20; C5 is judged by the exit of `tests/test_handoff.py` | `002-phase-1.md`, Q4 |
| Section 3 | "Three load another script at run time" | Five do | `004-phase-3.md` |
| Section 4, phase 1 | "bump, to 0.1.4" | 0.1.3 was never tagged; 0.1.4 is also #34, and 0.1.5 also #35 | `002-phase-1.md`, `006-phase-4.md`, this record |
| Section 4, phase 2 | "the retaken `docs/adopt.html` capture" | Kept, not retaken: D2 (d), the owner's ruling of 2026-11-22 | `003-phase-2.md` |
| Section 4, phase 3 | "no readers are fanned out" | The reread used four readers; partial reading left four entries false | `005-phase-3-reread.md` |
| Section 4, phase 4; section 9 | "`changed --base main`" | `origin/main`, after a fetch | `006-phase-4.md` |
| Section 7 | "the graph stays within `package_dir`" | It already holds a module outside it that the catalog names | `003-phase-2.md`, Q6 |
| Section 8, a3 | "the branch is rebased onto main" | `main` was merged into each branch, bottom up; nothing was rebased | `006-phase-4.md` |
| Status | (none) | Amendment c1 and the close are named | this record |

## Review

One round of the review helper, `--subject close`, reviewer Codex (read-only, effort
`high`), over 18 files: this record as drafted, the amended plan, records 001 to 006, the
milestone's `README.md`, the phase 4 spec, `.devtools/project.md`, the catalog with its
search cases and `REVIEW.md`, `handoff.py` with its reference and tests, and
`tests/test_own_index.py`. **One reviewer is one reviewer.**

| Round | Brief | Findings | Verdict |
|---|---|---|---|
| close-r1 | `d83e92c4…0d0e` | 0 | APPROVE |

- The review read this record at SHA-256
  `2207e2d76851c9c97cd9c5980870c821c5d1600268a8d1889041931630220103`. This section,
  the ruling above, the two matching entries of `gates`, five entries of `evidence` and
  the last sentence of the paragraph below were written afterwards, and carry no review
  opinion. Nothing else in the record changed.
- It checked: the 18 hashes; the strict index check at 12 of 12 with no baseline; the 9
  search cases and the negative one; the build check; that the sweep accounts for Q1 to
  Q15; and the 40 findings of the earlier ledgers, 39 fixed and 1 rejected.
- For `handoff.py`, whose repairs of `22d6258` no earlier round had read, it ran the
  writer and reader in memory over 516 scenarios (paths before and after the 25th, control
  characters, backticks, missing keys), with further probes of forged snapshot lines and
  of a rest line without its cut line, and found no case that reads as ready with a path
  missing.
- It did not run pytest, by the read-only rule: the 350, 103 and 8 passed above are this
  record's evidence, not the reviewer's. It did not check issue 28 or pull request 29 on
  GitHub; local history holds `Fixes #28`. Its file-system probes were in memory.
- No second round: the first found nothing.

**Which files a review covers at their present bytes.** `review_tool.py status` was run
over all fifteen earlier rounds on `main` at `811b4a3`. A file it calls unreviewed
carries no review opinion from those rounds:

- this milestone's own work: `skills/dev-handoff/scripts/handoff.py` and its two plugin
  copies, `skills/dev-handoff/references/handoff.md` and its copies, `tests/test_handoff.py`
  (all changed at `22d6258`, after phase-1-r4, and again by the merge of #34);
  `tests/test_own_index.py` (changed at `b807ca1`, after phase-4-r1);
  `.devtools/components/COMPONENTS.md` and `modules/skills.md` (changed at `181bde9`);
  `notes/phase-2-spec.md` (the owner's D2 (d) ruling), `notes/phase-4-spec.md`,
  `notes/phase-3-reading/handoff.md`, the milestone's `README.md`, `.gitignore`;
- other people's changes since: `skills/components/scripts/rules_check.py` (#34),
  `skills/milestone/process-phase/scripts/review_tool.py` (#34, #35) and
  `docs/milestone.html` (#35 and phase 4).

The close review read the first group, except the plugin copies (which the build check
shows equal to their sources), the generated `modules/skills.md` (which the index check
shows equal to what the script writes), `notes/phase-2-spec.md`,
`notes/phase-3-reading/handoff.md` and `.gitignore`.

## The open-questions sweep

Every record of the milestone was reread. Each question it raised is here once.

| Q | Question | Raised in | Disposition |
|---|---|---|---|
| Q1 | The import graph cannot see run-time loads. Should the index tool read `spec_from_file_location` and `runpy.run_path` calls with literal paths? | plan, section 10 | **Carried** to the owner, as proposed issue P1. A product change. The three subsystems state the five loads in `notes:` meanwhile |
| Q2 | One entry per file gives large scripts one entry each. Does search find what a planner asks for? | plan, section 10 | **Closed** by this record: 9 of 9 cases on `main`; and in use, phase 4's reuse searches and the search for #35's new check each put the right component first (`006-phase-4.md`; above). No finer grain is needed now |
| Q3 | A machine-readable inventory of ignored paths in every hand-off note, so `takeover` stops parsing Markdown | `002-phase-1.md` | **Carried** to the owner, as proposed issue P2 and a milestone of its own: it changes a format other projects' branches hold, which `.devtools/project.md` puts in the evidence lane. Four review rounds of phase 1 each found another way the Markdown misleads `takeover` |
| Q4 | Plan C5 names "T1 to T10" | `002-phase-1.md` | **Closed**: plan amendment c1 |
| Q5 | Should `.gitignore` carry `review.log`? | `002-phase-1.md` | **Closed** by `005-phase-3-reread.md`: `.planning/**/review.log`, at `3963a46` |
| Q6 | Plan section 7, "the graph stays within `package_dir`" | `003-phase-2.md` | **Closed**: plan amendment c1 |
| Q7 | Who takes `REVIEW.md`'s suggestions, and when | `004-phase-3.md` | **Carried** to the owner. Suggestion 4 is vasiloglou/dev-tools#33, filed 2026-11-22. 1 (one list of other planning tools), 2 (a test for `phase_selection.py`) and 6 (four docstrings, Q12) are fast-lane fixes: proposed issues P3, P4 and P5. 5 is Q10. 3 (split the three largest modules) is not proposed: R0.1 says a shipped script stands alone |
| Q8 | The six copies of `plugin_root`, `checkout_root` and `load_settings` were not compared | `004-phase-3.md` | **Closed** by `005-phase-3-reread.md`: the first two are the same code in all six; `load_settings` differs by design |
| Q9 | dvt-milestone ships `rules_check.py` without the `phase_tool.py` it names | `005-phase-3-reread.md` | **Carried** to the owner as vasiloglou/dev-tools#33. Record 005's wording is corrected here: `check --phase` exits 2 with a message that says why, which is a refusal, not the defect. The defect is `rules_check.py test`, which exits 1 with `2 wrong` on the starter rules `init` has just written; the dvt-phase copy prints `0 wrong` |
| Q10 | `review`'s same-named-definition leads look only under `package_dir` | `005-phase-3-reread.md` | **Carried** to the owner, as proposed issue P6. A product gap that phase 2's setting did not reach |
| Q11 | A tracked file whose name holds a newline is printed raw in the snapshot's uncommitted list | `005-phase-3-reread.md` | **Closed** in the code at `22d6258`: `_snapshot_text` now writes the uncommitted and the paused-phase paths through `_one_line`. `test_t17` pins the paused-phase list; no test pins the uncommitted list (a residual, below) |
| Q12 | Four docstrings say what their code does not do | `005-phase-3-reread.md` | **Carried** to the owner, as proposed issue P5 (with Q7) |
| Q13 | `changed` compares with the local `main`, which in a worktree nothing moves | `006-phase-4.md` | **Carried** to the owner, as proposed issue P7. Here the gate row names `origin/main` |
| Q14 | `--check --strict` cannot refuse a baseline | `006-phase-4.md` | **Carried** to the owner, as proposed issue P8. Here the test refuses the file itself |
| Q15 | After a change that keeps behaviour, is an entry reread, and how is its date brought forward? | `006-phase-4.md` | **Partly closed** by this record. The two entries `review` still lists (`handoff.notes`, `components.rules`) were read beside #34's diff at this close: it reformats strings, passes `check=False` and uses `datetime.UTC`, and both entries stay true. `review.rounds` was reread and edited at `181bde9`. What remains, a way to mark an entry reread without editing its `does` or `verbs`, is **carried** to the owner with P7 and P8 |

**Proposed issues** (none is filed; posting to GitHub needs the owner each time):

- P1. components: let the index see run-time loads written with literal paths (Q1).
- P2. dev-handoff: keep the ignored inventory machine-readably in the note (Q3). A
  milestone, not a fix.
- P3. One list of other planning tools for `sync.py` and `from_gsd.py` (Q7, suggestion 1).
- P4. A test that runs the `phase_selection.py` pytest plugin (Q7, suggestion 2).
- P5. Four docstrings that say what their code does not do (Q7, suggestion 6; Q12).
- P6. components: `review`'s same-name leads should follow `count_extra_dirs` (Q10).
- P7. components: `changed` should say when its base is behind its remote (Q13), and
  offer a way to mark an entry reread (Q15).
- P8. components: a way for `--check --strict` to refuse a baseline (Q14).

## Refactoring review

Each phase record answers for its own phase. The close confirms that every refactor a
phase saw and deferred has a row above with a named owner:

| Record | Its answer | Deferred | Row |
|---|---|---|---|
| `002-phase-1.md` | None executed; one deferred | The machine-readable ignored inventory | Q3, carried to the owner as P2 |
| `003-phase-2.md` | None executed; no candidate | none | -- |
| `004-phase-3.md` | None executed; the phase changed no code | `REVIEW.md`'s suggestions | Q7, carried to the owner |
| `005-phase-3-reread.md` | Three helpers added to `handoff.py` with the repair | none | -- |
| `006-phase-4.md` | None needed | Two product questions | Q13 and Q14, carried to the owner |

## Residuals the close accepts

- **Phase 1, in the reviewers' terms** (`002-phase-1.md`): a note written before 0.1.4
  whose ignored path holds a newline that prints as complete valid bullets can still read
  as ready. No writer since 0.1.4 prints such a note.
- The uncommitted list of a hand-off note is written escaped since `22d6258`, and no test
  names a file with a line break to pin it (Q11).
- With `count_extra_dirs` absent, an absolute `package_dir` gives `draft` stubs where the
  earlier version, by reading, exits 1. It was not run, and no test pins it
  (`003-phase-2.md`).
- The index's descriptions are as true as the reread of 2026-11-22 and the two later
  rereads beside a diff. The test checks coverage and the generated pages, not what an
  entry says.
- Every test ran on macOS only.

## Boundary -- what this close does NOT establish

- That 0.1.4 and 0.1.5 are released. Neither is tagged: `release_plugins.py status` says
  `released: 0.1.2`. Tagging is the owner's.
- Anything about #34 and #35 beyond their effect on this milestone's files. They are not
  this milestone's work, and no round of it reviewed them.
- That one reviewer's reading is more than that. All sixteen rounds had Codex in the one
  seat, read-only, so no round ran the test suite.
- That the proposed issues are wanted. They are proposals.

## Owner actions that remain

- Tag `plugins-v0.1.4` and `plugins-v0.1.5`, or one tag for what `main` now holds.
- Rule on the proposed issues P1 to P8.
- Merge the pull request that carries this record.
