---
milestone: issue-sweep
station: "phase-3"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-3
date: 2026-11-23
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_plugins.py tests/test_review_tool.py tests/test_handoff.py tests/test_from_gsd.py tests/test_sync.py -q"
    exit: 0
    output: "495 passed in 243.40s (0:04:03)"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "527 passed in 239.85s (0:03:59)"
    note: "the run before it, after the review repairs, printed 34 failed, 493 passed (spec K6). After this run two reread: lines were added to .devtools/components/COMPONENTS.md; the strict index check below ran after them"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 devtools/release_plugins.py status"
    exit: 1
    output: "0.1.7 is ready: after the merge, run `release_plugins.py tag` on main"
    note: "exit 1 is the expected value: a release is due"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base a247f4d --strict"
    exit: 0
    output: "changed against a247f4d (a247f4d): 37 file(s) differ; 0 to fix, 0 warning(s), 1 to reread"
    note: "the reread: line is handoff.notes, answered below"
  - command: "uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml rules_check.py, review_tool.py and handoff.py under skills/, and their copies under plugins/"
    exit: 0
    output: "All checks passed!"
  - command: "ruling: delegated (auto=true) approved .planning/milestones/issue-sweep/notes/phase-3-spec.md sha256 3b87219b5bc6ec7d97e1d6ea5276df19b3066972ba1a4f12370f484289dc9641"
    exit: "n/a -- ruling"
slow_cadence:
  command: "none beyond the full suite"
  trigger: "n/a"
  reason: "the full suite is the repository's only test lane, and it ran (above)"
evidence:
  - path: skills/components/scripts/rules_check.py
    sha256: 406421faffc39d0bc2461011c19e21e8d9fd366002aa679490bd60203d2f1203
  - path: skills/components/scripts/components_index.py
    sha256: 5db4c390c7f9b2bf83ffa51c3dcd2c405676d7a03fdee944bcc34e3c4a8e9c36
  - path: skills/milestone/process-phase/scripts/review_tool.py
    sha256: c95e475d6f4cdaccb10a1a6c7c0681f2079c09c8ed66f90eb23c1486d8ed8422
  - path: skills/dev-handoff/scripts/handoff.py
    sha256: 49836ced0ebfb9526c4c1f457f8e8c150f711ba0e738a64ed113883ce9703fd9
  - path: skills/phase/process-phase/scripts/phase_tool.py
    sha256: 25a1d5cc83853f40c42ebb0edfc682384b332e73971de9b8b6673bab28dbe445
  - path: skills/phase/process-phase/scripts/coder_pool.py
    sha256: 3f23de0f51ca2d96df305c550c50ff839ab93b48fb1a46611bf6183abd99f585
  - path: devtools/from_gsd.py
    sha256: fcb719f18739b87ab41b2b88478bf75db98c4e57347073849896facdb7ebc2cb
  - path: skills/components/SKILL.md
    sha256: a973c10a32f2a83ff88096a1d2bdd5882db39bf17a034d58784ba044fe25dbcc
  - path: skills/components/references/rules.md
    sha256: ef9f5fbc1a5334f27ac06c9c65cb151b70e2cf9c2b9c9e404c691777deaade3d
  - path: docs/rules.html
    sha256: a9c7d68d9747f5543b7959c177384f1f027dcc54803f1a20a7905a34767a9069
  - path: tests/test_tools.py
    sha256: 2dcdaf6dcf2e6c15727c4e111f37f56318f999fa05e28a174fe0e4e17c37b319
  - path: tests/test_plugins.py
    sha256: e2e0ba102658956ca00137be472d44d07f130801e1a68a4760604c3d2740a936
  - path: tests/test_review_tool.py
    sha256: 670d731fa6a2dbbbbef0cadfc544043e3de00e00bfedf3dfa8b2cb003d6512d0
  - path: tests/test_handoff.py
    sha256: 8761a7cf5e3f7a87fb95504e2be8c889585be96b0d0cb6dfea009d3f9bd434e2
  - path: .devtools/components/COMPONENTS.md
    sha256: b5051c5d439b0a0dda70d309260232c5b72692f03a4e81c24b6996d3bc8d7625
  - path: .planning/milestones/issue-sweep/notes/phase-3-spec.md
    sha256: a95961991aaad843565e8017efdc0253cc0dec11a5d3f02ade191f9ce9d3e93f
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-3-r1/BRIEF.md
    sha256: a0dbaefcd587572ce521cb4b8b4d5d49f06b554e867476b6da34c6deeb95fe6b
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-3-r1/diff.patch
    sha256: a18f64b4cc2c0a01d567b7b6ab1fd91bc8a927ee2bc808d3c30f26e2908bb658
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-3-r1/review.md
    sha256: f29fbe2e970d5245d8c7fcf0d453cbeaf34c93e97a781e7faa01a18db99d759c
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-3-r1/FINDINGS.md
    sha256: 95d232b7ac489a7c3323183518220398b074934743bfbbc37aeb57a9934ea0f7
