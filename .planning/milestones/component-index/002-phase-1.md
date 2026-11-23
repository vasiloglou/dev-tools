---
milestone: component-index
station: "phase-1"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-1
date: 2026-11-21
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests/test_handoff.py -q"
    exit: 0
    output: "84 passed in 43.82s"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 1
    output: "FAILED tests/test_tools.py::test_suggestions_and_generated_cases_with_newer_gnd -- 1 failed, 306 passed in 153.29s (0:02:33)"
    note: >-
      Plan section 9 expects exactly this: 1 failure, the R5 case. The failure is the known
      red proven at c9648dd (001-plan.md, boundary), with the same cause: GND lacks its
      'synth' extra on this machine.
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
    output: "(no output)"
slow_cadence:
  command: "uv run --no-project --with pytest python -m pytest tests -q"
  trigger: "n/a -- the plan mandates the full suite for this phase, and it ran (the second gate)"
  reason: "this repository has no broader lane than the full suite"
evidence:
  - path: skills/dev-handoff/scripts/handoff.py
    sha256: dbab0519e8689154579ec06bc0894125d08b5244ea738d547b66947537d16a6a
  - path: plugins/dvt-milestone/skills/dev-handoff/scripts/handoff.py
    sha256: dbab0519e8689154579ec06bc0894125d08b5244ea738d547b66947537d16a6a
  - path: tests/test_handoff.py
    sha256: b1c98487f83ee8b84f6e6757329172a538786e359bb3e3233655c863cc138b67
  - path: skills/dev-handoff/references/handoff.md
    sha256: 81ce6d44aa595922f59d8b6d4f5151978d6538b2cd0f64ba5f06bd65c481a4b3
  - path: docs/handoff.html
    sha256: 33880b4fac821bf766c802d81ef25158470d36747b192f02fa410981db24b6a7
  - path: devtools/PLUGIN_VERSION
    sha256: 8a3dad16d348c163566a456fcf650d85d7aeeda5e53d01ee1fa8dc15212915a7
  - path: .gitignore
    sha256: 5b0d7f0ad8bc998c48ee905c533a5dfe728bbb1dc7fb318e1f7e7ab1456c085a
  - path: .planning/milestones/component-index/notes/phase-1-spec.md
    sha256: 77f589b5f47729bcb47626ba93591c111fc305866c699fad838963969f409a9f
  - path: .planning/milestones/component-index/notes/reviews/phase-1-r1/BRIEF.md
    sha256: c8f50889fbda5c75a7ba7f41479bca4b4c38a5b34686c796bf45ee554364c490
  - path: .planning/milestones/component-index/notes/reviews/phase-1-r1/review.md
    sha256: c6c5f22687c7b3f76fb95d8bc8cfa6bf37f6ca2878b98e5e36a9c1c6991150f6
  - path: .planning/milestones/component-index/notes/reviews/phase-1-r1/FINDINGS.md
    sha256: c8faf63ce3990e8513863547309370a116da852a8b6462d8c03d50403079aa5a
  - path: .planning/milestones/component-index/notes/reviews/phase-1-r2/BRIEF.md
    sha256: d0f50d879392cbf653f072c064ae6133a377ef259cb82e4093120c948ebabc02
  - path: .planning/milestones/component-index/notes/reviews/phase-1-r2/review.md
    sha256: cc5044b05a9c187b3dbcd12af8955a5fc55408ecff436badcb0772f77d03bdc5
  - path: .planning/milestones/component-index/notes/reviews/phase-1-r2/FINDINGS.md
    sha256: dec990ecb3676568f6df6a81514e91f1d84f72a170f6d11c73b52591ed175fba
---

# Claim

`pytest tests/test_handoff.py` exited 0 with 84 passed. The full suite exited 1 with 1
failed and 306 passed; the failure is the known R5 case the plan expects.
`build_plugins.py --check` exited 0. All three ran on the tree committed as `4903752`,
which implements phase 1 of the plan (issue 28).

## What shipped

`skills/dev-handoff/scripts/handoff.py`, 68 lines added and 4 removed (estimated: about
25). The spec's amendments IF5 and IF6, each made after a review round reproduced a way
past the earlier rule, account for the difference.

