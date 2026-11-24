---
milestone: issue-sweep
station: "close"
skill: process-milestone (dvt-milestone 0.1.3)
scope: close
date: 2026-11-23
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "527 passed in 211.95s (0:03:31)"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main"
    exit: 0
    output: "changed against origin/main (cecebc6): 85 file(s) differ; 0 to fix, 0 warning(s), 1 to reread"
    note: "after git fetch origin; the reread: line is handoff.notes, answered in 004-phase-3.md"
  - command: "python3 devtools/release_plugins.py status"
    exit: 1
    output: "0.1.7 is ready: after the merge, run `release_plugins.py tag` on main"
    note: "exit 1 is the expected value: a release is due, and tagging is the owner's"
  - command: "uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml rules_check.py, review_tool.py and handoff.py under skills/, and their copies under plugins/"
    exit: 0
    output: "All checks passed!"
  - command: "python3 plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py status .planning/milestones/issue-sweep/notes/reviews"
    exit: 1
    note: "exit 1 because files are unreviewed after their last repair; listed below, as the helper intends"
  - command: "ruling: delegated (auto=true) approved .planning/milestones/issue-sweep/notes/issue-sweep-plan.md sha256 21da842fc08caa6b9e3294a8c61c21616ae2ac7b440913e3f01953feeed9aadc"
    exit: "n/a -- ruling"
evidence:
  - path: .planning/milestones/issue-sweep/notes/issue-sweep-plan.md
    sha256: 21da842fc08caa6b9e3294a8c61c21616ae2ac7b440913e3f01953feeed9aadc
  - path: .planning/milestones/issue-sweep/README.md
    sha256: 9f5c07e829efcb166d46c79bb8a2ffbf0ad7c17a018dd0bb28249f8851263fa6
  - path: .planning/milestones/issue-sweep/001-plan.md
    sha256: 750f4b85636d7150f9d06d1faa8b735bf62db2981a9976d4fbebf7fb712a4823
  - path: .planning/milestones/issue-sweep/002-phase-1.md
    sha256: af16b3a345b415abd9f28339f9a59c2e95b70fea226b96ebfb4d3b9922b3195b
  - path: .planning/milestones/issue-sweep/003-phase-2.md
    sha256: 8c443917ddf13cbba4d3d7cc555646e2e1ed197082b46279292a9d30748771fe
  - path: .planning/milestones/issue-sweep/004-phase-3.md
    sha256: 4bf9c79564a64825ac23622fec0321b0b48934473b93f5c196a8c06e7ca29068
  - path: .planning/milestones/issue-sweep/005-phase-3-correction.md
    sha256: 37e99d6c635e285d06fc5b2619d2b1dbf5f39d86d618d235bfda152ebd9f94c1
  - path: .planning/milestones/issue-sweep/notes/phase-1-spec.md
    sha256: 15fb2bd0ae753f741b2ff0e2e25d7bcde3c5482bbe1df7197b2855681223b30e
  - path: .planning/milestones/issue-sweep/notes/phase-2-spec.md
    sha256: 67ab21cb211951dff411dd829e50482d0a1af872a5d38b460191038a6be19532
  - path: .planning/milestones/issue-sweep/notes/phase-3-spec.md
    sha256: a95961991aaad843565e8017efdc0253cc0dec11a5d3f02ade191f9ce9d3e93f
  - path: .planning/milestones/issue-sweep/notes/reviews/close-r1/BRIEF.md
    sha256: 71459bd982a8817aab7327a1938422776adf3cc61bdb02700382bd574f63efef
  - path: .planning/milestones/issue-sweep/notes/reviews/close-r1/review.md
    sha256: a2d93751aaa2cf896e00a27023049a40427e9494479ae2d89bcd868f6dc02ed4
  - path: .devtools/components/COMPONENTS.md
    sha256: 45e9ff0698ed0d1a0796aa171f562c3c16ff62802baad7e3d6fc4c610efc9b88
---

# Claim

The milestone `issue-sweep` is closed by delegated approval (auto=true): its three phases
are recorded, the full suite exited 0 on the close's head, eight of the ten issues are
fixed as the table below says and the other two are left out by the owner's ruling, and
each completion predicate C1 to C9 is met as the next table says, with the residuals and
the unreviewed bytes listed.

## Completion predicates

