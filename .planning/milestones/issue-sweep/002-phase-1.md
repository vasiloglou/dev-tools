---
milestone: issue-sweep
station: "phase-1"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-1
date: 2026-11-23
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_phase_selection.py tests/test_from_gsd.py tests/test_sync.py tests/test_own_index.py -q"
    exit: 0
    output: "290 passed in 121.31s (0:02:01)"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "471 passed in 197.02s (0:03:17)"
    note: "run on the repaired tree, before one sentence of a notes: line in .devtools/components/COMPONENTS.md changed; the first gate, which holds tests/test_own_index.py, ran after it"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 devtools/release_plugins.py status"
    exit: 1
    output: "0.1.6 is ready: after the merge, run `release_plugins.py tag` on main"
    note: "exit 1 is the baseline's: a release was already due before the phase. The four lines are the baseline's"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base dd0e7a1 --strict"
    exit: 0
    output: "changed against dd0e7a1 (dd0e7a1): 13 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "GND_COMMAND=\"uvx -q --isolated --from get-nick-done==0.4.0 gnd\" uv run -q --no-project --with pytest python -m pytest tests/test_tools.py -q -rs -k suggestions_and_generated"
    exit: 0
    output: "1 skipped, 82 deselected in 17.72s"
  - command: "ruling: delegated (auto=true) approved .planning/milestones/issue-sweep/notes/phase-1-spec.md sha256 2fb05b9132ca30f0615f85abd32a201bfbbdafc4251951edd437c92dd0ebca97"
    exit: "n/a -- ruling"
slow_cadence:
  command: "none beyond the full suite"
  trigger: "n/a"
  reason: "the full suite is the repository's only test lane, and it ran (above)"
evidence:
  - path: tests/test_tools.py
    sha256: ad2bdb1eaf83f166dd409d04c2f3e40eb96b982aec9c9dec58995e34a174d840
  - path: tests/test_phase_selection.py
    sha256: ce46d6f1969eb8c650f5126142fae17c14541aa50a6c163f716c3ffd72be0662
  - path: tests/test_from_gsd.py
    sha256: 9b3c4a12fca5be70278e70a07e424abc533841bb17b174c52fd99b993af2d4cf
  - path: devtools/from_gsd.py
    sha256: 67983517b29c9c62a687772c616cd39d40c003259b11d36e05df8a15fee273a8
  - path: .devtools/components/COMPONENTS.md
    sha256: 5dc76d26481452c9a04112e54ff09cd201956f75f9fa81f1de1dbb924e38f838
  - path: .devtools/components/modules/_root.md
    sha256: d603e2622c30e848ae895c51b06d094e12c5ecdbd4f765c3a3bbb064973700ac
  - path: .planning/milestones/issue-sweep/notes/phase-1-spec.md
    sha256: 15fb2bd0ae753f741b2ff0e2e25d7bcde3c5482bbe1df7197b2855681223b30e
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-1-r1/BRIEF.md
    sha256: 1e67658134e9624558fd11a3c9575ec0910942296712fb14ad81b611bfdb49af
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-1-r1/diff.patch
    sha256: e474234961d434bfc2e565b97dbc49db152f42fe056d5e6f56ea0b714c64f3c1
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-1-r1/review.md
    sha256: c66bfa0af981b9b578250a18bb7e0fb548f7c9058a78bd66bbf8177e9f7410ae
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-1-r1/FINDINGS.md
    sha256: aae1aaaee1c1c00fef728cca0d42810a33df353c06a5a199d1447d03d372e90c
---

# Claim

Phase 1's selected gates each exited 0 on the phase's head, except the release status,
which exits 1 as it did before the phase: the test of generated cases is skipped, not
failed, for a GND without its `synth` extra; a new test file holds the branches of the
pytest plugin; and `from_gsd.py` reads `sync.py`'s list of other planning tools.

## What shipped

Commits `2921a3b` (the work) and `1e4d5ff` (the review repairs), on the base `dd0e7a1`
(the spec and its delegated gate).

- **Issue 31, `tests/test_tools.py`.** `without_synth_extra(code, out)` and
  `skip_without_synth_extra(code, out)`: the guarded test skips when `rules_check.py
  test` exited 0 and printed the note `gnd synth --guarded-cases built no cases (exit
  5): …` with GND's sentence about the extra. The stand-in `gnd` can now refuse `synth`
  (`synth_exit`, `synth_stderr`). Three tests hold the guard: the refusal skips; four
  other outcomes do not; a refusal beside a wrong example does not. `rules_check.py` is
  unchanged.
