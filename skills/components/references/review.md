# Review: the whole index against the code

The checks that run with every change test the form of the index: paths exist, new files
are claimed, generated pages match the source. They cannot tell whether an entry's
sentence is still true, whether two components are one, or whether the code the index
describes should exist. A review does that, from the top, and produces two things:

1. **A repaired index**, committed on its own.
2. **A list of suggested code changes**, in `REVIEW.md` in `docs/components/`, for the user to
   accept, defer or reject. The review makes none of them.

Run it when asked; when searches keep missing things that exist; before planning a large
piece of work (a milestone, several phases); after a large merge or reorganisation; and
when the `review` command's first group has grown long.

## 1. Get the leads

```bash
python3 scripts/components_index.py write
python3 scripts/components_index.py --check --strict
python3 scripts/components_index.py review
```

The first two print nothing when all is well; fix anything they report before going on.
In a project with rules of its own (`docs/components/rules.json`), also run
`python3 .claude/skills/components/scripts/rules_check.py check` with no base: every
`fail:` and `warn:` line is a lead of the kind "Rule broken" ([`rules.md`](rules.md)).
Ten are printed for a rule; `--format json` has the rest.
Note the commit you are reading the code at (`git rev-parse --short HEAD`) for the
report. The third prints groups of leads (the first 40 of each group; `review --all` prints
every one, and `review <area>` prints all the leads for the components whose id starts
with `<area>`). The leads cover what imports and names can show; they do not cover
unused functions inside a module, or wrong docstrings. A lead is a place to look, not a finding:
every one is checked in the code before it is acted on or written down. The absence of
a lead proves nothing either.

| Group | What it may mean | How to check |
|---|---|---|
| Descriptions older than their code | The entry no longer says what the code does | Read the entry, then `git log -p <commit>..HEAD -- <the entry's modules>`, with the commit the lead prints. An edit to `does` or `verbs` resets this lead, so an entry without one may still be out of date |
| Retired components that are still called | A consolidation was started and not finished | Read each calling module the lead names: can it call the replacement? If the retired entry's `notes` names no replacement, find it and add it |
| Retired components nothing calls | The retirement is finished and the code can go | Search for uses outside the package (`show <id>`, `git grep`), then suggest removing it |
| Components that import each other | A module sits under the wrong entry (an index repair), or the boundary in the code is in the wrong place (a suggestion) | Read the imports the lead names, up to three each way; `graph.md` and `show <id>` have the rest. Rerun `review` after repairing the entries: what remains is in the code |
| Loops of imports through three or more components | The same as a pair, spread over more entries: no one of them can be changed, tested or moved alone | Start from the pairs above; they are usually inside the loop. For a large group, `facts` lists every import inside it (`component_uses_in_cycle`, with the files under `evidence`): look for the few imports that point from a low-level component back up |
| Components nothing in the package imports | An entry point (fine; the lead says when a module defines `main`), or code nothing uses | Look for a command-line entry, a plugin registration, a dynamic import, a use from tests or scripts: `git grep` the module and its public names |
| Modules nothing imports, inside a component that is used | A file that sits under an entry it is not part of, or code nothing uses | The same search. If it is a capability of its own, give it its own entry, so the index shows nothing calls it |
| The same public name in two or three components | The capability was written twice | Read both. Same job: record it (`SKILL.md`, "Duplicate found"). Same word for two jobs: add `distinct_from: <other id>` to one entry with the reason in `notes:`. Either way the lead stops printing |
| Modules listed under more than one component | Two entries overlap | Decide which owns it, or whether the module should be split |
| Components that cover more than 12 modules | Several capabilities under one entry | Read the `modules/` page for the folder: can you name more than one capability? |
| Components with no tests listed | Tests exist and are not listed, or there are none | `git grep` the module name under the tests |
| Flow steps that no earlier step imports | The order in `flow:` is wrong, or the step is reached through a component the flow leaves out | Follow the calls from the entry point |
| Entries marked as checked in part | The entry was written without reading all of its code | Reread these first; remove the `checked:` line when done |
| Test files that import one component only and are not in its tests | The `tests:` line is incomplete | Open the test: does it test this component? Add it |
| No subsystem entries | The main paths through the system are not described | Add them as in [`build.md`](build.md) step 6 |
| Modules with no docstring | The module search and the inventory cannot describe them | Suggest a one-line docstring |
| Modules with no component | The baseline was never worked off | Assign them now (see [`build.md`](build.md)) |

## 2. Reread every entry

The leads cover what a script can see. The main work is to read each entry beside its
code, including the entries no lead names.

For each component, run `python3 scripts/components_index.py show <id>`: it prints the
entry, and for each module its names, what it imports, what imports it, and the tests
and scripts that use it. Then open the modules. Read the imports first (they show
whether the module belongs to this component), then the public functions the entry's
sentence is about; for a module over about 300 lines, read the outline before the body.
Say in the report which modules you read in full and which in part. Then ask:

- **`does`**: is the sentence true of the code today? Does it name what a planner would
  need to know, or only what the file is called?
- **`verbs`**: would someone looking for this capability type one of these? Is a public
  function here that none of the verbs would find?
- **`modules`**: does every listed file belong to this capability? Does a file elsewhere
  belong to it and sit under another entry, or under none?
