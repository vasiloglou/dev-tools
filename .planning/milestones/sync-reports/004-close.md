---
milestone: sync-reports
station: "close"
skill: process-milestone (dvt-milestone 0.1.3)
scope: close
date: 2026-11-23
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "431 passed in 267.15s (0:04:27)"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py status .planning/milestones/sync-reports/notes/reviews"
    exit: 1
    note: "exit 1 because files are unreviewed after their last repair; listed below, as the helper intends"
  - command: "ruling: delegated (auto=true) approved .planning/milestones/sync-reports/notes/sync-reports-plan.md sha256 d89a7175429c521932aba262848aff0989044355590c50f80d7a5f52a1936ad9"
    exit: "n/a -- ruling"
evidence:
  - path: .planning/milestones/sync-reports/notes/sync-reports-plan.md
    sha256: d89a7175429c521932aba262848aff0989044355590c50f80d7a5f52a1936ad9
  - path: .planning/milestones/sync-reports/README.md
    sha256: 4fa4723b7a2ed0fb3c5b1a6470173c396b02853a0bde7d94a3e98a2d2a3a1cf8
  - path: devtools/sync.py
    sha256: 066dc017f29caf02abde98ea14a43633ae1820b7a7f4ae92004bb1d968da224b
  - path: tests/test_sync.py
    sha256: 2b381a9ab70aa88f73018db4c0c20d12412fe7a68fd824dcfbe9e54a7e235421
  - path: README.md
    sha256: 914ffdefc044d530c3042298f4d3d4ebc6be111abacc6311e4a75c7b294f4be4
  - path: docs/adopt.html
    sha256: 7299f8ddbb8cbc6e42816c6dc108fc11f398f3447aa5ba8649fcc8ea58c91117
  - path: skills/adopt-devtools/SKILL.md
    sha256: 6ef26eb4aee3e03fd181c70cfa2c648735ffa2e2cbb2640766f92ad9ef280b16
  - path: examples/milestone-project.devtools.toml
    sha256: 7221089d737f9e94711e1da7eed26a1140d4e5e50d41b139e376f5351945a2e3
  - path: examples/phase-project.devtools.toml
    sha256: 71caa4a90c9d365c5a9e77dde8267fa6a74a962ca9c085bc82074b58647b8769
  - path: .planning/milestones/sync-reports/001-plan.md
    sha256: e6fc8c03f5e86b35af37fb6fe587afb90bcb2e44ec727399e8a5592eafdb5375
  - path: .planning/milestones/sync-reports/002-phase-1.md
    sha256: 481261f9099b2fb27bc838f3bbaabf654e57059421fe3ed04edb34b5438cc42f
  - path: .planning/milestones/sync-reports/003-phase-2.md
    sha256: b8cd5012a85b25d8c155a70fa8aefabc58702e21b88e54e2b65da30533a08f1a
  - path: .planning/milestones/sync-reports/notes/reviews/close-r1/BRIEF.md
    sha256: da97ba222e6d951fe9c87ddbe0fba68b1fc34d80eedd76dd1b95c80994f213be
  - path: .planning/milestones/sync-reports/notes/reviews/close-r1/review.md
    sha256: 5447fa50b4579c2311d884970994bf9732692a2f9702a5dce4e944b78513b34a
  - path: .planning/milestones/sync-reports/notes/reviews/close-r1/FINDINGS.md
    sha256: d0c35b3517c946a47699da5e2b3aa17ebe7692660bba05125def245f8abc2d80
---

# Claim

The milestone `sync-reports` is closed by delegated approval (auto=true): its two phases
are recorded, the full suite exited 0 at d7296f6, the close's head before this record, and each completion predicate
C1 to C7 is met as the table below says, with the residuals and the unreviewed bytes
listed.

## Completion predicates

