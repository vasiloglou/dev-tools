---
milestone: reread-answers
station: "the owner's rulings of 2026-11-26: findings F3, F4 and F5 of pr-51-r1 repaired, a regrouped module asks both components, and part 4 of issue 50"
skill: "n/a -- made outside process-phase, as the rest of this milestone was"
scope: rulings
date: 2026-11-26
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "578 passed in 373.63s (0:06:13)"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (31249da): 28 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "devtools/ci_local.sh"
    exit: 0
    output: "macos-3.14: 578 passed; linux-3.11: 574 passed, 4 skipped; linux-3.14: 574 passed, 4 skipped"
  - command: "python3 devtools/release_plugins.py status"
    exit: 1
    output: "0.1.8 is ready: after the merge, run `release_plugins.py tag` on main"
    note: "exit 1 is this command's way of saying a release is due; 0.1.8 is not tagged"
evidence:
  - path: .planning/reviews/pr-51-r1/review.md
    sha256: ed61c285253c1d56e6b9cc83ce96e14353be14f4cd603968d65a4b91f49fe390
  - path: .planning/reviews/pr-51-r1/FINDINGS.md
    sha256: 1fe8e39151fd27601e90f77eae01e70fc9358698999753af59aee917688a4a13
  - path: .planning/milestones/reread-answers/notes/issue-50.md
    sha256: b9e52bbfa75d714c492d8d082eb8dae109d92a4cd393c56e33690b8b7c944bea
  - path: skills/components/scripts/components_index.py
    sha256: 3480301a97a4a2064927f280798d0cc5dfde5fca0ddb656ddb32623c1f2c32e3
  - path: tests/test_tools.py
    sha256: 130421b3a1a3e2950d5d805b9899389d58ed657dd9bca2c229043d0c3a59eeb3
  - path: skills/components/SKILL.md
    sha256: 4f1e833d9a4709b0996f969fbb6e185e8ba4ac7e0d06fadb8cfc6cde75380daa
  - path: docs/components.html
    sha256: e7e3c3e8c395ef1cb197122ee8171e7cde42af9632a1a306fbd1223c51f08432
  - path: .devtools/components/COMPONENTS.md
    sha256: 435a672dc2e07cfcbee2bcca59c6e2bff5505d39b47be9cebdd67bce50c9e65c
  - path: .planning/milestones/reread-answers/001-issue-50.md
    sha256: 7b4b36272a1b399125d71ef96f4af82e1decc678745d81b507b883fc25c90d2a
  - path: .planning/milestones/reread-answers/002-pr-51-r1.md
    sha256: 39948ff1e752e3e14b45a1077d78f30f1cf1db5130ca138f1b7c2b990e6e4703
---

# Claim