- **Issue 42, `tests/test_phase_selection.py`** (new, 128 lines, 10 functions, 16
  cases). The plugin as a project's `conftest.py`; each test checks which tests pytest
  kept. The plugin is unchanged: it passed every case on the first complete run. Two
  older tests in `tests/test_tools.py` already ran the plugin; they stay, and the index
  entry `phase.test_selection` now lists both files.
- **Issue 41, `devtools/from_gsd.py`.** Its own `OTHER_PLANS` and its walk are gone; it
  loads `sync.py` by path and `other_plans` adapts `sync.other_plans`. `sync.py` is
  unchanged. Two tests: one list serves both; the rows and their order are as before.
- **The index.** `sync.copies` says `distinct_from: migrate.from_gsd` where it said
  `duplicates: devtools/from_gsd.py`; `migrate.from_gsd` notes the load, which the index
  cannot see.

Decisions that survived: D1 (the guard reads the note), D2 (the list lives in
`sync.py`), D4 (one run with a real GND without the extra), D5 (keep the existing tests,
add a file). D3 did not apply: no defect in the plugin was found.

Size, measured against `dd0e7a1`: `devtools/from_gsd.py` +7 -10; `tests/test_tools.py`
+85 -4; `tests/test_phase_selection.py` +128; `tests/test_from_gsd.py` +18;
`COMPONENTS.md` +4 -3. The spec estimated 35 lines of source and 215 of tests.

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_phase_selection.py tests/test_from_gsd.py tests/test_sync.py tests/test_own_index.py -q
    290 passed in 121.31s (0:02:01)
    $ uv run --no-project --with pytest python -m pytest tests -q
    471 passed in 197.02s (0:03:17)
    $ python3 devtools/build_plugins.py --check
    (no output; exit 0)
    $ python3 devtools/release_plugins.py status
    version in the tree: 0.1.6
    released: 0.1.2 (plugins-v0.1.2)
    28 plugin file(s) changed since plugins-v0.1.2
    0.1.6 is ready: after the merge, run `release_plugins.py tag` on main
    (exit 1, as at the baseline)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base dd0e7a1 --strict
    changed against dd0e7a1 (dd0e7a1): 13 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py review   (two of its groups)
    ## The same public name in two or three components (a duplicate?) (0)
    ## Components with no tests listed (0)
    $ GND_COMMAND="uvx -q --isolated --from get-nick-done==0.4.0 gnd" uv run -q --no-project --with pytest python -m pytest tests/test_tools.py -q -rs -k suggestions_and_generated
    SKIPPED [1] tests/test_tools.py:1361: this GND lacks its synth extra: uv tool install --force 'get-nick-done[synth]'
    1 skipped, 82 deselected in 17.72s

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/issue-sweep/notes/phase-1-spec.md, as committed at dd0e7a1
    sha256: 2fb05b9132ca30f0615f85abd32a201bfbbdafc4251951edd437c92dd0ebca97
    date: 2026-11-23
    authorization: the owner's "process-milestone issue-sweep auto", for this milestone
    decisions: D1 to D5 of the spec, each as proposed
    instrument: the spec's prose; phase review by review_tool.py, at most r1 and r2
    not covered: pushing, the pull request, merging, tagging, anything posted to GitHub

This is an agent's ruling under the owner's delegation, not the owner's own reading. The
spec has grown since that digest by its appended sections only (implementation findings
and the review round); its digest now is in the evidence list.

## Criteria

| Criterion | Evidence | Met |
|---|---|---|
| P1.1 The stand-in refuses: exit 0, the note, the guard skips | `test_a_gnd_without_its_synth_extra_is_a_note_and_the_guard_skips` | yes |
| P1.2 The guard skips for nothing else | `test_the_guard_skips_for_the_missing_extra_only` (4 cases) and, after r1 F1, `test_the_guard_does_not_hide_a_rule_that_is_wrong` | yes |
| P1.3 Each branch of the plugin has a case | The spec's table B1 to B18 against `tests/test_phase_selection.py`; ten one-line breaks of the plugin each failed at least one case (spec, I5) | yes |
| P1.4 One list | `test_one_list_of_other_planning_tools_serves_both_scripts`; `tests/test_from_gsd.py` and `tests/test_sync.py` otherwise unedited, in the first gate | yes |
| P1.5 `review` prints 0 for both groups | Gate output above | yes |
| P1.6 No file under `plugins/` changes | `git diff --stat dd0e7a1 HEAD -- plugins skills agents` is empty; the build check exited 0 | yes |
| C1 (plan) skipped, not failed, with a real GND without the extra | At `dd0e7a1` in a scratch worktree: `1 failed`. On the head: `1 skipped` (above) | yes |

