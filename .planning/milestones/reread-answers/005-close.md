---
milestone: reread-answers
station: "close"
skill: process-milestone (dvt-milestone 0.1.8), close only; the milestone had no plan or phases
scope: close
date: 2026-11-26
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "591 passed in 250.75s (0:04:10)"
    note: "run on main d82c87e, before this close's files were written; the close adds records and two index entries, no code"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (d82c87e): 7 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "python3 devtools/release_plugins.py status"
    exit: 0
    output: "released: 0.1.8 (plugins-v0.1.8); no change since the last release"
    note: "run on main d82c87e"
  - command: "python3 plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py status .planning/milestones/reread-answers/notes/reviews/close-r1"
    exit: 1
    note: "exit 1 for F7 to F9, whose ledger names this record's commit as the repair; see Gate output"
  - command: "ruling: owner approved .planning/milestones/reread-answers/notes/reviews/close-r1/review.md sha256 675a4b338dc2b63075fbfd99d5e63923031eaf6334a4b9160d6ae22dd590bd4a"
    exit: "n/a -- ruling"
evidence:
  - path: .planning/milestones/reread-answers/README.md
    sha256: 0afd4e29f812ae6452c1a3e9f13430deb437de2e1b56d1ef101751d173bc8e3b
  - path: .planning/milestones/reread-answers/001-issue-50.md
    sha256: 7b4b36272a1b399125d71ef96f4af82e1decc678745d81b507b883fc25c90d2a
  - path: .planning/milestones/reread-answers/002-pr-51-r1.md
    sha256: 39948ff1e752e3e14b45a1077d78f30f1cf1db5130ca138f1b7c2b990e6e4703
  - path: .planning/milestones/reread-answers/003-rulings.md
    sha256: 2e1947e0dde94f4075802cf17737a3e7c1da9a6ca2d4066a0b4f7a5e056c19c8
  - path: .planning/milestones/reread-answers/004-pr-51-r2.md
    sha256: c255e30ae1edf1dec1651a5b39a8cc4e09de57256ac96b0308c995c0ef52cf95
  - path: .planning/milestones/reread-answers/notes/issue-50.md
    sha256: b9e52bbfa75d714c492d8d082eb8dae109d92a4cd393c56e33690b8b7c944bea
  - path: .planning/reviews/pr-51-r1/FINDINGS.md
    sha256: 1fe8e39151fd27601e90f77eae01e70fc9358698999753af59aee917688a4a13
  - path: .planning/reviews/pr-51-r2/FINDINGS.md
    sha256: dd1a542d02afa7eada6fa694784e46360ac352a1dad40b247905395d1e13aad8
  - path: .planning/milestones/reread-answers/notes/reviews/close-r1/BRIEF.md
    sha256: 9a80383aa0ddb518089ac38740e56bf61f263242097a59412e1cee8001732b95
  - path: .planning/milestones/reread-answers/notes/reviews/close-r1/review.md
    sha256: 675a4b338dc2b63075fbfd99d5e63923031eaf6334a4b9160d6ae22dd590bd4a
  - path: .planning/milestones/reread-answers/notes/reviews/close-r1/FINDINGS.md
    sha256: e723ca326095dac8b76b36b51ecc1bf48aaa4927bf2f3fbcda041a61fafa6451
  - path: skills/components/scripts/components_index.py
    sha256: b1131276e324cfbcfaf8620db8b0e5e8c0e9eebf119aaa54204fceadbedf2811
  - path: tests/test_tools.py
    sha256: 9d648b58f9108fdbad3480840414f30f509cbfe365dbf03c5738d7408c1d5ba2
  - path: .devtools/components/COMPONENTS.md
    sha256: 6955dc2e111a5a110c01aeeca697b58eaed6049328dbc18b71953885da65ecaa
---

# Claim

The milestone `reread-answers` is closed by the owner's ruling: issue 50's four parts are
merged in pull request vasiloglou/dev-tools#51 (`d82c87e`) and released as plugins 0.1.8,
the fourteen findings of its two pull request rounds are repaired, and the close review
read the last repair (`24003fd`), which no round had read. That review found one blocking
regression in `24003fd` (close-r1 F1) and five hardening gaps, none repaired here; they are
listed below with the questions the records left, for the owner.

## What the milestone was