- **`_snapshot_text`.** When more than 25 ignored paths are listed, the snapshot gains one
  line after `- and N smaller path(s)`: `<!-- ignored-rest: [{"path":…,"kind":…},…] -->`,
  holding the paths after the 25th as compact JSON, each `>` written `>`.
  - A path holding a control character is printed JSON-escaped on one line, with
    `, written escaped` at the end of its bullet.
  - A note of 25 ordinary paths or fewer is unchanged.
- **`_ignored_rest`** (new). It returns the rest line's items, or `None` when the line:
  - is absent, or is not JSON;
  - nests too deep to decode;
  - is not a list of `{path: str, kind: "carry" | "large" | "key"}`;
  - has a length other than the `N` of the cut line.
- **`takeover`.**
  - *Where it reads.* The ignored-files section starts at the last line that begins with
    `Files git ignores`.
  - *What it checks.* Every bullet, an escaped one decoded, and every item of a readable
    rest line. A missing key file goes to `missing_keys`, which does not block. Any other
    missing path goes to `missing_ignored`.
  - *`unlisted_ignored`*, always present in the report, is the sum of:
    - `N` for a cut list whose rest line cannot be read;
    - 1 for each run of lines that the snapshot does not write;
    - 1 for each escaped bullet that does not decode.
  - *Ready* requires `unlisted_ignored == 0`.
- **The text report.** One line,
  `ignored paths the note did not list: N  (compare with handoff.py ignored in the old checkout, or handoff.py pull --from-checkout <old checkout>)`,
  printed only when N is above 0.
- **Text.** `skills/dev-handoff/references/handoff.md` (what ready checks) and
  `docs/handoff.html` (one sentence).
- **Release.** `release_plugins.py bump`: 0.1.3 to 0.1.4, with `plugins/` rebuilt by it and
  by `build_plugins.py` after each repair.
- **`.gitignore`** line 7, `notes/` to `/notes/` (plan amendment a2), committed with the
  plan at `ada0d1a`.

`tests/test_handoff.py`, 162 lines added (estimated: about 80): T1 to T12 of the spec,
with T5, T7/T8 and T10 parametrized. That makes 19 test cases where main has none of them.

## Criteria, measured