At `c6d55ca`, pull request vasiloglou/dev-tools#51 also holds what the owner ruled on
2026-11-26: findings F3, F4 and F5 of review `pr-51-r1` are repaired, a module regrouped from
one component into another without an edit asks both for a reread, and part 4 of issue 50 is
built (a component's `reread:` line names the public names its entry leaves out). Each has
tests in `tests/test_tools.py`, fifteen of which fail on the script of `2b22500`, and the six
gates above ran on that commit with the exits shown. **These bytes are unreviewed**: the only
round, `pr-51-r1`, read `8475b62`.

## What this record follows on

`002-pr-51-r1.md` left Q5 (F3 to F5), Q6 (a module moved without an edit) and Q7 (a second
round) to the owner, and `001-issue-50.md` left Q1 (part 4 of issue 50) and Q3 (tagging
0.1.8). The owner has ruled on all five. This record covers the code that follows from Q1, Q5
and Q6. Q7, the merge and the tag come after this commit and are not in this record.

The decision of `002-pr-51-r1.md` that a module moved without an edit asks nothing is
replaced by the owner's ruling. That record is not edited.

## The owner's words

Said to this session directly, in its own conversation, on 2026-11-26.

This session had listed five "Decisions waiting on you": whether to repair F3, F4 and F5
before merging; whether a file moved between components without being edited should trigger
a recheck ("I chose no"); whether to run a second review round on the repairs; whether to
merge the pull request and release 0.1.8; and part 4 of the original issue, "which I left
open as instructed".

| What the owner was asked | What the owner said | What it was taken to cover |
|---|---|---|
| The five decisions above | "yes to all" | Repairing F3, F4 and F5; a second review round; merging pull request 51 and tagging 0.1.8. Two of the five were not yes-or-no questions, so the session asked them again |
| "A file moved from one component to another with no edit to the file: should the strict check ask both components to reconfirm their descriptions?" (the choices: "Keep: ask nothing", "Change: ask both") | "Change: ask both" | The rule of Q6 |
| "Part 4 of issue 50 (the reread line also names new public functions that the description does not mention): build it now, or leave it for later?" (the choices: "Later, own pull request", "Now, in pull request 51", "Do not build it") | "Now, in pull request 51" | Building part 4 on this branch, before the second round |

No plan and no spec were written for this work and none was approved. The rulings above are
the approval there is. Nothing in them covers posting to GitHub, and nothing was posted.

## What changed, in `c6d55ca`

14 files, +456 −159: `skills/components/scripts/components_index.py`, `tests/test_tools.py`,
`skills/components/SKILL.md`, `skills/milestone/process-phase/SKILL.md`,
`skills/phase/process-phase/references/close.md`, the built copies of the four product files
in `plugins/`, `docs/components.html`, and dev-tools' own catalog and its generated page.

**Part 4 of issue 50. What to look for.** A component's `reread:` line now ends with a lead:

    reread: core.rows (only modules edited): src/widget/parse.py; new public names not in does or verbs: parse
    reread: core.sizes (only modules edited): src/widget/parse.py; removed public names still in does or verbs: parse

- The names are the public top-level classes and functions of the listed `.py` files: what
  the entry's files defined at the base, against what they define now. A name that moved
  between two files of one component is in neither list.
- A name is "in does or verbs" when each of its words is, read as `search` reads prose
  (`tokens`: lower case, plural endings dropped, the stopwords left out), with underscores
  and capital humps as word breaks. `format_count` is in "Format a byte count".
- Private names and methods are left out. Eight names are shown, then `+N more`.
- The lead fails nothing: the exit codes are those of the line it is on.
- A subsystem's line has no lead.

**Q6. A module regrouped without an edit.** A component is asked when its `modules` line took
a file in or gave one up, whether or not the file differs: `code_paths` in `changed`. The
component that gave the file up and the one that took it are both asked. An entry written in
the change is still not asked, so a module split out into a new entry asks the one that gave
it up only. The same files named another way (reordered, or a folder that holds the same
files) ask nothing.

**F3. A line that is no field.** `parse_components` keeps, as `_rest`, the lines of an entry
that are no field (a key the reader does not take, such as `owner2` or `audit-owner`, or no
key at all), up to the next heading or generated block. `changed` reports an edit to them as
`only other lines edited`, or `only notes, other lines edited`. Blank lines are not an edit.
The field reader is unchanged: such a line is still no field. The skill's table of fields
now says a field's key is lower-case letters and underscores.

**F4. The sentence about a subsystem's line.** The `changed` row of the command table in
`skills/components/SKILL.md` now says the line is for a subsystem with a member whose code
changed while none of the subsystem's own four lines was edited, whether or not that
member's entry was answered. The "Reread" bullet of `docs/components.html` names the
advisory line. No code changed for F4.

**F5. A SHA-256 repository.** `entry_commits` reads a commit id of 40 or 64 digits from
`git blame`, so `review` dates entries in a repository made with `--object-format=sha256`.

## Decisions

| Decision | What was chosen | Why | Who |
|---|---|---|---|
| A module moved to another component without an edit | Both are asked; `changed --strict` exits 1 until both are answered | The ruling | The owner |
| `test_changed_does_not_call_a_regrouped_import_new` | Keeps its subject (no `warn:` for a regrouped import) and now expects exit 1, with the line of the component that gave the module up; the plain form still exits 0 | The ruling changes what the strict form refuses; the session that ran the round had named this as the choice | This session |
| A file taken in that no entry held (an unassigned module) | The entry that took it is asked | Its code is more than it was. The same rule: its `modules` line took a file in | This session |
| Which removed names to list | The ones `does` or `verbs` still speak of | The issue's sentence reads "the public names the change added to (or removed from) the entry's modules that appear nowhere in its `does` and `verbs`". A removed name the entry never spoke of asks for nothing; one it still speaks of is a sentence that may say too much. **This departs from the letter of the issue** | This session |
| When a name is "in" `does` or `verbs` | Each of its words is there, by `tokens` | The issue says "no verb finds"; `search` finds by shared words. Asking for the identifier itself would list nearly every new function, since verbs are prose | This session |
| Whether the entry's id counts | No: `does` and `verbs` only | The issue's words. `search` also reads the id, so a name whose only word is the id's is listed though a search would find the entry | This session |
| Which files' names are compared | The files listed on the line: those that differ or were regrouped | The component's other files are the same on both sides. A name that one of them also defines is still listed as new | This session |
| A lead on an answered entry | None: the entry has no line | The issue: "when `changed` prints a `reread:` line, add..." | This session |
| F3: widen the field reader, or keep the lines | Keep the lines (`_rest`), and say in the skill which keys are fields | A wider reader would make fields of lines every project's catalog has treated as prose since `0e0e52f`, in every command. The label is the only thing that was wrong | This session |
| What `_rest` holds | The entry's lines up to the next heading (`#`) or generated block (`<!--`) | What follows an area heading is the catalog's prose, not the entry's | This session |
| F4 | The sentence is repaired; the behaviour stays | The ledger: "the pull request's test expects the script's behaviour, so the repair is to the sentence" | This session |
| F5's test | A real repository made with `git init --object-format=sha256`, not porcelain text in memory | It runs `review` as a project would. Needs git 2.29 or newer; the three CI jobs have it | This session |
| The shared fixture `code_moved` | Its change now adds `format_count`, a name the entry "Format a byte count" speaks of, in place of `parse` | The earlier tests of this pull request compare the line of that fixture exactly; with `parse` each would carry part 4's lead. They keep their own subject, and the lead has tests of its own | This session |
| The plugin version | Stays 0.1.8 | 0.1.8 is not released. This session ran `release_plugins.py bump`, which raised it to 0.1.9, saw that a bump always raises, and set it back before the build | This session |

## The tests, red and green

Red: the tests of `c6d55ca` run against the script of `2b22500`
(`git show 2b22500:skills/components/scripts/components_index.py` written over the working
copy, then the new script restored).

    $ uv run --no-project --with pytest python -m pytest tests/test_tools.py -q -k "reread or changed or regrouped or review"
    FAILED tests/test_tools.py::test_changed_does_not_call_a_regrouped_import_new
    FAILED tests/test_tools.py::test_changed_names_every_other_field_that_was_edited
    FAILED tests/test_tools.py::test_changed_asks_the_component_that_gave_up_a_deleted_module
    FAILED tests/test_tools.py::test_changed_asks_both_components_when_a_module_moves_from_one_to_the_other[True]
    FAILED tests/test_tools.py::test_changed_asks_both_components_when_a_module_moves_from_one_to_the_other[False]
    FAILED tests/test_tools.py::test_changed_asks_nothing_when_modules_names_the_same_files_another_way
    FAILED tests/test_tools.py::test_changed_asks_a_component_that_takes_in_a_module_no_entry_held
    FAILED tests/test_tools.py::test_changed_says_an_entry_was_edited_when_the_edited_line_is_no_field[- audit-owner: caf\xe9\n-- audit-owner: \u0394\n-only other lines edited]
    FAILED tests/test_tools.py::test_changed_says_an_entry_was_edited_when_the_edited_line_is_no_field[- owner2: caf\xe9\n-- owner2: \u0394\n-only other lines edited]
    FAILED tests/test_tools.py::test_changed_says_an_entry_was_edited_when_the_edited_line_is_no_field[Kept for the report.\n-Kept for the report and the export.\n-only other lines edited]
    FAILED tests/test_tools.py::test_changed_says_an_entry_was_edited_when_the_edited_line_is_no_field[- notes: One.\n- owner2: caf\xe9\n-- notes: Two.\n- owner2: \u0394\n-only notes, other lines edited]
    FAILED tests/test_tools.py::test_review_dates_an_entry_in_a_sha256_repository
    FAILED tests/test_tools.py::test_changed_names_the_public_names_the_entry_does_not_speak_of
    FAILED tests/test_tools.py::test_changed_names_the_removed_names_the_entry_still_speaks_of
    FAILED tests/test_tools.py::test_changed_shows_eight_names_and_counts_the_rest
    15 failed, 63 passed, 105 deselected in 94.71s (0:01:34)

Green, the same command with the new script:

    78 passed, 105 deselected in 97.62s (0:01:37)

Of the fifteen:

- **Q6**, five: the regrouped import, the two cases of a module moved from one component to
  the other (both also carry part 4's lead), the folder that takes more files in, and the
  unassigned module taken in.
- **F3**, four: `audit-owner`, `owner2`, a line with no key, and a field and such a line
  edited together. Three more cases hold before and after (a real field, blank lines, prose
  under the next heading).
- **F5**, one.
- **Part 4**, three: the new names, the removed names, the eight shown.
- Two earlier tests whose expected line changed: `test_changed_names_every_other_field_that_was_edited`
  (the file taken in is named beside the one edited) and
  `test_changed_asks_the_component_that_gave_up_a_deleted_module` (the removed name the
  entry still speaks of).

`test_changed_does_not_name_a_public_name_that_moved_inside_the_component` is new and holds
before and after. F4 has no test: it is a sentence.

## Gate output (verbatim)

On `c6d55ca`, with `origin/main` at `31249da`. The test suite ran in the working tree
before the commit, on the bytes the commit holds; the four index, plugin and release commands
ran in the working tree at the commit, with the ledger rows, the README and this record not
yet committed. No test reads `.planning/`. `ci_local.sh` ran its three jobs on a clean clone
of `c6d55ca`.

    $ uv run --no-project --with pytest python -m pytest tests -q
    578 passed in 373.63s (0:06:13)
    (exit 0)

    $ python3 devtools/build_plugins.py --check
    (exit 0)

    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (exit 0)

    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main --strict
    changed against origin/main (31249da): 28 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    (exit 0)

    $ devtools/ci_local.sh
    ci_local: head c6d55ca, base origin/main 31249da, in <tmp>/dev-tools-ci.vql3gt
    macos-3.14: exit 0, 578 passed in 251.99s (0:04:11) (<tmp>/dev-tools-ci.vql3gt/macos-3.14.log)
    linux-3.11: exit 0, 574 passed, 4 skipped in 112.30s (0:01:52) (<tmp>/dev-tools-ci.vql3gt/linux-3.11.log)
    linux-3.14: exit 0, 574 passed, 4 skipped in 124.32s (0:02:04) (<tmp>/dev-tools-ci.vql3gt/linux-3.14.log)
    (exit 0)

    $ python3 devtools/release_plugins.py status
    version in the tree: 0.1.8
    released: 0.1.7 (plugins-v0.1.7)
    6 plugin file(s) changed since plugins-v0.1.7
    0.1.8 is ready: after the merge, run `release_plugins.py tag` on main
    (exit 1)

The `ci_local.sh` lines are edited in one respect: the temporary folder of the machine it
ran on is written `<tmp>`. Its logs are outside history and were not kept.

dev-tools' own index: `components.index` has its `does` and `verbs` edited for this change.
It was already answered against `origin/main` by the earlier commits, so the strict form
prints no line for it. Against the pushed head, `changed --base 2b22500 --strict` prints
`reread: subsystem.rule_check (entry not edited): its members changed: components.index`
and exits 0.

## The standing design rules, for this change

| Rule | Where it stands |
|---|---|
| A script change comes with a test | `changed`, `parse_components`, `entry_commits`, `public_names` and `name_words` of `components_index.py`; the tests quoted above as failing on `2b22500`'s script |
| The plugins are rebuilt, and released under a new version | Rebuilt at 0.1.8, which is not released; `build_plugins.py --check` exited 0. Not tagged at this commit |
| A wording change says what prompted it | Review `pr-51-r1`, F3 ("any other key") and F4 (the subsystem clause and the site's bullet); the owner's ruling on Q6 (the sentence "A file moved to another entry without an edit asks nothing" is gone); part 4 (the lead is described where the line is) |
| Shared skills stay general | The sentences added hold in any project with a component index |
| Both agents read the same file | The changed skill files name no tool. Built for both plugins; not run in Claude Code or in Codex |
| Captures on the site are real output | No capture was replaced. The capture in `docs/components.html` shows `reread: fs.scan (entry not edited): src/shelf/scan.py` for a commit that changed what a scan leaves out. The demo project it came from is not in this repository, so whether that commit added a public name the entry does not speak of, which would now add a lead to that line, was not checked |
| The page that describes it is updated too | `docs/components.html`, the "Reread" bullet: the names, and the advisory line of F4 |

`examples/components-check.yml` and the `--strict` help string were read and needed no
change: neither says what makes a component's code count as changed.

## Refactoring review

- **Executed:** the field pattern is one constant, `FIELD`, and the keys `parse_components`
  adds to an entry are one set, `NOT_FIELDS`, which `changed` and `show` both leave out.
- **Not done:** `entry_commits` has its own pattern for a dating line, because it also asks
  for a word after the colon. `changed` is now 117 lines with four inner functions;
  splitting it is a change of its own.

## Boundary -- what this result did NOT establish

- **No one has reviewed `c6d55ca`**, nor `0c3e0b3` before it. The owner has asked for a
  second round; it is run after this commit and is not in this record.
- The lead is a lead. A name it lists may need no verb (a helper that is public by
  accident), and a capability that changed without a name changing is not listed.
- The lead was not run on the project issue 50 came from, where the 29 descriptions found
  wrong were. Whether it would have named them is not established.
- A regrouping of `modules:` lines now fails `changed --strict` in every project that gates
  on it, until both entries are answered. No such project was run.
- F5's repair was run on a repository of two commits. `rules_check.py` and the other
  scripts were not run in a SHA-256 repository.
- The built plugins were not installed and run in Claude Code or in Codex.
- The gates above ran on `c6d55ca`. The commit that adds this record changes files under
  `.planning/` only; the runs made after it are in the pull request, not here.

## Open questions

| # | Question | Whose |
|---|---|---|
| Q8 | Issue 50 asked for removed names "that appear nowhere" in `does` and `verbs`; this change lists the removed names that are still there. Is that what is wanted? | The owner |
| Q9 | dev-tools' own gate still runs the plain `changed --base origin/main` (Q2 of `001-issue-50.md`). Should it run `--strict`? | The owner |
| Q10 | Does the milestone get a close (the rest of Q4 of `001-issue-50.md`)? | The owner |
| Q11 | Closing issue 50 once part 4 is merged: a post to GitHub | The owner |

Answered since `002-pr-51-r1.md`: Q1 (build part 4 here), Q3 (tag 0.1.8 after the merge),
Q5 (repair F3 to F5), Q6 (ask both), Q7 (run a second round).

## Refuted premises

- `002-pr-51-r1.md`, under "Decisions": a file moved from one component to another without
  an edit asks nothing, because no file differs and an existing test says a regrouping
  passes the strict form. The test recorded what the script did, not a ruling. The owner
  ruled the other way, and the test now expects the refusal.
- This session's own, while writing part 4's tests: that a file which did not parse at the
  base would give the lead no names. `changed` stops before that, with the syntax error, as
  it did before this change (the import graph of the base reads the same text). The test was
  dropped and the guard it was written for removed.
- This session's own: that `release_plugins.py bump` leaves the version alone when the
  version in the tree is already ahead of the last tag. It raises it every time.