| Predicate | Evidence | Met |
|---|---|---|
| C1 The test of generated cases is skipped, not failed, for a GND without its `synth` extra; it runs where GND has the extra; a stand-in that refuses holds the guard | `002-phase-1.md`: at `dd0e7a1` with an isolated GND `1 failed`, on the head `1 skipped`; the guard's three tests, and r1 F1's | yes |
| C2 The pytest plugin's index entry lists the tests that run it, and `tests/test_phase_selection.py` holds the other branches; `review` prints 0 for components with no tests | `002-phase-1.md` (16 cases; ten one-line breaks of the plugin each failed a case); the review output of that record | yes |
| C3 One list of other planning tools, followed by both scripts; the tests of `tests/test_from_gsd.py` and `tests/test_sync.py` at `cecebc6` unedited | `002-phase-1.md`, G1 and G2; `git diff cecebc6 -- tests/test_from_gsd.py tests/test_sync.py` adds two tests and edits none | yes |
| C4 The index tool can refuse a baseline (46), reads a stale base's upstream and says so (45, part 1), takes a `reread:` line (45, part 2), and reviews the counted folders (44) | `003-phase-2.md`, A1 to E2 and the review repairs | yes, with the refused write exiting 1 (c1) |
| C5 `init` then `test` prints `0 wrong`, exit 0, with each plugin | `004-phase-3.md`, T1 and the by-hand runs | yes |
| C6 The four docstrings say what the code does; a settings file a script cannot use exits as D10 rules; `phase_tool.py` as D11 rules; the three lint-clean scripts stay clean | `004-phase-3.md` | yes, with D10 amended for `coder_pool.py` (c1) |
| C7 The full suite, the build check and the strict index check exit 0 | Gates above | yes |
| C8 The pages and skills describe the changed behaviour; dev-tools' "no baseline" gate is one command | `003-phase-2.md` and `004-phase-3.md`, "What shipped"; `.devtools/project.md` | yes |
| C9 A close record, after the close review, that names what became of each of the ten issues | This record, "The ten issues"; `notes/reviews/close-r1` | yes |

## The ten issues

