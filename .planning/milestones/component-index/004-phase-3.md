---
milestone: component-index
station: "phase-3"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-3
date: 2026-11-21
gates:
  - command: "ruling: delegated (auto=true) approved .planning/milestones/component-index/notes/phase-3-spec.md, committed at f25d3a5"
    exit: "n/a -- ruling"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py write"
    exit: 0
    output: "(no output)"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
    output: "(no output)"
  - command: "test ! -e .devtools/components/unassigned-baseline.txt"
    exit: 0
    output: "(no output)"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py review"
    exit: 0
    output: "## Components that import each other (0); ## Flow steps that no earlier step imports (wrong order, or reached another way?) (4); ## Entries marked as checked in part (10)"
    note: >-
      The four flow steps are the run-time loads the three subsystems' notes state
      (spec, section 6, and IF1).
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py search <each case of search-cases.md>"
    exit: 0
    output: "9 of 9 cases put the expected component first; the negative case printed 'no component matched'"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
    output: "(no output)"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "321 passed in 147.63s (0:02:27)"
    note: >-
      The first full-suite run of the milestone with no failure. The known red R5 passes
      since this machine's GND was installed with its synth extra (section "What changed
      on this machine"); its skip guard is vasiloglou/dev-tools#31.
slow_cadence:
  command: "uv run --no-project --with pytest python -m pytest tests -q"
  trigger: "n/a -- the spec mandates the full suite for this phase, and it ran (G7)"
  reason: "this repository has no broader lane than the full suite"
evidence:
  - path: .devtools/components_index.settings.json
    sha256: 56717af02b363be6354f9fc760ea2a8e56151821c33bfa58342296d1adad6893
  - path: .devtools/components/COMPONENTS.md
    sha256: 62adb3fd8137e57fa1c0623f19da5ed7c0c032044071baec11908701009546b0
  - path: .devtools/components/graph.md
    sha256: 3d3df2e0ad8132479eee1a84bff3f96280856e5fd9a61f8477914c64591a49b5
  - path: .devtools/components/modules/_root.md
    sha256: a37b3a8d191d88feb586df3d33450981e6db68e2b6970cba9b5d5548aab1b9db
  - path: .devtools/components/modules/skills.md
    sha256: da944750555d7f475ad63363950f00d9645eb75cdc92ec09f3c8f195b1a48f0f
  - path: .devtools/components/search-cases.md
    sha256: 876fab2dc57cca4dca143346783934556b2caadaf0b3d4415aa1caab616a5453
  - path: .devtools/components/REVIEW.md
    sha256: 507255a5ecfb25380cd6a6c2626baf285c47ebfffa7b04b73e71184882593c09
  - path: .planning/milestones/component-index/notes/phase-3-spec.md
    sha256: cb2825bc1b2da14c15859b9834766d0b8d22105c33742c9313556d78b5cf6e7a
  - path: .planning/milestones/component-index/notes/reviews/phase-3-r1/BRIEF.md
    sha256: 5cce6af1b08f3c2c0d4db0adab9719c1d09604fe14e8c70050c2edeecb86e953
  - path: .planning/milestones/component-index/notes/reviews/phase-3-r1/review.md
    sha256: 660eec4cc263b2c7cb0d0a3da6e7ffadb3c5d17bc57900d2f9bbad8feb20b10d
  - path: .planning/milestones/component-index/notes/reviews/phase-3-r1/FINDINGS.md
    sha256: f5cecaeabb9036a4027eb9607339e40e85f534f8811b7b2fd6413a8794f066fc
---

# Claim

Run from the repository root at `bdb0287`, the built copy's `write` and `--check --strict`
exited 0 at `coverage: 12/12 devtools, skills modules assigned to components`, with no
baseline file. `review` exited 0 with no components that import each other, and its flow
group lists only the stated run-time loads. Each of the 9 search cases puts its component
first, and the negative case matches nothing. `build_plugins.py --check` and the full
suite exited 0. The tree is phase 3 of the plan, on a branch stacked on phase 2's (plan
amendment a3).

