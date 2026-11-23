---
milestone: component-index
station: "close"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: close-correction
date: 2026-11-23
gates:
  - command: "review_tool.py run .planning/reviews/pr-37-r1 (the review of the close's pull request, Codex, read-only)"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED; 2 findings, 1 blocking"
  - command: "uv run --no-project --with pytest python -m pytest tests/test_handoff.py -q -k 't21 or t22'   (the new tests on the tree of 811b4a3, before the fix)"
    exit: 1
    output: "9 failed; test_t21: assert 2 == 1 (two snapshot end markers). The same case run by hand returned ready: True with out0/ missing"
    note: >-
      Expected to exit 1: this is the counterexample to C5 that record 007 did not have.
  - command: "review_tool.py run .planning/reviews/pr-38-r1 (the review of the fix, Codex, read-only)"
    exit: 0
    output: "VERDICT: APPROVE; no findings"
  - command: "uv run --no-project --with pytest python -m pytest tests/test_handoff.py -q"
    exit: 0
    output: "115 passed in 66.53s (0:01:06)"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "362 passed in 196.01s (0:03:16)"
    note: >-
      Run at acceaab, whose tree is main's at 823a55f. This branch differs from that
      tree only under .planning/.
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
    output: "(no output)"
  - command: "test ! -e .devtools/components/unassigned-baseline.txt"
    exit: 0
    output: "(no output)"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py search --explain <each case of search-cases.md>"
    exit: 0
    output: "9 of 9 cases put the expected component first"
  - command: "uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q"
    exit: 0
    output: "8 passed in 5.79s"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
    output: "(no output)"
  - command: "ruling: delegated (auto=true) approved the close of component-index again, on the corrected evidence"
    exit: "n/a -- ruling"
slow_cadence:
  command: "uv run --no-project --with pytest python -m pytest tests -q"
  trigger: "n/a -- the full suite is completion predicate C3, and it ran"
  reason: "this repository has no broader lane than the full suite"
evidence:
  - path: .planning/milestones/component-index/notes/component-index-plan.md
    sha256: 239ccf247496d73b7eb4eabf952bbdae693f332c62e7b176e3b627be52ebe1de
  - path: skills/dev-handoff/scripts/handoff.py
    sha256: 56e59d628e48b864af2818a202f11478fd025ed0112be5dbf9735ff556c05522
  - path: tests/test_handoff.py
    sha256: 5751bb67f51c29e78504f712410a01d88f74f860ad9fbe3492cc24e4f0609fa9
  - path: .planning/reviews/pr-37-r1/BRIEF.md
    sha256: fd9a927acb4c9e95a1767fc4189162a3d0fe77f2a6d7d69796334e35fe3f738d
  - path: .planning/reviews/pr-37-r1/review.md
    sha256: 1aeec1217056d7aabaf1138ee94bc782b654201602c09019c82a9645c24e87d1
  - path: .planning/reviews/pr-38-r1/BRIEF.md
    sha256: 6dd7d03edb2b485b143cef96ec617526ce5e2dc139714cd29fe26e904608604f
  - path: .planning/reviews/pr-38-r1/review.md
    sha256: 399793eb31c3afead4a9c7b7d4da68ef7e4ea05fc38446ea28e69abb2a275219
---

# Claim

Record 007 said completion predicate C5 held on `main` at `811b4a3`. It did not. An
independent review of the close's pull request found a note, written by the code of that
commit, that `takeover` reads as ready while an ignored path is missing. The defect is
fixed in vasiloglou/dev-tools#38, merged as `823a55f`. On that tree the five measurable
predicates were measured again and hold, as far as the tests and one further review show.
This record corrects 007 in two places and rules on the close again. It does not edit
007.

## What the review of the close's pull request found

The owner asked for a review of vasiloglou/dev-tools#37 (`/dvt-milestone:review-pr`).
One round, `.planning/reviews/pr-37-r1`, reviewer Codex, read-only, over the pull
request's diff at `6650e45` with records 001 to 006 as context. **One reviewer is one
reviewer.** `VERDICT: CHANGES_REQUESTED`.