| Issue | What became of it | Commits |
|---|---|---|
| 31 A test fails instead of skipping when GND lacks its synth extra | Fixed: the guard reads `rules_check.py test`'s note, skips only on exit 0 with GND's refusal | `2921a3b`, `1e4d5ff` |
| 33 In a dvt-milestone install, `rules_check.py test` fails on its own starter rules | Fixed: a rule about plans is skipped where the phase tool is not; a test runs `init` then `test` in each plugin | `6c2ada5`, `43f6d83` |
| 39 The index cannot see one script running another | Not in this milestone (plan D1, the owner's "Yes, eight"): a format change with a design to settle | -- |
| 40 Keep a hand-off note's ignored paths in a form takeover can parse | Not in this milestone (plan D1): a note-format change with its own design question | -- |
| 41 `sync.py` and `from_gsd.py` each carry the same list | Fixed: `from_gsd.py` reads `sync.py`'s list | `2921a3b` |
| 42 No test runs the `phase_selection.py` plugin | Fixed, with its premise refuted in part: two tests already ran it through the sync. The entry lists them, and a new file holds the other branches | `2921a3b`, `1e4d5ff` |
| 43 Four module docstrings say what their code does not do | Fixed: the docstrings, and a settings file five scripts cannot use now exits 2 (one envelope for `phase_tool.py`); `coder_pool.py` keeps its documented exit 1 | `6c2ada5`, `43f6d83` |
| 44 `review`'s same-name leads ignore the folders `count_extra_dirs` counts | Fixed: the groups read from the modules cover the counted folders | `47dc420` |
| 45 `changed` can judge against a stale local base; an entry cannot be marked as reread | Fixed, both parts: the upstream of a base strictly behind it, with a note, and the `reread:` line | `47dc420`, `ba1d686` |
| 46 `--check --strict` cannot refuse a baseline file | Fixed: `allow_baseline`; dev-tools sets it false | `47dc420` |

None of these is closed on GitHub. The pull request that merges this branch should name
the eight it fixes; closing them is the owner's (S0.4).

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests -q
    527 passed in 211.95s (0:03:31)
    $ python3 devtools/build_plugins.py --check
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (no output; exit 0)
    $ git fetch origin; python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main
    reread: handoff.notes (entry not edited): skills/dev-handoff/scripts/handoff.py
    changed against origin/main (cecebc6): 85 file(s) differ; 0 to fix, 0 warning(s), 1 to reread
    $ python3 devtools/release_plugins.py status
    version in the tree: 0.1.7
    released: 0.1.2 (plugins-v0.1.2)
    34 plugin file(s) changed since plugins-v0.1.2
    0.1.7 is ready: after the merge, run `release_plugins.py tag` on main
    $ uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml <the three scripts and their copies>
    All checks passed!
    $ python3 plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py status .planning/milestones/issue-sweep/notes/reviews
    .planning/milestones/issue-sweep/notes/reviews/plan-r1: plan review by codex (codex default), done, 5 finding(s) in the ledger
    .planning/milestones/issue-sweep/notes/reviews/phase-1-r1: phase review by codex (codex default), done, 2 finding(s) in the ledger
    .planning/milestones/issue-sweep/notes/reviews/phase-2-r1: phase review by codex (codex default), done, 2 finding(s) in the ledger
    .planning/milestones/issue-sweep/notes/reviews/phase-3-r1: phase review by codex (codex default), done, 3 finding(s) in the ledger
    .planning/milestones/issue-sweep/notes/reviews/close-r1: close review by codex (codex default), done, 4 finding(s) in the ledger
      problem: F2: Repaired at '(the close commit)' is not a commit or tag here
      problem: F4: Repaired at '(the close commit)' is not a commit or tag here
    unreviewed: .devtools/components/COMPONENTS.md (changed since .planning/milestones/issue-sweep/notes/reviews/close-r1 read b5051c5d439b)
    unreviewed: .devtools/components/modules/skills.md (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 5388364738e7)
    missing: .planning/milestones/issue-sweep/005-close.md (.planning/milestones/issue-sweep/notes/reviews/close-r1)
    unreviewed: .planning/milestones/issue-sweep/README.md (changed since .planning/milestones/issue-sweep/notes/reviews/close-r1 read 6ac0310fb63e)
    unreviewed: .planning/milestones/issue-sweep/notes/issue-sweep-plan.md (changed since .planning/milestones/issue-sweep/notes/reviews/close-r1 read 56bb9160470f)
    unreviewed: plugins/dvt-milestone/skills/components/scripts/components_index.py (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 5419276cad70)
    unreviewed: plugins/dvt-milestone/skills/components/scripts/rules_check.py (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 141c8d6dffb3)
    unreviewed: plugins/dvt-milestone/skills/dev-handoff/scripts/handoff.py (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 7779a0c7ab10)
    unreviewed: plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 5fade2fcb3ce)
    unreviewed: plugins/dvt-phase/skills/components/scripts/components_index.py (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 5419276cad70)
    unreviewed: plugins/dvt-phase/skills/components/scripts/rules_check.py (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 141c8d6dffb3)
    unreviewed: plugins/dvt-phase/skills/dev-handoff/scripts/handoff.py (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 7779a0c7ab10)
    unreviewed: plugins/dvt-phase/skills/process-phase/scripts/phase_tool.py (changed since .planning/milestones/issue-sweep/notes/reviews/phase-3-r1 read 7714ffc3c3bd)
    (51 lines `reviewed: …`, one per file whose bytes a finished round read, not shown)

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/issue-sweep/notes/issue-sweep-plan.md (repaired at the close, c1)
    sha256: 21da842fc08caa6b9e3294a8c61c21616ae2ac7b440913e3f01953feeed9aadc
    date: 2026-11-23
    authorization: the owner's "process-milestone issue-sweep auto", for this milestone
    scope: the close ruling of issue-sweep and the plan repairs c1
    not covered: pushing, opening the pull request, merging, tagging, releasing, and
      anything posted to GitHub

This is an agent's ruling under the owner's delegation, not the owner's own reading.

The review status above was run before the commit that holds this record. Its two
`problem:` lines are F2 and F4 of the close round, whose ledger names this record's
commit; the ledger is committed in the commit after it, as the plan gate's was. Its
`missing:` line is the draft of this record, which the round read as `005-close.md`
before it was renamed `006-close.md` to make room for the correction record.

## Records

