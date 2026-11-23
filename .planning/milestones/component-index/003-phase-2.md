---
milestone: component-index
station: "phase-2"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-2
date: 2026-11-21
gates:
  - command: "ruling: delegated (auto=true) approved .planning/milestones/component-index/notes/phase-2-spec.md sha256 da85aa946edfe4fd8435cfd6e06518db2ef22e2f4b02d8965c5e4f7c1247df16, and plan amendment a3, plan sha256 3cc5eb4924e69fb5584fd2613a0246718a27b5b3dd9e58f34afebabb97b886a9"
    exit: "n/a -- ruling"
  - command: "uv run --no-project --with pytest python -m pytest tests/test_tools.py -q"
    exit: 1
    output: "FAILED tests/test_tools.py::test_suggestions_and_generated_cases_with_newer_gnd -- 1 failed, 76 passed in 66.73s (0:01:06)"
    note: >-
      The spec's G1 expects exit 0 apart from the R5 case; the R5 case is the only failure.
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 1
    output: "FAILED tests/test_tools.py::test_suggestions_and_generated_cases_with_newer_gnd -- 1 failed, 320 passed in 134.22s (0:02:14)"
    note: >-
      The spec's G2 expects exactly this: 1 failure, the R5 case, the known red proven at
      c9648dd (001-plan.md, boundary).
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
    output: "(no output)"
slow_cadence:
  command: "uv run --no-project --with pytest python -m pytest tests -q"
  trigger: "n/a -- the spec mandates the full suite for this phase, and it ran (G2)"
  reason: "this repository has no broader lane than the full suite"
evidence:
  - path: skills/components/scripts/components_index.py
    sha256: 3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14
  - path: plugins/dvt-milestone/skills/components/scripts/components_index.py
    sha256: 3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14
  - path: tests/test_tools.py
    sha256: 8453af3f28b0c1fa31d35f563fa71b5e99409253488bee247d53fa574ef31df8
  - path: skills/components/SKILL.md
    sha256: 1232e277b0b9b116325956b0084027963491aa02065d441392698eb5013d1e10
  - path: skills/components/references/build.md
    sha256: f01ae0b3865c4f5028a2075b988a3a84ec4665436d2120a7df97a1c82562fb32
  - path: docs/components.html
    sha256: cee6abaf6d2eb176487a16ef48f6d3c5c0953a757b772b46793c02b9ec31a976
  - path: docs/adopt.html
    sha256: 82fbf18d3138cee2acecc760218b02dd5ec97fb8dc326b85da4e1f932bbe2e37
  - path: examples/phase-project.devtools.toml
    sha256: af7c9ba367e74745fbe582fdd4d2788ca85b46aebd8ff512b638d6aadbedeae1
  - path: devtools/PLUGIN_VERSION
    sha256: 800cf1c0392b24de7c0a1c6ea6778ecb433dec71c49a150bce96a98477527b2f
  - path: .planning/milestones/component-index/notes/phase-2-spec.md
    sha256: da85aa946edfe4fd8435cfd6e06518db2ef22e2f4b02d8965c5e4f7c1247df16
  - path: .planning/milestones/component-index/notes/component-index-plan.md
    sha256: 3cc5eb4924e69fb5584fd2613a0246718a27b5b3dd9e58f34afebabb97b886a9
  - path: .planning/milestones/component-index/notes/reviews/phase-2-r1/BRIEF.md
    sha256: 5803d2e106ec7ac34e3c88699d37c4118367cadc4b69bcf43f7e73667a72f4d0
  - path: .planning/milestones/component-index/notes/reviews/phase-2-r1/review.md
    sha256: 922431c27090b0dd425447d4c42a328ddcf23a67923e39b5945333b784df39c9
  - path: .planning/milestones/component-index/notes/reviews/phase-2-r1/FINDINGS.md
    sha256: caca54f89a9bfea201e468a36f6a5d599bf315f789bbacff181817c6a58918c7
  - path: .planning/milestones/component-index/notes/reviews/phase-2-r2/BRIEF.md
    sha256: d2cafd834ca66cd8d1351c5d95da99c4ef2902ac5b1f688d9cfe55b3982d9737
  - path: .planning/milestones/component-index/notes/reviews/phase-2-r2/review.md
    sha256: 032db4a2cb66193dca5276f8fbb647ea49c5b2f4a400ae9b9a889ed84eafe1e1
  - path: .planning/milestones/component-index/notes/reviews/phase-2-r2/FINDINGS.md
    sha256: 4d56592a573d8afe0cc0be15e31cbac77f2e635f8c9f53f2a201ad9754a660ff
---

# Claim