---

# Claim

Phase 3's selected gates each exited 0 on the phase's head, except the release status,
which exits 1 as expected: in a new project `rules_check.py init` then `test` prints `0
wrong` and exits 0 with either plugin (issue 33); a settings file that five of the six
scripts cannot use exits 2 with its reason, one envelope for `phase_tool.py` (issue 43);
and the docstrings of issue 43 say what the code does.

## What shipped

Commits `6c2ada5` (the work) and `43f6d83` (the review repairs, with the defect of K6
fixed in them), on the base `a247f4d` (the spec and its delegated gate).

- **Issue 33, `rules_check.py`** (+35 -3 with the settings rule). `test` leaves out a rule
  about plans when the phase tool is not there, with one `skip:` line, and leaves it out
  of what `gnd synth` is given; the summary says how many were skipped. `init` is
  unchanged.
- **Issue 43, the settings files.** `rules_check.py`, `components_index.py` and
  `handoff.py` end through a `settings_error` helper of their own (exit 2, the reason on
  standard error); `review_tool.py` through its `Stop` (exit 2). Each refuses an unknown
  key, a value whose type is not its default's, a list holding anything but strings,
  text that is not JSON, and JSON that is not an object. `phase_tool.py` records the
  error at load, keeps the defaults so the module loads, and every command prints one
  envelope with `"code": "SETTINGS"` and exits 2, after the command line is parsed.
  `coder_pool.py` keeps its documented exit 1 (spec D1).
- **The docstrings**: `phase_tool.py` (exit codes, `status`), `review_tool.py` (exit 2),
  `from_gsd.py` (git only reads), `coder_pool.py` (the fallback needs `claude` on PATH),
  `handoff.py` (exit 2).
- **The skill and the page**: `references/rules.md` (the `skip:` line; the settings
  exit), the components `SKILL.md` (the settings exit), `docs/rules.html` (the `skip:`
  line).
- **The index**: three notes that quoted the wrong docstrings corrected; eight entries
  read beside this phase's diff and marked `reread:`.
- **Tests**: +106 in `tests/test_tools.py`, +18 in `tests/test_plugins.py`, and the
  settings assertions of `tests/test_review_tool.py` and `tests/test_handoff.py` moved to
  2 with new cases.
- **The plugins**: rebuilt under 0.1.7, the milestone's one version.

Decisions that survived: D1 to D4 of the spec. D1 amends the plan's D10 for
`coder_pool.py`; the plan is repaired at the close.

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_plugins.py tests/test_review_tool.py tests/test_handoff.py tests/test_from_gsd.py tests/test_sync.py -q
    495 passed in 243.40s (0:04:03)
    $ uv run --no-project --with pytest python -m pytest tests -q
    527 passed in 239.85s (0:03:59)
    $ python3 devtools/build_plugins.py --check
    (no output; exit 0)
    $ python3 devtools/release_plugins.py status
    version in the tree: 0.1.7
    released: 0.1.2 (plugins-v0.1.2)
    30 plugin file(s) changed since plugins-v0.1.2
    0.1.7 is ready: after the merge, run `release_plugins.py tag` on main
    (exit 1)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base a247f4d --strict
    reread: handoff.notes (entry not edited): skills/dev-handoff/scripts/handoff.py
    changed against a247f4d (a247f4d): 37 file(s) differ; 0 to fix, 0 warning(s), 1 to reread
    $ uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml <the three scripts and their copies>
    All checks passed!

    By hand, in scratch projects (spec K4):
    rules test: 5 rule(s), 10 example(s); 0 wrong; 1 rule(s) about plans skipped    (dvt-milestone, exit 0)
    rules test: 6 rule(s), 12 example(s); 0 wrong                                   (dvt-phase, exit 0)
    phase_tool.py --format json status, unknown key: one envelope, "code": "SETTINGS", exit 2
    review_tool.py status ., unknown key: error: …: unknown setting(s): nope, exit 2
    coder_pool.py show --json, PATH=/usr/bin:/bin: pool [], effective_tracks 0, exit 0

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/issue-sweep/notes/phase-3-spec.md, as committed at a247f4d
    sha256: 3b87219b5bc6ec7d97e1d6ea5276df19b3066972ba1a4f12370f484289dc9641
    date: 2026-11-23
    authorization: the owner's "process-milestone issue-sweep auto", for this milestone
    decisions: D1 to D4 of the spec, each as proposed
    instrument: the spec's prose; phase review by review_tool.py, at most r1 and r2
    not covered: pushing, the pull request, merging, tagging, anything posted to GitHub