## Spec gate (verbatim)

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/component-index/notes/phase-3-spec.md
    committed: f25d3a5, sha256 bd9470e3f60b6792333b501cd009e5af265bfecf2d93ae5adc86c7f18d3a5cf9
    date: 2026-11-21
    authorization: the owner's invocation "/dvt-milestone:process-milestone auto" for
      component-index, and the owner's "go on" after phase 2's pull request was opened
    decisions:
      D1 script_path names the built copy                       -- as proposed (A)
      D2 one component per module, 12                           -- as proposed (A)
      D3 three subsystems, where one script runs another        -- as proposed (A)
      D4 reading depth, with checked: partial where not in full -- as proposed (A)
    instrument: prose, with the search cases as the corpus, written before the entries

This is an agent's ruling under the owner's delegation, not the owner's own reading. The
spec then gained IF1 (r1 F2), with its earlier wording kept, at `bdb0287`: the binding
SHA-256 above is the approved bytes; the evidence list holds the amended ones.

## What shipped

All under `.devtools/`; no file under `skills/`, `agents/` or `plugins/` changed, so there
is no version bump.

- `components_index.settings.json`: `package_dir: devtools`, `import_prefix: devtools`,
  `extra_source_dirs: [skills]`, `count_extra_dirs: true`, `docs_dir: .devtools/components`,
  and `script_path` naming the built copy.
- `components/COMPONENTS.md`: 12 components, one per module (the ids of spec section 6),
  in six groups, and 3 subsystems (`subsystem.release`, `subsystem.rule_check`,
  `subsystem.phase_status`). `sync.copies` records `duplicates: devtools/from_gsd.py`;
  `migrate.from_gsd` records `distinct_from: plugins.release, plugins.build`.
- `components/modules/_root.md`, `modules/skills.md` and `graph.md`, generated by `write`.
- `components/search-cases.md`: the 9 cases and the negative one of spec section 6.
- `components/REVIEW.md`: three suggestions (the duplicated `OTHER_PLANS` and
  `other_plans`; no test for `phase_selection.py`; three large modules) and two
  unconfirmed leads. None was acted on.

1,034 lines of Markdown in all (estimated: about 180 for the catalog, plus the generated
pages).

**Read in full:** `phase.codex_gate` and `phase.test_selection`. **Read in part**
(`checked: partial`, P3.3): `plugins.build`, `plugins.release`, `sync.copies`,
`migrate.from_gsd`, `components.index`, `components.rules`, `handoff.notes`,
`review.rounds`, `phase.state`, `phase.coder_pool`. Each was read through its module
docstring, its command line and its documented functions. For `components.index` and
`handoff.notes`, the parts phases 1 and 2 changed were read too. Each entry's `notes:` says
what was read.

## Criteria, measured

| Criterion | Measurement |
|---|---|
| C1 Every module has a component, with no baseline | G2 exit 0 at `12/12`; G3 exit 0 |
| C2 Each search case puts its component first; the negative case matches nothing | G5: 9 of 9; `no component matched` |
| P3.1 `write`, then `--check --strict`, exit 0 | G1, G2 |
| P3.2 No components importing each other; no unstated flow step | G4: `(0)`; the 4 flow steps are the loads stated in `notes:` |
| P3.3 Every entry read from the code; partial ones listed | Above: 2 in full, 10 in part |

## Gate output (verbatim)

    $ C=plugins/dvt-milestone/skills/components/scripts/components_index.py
    $ python3 $C write                          -> exit 0
    $ python3 $C --check --strict               -> exit 0
    $ test ! -e .devtools/components/unassigned-baseline.txt  -> exit 0
    $ python3 $C review                          -> exit 0
    ## Components that import each other (0)
    ## Flow steps that no earlier step imports (wrong order, or reached another way?) (4)
    ## Entries marked as checked in part (10)
    $ python3 $C stats | head -1
    coverage: 12/12 devtools, skills modules assigned to components; external: none
    $ python3 devtools/build_plugins.py --check  -> exit 0
    $ uv run --no-project --with pytest python -m pytest tests -q
    321 passed in 147.63s (0:02:27)
    exit 0