| Id | Finding | Class | Disposition |
|---|---|---|---|
| F1 | A hand-off note prints the git remote's path as it is. A remote whose path holds line breaks prints a second "Files git ignores" section and an early snapshot end marker, and `takeover` then reports ready with an ignored path missing. C5 says that cannot happen | blocking | fixed at `17e63c6` (vasiloglou/dev-tools#38) |
| F2 | 007's paragraph on which files a review covers lists the milestone's `README.md` among those the close review read; the pull request changed that file afterwards | completeness | fixed by this record, below |

Both were reproduced before they were believed. F1 was reproduced on real files, not in
memory: `git remote add origin` with such a path, `write_note`, a clone without `out0/`,
then `takeover`, which returned `head: ok, ready: True, missing_ignored: [],
unlisted_ignored: 0`. The note held 2 end markers and 2 ignored headings.

The close review of record 007 (`close-r1`) had run the note writer and reader over 516
in-memory scenarios and found nothing. Its account of them names paths, control
characters, backticks and key files, and no remote.

## The fix (vasiloglou/dev-tools#38)

The owner said to fix it in its own pull request before the close merges.

- **It was wider than the remote.** With a forged section put into each text value of the
  note in turn, every one could add a line of its own. Of those, the base, `--from` and
  the project's `setup_command` can be given a line break, as the remote can.
- **One rule, at the place the note is put together.** Every line the writer generates,
  in the header and in the snapshot, is kept to one line, whatever a value holds, by the
  helper (`_one_line`) that already did this for two lists of paths. A note with no
  control character in any value is written byte for byte as before.
- **Two tests, seen failing first.** `test_t21` is the review's case with a real remote.
  `test_t22` walks the note's data and forges each string in turn, for each line break
  Python's `splitlines` breaks at: the 10 characters, asked of Python, and CR LF. All 11
  fail on `main`'s script at `811b4a3` and pass with the fix.
- Plugins 0.1.6, rebuilt; the index page regenerated; the `handoff.notes` entry updated.
- **Reviewed once** (`.planning/reviews/pr-38-r1`, Codex, read-only, at `17e63c6`):
  `VERDICT: APPROVE`, no findings. It ran the writer and reader in memory over 121
  injection cases and 44 repeated-write cases, and compared 290 control-free outputs with
  the earlier implementation. It did not run pytest or a real cloned checkout. It
  remarked that `test_t22` then listed 8 line breaks where Python splits at more; the
  test was changed to take them from Python at `acceaab`, which no review read.
- The owner asked for #38 to be merged; the agent merged it with a merge commit
  (`823a55f`). `main`'s tree is the tree of `acceaab`.

## Corrections to record 007

1. **Its Claim, its C5 row and its gate entry for `tests/test_handoff.py`.** "C5 holds"
   was false at `811b4a3`. The 103 tests passed there, and none of them set a remote. C5
   is measured again below, on `main` at `823a55f`.
2. **Its paragraph "Which files a review covers at their present bytes"** says the close
   review read the milestone's `README.md`. It read that file at SHA-256 `b5930774…`,
   before the pull request added the link to 007 and the close declaration to it. Those
   additions, and all of 007's Review and Close ruling sections, were read by no review
   until `pr-37-r1`, which read 007 and the `README.md` as the pull request then held
   them. This record and the lines the `README.md` and the plan gain with it are read by
   no review.

Everything else in 007 stands: C1 to C4, the sweep of Q1 to Q15, the ten plan repairs,
the residuals and the proposed issues. `pr-37-r1` checked the sweep's counts, the ten
repairs, the 40 findings of the earlier ledgers, and that issue 28 is closed and
vasiloglou/dev-tools#29 says `Fixes #28`, and found each true.

## Completion predicates, measured again