- `001-plan.md`: the plan gate (the owner's approval).
- `002-phase-1.md`: the GND guard, the plugin's tests, one list of other planning tools.
- `003-phase-2.md`: the index tool refuses a baseline, reads a stale base's upstream,
  takes a `reread:` line, reviews the counted folders; plugins 0.1.7.
- `004-phase-3.md`: starter rules pass without the phase tool; a settings file a script
  cannot use exits 2; the docstrings.
- `005-phase-3-correction.md`: one line of `004-phase-3.md`'s gate output, misquoted (30
  plugin files where the command printed 34). The close's own gate output above is from
  runs on its head.

## Reviews

| Round | Subject | Findings | Blocking | Self-inflicted | Repaired at |
|---|---|---|---|---|---|
| plan-r1 | the plan and the phase 1 spec | 5 | 3 | 0 / 5 | `3663a15` |
| phase-1-r1 | phase 1 | 2 | 1 | 0 / 2 | `1e4d5ff` |
| phase-2-r1 | phase 2 | 2 | 1 | 0 / 2 | `ba1d686` |
| phase-3-r1 | phase 3 | 3 | 2 | 0 / 3 | `43f6d83` |
| close-r1 | the milestone's evidence and the repaired code | 4 | 0 | 0 / 4 | `92d936e` and this record's commit |

Every round had one seat, Codex, read-only, effort `high`. One reviewer is one reviewer.

The close round read 26 files at the bytes its brief names (SHA-256 `71459bd9…efef`),
among them the five settings loaders, `components_index.py`, `rules_check.py`, the test
files and the index, so the repairs of phases 1 to 3 and the fix of K6 now carry its
opinion where `review_tool.py status` says `reviewed`. It confirmed: the ten-issue table
against the issues' text and commits; the three substantive c1 repairs and their prior
wording; the build and strict index checks; the stale base and the two equal `facts`
documents; the five loaders in 74 in-memory checks (missing file, malformed input, wrong
types); the guard and the parsed envelope, with in-memory negative controls; that K6's
loops are inside the file branch; the planning-tool adapter for all 256 combinations; and
the four earlier rounds' states and digests. It could not run pytest or ruff, nor any
fresh-project or GND check. Its four findings, each reproduced:

- F1 (hardening): the close counted 13 leads and two older entries; `review` printed 15
  and six. Four entries reread before phase 3's repairs were reread beside them
  (`92d936e`); the counts are now 15 and two.
- F2 (completeness): C9 was marked met in a draft with placeholders. This record
  completes them; its final bytes carry no review opinion.
- F3 (hardening): `004-phase-3.md` misquoted its release status (30 where the command
  printed 34). Corrected by `005-phase-3-correction.md` (`92d936e`).
- F4 (completeness): one question was swept twice; merged.

The plugin copies the round lists as unreviewed are byte for byte the reviewed sources,
which `build_plugins.py --check` shows; `.devtools/components/modules/skills.md` is
generated, and `--check --strict` shows it is what the script writes.
Every finding was reproduced before it was believed, and every code finding has a test
that failed on the reviewed code.

Three defects of this milestone's own were found by the full suite, not by a review:
phase 2's tie within one second (`1 failed`), and phase 3's type loop outside the file
branch (`34 failed`), after a repair; and one by the reviewer of phase 2 (a tag and a
branch of one name). Two commit messages and one record were corrected before anything
was built on them: phase 1's work commit said `470 passed` where the suite printed
`469`; phase 2's said the suite had passed before it was read (`1 failed`); phase 2's
record named the work commit by its hash before an amend. One committed record could not
be corrected that way: `004-phase-3.md` quotes a line copied from phase 2's record, and
`005-phase-3-correction.md` corrects it.

## Plan repairs (amendment c1)

Each written into `notes/issue-sweep-plan.md` at its site, marked `(c1)`, with the prior
wording kept and the record that raised it named.