`pytest tests/test_tools.py` exited 1 with 1 failed and 76 passed; the full suite exited 1
with 1 failed and 320 passed. In both the failure is the known R5 case the spec expects.
`build_plugins.py --check` exited 0. All three ran on the tree committed as `882aa52`,
which implements phase 2 of the plan (`count_extra_dirs`) on a branch stacked on phase 1's
(plan amendment a3).

## Spec gate (verbatim)

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/component-index/notes/phase-2-spec.md
    sha256: da85aa946edfe4fd8435cfd6e06518db2ef22e2f4b02d8965c5e4f7c1247df16
    date: 2026-11-21
    authorization: the owner's invocation "/dvt-milestone:process-milestone auto" in this
      session, for component-index; after phase 1's pull request was opened, the owner
      said "go on"
    decisions:
      D1 a new key, count_extra_dirs                          -- as proposed (A)
      D2 the adopt page's survey capture                      -- (d), not the proposed (a)
      D3 the survey writes count_extra_dirs as TODO           -- as proposed
    plan amendment a3: phase 2's branch is cut from phase 1's open branch (24b2d83), and
      its pull request names that branch as its base
    instrument: prose, with T1 to T10 written first and seen to fail
    committed: ca6712a

This is an agent's ruling under the owner's delegation. It is not the owner's own reading
of the spec. D2 departs from the proposed reading: the spec, section 12, gives the reason.
The capture depends on the demo project's own older copies, which are gone and recorded
nowhere, so a retake would have had to invent them.

## What shipped

`skills/components/scripts/components_index.py`, 37 lines added and 7 removed (estimated:
about 25). The four repairs of the two review rounds account for the difference.

- **Setting.** `count_extra_dirs`, default `false`, with a comment in `DEFAULT_SETTINGS`.
  `load_settings` refuses a value that is not a boolean.
- **`counted_modules(root)`** (new): the package's modules in `sources()` order, then with
  the setting on each extra folder's, in the order of `extra_source_dirs`, each path once.
  `counted_dirs()` (new) names the folders for the coverage line.
- **Sites.** `coverage()`, so `stats`, `--check --strict` and `draft` follow; `changed`'s
  new-file check; `review`'s "Modules with no component"; and `show`'s module sections.
  The import graph is untouched.
- **`draft`.** A module's folder is found by comparing paths under the project root, so
  `tools`, `./tools`, `tools/` and an absolute path all work. An extra folder's area is its
  last name, cleaned to an id. The package's area is `PACKAGE.lower()`, as before.
- **Text.** `skills/components/SKILL.md` (the settings line), `references/build.md`
  (step 1), `docs/components.html` (one sentence where strict coverage is described), the
  commented line in `examples/phase-project.devtools.toml`, and the caption of
  `docs/adopt.html`'s survey capture (D2 (d)). The capture itself is unchanged.
- **Release.** `release_plugins.py bump`: 0.1.4 to 0.1.5, with `plugins/` rebuilt by it and
  by `build_plugins.py` after each repair.

`tests/test_tools.py`, 116 lines added (estimated: about 90). These are T1 to T10 of the
spec, with T2b inside T2 and T4 parametrized, plus three regression tests from the review
rounds: 14 test cases where `ca6712a` has none of them.

## Criteria, measured

| Criterion | Measurement |
|---|---|
| P2.1 With the setting on, `stats`, `--check --strict`, `draft`, `changed` and `review` name a module in an extra folder | T2 exit 1, `no component: tools/report.py`; T3 `### tools.report`; T4 true, exit 1, `fail: no component: tools/new.py (new file;`; T5 `## Modules with no component (1)\ntools/report.py`; T6 `coverage: 1/2 src/widget, tools modules assigned`; T9 `## tools/report.py (` |
| P2.2 With the setting off or absent, every existing test exits as on main | G2: the only failure is R5. T1, T10, T4 false, and the `widget_` regression test pin the unchanged behaviour |
| P2.3 `draft` stubs a module in an extra folder and does not raise | T3, and the three folder spellings of `test_draft_takes_a_folder_written_with_a_leading_dot` |
| P2.4 `build_plugins.py --check` exits 0 | G3, exit 0 |

Run against the code at `ca6712a`, from a throwaway worktree holding this phase's first
test file: 8 of the 10 new cases failed, and the two that passed were T1 and T10, which pin
unchanged behaviour. The three regression tests were each seen failing on the code before
their repair; the ledgers hold the messages.

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests/test_tools.py -q
    FAILED tests/test_tools.py::test_suggestions_and_generated_cases_with_newer_gnd
    1 failed, 76 passed in 66.73s (0:01:06)
    exit 1

    $ uv run --no-project --with pytest python -m pytest tests -q
    FAILED tests/test_tools.py::test_suggestions_and_generated_cases_with_newer_gnd
    1 failed, 320 passed in 134.22s (0:02:14)
    exit 1

    $ python3 devtools/build_plugins.py --check
    exit 0