| Criterion | Measurement |
|---|---|
| P1.1 A missing path after the 25th blocks; a missing key file does not | T1 `missing_ignored == ["out25/"]`, `ready is False`; T4 `missing_keys == [".env.local"]`, `ready is True` |
| P1.2 An older note with a cut list is not ready | T3 `unlisted_ignored == 1`, `ready is False`; T6 prints the line, exit 0 |
| P1.3 A note of 25 paths or fewer is written as on main | T5 at 2 and 25 paths. A one-off comparison against main's `handoff.py`, run from a throwaway worktree at `c9648dd` (spec, IF2), printed `2 paths: identical=True` and `25 paths: identical=True`; at 26, only the rest line differs. It was run again after the last repair, with the same output. That output lives outside history |
| P1.4 `build_plugins.py --check` exits 0 | the third gate, exit 0 |
| C5 (plan) | T1 to T11 exit as the spec lists. The pull request carries `Fixes #28` (the commit body does) |

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests/test_handoff.py -q
    ........................................................................ [ 85%]
    ............                                                             [100%]
    84 passed in 43.82s
    exit 0

    $ uv run --no-project --with pytest python -m pytest tests -q
    FAILED tests/test_tools.py::test_suggestions_and_generated_cases_with_newer_gnd
    1 failed, 306 passed in 153.29s (0:02:33)
    exit 1
      (the failure's own message: "gnd synth --guarded-cases built no cases (exit 5):
       ERROR: the synthetic-value generator needs the optional 'synth' extra.")

    $ python3 devtools/build_plugins.py --check
    exit 0

`git diff 1a5f14c | shasum -a 256` gave
`1391fae585f2d1849c8ebfd15d5fcfde79f1f8f56aa8fcac1dd91d6730d07f19` before and after the
second and third gates, so they ran on one tree. That tree was committed as `4903752`.

## Verification-selection ledger (as run)

| Obligation | Disposition | Result |
|---|---|---|
| T1 to T12, P1.1 to P1.3 | run | `tests/test_handoff.py`, exit 0, 84 passed |
| Plan section 9, phase 1 row 2 | run | the full suite, 1 failed (R5), 306 passed |
| P1.4 | run | `build_plugins.py --check`, exit 0 |
| The known red (R5) | inherit | `001-plan.md`, boundary. Its inputs (GND's install, `rules_check.py`, `components_index.py`) are unchanged by this phase |

## Review

Two rounds of the review helper, `--subject phase --base 1a5f14c`, reviewer Codex
(read-only, effort `high`). **One reviewer is one reviewer.** The reviewer did not run
pytest, by the brief's read-only rule, and reproduced with in-memory probes.

| Round | Brief | Findings | Blocking | Self-inflicted | Verdict |
|---|---|---|---|---|---|
| r1 | `c8f50889…c490` | 2 | 2 | 0 / 2 | CHANGES_REQUESTED |
| r2 | `d0f50d87…bc02` | 3 | 2 | 2 / 3 | CHANGES_REQUESTED |

All 5 findings were reproduced, fixed and given a regression test. Each test was observed
red against the code before its fix, with the outputs in the ledgers. The budget declared
before r2 was one more round. After r2 the stop rule also fired, at 2/3 self-inflicted. The
r2 repairs are therefore unreviewed: `review_tool.py status` lists `handoff.py` (both
copies), `tests/test_handoff.py` and the spec as changed since r2 read them. A first round
was started over a brief that named 42 files, unrelated untracked ones among them. It was
stopped before it reported, and set aside outside the tree (spec, IF4).

## Refactoring review

None executed. Deferred: one, below.

- What the phase touched is `_snapshot_text` and `takeover`. The phase showed that
  `takeover` reads back a Markdown rendering written for people. Five of the phase's
  findings were ways that rendering failed to round-trip a path: r2 F2, r3 F1, phase r1 F1,
  and phase r2 F1 and F2.
- The structural fix is to write the whole ignored inventory machine-readably in every
  note, and have `takeover` read only that. It changes every note's bytes, which O4 and P1.3
  forbid in this phase.
- It is deferred as an open question below, not done.

## Boundary -- what this phase does NOT establish

- **Residual (spec, IF6), in the reviewers' terms.** A note written before 0.1.4 whose
  ignored path holds a newline that prints as complete valid bullets can still read as
  ready. The 0.1.4 writer never prints such a note.
- The r2 repairs carry no review opinion. Two single-seat rounds are one reviewer's
  reading.
- The tests run on macOS (APFS) only. Whether a folder named with a newline can be made on
  another file system was not tried.
- The released 0.1.3 was never tagged (`release_plugins.py status`: `released: 0.1.2`). The
  owner tags `plugins-v0.1.4` after the merge; nothing here tags or publishes.
- Nothing was posted to issue 28. The reply is the owner's.

## Open questions

- Q3 (new). A machine-readable ignored inventory in every hand-off note, so that
  `takeover` stops parsing Markdown. It is a format change for every note. It is carried
  to this milestone's close sweep, which names the milestone that owns it.
- Q4 (new). Plan C5 names "the tests T1 to T10"; the spec now has T1 to T12, with T10b.
  Repair the plan's wording at the close.
- Q5 (new). `.planning/**/review.log` and the PR 26 rounds are excluded only in this
  machine's `.git/info/exclude`. On another machine, `review_tool.py brief --subject phase`
  names them again. Should `.gitignore` carry `review.log`? Carried to the close sweep.

## Refuted premises

- "Released 0.1.3" (plan sections 4 and 9, "0.1.3 to 0.1.4"): 0.1.3 was never tagged. The
  bump still went to 0.1.4, since installs of 0.1.3 exist (spec, IF3). Repair at the close.
- The spec's section 6 bullet rule, "the bullet lines, as today" and then the r2 and r3
  patterns, was refuted three times by review (r3 F1, phase r1 F1, phase r2 F1). It was
  amended in place, the prior wording kept (spec, IF5 and IF6).