## Review

One round of the review helper, `--subject phase --base dd0e7a1`, reviewer Codex,
read-only, effort `high`. **One reviewer is one reviewer.**

| Round | Brief | Findings | Blocking | Self-inflicted | Verdict | Repaired at |
|---|---|---|---|---|---|---|
| phase-1-r1 | `1e676581…49af` | 2 | 1 | 0 / 2 | CHANGES_REQUESTED | `1e4d5ff` |

- F1 (blocking): the guard skipped before the exit was looked at, and would have hidden
  a wrong example. F2 (hardening): the plugin tests failed under `PY_COLORS=1`. Both
  were reproduced before they were believed; each has a regression test seen red. The
  ledger has the reproductions.
- The reviewer confirmed: the build check and the strict index check exit 0; `review`
  prints 0 for both groups; no change under `plugins/`, `skills/` or in `sync.py`; the
  old and new readers of planning tools agree for all 256 combinations of the eight
  signs; its in-memory probes of the plugin match S1 to S7 and S9.
- It could not rerun the suites, the breaks of the plugin or a real GND, by the
  read-only rule. Those are this record's evidence, not the reviewer's.
- `review.md` was passed through `review_tool.py sanitize` (2 paths) and says so on its
  first line; `run.json` holds the original's digest,
  `12ae92ec35a750b4b194659687ee08318ab34995d16219d3ef0b11c48b6218d6`.
- Round 2 was not run: the repairs are a few lines of test code, each held by a test.

`review_tool.py status` reports as `unreviewed`, since each changed after the round read
it: `tests/test_tools.py`, `tests/test_phase_selection.py`,
`.devtools/components/COMPONENTS.md` and the spec. No review opinion covers the repairs.

## Refactoring review

Refactors executed: one, and it is the phase's own deliverable. `from_gsd.other_plans`
re-implemented `sync.other_plans` line for line; it now calls it.

Seen and deferred: none. The phase touched test helpers and one function. The two older
plugin tests and the new file each build a pytest project in their own way; they test
different things (the plugin as synced, and the plugin alone) and share no code worth
moving.

## Boundary -- what this phase does NOT establish

- That the guard matches any GND but 0.4.0. It reads GND's own sentence; a release that
  rewords it makes the test fail again, which is loud.
- Anything about the plugin under a pytest other than the one `uv` resolved here
  (9.2.0; the reviewer's probes used 9.0.3).
- That `from_gsd.py` prints the same for every project. The existing tests and the
  reviewer's 256 combinations cover the list and the walk; no real GSD project was run.
- The index still cannot see `from_gsd.py` loading `sync.py` (issue 39, out of the
  milestone). The entries say it by hand.
- The review repairs carry no review opinion. One reviewer is one reviewer, and it ran
  no test.
- Every run was on macOS. Nothing is pushed, and no issue was commented on or closed.

## Open questions

- Q2 of the plan (issue 31's failure not reproduced) is closed here: reproduced at
  `dd0e7a1` with an isolated GND (spec, I3).
- The first by-hand command, `uvx --from …` without `--isolated`, reused the installed
  GND's environment and tested nothing (spec, I2). A plan repair for the close: section 9
  of the plan and D4 of the spec name the command without `--isolated`.
- Issue 42 said no test runs the plugin; two did. Whether the issue is closed as fixed
  or answered is the owner's, at the close.

## Refuted premises

- "The existing test is the one test of the plugin" (spec, section 6.2, after r1 F5 of
  the plan review). Refuted by `tests/test_tools.py`,
  `test_phase_numbers_above_99_work_like_any_other`, SHA-256 of the file
  `ad2bdb1eaf83f166dd409d04c2f3e40eb96b982aec9c9dec58995e34a174d840`: two tests ran it.
- "`uvx --from get-nick-done==0.4.0 gnd` is a GND without the extra" (spec, D4). Refuted
  by the run recorded in the spec's I2: 22 passed, none skipped, and `faker` importable.