- **`tests`**: do the listed files test this component? Is a test file named for one of
  its modules missing from the list? (The list is a pointer to about six files, not a
  coverage record.)
- **`status`**: is `canonical` still right? Has the project stopped using it?

- **`modules`, again**: is a listed file imported by none of the component's other files
  and by nothing else? It is a capability of its own, or unused.

For each subsystem, follow the calls from its entry point and compare with `flow:`
(the order in which components are first reached; loops and conditions go in `notes`). If
a main path through the system has no subsystem entry, add one as in
[`build.md`](build.md) step 6.

Repair as you go: edit the hand-written fields, split an entry that holds two
capabilities, merge two that are one, assign unclaimed modules. Regenerate after each
batch (`python3 scripts/components_index.py write`). Splitting or merging entries
rewrites the generated `uses` and `used_by` lines of every entry that touches them and
much of `graph.md`, so expect a wide diff from a small repair.

On a large catalog, fan out the reading by area as in [`build.md`](build.md), "Large
codebases": readers return proposed entry text and findings with evidence; one writer
edits the catalog; a sample of each reader's claims is checked in the code.

## 3. Test the search

As in [`build.md`](build.md) step 7: five to ten capabilities in a newcomer's words,
`search --explain`, the right component first among the components, the entry fixed when
it is not. Include the searches that are known to have missed: ask the user, and in a
phase project look at the plans for capabilities that were built new although they
existed (`grep -rn "new_component:" .planning/phases/*/*-PLAN.md`). When you cannot ask
(you are running unattended), say so under "Not confirmed" in the report.

## 4. Write down the code changes you would suggest

While rereading you will see things the index cannot fix. Record them; do not fix them,
and do not write the todo that Update mode asks for: `REVIEW.md` is the record until the
user accepts a suggestion.

| Kind | What you saw | What to suggest |
|---|---|---|
| Duplicate | One capability implemented twice | Which one stays and why, and the callers that would move. Record it in the catalog now (`SKILL.md`, "Duplicate found": `duplicate-of` for a whole module, `duplicates:` and `notes:` for one function) |
| Unused | A module or public function with no caller and no entry point (one that only its own tests call counts) | Remove it, after the owner confirms nothing outside the repository uses it |
| Unfinished retirement | A `deprecated` or `duplicate-of` component still has callers | The callers, and what each should call instead |
| Tangle | Two components import each other | The function or class to move, and where |
| Rule broken | `rules_check.py check` prints a `fail:` or `warn:` for one of the project's own rules | The import to move or remove; or, when a module sits under the wrong entry, the index repair |
| Misplaced | A module used only by another component, or sitting in the wrong folder | Where it belongs |
| Too large | A component or module that holds several capabilities | Where to cut it |
| Untested | A component with no tests | The behaviour most worth pinning first |
| Undescribed | A docstring that is missing or wrong, or a README that does not mention a capability | The one-line docstring, or the paragraph |
| Private name used elsewhere | Another module imports a name that starts with `_` | Make it public, or move the caller's need into the owning module |
| Defect | Behaviour that looks wrong, seen while reading | The input that shows it, what happens and what you expected. A review does not hunt for these, but does not keep quiet about one it sees |

Rules for a suggestion:

- **Checked in the code.** You have read the lines it is about. For "unused" you have
  searched for dynamic uses (`git grep` the name as a string, entry points, plugin
  tables) and say what you searched.
- **Specific.** It names files and functions, says what would change, and says what
  could break (the component's `used_by` is the list of callers).
- **Sized.** Small (one file, no caller changes), medium (callers change), or large
  (a design decision).
- **Honest about doubt.** If you could not confirm it, say what you would need to know.

## 5. Write the report

`REVIEW.md` in `docs/components/` is replaced at each full review. A review of one area
writes `REVIEW-<area>.md` beside it and leaves the full report alone. Keep it
short enough to read in one sitting:

```markdown
# Component index review, <date>

Scope: <the whole index | the components whose id starts with ...>.
Code read at commit <HEAD before this review>. <N> components and <S> subsystems after the repair (<n> and <s> before), <M> modules
(<k> read in full, <j> in part).

## What was repaired in the index
- <entry>: <what changed and why>, one line each

## Suggested code changes
| # | Kind | What | Where | Size | Checked how |
|---|---|---|---|---|---|
| 1 | Duplicate | `export.humanize_bytes` repeats `format.sizes` with different rounding | src/shelf/export.py:7, src/shelf/units.py:12 | small | read both; one caller, `to_csv` |

### 1. <title>
<Two to five lines: what is there, what you suggest, what could break.>

## Not confirmed
- <lead you could not settle, and what would settle it>

## Searches tried
- "<words>" -> <first hit>
```

## 6. Finish

1. `python3 scripts/components_index.py write`, then `--check --strict`: clean.
2. Commit the index and the report only (`docs/components/`). No source file is in the
   commit.
3. Show the user the suggestions, most valuable first, and ask which to take up. (When
   you are running unattended, the report is the hand-over; say in your final message
   that nothing was chosen.) An
   accepted suggestion becomes work in the project's own way: a todo or a phase in the
   phase workflow, a row in a milestone plan, or an ordinary PR. A rejected one is
   removed from the report with a line in the entry's `notes:` when the reason is worth
   keeping (for example "kept separate from `format.sizes` on purpose: binary units").