All ran at `bdb0287`. `git diff HEAD | shasum -a 256` gave the empty-input hash,
`e3b0c442…b855`, so nothing uncommitted was under test. The search cases ran after the
r1 repair: `G5: 9/9 first`, and `no component matched` for the negative case.

## Verification-selection ledger (as run)

| Obligation | Disposition | Result |
|---|---|---|
| O1, O3, O9 | run | G1, G2, G3 |
| O2 | run | G5 |
| O4 | run | G4 |
| O5 | inspection | the `checked:` lines, and `review`'s "checked in part" group, 10 |
| O6 | inspection | `REVIEW.md`; each suggestion's "Checked how" column |
| O7 | inspection | every gate names the built copy |
| O8 | run | `review`'s same-name group printed `(0)` after `distinct_from` and `duplicates` |
| The full suite | run | G7, exit 0 |

## Review

One round of the review helper, `--subject phase --base f25d3a5`, reviewer Codex
(read-only, effort `high`), over the index and all 12 modules. **One reviewer is one
reviewer.** By the brief's read-only rule the reviewer did not run `write` or pytest; it
ran the strict check, `stats`, `review` and the build check, and traced code in memory.

| Round | Brief | Findings | Blocking | Self-inflicted | Verdict |
|---|---|---|---|---|---|
| r1 | `5cce6af1…e953` | 2 | 0 | 0 / 2 | CHANGES_REQUESTED |

Both findings were reproduced by reading the code they cite, and fixed at `bdb0287`. Both
are completeness: an entry that said less than the code does, and a subsystem's notes that
assigned a load to the wrong command. Neither changes a gate. Under
`review-convergence.md`, a round whose findings are all completeness ends the loop, so
there is no r2. The repaired bytes, `COMPONENTS.md` and the spec's IF1, carry no review
opinion.

The reviewer confirmed: 12/12 with each module once and nothing counted under `plugins/`,
`tests/` or `.claude/`; the 9 searches and the negative one; the review groups; every
point of `REVIEW.md`; and, reading them itself, that the two entries without
`checked: partial` are true of their modules. It could not establish whether those two
were first read in full.

## What changed on this machine

On 2026-11-21, with the owner's yes, GND was reinstalled with its `synth` extra
(`uv tool install --force 'get-nick-done[synth]==0.4.0' --with pytest==9.1.1`; it added
`faker 40.36.0`). The known red R5 of records 001 to 003 now passes here. The test's skip
guard, which let it fail rather than skip, is vasiloglou/dev-tools#31, filed the same day
with the owner's yes.

## Refactoring review

None executed. The phase changed no code. What the build noticed is in `REVIEW.md` as
suggestions: one duplicate (small), one module with no test, three large modules. Each is
deferred to the owner, with no target named here; the close sweep names one.

## Boundary -- what this phase does NOT establish

- Ten entries were written from docstrings and command lines, not from every body. They
  are as true as those docstrings, and `review` lists them for rereading.
- Nothing yet keeps the index current: a module added, moved or renamed leaves it stale
  without failing any gate. That is phase 4.
- The r1 repairs carry no review opinion.
- Phases 1 and 2 are not merged. This branch carries their commits under it, and its pull
  request will name phase 2's branch as its base (amendment a3).

## Open questions

- Q7 (new). `REVIEW.md`'s three suggestions: who takes them, and in which milestone. For
  the close sweep.
- Q8 (new). The six copies of `plugin_root`, `checkout_root` and `load_settings` under
  `skills/` were not compared. A `diff` would settle whether they drifted. For the close
  sweep.

## Refuted premises

- Plan section 3, "Three load another script at run time": there are five. `rules_check.py`
  also runs `components_index.py facts`, and `phase_tool.py` runs `coder_pool.py`. The
  spec, section 12, recorded it at the gate. Repair the plan's wording at the close.
- Spec section 6's account of `subsystem.rule_check` (r1 F2): `check --phase` runs the phase
  tool first, and the `importlib` load belongs to `test`. Amended as IF1.
- Records 001 to 003: "the known red R5" is not a property of the code, only of how GND
  was installed here.