It was recorded after the fact (`README.md`): no plan, no phase spec, no phase. The change
was made as a fix on a pull request, and the owner then ruled that a change to what a gate
refuses takes a milestone record. So this close has no plan to repair and no phase records
to count. Its predicates are the four parts of issue 50 (`notes/issue-50.md`) and the two
review rounds of the pull request.

## Completion predicates

| Predicate | Evidence | Met |
|---|---|---|
| P1 Part 1: process-phase sends a `reread:` line to the entry (edit `does` or `verbs`, or add or update the entry's `reread:` line), not only to the phase record | `001-issue-50.md` (`95551f0`): `skills/milestone/process-phase/SKILL.md` step 6, `skills/phase/process-phase/references/close.md`; close-r1, "What checked out" | yes |
| P2 Part 2: `changed` and `review` read one rule for whether an entry was answered | `DATING` and `answered` (`001`, `002`); `review` gives way on a blank (`004`, F6) | yes, for the words of a line; they still disagree on a line whose words did not change (close-r1 F4; `002`, "Not done") |
| P3 Part 3: `changed --strict` exits 1 while a component's `reread:` line is unanswered; a subsystem's line is advice | `001` (`95551f0`, `8ae1e84`) and its tests; close-r1 replayed both cases | yes |
| P4 Part 4: the line names the public names a change added that `does` and `verbs` leave out, and removed ones they still mention | `003-rulings.md` (`c6d55ca`); `004` F9 (`24003fd`) | yes, for names with ASCII words; a name with none is never listed (close-r1 F6) |
| P5 Every finding of `pr-51-r1` (5) and `pr-51-r2` (9) is repaired; each code finding has a test that fails without its repair | `002`, `003`, `004`; the two ledgers. Round 1's F4 is a sentence of the skill and site and has no test (`003`). close-r1 replayed all 13 cases of round 2's tests red on `24003fd^` and green on `24003fd` | yes, with round 1's F4 tested by no test; and `24003fd`'s F1 repair lost the "ask both" behaviour for an untracked module named one by one (close-r1 F1) |
| P6 The full suite, the build check, the strict index check and `changed --strict` exit 0 on `main`; 0.1.8 is released | Gates above; GitHub's three `gates` jobs on `d82c87e` | yes |
| P7 A close review reads the bytes of `24003fd` | `notes/reviews/close-r1`, at `d82c87e` (the brief's 14 files, SHA-256 `9a80383a…2b95`) | yes |

## Records

- `001-issue-50.md`: parts 1 to 3 (`95551f0`, `8ae1e84`), recorded after the fact.
- `002-pr-51-r1.md`: round 1 of the pull request, and the repair of its F1 and F2 (`0c3e0b3`).
- `003-rulings.md`: the owner's rulings; F3 to F5 of round 1, "ask both" for a regrouped
  module, and part 4 (`c6d55ca`).
- `004-pr-51-r2.md`: round 2, and the repair of its nine findings (`24003fd`).

## Reviews

| Round | Subject | At | Findings | Blocking | Repaired at |
|---|---|---|---|---|---|
| pr-51-r1 | the pull request | `8475b62` | 5 | 2 | `0c3e0b3`, `c6d55ca` |
| pr-51-r2 | the pull request | `6751dbd` | 9 | 3 | `24003fd` |
| close-r1 | the milestone's evidence and `24003fd` | `d82c87e` | 9 | 1 | F7 to F9 in this record's commit; F1 to F6 deferred |

Every round had one seat, Codex, read-only. One reviewer is one reviewer.

The close round checked the brief's 14 digests, replayed the 13 cases of `24003fd`'s
tests against `24003fd^` (each failed) and `24003fd` (each passed), confirmed P1, the
question sweep's inventory, issue 50's state and the release, and built inputs the tests
lack for each repair's class. It could not run pytest or `ci_local.sh` (its sandbox writes
nothing). Each finding was reproduced here before it was believed where it is marked so,
in a project the test helpers make, with the script at `24003fd^` and at `24003fd`:

- **F1 (blocking, deferred):** an untracked module named one by one in `modules:` (an
  ignored `tools/gen.py`) moves to another component without an edit. At `24003fd^`
  `changed --strict` asked both and exited 1; at `24003fd` it says `0 to reread` and exits
  0. `24003fd` takes the candidates from `git ls-files` only. A regression, against the
  owner's "ask both"; it fails open, as round 2's F1 did, so it is classed as that was.
- **F2 (hardening, deferred):** `git ls-files -z` is read as text. A tracked
  `src/widget/a\rfile.py` under a catalogued folder, edited, stops plain `changed` with
  `git cannot read src/widget/a` (the carriage return read as a line break), exit 1. The
  reviewer's byte 0xff case cannot be built on macOS (`Errno 92`); not reproduced here.
  Fails closed.
- **F3 (hardening, deferred):** a `- reread:` line under an indented `  ## ` heading after
  the last entry answers it: exit 0 at `24003fd^` and `24003fd` alike. Not a regression.
- **F4, F5, F6 (hardening, deferred, not rerun here):** a space added inside an unchanged
  `reread:` line, and U+0085 in one, split `changed` from `review` (the two-roads gap `002`
  records); a Latin-1 or BOM-headed Python file stops plain `changed` at the base import
  graph; a public name with no ASCII word is never listed. The reviewer reports F5 and F6
  on `24003fd^` too.
- **F7 to F9 (completeness, fixed here):** P5 said every finding has a test; the draft
  bound the ruling to README bytes and carried placeholders, and the README still named
  the merge and tag as next; "every test ran on macOS and Linux" left out the Linux skips.

The ledger is `notes/reviews/close-r1/FINDINGS.md`. No code is changed by this close.

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests -q        (on d82c87e)
    591 passed in 250.75s (0:04:10)
    $ python3 devtools/build_plugins.py --check
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (no output; exit 0)
    $ git fetch origin; python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main --strict
    changed against origin/main (d82c87e): 7 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    $ python3 devtools/release_plugins.py status                         (on d82c87e)
    version in the tree: 0.1.8
    released: 0.1.8 (plugins-v0.1.8)
    no change since the last release
    $ python3 plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py status .planning/milestones/reread-answers/notes/reviews/close-r1
    .planning/milestones/reread-answers/notes/reviews/close-r1: close review by codex (codex default), done, 9 finding(s) in the ledger
      problem: F7: Repaired at '(the close commit)' is not a commit or tag here
      problem: F8: Repaired at '(the close commit)' is not a commit or tag here
      problem: F9: Repaired at '(the close commit)' is not a commit or tag here
    unreviewed: .planning/milestones/reread-answers/005-close.md (changed since .planning/milestones/reread-answers/notes/reviews/close-r1 read ec3b99186731)
    unreviewed: .planning/milestones/reread-answers/README.md (changed since .planning/milestones/reread-answers/notes/reviews/close-r1 read da08a9223721)
    (12 lines `reviewed: …`, one per file whose bytes the round read, not shown)

    ruling: owner approved
    words: "review and then close", 2026-11-26, in the owner's message to the session
      that drove this close (the same message asked for pull requests
      syncing 0.1.8 into the repositories that take dev-tools)
    artifact: .planning/milestones/reread-answers/notes/reviews/close-r1/review.md
    sha256: 675a4b338dc2b63075fbfd99d5e63923031eaf6334a4b9160d6ae22dd590bd4a
    scope: closing reread-answers after the close review
    not covered: merging the pull request that holds this record, repairing the deferred
      findings, filing the proposed issues

The ruling was given before the review ran. It is a ruling to close after a review, not
the owner's reading of this review's findings; those are put to the owner below.

## Question sweep

Every record of the milestone was reread. Each question it raised is here once.

| Question | Raised in | Disposition |
|---|---|---|
| Q1 Part 4: should a `reread:` line name new public names the entry leaves out? | `001` | **Closed** by `003-rulings.md`: built in `c6d55ca` |
| Q2, Q9 Should dev-tools' own gate run `changed --strict`? | `001`, `003` | **Carried** to the owner. `gates.yml`, `ci_local.sh` and `.devtools/project.md` still run the plain form; the close's own `--strict` run above exited 0 |
| Q3 Tagging 0.1.8 | `001` | **Closed**: tagged and released, `plugins-v0.1.8` |
| Q4, Q10 Does the milestone get a close? | `001`, `003` | **Closed** by the owner's "review and then close": this record |
| Q5 F3, F4 and F5 of round 1 | `002` | **Closed** by `003-rulings.md` (`c6d55ca`) |
| Q6 A file moved between components without an edit: ask both? | `002` | **Closed** by `003-rulings.md`, "Change: ask both"; close-r1 F1 is an untracked file the repair of `24003fd` no longer asks for |
| Q7 A second round | `002` | **Closed** by `004-pr-51-r2.md` |
| Q8 Removed names: those that appear nowhere, or those `does` and `verbs` still mention? | `003` | **Carried** to the owner. The code lists the removed names still mentioned |
| Q11 Closing issue 50 | `003` | **Closed**: closed on GitHub as completed, 2026-11-26, on the owner's word |
| Q12 A `modules:` path naming a folder without its trailing `/` | `004` | **Carried** to the owner; such a path covers nothing, as before |
| Q13 Declare the stop rule for review rounds in the first round's brief | `004` | **Carried** to the owner, as a rule for `.devtools/project.md` |
| close-r1 F1 to F6 | close-r1 | **Carried** to the owner, as the proposed issues below |

**Proposed issues** (none is filed; posting to GitHub needs the owner each time):

- `changed` no longer asks both components for an untracked module named one by one
  (close-r1 F1, blocking), and reads `git ls-files -z` as text (F2). One reader; a repair
  would take the tracked files and the named paths, as bytes. A 0.1.9.
- `changed` and `review` reach "answered" by two roads (`002`, "Not done"; close-r1 F4),
  with the refactors `003` and `004` deferred (`entry_commits`' own pattern, `changed`'s
  length, `review`'s leads comparing paths as written).
- Entry boundaries: an indented heading and an HTML comment (close-r1 F3).
- Encodings and names: a non-UTF-8 Python file at the base (F5); a public name with no
  ASCII word (F6).
- `devtools/sync.py:445` reads a `cat-file --batch` header's size without checking for a
  `missing` reply; an IndexError there is not turned into "upstream-unreadable" (found in
  the reread of `sync.copies` for this close; not reproduced).
- Q2/Q9, Q8, Q12, Q13 as the sweep says.

## Refactoring review

| Record | Its answer | Deferred | Row |
|---|---|---|---|
| `001` | Executed: `DATING`, one set | none | -- |
| `002` | Executed: `answered`, one function | `changed` and `review` reach the rule by two roads | **Carried**, the second proposed issue |
| `003` | Executed: `FIELD`, `NOT_FIELDS` | `entry_commits` keeps its own dating pattern; `changed` is 117 lines with four inner functions | **Carried**, the same issue |
| `004` | Executed: `ENTRY`, the two parser keys | `tests` and `duplicates` paths are compared as written in `review`'s leads | **Carried**, the same issue |

## The index, for this close

`review` listed `handoff.notes` and `sync.copies` as older than their code (carried as J7
from the issue-sweep close). Both were read beside their module's diff since that edit,
at `d82c87e`: `sync.copies`' `does` and `verbs` now say that `sync.py` reads the upstream
commit's tree with git's modes (no longer `git archive`) and what counts as the checkout's
own work; `handoff.notes` keeps its words with a `reread:` line. `review` now lists none.

## Residuals the close accepts

- close-r1 F1 to F6, until the owner rules on them.
- A file whose name holds a newline is not read by `files_at` (`004`, decisions, F5).
- A folder named in `modules:` without its `/` covers nothing (Q12).
- The suite ran on macOS with Python 3.14 (591 passed) and, through `ci_local.sh`, on Linux
  with 3.11 and 3.14, where four tests are skipped (`004`); GitHub's three `gates` jobs on
  `d82c87e` (macOS 3.14, Ubuntu 3.14, Ubuntu 3.11; run 45879939530) report `588 passed, 3
  skipped` each.

## Boundary -- what this close does NOT establish

- That one reviewer's reading is more than that. Every round, the close's included, had
  Codex in the one seat, read-only; no round ran the suite.
- That the milestone was run as the lane requires. It had no plan, no plan review, no spec
  and no phase; `001-issue-50.md` lists what is missing, and nothing was written afterwards
  to fill it.
- That 0.1.8 is free of the deferred findings: it ships close-r1 F1 to F6.
- That the carried questions are answered, or that the proposed issues are wanted.
- That this record's final bytes, the README's, or the two index entries carry a review
  opinion: the close round read the draft.
- Anything posted: this close posts nothing to GitHub.

## Owner actions that remain

- Rule close-r1 F1 and F2: a 0.1.9 now, or the proposed issue.
- Rule the carried rows: Q2/Q9, Q8, Q12, Q13, and whether the other proposed issues are filed.
- Merge the pull request that holds this record.