| Site | Prior wording | Repair | Raised in |
|---|---|---|---|
| P2.1 | "writes nothing and exits 2" | exits 1, as every refusal of that script does | `003-phase-2.md` (phase 2 spec D1) |
| Section 9, phase 1, by hand | no command (the phase 1 spec's D4 named `uvx --from …` without `--isolated`) | `uvx -q --isolated --from get-nick-done==0.4.0 gnd` | `002-phase-1.md` (spec I2) |
| Section 2, phase 3, issue 43; D10 | "exit 2, in every one" | except `coder_pool.py`, which keeps its documented exit 1 | `004-phase-3.md` (phase 3 spec D1, a refuted premise) |
| Status | "Approved … No phase has started" | the close | this record |

The phase 1 spec's D4 is not repaired: a spec is a note of its phase, and its finding I2
says what the command should have been.

## Question sweep

Every record of the milestone was reread. Each question it raised is here once.

| Question | Raised in | Disposition |
|---|---|---|
| Q1 Which of 39 and 40 comes next, and whether 39 is a milestone or a phase of one | plan, section 10 | **Carried** to the owner. Both stay open on GitHub with their reason in the plan's section 7 |
| Q2 Issue 31's failure was not reproduced here | plan, section 10 | **Closed** by `002-phase-1.md`: reproduced at `dd0e7a1` with an isolated GND |
| Q3 Whether the index review offered in the plan is taken before phase 2 | plan, section 10 | **Retired**: not taken; phase 2 added the `reread:` field it would use. What remains is in the J7 row |
| The index lists 3 of 12 entries as older than their code; a review was offered | `001-plan.md` | **Carried** with J7 |
| The `uvx` command without `--isolated`; P2.1's exit | `002-phase-1.md`, `003-phase-2.md` | **Closed**: plan repair c1 |
| Whether issue 42 is closed as fixed or answered | `002-phase-1.md` | **Carried** to the owner. Proposed: fixed; the entry said no test ran the plugin, and most of its branches had none |
| J4: `rules_check.py check --base` names the base as asked, not the one used | `003-phase-2.md` | **Carried** to the owner, as a possible issue. The note on standard error says which was used |
| J7: an index review for the 15 same-name leads `review` now prints (13 when phase 2 recorded it; `settings_error` and `read_settings_file` are copies phase 3 made on purpose, S0.2), and for `handoff.notes` (6 commits) and `sync.copies` (5), still older than their code | `003-phase-2.md`; close-r1 F1 | **Carried** to the owner: the components skill's Review mode, its to accept |
| K6: a focused gate for a change to a settings loader should include a run with no settings file | `004-phase-3.md` | **Carried** to the owner: a rule for `.devtools/project.md`'s verification selection, which is the project's to write |
| D10 amended for `coder_pool.py` | `004-phase-3.md` | **Closed**: plan repair c1 |

**Proposed issues** (none is filed; posting to GitHub needs the owner each time):

- `rules_check.py check --base` names the base as asked, not the one read (J4).
- A review of dev-tools' component index: the 15 same-name leads and the two entries older
  than their code (J7).

## Refactoring review

Each phase record answers for its own phase. The close confirms every refactor a phase
saw and deferred has a row:

| Record | Its answer | Deferred | Row |
|---|---|---|---|
| `002-phase-1.md` | One executed: `from_gsd.other_plans` calls `sync.other_plans` | none | -- |
| `003-phase-2.md` | None beyond the phase's own (`resolve_base` is the base rule's one home) | the same-name leads (13 then, 15 now) | J7 |
| `004-phase-3.md` | None beyond the phase's own | six `load_settings` of one shape | **Retired**: S0.2, a shipped script stands alone |

## Residuals the close accepts

- `handoff.notes` and `sync.copies` stay listed as older than their code, and `review`
  prints 15 same-name leads (J7).
- A setting's value is checked for its type only (`004-phase-3.md`, boundary).
- `coder_pool.py`'s settings exit stays 1 (D10, c1).
- `rules_check.py check --base`'s summary names the base as asked (J4).
- Every test ran on macOS, with GND 0.4.0 and Python 3.14.

## Boundary -- what this close does NOT establish

- That 0.1.7 is released: tagging is the owner's. `release_plugins.py status` says 0.1.7
  is ready.
- Anything pushed, merged or posted: the branch is local; no pull request is open; no
  issue was commented on, labelled or closed.
- That one reviewer's reading is more than that. Every round had Codex in the one seat,
  read-only; no round ran the suite.
- That the bytes `review_tool.py status` lists as unreviewed carry a review opinion.
- That the proposed issues are wanted. They are proposals.

## Owner actions that remain

- Rule the carried rows: Q1 (39 or 40 next), issue 42's disposition, J4, J7, K6.
- Push the branch and open the pull request, naming issues 31, 33, 41 to 46.
- Merge it, then `python3 devtools/release_plugins.py tag` for 0.1.7.