This is an agent's ruling under the owner's delegation, not the owner's own reading. The
spec has since grown by its findings and review round, with two corrections marked at
their sites; its digest now is in the evidence list.

**The `reread:` line.** `handoff.notes` was read beside this phase's change to
`handoff.py` (its settings loader and one docstring sentence): its `does`, `verbs` and
notes are still true, and none speaks of the settings exit. It is not marked `reread:`,
because `review` lists it as older than its code for four earlier commits this milestone
did not read; a `reread:` line would claim it had.

## Criteria

| Criterion | Evidence | Met |
|---|---|---|
| P3.1 `init` then `test`: `0 wrong`, exit 0, each plugin | T1 in `tests/test_plugins.py`; the by-hand runs | yes |
| P3.2 A rule not about plans that names an unknown fact type is still wrong | T3 | yes |
| P3.3 With the phase tool, `test` as before | T4, the existing tests unedited; the reviewer's controlled comparison | yes |
| P3.4 Exit 2 with the reason for a settings file a script cannot use | T5 to T8, the wrong-type cases (r1 F1, F2) | yes, for five scripts; `coder_pool.py` keeps 1 (D1) |
| P3.4b One envelope from `phase_tool.py`, exit 2, `status` too; the module loads | T9, T10, the parsed-command-line cases (r1 F3) | yes |
| P3.5 The docstrings say what the code does | The by-hand runs above; the reviewer's inspection | yes |
| P3.6 The three scripts and their copies stay lint-clean | The lint gate | yes |
| C5, C6 (plan) | As P3.1 and P3.4 to P3.6 | yes, with D1 |

## Review

One round of the review helper, `--subject phase --base a247f4d`, reviewer Codex,
read-only, effort `high`. **One reviewer is one reviewer.**

| Round | Brief | Findings | Blocking | Self-inflicted | Verdict | Repaired at |
|---|---|---|---|---|---|---|
| phase-3-r1 | `a0dbaefc…fe6b` | 3 | 2 | 0 / 3 | CHANGES_REQUESTED | `43f6d83` |

- F1 and F2 (blocking): values of the wrong type still ended in a traceback, in all five
  loaders. F3 (hardening): the settings envelope did not follow the parsed command line.
  Each reproduced before it was believed; the ledger has each reproduction and test.
- The reviewer confirmed: the build check, the strict index check and the lint gate;
  that all five loaders refuse malformed JSON, a non-object and an unknown key with exit
  2; the `about == "plans"` match; that a rule not about plans stays wrong; that with the
  phase tool output, exit and the model given to `gnd synth` match the baseline; D1's
  reason; that `from_gsd.py`'s git commands only read.
- It could not run the tests, the fresh-project integration or any mutation, by the
  read-only rule.
- `review.md` was passed through `review_tool.py sanitize` (6 paths) and says so;
  `run.json` holds the original's digest,
  `25e9f0907474203acc9331c2fa7c8b1829350bcdbd320a3b535d8710cbcf596a`.

`review_tool.py status` reports every file the repairs changed as `unreviewed`: the five
loaders and their plugin copies, the four test files, the spec. No review opinion covers
them, including the fix of K6.

## Refactoring review

Seen and deferred: the six `load_settings` functions now share a shape (read, refuse an
unknown key, check each value's type) written out six times. S0.2 keeps it so: a shipped
script stands alone. No target: it is the price of that rule, and stated here so it is
not silent.

Executed: none beyond the phase's own.

## Boundary -- what this phase does NOT establish

- That every value a setting can hold is usable. The rule checks types; a string that
  names a missing file, a negative `max_mb` or an unknown `reviewer` model is not
  checked, except where a script already checked it.
- `coder_pool.py`: its settings exit stays 1 (D1), and its TOML errors were not changed.
- That a dvt-milestone project gets the rule about plans judged anywhere: it is skipped
  there by design (D9 of the plan).
- The review repairs, and the fix of K6 inside them, carry no review opinion. One
  reviewer is one reviewer, and it ran no test.
- Every run was on macOS, with GND 0.4.0. Nothing is pushed, and no issue was commented
  on or closed.

## Open questions

- K6 shows the focused selection can miss a defect that only a project without a
  settings file reaches. A focused gate for a change to a loader should include a run
  with no settings file. For the close: whether that belongs in the verification
  selection of `.devtools/project.md`.
- The plan's D10 is amended by this phase's D1, for the close's plan repairs.

## Refuted premises

- "Exit 2 is the code each docstring already gives to 'could not run'" (the plan's D10,
  for every script under `skills/`). Refuted for `coder_pool.py` by its docstring at
  `6c2ada5`, which gives 1 to "a settings or configuration file cannot be used".
- "The settings refusals each script has today, plus two" (spec 6.2) covers "a wrong
  value" (spec, section 5). Refuted by r1 F1 and F2: values of the wrong type passed
  every check and ended in a traceback.