The first gate ran on the bytes committed as `882aa52`, before the commit. The second ran
after it: `git diff HEAD | shasum -a 256` gave the empty-input hash, `e3b0c442…b855`, so
nothing uncommitted was under test.

## Verification-selection ledger (as run)

| Obligation | Disposition | Result |
|---|---|---|
| O1, O3, T2 to T9 | run | `tests/test_tools.py`, the new cases pass |
| O2, T1, T10 | run | the full suite, 1 failed (R5), 320 passed |
| O4 | run | `build_plugins.py --check`, exit 0 |
| O5, O6 | run by inspection, and T7 | the four text sites name the setting and 0.1.5; T7 gives `count_extra_dirs must be true or false` |
| O7 | ruled (D2 (d)) | the capture is kept byte for byte, and its caption updated. A scratch survey of a project holding the `ca6712a` components skill printed `count_extra_dirs = "TODO"  # default false (an empty value is valid)`, and `compare` named it before `verb_list`, as the caption says. That output lives outside history |
| O8 | inspection | no gate runs `components_index.py` against this repository |
| The known red (R5) | inherit | `001-plan.md`, boundary. Its cause, GND's install, is unchanged by this phase |

## Review

Two rounds of the review helper, `--subject phase --base ca6712a`, reviewer Codex
(read-only, effort `high`). **One reviewer is one reviewer.** By the brief's read-only rule
the reviewer did not run pytest. It reproduced with in-memory probes.

| Round | Brief | Findings | Blocking | Self-inflicted | Verdict |
|---|---|---|---|---|---|
| r1 | `5803d2e1…f0d4` | 2 | 1 | 0 / 2 | CHANGES_REQUESTED |
| r2 | `d2cafd83…9d37` | 2 | 2 | 2 / 2 | CHANGES_REQUESTED |

All 4 findings were reproduced and fixed. Each code finding has a regression test that was
seen failing before its repair. After r1 the budget was declared as one more round. After
r2 the stop rule fired at 2/2 self-inflicted, and the budget was spent. The r2 repairs
(`882aa52`) therefore carry no review opinion: `review_tool.py status` lists
`components_index.py` (all three copies) and `tests/test_tools.py` as changed since r2
read them.

## Refactoring review

None executed. No candidate came up worth deferring.

- The phase adds one function used at four sites and leaves the import graph alone.
- `review` builds `owners` over the package and the no-component group over
  `counted_modules`. That keeps the other groups exactly as at `ca6712a`, and it is
  deliberate: plan section 7 keeps extra folders out of the import-graph leads.

## Boundary -- what this phase does NOT establish

- The r2 repairs carry no review opinion. Two single-seat rounds are one reviewer's reading.
- With the setting absent, an absolute `package_dir` now gives `draft` stubs. By reading
  the code at `ca6712a`, that version exits 1 there (`Path.relative_to` raises, and `main`
  prints it); this was not run. If so, it is a change of default behaviour, from a failure
  to a result. No test pins it, and no review read it.
- The adopt page's survey capture is not a retake. It shows what that day's commands
  printed, and its caption says what 0.1.5 prints besides (D2 (d)).
- Phase 1 is not merged, so this branch carries phase 1's commits under it. Its pull request
  names phase 1's branch as its base (amendment a3). The owner merges phase 1 first, then
  this, and tags `plugins-v0.1.4` and `plugins-v0.1.5`; nothing here tags or publishes.

## Open questions

- Q6 (new). The plan's claim C5 for phase 2 in the round briefs, "the import graph stays
  inside package_dir", is not quite so: r1 found that `module_graph` already holds modules
  outside `package_dir` that the catalog names, at `ca6712a` and after. The phase changes
  nothing there. Repair the wording of plan section 7 at the close.

## Refuted premises

- "`docs/components.html`: the same sentence where the page names the settings" (spec,
  section 6, Text). The page names no setting. The sentence was first left out on that
  ground, and r1 F2 showed the place it belongs: the paragraph on strict coverage.
- D2 (a), "re-make a demo project to the notes' description and retake that one block"
  (spec, section 7): the block depends on the demo's own older copies, which the notes do
  not describe (spec, section 12).
- "The plan's phases are cut from main after the previous phase merges" (plan, section 8)
  did not hold while phase 1's pull request waited for the owner. Amended as a3.