On this branch after `main` at `823a55f` was merged into it (`42e6c1e`); it differs from
`main`'s tree only under `.planning/`.

| Predicate | Measurement |
|---|---|
| C1 | `--check --strict` exit 0; `coverage: 12/12 devtools, skills modules assigned to components`; no baseline |
| C2 | 9 of 9 search cases |
| C3 | `362 passed`, exit 0, at `acceaab` (the same tree as `main`); `tests/test_own_index.py`: 8 passed |
| C4 | Unchanged since 007 |
| C5 | `tests/test_handoff.py`: 115 passed, exit 0, with `test_t21` and the 11 cases of `test_t22`. The counterexample of `pr-37-r1` now gives `ready: False` and reports `out0/` missing |
| C6 | Record 007, corrected by this one |

**C5 is a claim about every note, and tests do not prove it.** Eight review rounds have
now each found a way that the Markdown of a note misleads `takeover`: plan r2 and r3,
phase 1 r1 to r4, phase 3 r4 and `pr-37-r1`. Each earlier fix closed the cases its round
found. This one is a rule about everything the writer prints. It says nothing about a
note that someone edits by hand, and `takeover` still reads the note as Markdown. (The
ledger of `pr-37-r1` and the description of #38 call this the sixth round; the count is
eight.)

## Close ruling (verbatim)

    ruling: delegated (auto=true) approved, replacing the ruling of 007-close.md
    subject: the close of the component-index milestone
    date: 2026-11-23
    authorization: the owner's invocation "/dvt-milestone:process-milestone auto" of
      2026-11-21, which delegates the close ruling of this milestone; the owner's "Yes,
      run the close", "Yes, fix it first" and "Yes, merge #38" of 2026-11-23
    prior ruling, kept: 007-close.md approved the close on C1 to C5 measured at 811b4a3.
      C5 was false there (pr-37-r1 F1).
    on: C1 to C5 measured again on main's tree at 823a55f; pr-37-r1's two findings, both
      fixed; pr-38-r1's APPROVE with no findings; everything else of 007 as it stands
    accepts: the five residuals of 007, and the one below
    carries: as 007, with P2 as below

This is an agent's ruling under the owner's delegation, not the owner's own reading. It
covers neither the merge of the pull request that carries this record, nor a release tag,
nor the filing of any proposed issue.

## Changes to the sweep of 007

- **Q3, carried as proposed issue P2** (a machine-readable inventory of ignored paths in
  the note). Its case is stronger: an eighth round found the same class again, in a
  place seven rounds and 516 probes had not looked. P2 is the one proposal the owner should
  read first.
- **Q16 (new).** Plugin versions are taken by whichever pull request merges first, so
  0.1.4 is #34 and phase 1, 0.1.5 is phase 2 and #35, and 0.1.6 is #38; none is tagged,
  and `release_plugins.py status` says `released: 0.1.2`. Which commits get which tags is
  **carried** to the owner.

## A further residual the close accepts

- `takeover` reads a note written before 0.1.6 as it stands. Such a note, written from a
  checkout whose remote, base, sender or setup command held a line break, can read as
  ready with a path missing. No writer since 0.1.6 prints one.

## Refuted premises

- Record 007, "C5 … `tests/test_handoff.py` exits 0": the exit was 0 and the predicate
  was false. A predicate about every note is not measured by the tests that exist.
- The close review `close-r1`, "found no case that reads as ready with a path missing"
  over 516 scenarios: true of what it tried. A second reviewer with the same instrument,
  asked about the same file, found one.
- Pull request #38 as first opened, "the 8 line breaks Python splits lines at": Python
  splits at 10 characters. The test now asks Python.

## Boundary -- what this record does NOT establish

- That no other route exists. The fix covers what the writer prints.
- Anything about `acceaab` (the test change), this record, or the lines the plan and the
  `README.md` gain with it: no review read them.
- That 0.1.6 is released. It is not tagged.
- The two rounds' ledgers are completed in the commit after this record, since the row
  for F2 names this record's commit.