| Predicate | Evidence | Met |
|---|---|---|
| C1 The observed case as a test; `apply --dry-run` 0 naming `review-pr`, `check` 0 with the count, `check --strict` 5 | `test_the_observed_case_a_missing_named_skill_and_a_receipt_older_than_the_source`; the by-hand run in `002-phase-1.md` (exits 0, 0, 5) | yes |
| C2 Every test of `tests/test_sync.py` at `811b4a3` exits as there, unedited | The file at `811b4a3` is an unchanged prefix of the file at the close (close review r1, C2); the suite exited 0 | yes |
| C3 `check --receipt-only` prints main's lines, reads no source, starts no git | T16 of phase 1, with `subprocess.run` made to raise; confirmed by the close review against main's code | yes |
| C4 Behind: the upstream's files, the checkout unchanged; own work as it is with a warning; a failed fetch a warning, exit 0 | Phase 2 T1 to T17 and the regression tests; the by-hand run in `003-phase-2.md` | yes, with local upstreams only (boundary) |
| C5 The suite, the plugin check and the index check exit 0 | Gates above | yes |
| C6 The README, the site, the examples and the adopt skill describe the behaviour; changed captures are real output | Phase records; close review r1 F2 repaired at `0ebf855` | yes, except the walk-through frames of Q4 (residual) |
| C7 A close record after the close review | This record; `notes/reviews/close-r1` | yes |

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests -q
    431 passed in 267.15s (0:04:27)
    $ python3 devtools/build_plugins.py --check
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py status .planning/milestones/sync-reports/notes/reviews
    .planning/milestones/sync-reports/notes/reviews/plan-r1: plan review by codex (codex default), done, 6 finding(s) in the ledger
    .planning/milestones/sync-reports/notes/reviews/phase-1-r1: phase review by codex (codex default), done, 5 finding(s) in the ledger
    .planning/milestones/sync-reports/notes/reviews/phase-2-r1: phase review by codex (codex default), done, 5 finding(s) in the ledger
    .planning/milestones/sync-reports/notes/reviews/phase-2-r2: phase review by codex (codex default), done, 4 finding(s) in the ledger
    .planning/milestones/sync-reports/notes/reviews/close-r1: close review by codex (codex default), done, 2 finding(s) in the ledger
    reviewed: .devtools/components/COMPONENTS.md (.planning/milestones/sync-reports/notes/reviews/phase-2-r1)
    unreviewed: .devtools/components/modules/_root.md (changed since .planning/milestones/sync-reports/notes/reviews/phase-2-r2 read a6d3c83ff71c)
    reviewed: .devtools/project.md (.planning/milestones/sync-reports/notes/reviews/plan-r1)
    reviewed: .planning/PROJECT.md (.planning/milestones/sync-reports/notes/reviews/plan-r1)
    reviewed: .planning/milestones/sync-reports/001-plan.md (.planning/milestones/sync-reports/notes/reviews/close-r1)
    reviewed: .planning/milestones/sync-reports/002-phase-1.md (.planning/milestones/sync-reports/notes/reviews/close-r1)
    reviewed: .planning/milestones/sync-reports/003-phase-2.md (.planning/milestones/sync-reports/notes/reviews/close-r1)
    unreviewed: .planning/milestones/sync-reports/README.md (changed since .planning/milestones/sync-reports/notes/reviews/phase-2-r1 read 196f8c6c3385)
    reviewed: .planning/milestones/sync-reports/notes/phase-1-spec.md (.planning/milestones/sync-reports/notes/reviews/close-r1)
    reviewed: .planning/milestones/sync-reports/notes/phase-2-spec.md (.planning/milestones/sync-reports/notes/reviews/close-r1)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/BRIEF.md (.planning/milestones/sync-reports/notes/reviews/phase-2-r1)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/FINDINGS.md (.planning/milestones/sync-reports/notes/reviews/phase-2-r1)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/brief.json (.planning/milestones/sync-reports/notes/reviews/phase-2-r1)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/diff.patch (.planning/milestones/sync-reports/notes/reviews/phase-2-r1)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/review.md (.planning/milestones/sync-reports/notes/reviews/phase-2-r1)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-1-r1/run.json (.planning/milestones/sync-reports/notes/reviews/phase-2-r1)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/BRIEF.md (.planning/milestones/sync-reports/notes/reviews/phase-2-r2)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/FINDINGS.md (.planning/milestones/sync-reports/notes/reviews/phase-2-r2)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/brief.json (.planning/milestones/sync-reports/notes/reviews/phase-2-r2)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/diff.patch (.planning/milestones/sync-reports/notes/reviews/phase-2-r2)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/review.md (.planning/milestones/sync-reports/notes/reviews/phase-2-r2)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-2-r1/run.json (.planning/milestones/sync-reports/notes/reviews/phase-2-r2)
    reviewed: .planning/milestones/sync-reports/notes/reviews/phase-2-r2/diff.patch (.planning/milestones/sync-reports/notes/reviews/phase-2-r2)
    unreviewed: .planning/milestones/sync-reports/notes/sync-reports-plan.md (changed since .planning/milestones/sync-reports/notes/reviews/close-r1 read 8dc8f11e9aa1)
    reviewed: AGENTS.md (.planning/milestones/sync-reports/notes/reviews/plan-r1)
    reviewed: CONTRIBUTING.md (.planning/milestones/sync-reports/notes/reviews/plan-r1)
    unreviewed: README.md (changed since .planning/milestones/sync-reports/notes/reviews/close-r1 read db3ed84d9df6)
    unreviewed: devtools/sync.py (changed since .planning/milestones/sync-reports/notes/reviews/close-r1 read 56759e3a89f2)
    unreviewed: docs/adopt.html (changed since .planning/milestones/sync-reports/notes/reviews/close-r1 read 077343d19932)
    reviewed: examples/milestone-project.devtools.toml (.planning/milestones/sync-reports/notes/reviews/close-r1)
    reviewed: examples/phase-project.devtools.toml (.planning/milestones/sync-reports/notes/reviews/close-r1)
    unreviewed: skills/adopt-devtools/SKILL.md (changed since .planning/milestones/sync-reports/notes/reviews/close-r1 read 8c735a4db210)
    unreviewed: tests/test_sync.py (changed since .planning/milestones/sync-reports/notes/reviews/close-r1 read 668c3b0d1ad7)

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/sync-reports/notes/sync-reports-plan.md (repaired at the close)
    sha256: d89a7175429c521932aba262848aff0989044355590c50f80d7a5f52a1936ad9
    date: 2026-11-23
    authorization: the owner's "Milestone, auto=true" for sync-reports, relayed 2026-11-23 (001-plan.md)
    scope: the close ruling of sync-reports and the plan repairs below
    not covered: pushing, opening the pull request, merging, tagging, releasing

This is an agent's ruling under the owner's delegation, not the owner's own reading.

## Records

- `001-plan.md`: the plan gate.
- `002-phase-1.md`: the unit report, `declined`, `shipped`, `check` against a source,
  `--receipt-only`, `--strict`.
- `003-phase-2.md`: the sync reads the latest dev-tools.

## Reviews

| Round | Subject | Findings | Blocking | Self-inflicted | Repaired at |
|---|---|---|---|---|---|
| plan-r1 | the plan and the phase 1 spec | 6 | 3 | 0 / 6 | `e6c3e2b` |
| phase-1-r1 | phase 1 | 5 | 2 | 0 / 5 | `2120090` |
| phase-2-r1 | phase 2 and the phase 1 repairs | 5 | 2 | 0 / 5 | `90dca94` |
| phase-2-r2 | the phase-2-r1 repairs | 4 | 1 | 4 / 4 | `e6a5c28` (the stop rule fired) |
| close-r1 | the milestone's evidence | 2 | 1 | 0 / 2 | `0ebf855` |

Every round had one seat, Codex, read-only, effort `high`. One reviewer is one reviewer.
Every finding was reproduced before it was believed; every code finding has a test that
failed on the reviewed code. 22 findings in all, 22 fixed.

`review_tool.py status` lists, as `unreviewed`, each file changed after the last round
that read it (output above). Those bytes carry no review opinion: the repairs of
phase-2-r2 and of close-r1, the plan's repairs and status lines, and the records.

## Plan repairs

Made at the close, each with the prior wording kept at its site:

- Section 2, phase 2 table: the upstream is read from git's tree, not with `git
  archive` (`003-phase-2.md`; phase-2-r1 F1, F3).
- Section 3, "What the code depends on": `shutil` and `ls-tree`/`cat-file`, not
  `tarfile` and `git archive` (same source).
- Section 10: Q4 added (`002-phase-1.md`).

## Question sweep

| Question | Disposition |
|---|---|
| Q1 A named unit taken into another folder than the file that names it | Residual, accepted. The report says "taken" for a unit taken anywhere. A follow-up for the owner to choose; it needs a rule for which taken copy a `../` path means when both workflows ship a folder of that name |
| Q2 A unit taken for `.claude/skills` and not for `.codex/skills` | Residual, accepted, for the same reason as Q1 |
| Q3 Run the fetched `sync.py` when the checkout is behind | Deferred to the owner: it runs code the owner has not pulled. Until then the sync says on standard error when the tool that runs differs from the one read (K6) |
| Q4 The adopt walk-through frames of `docs/adopt.html` come from a demo project not in the repository | Residual, accepted. Retaking them needs the demo project rebuilt; a follow-up |

## Release

No file under `plugins/` changed (`build_plugins.py --check` exited 0), and
`skills/adopt-devtools` is in no plugin: this milestone needs no plugin release of its
own. `devtools/sync.py` reaches a project from a dev-tools checkout, so a project takes
it when its checkout has the merge.

## Boundary -- what this close does NOT establish

- Nothing is pushed, no pull request is open, nothing is merged or tagged: the owner's,
  not delegated.
- No real downstream project was synced with this code; the brief's figures for one (62
  files, 21 to update) stay an inherited claim. The observed case was rebuilt from
  dev-tools at `c9648dd` in a scratch project.
- No test or run reached a network remote; fetch behaviour on a network is covered by a
  failing local remote and a simulated timeout.
- The bytes `review_tool.py status` lists as unreviewed carry no review opinion.
- Each review was one reviewer's reading, without pytest.

## Open questions

- Q1 to Q4, as swept above.
