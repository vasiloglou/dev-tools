# Build: write the catalog for a codebase that has none

Use this when `docs/components/COMPONENTS.md` does not exist, holds only the starter
text, or covers a small part of the package. The result is a catalog an agent can search
by capability, a generated inventory, and a recorded list of whatever was left for later.

The build changes no code. Things you notice on the way (the same capability written
twice, a module nothing calls) are marked in the catalog and listed for the user; fixing
them is separate work.

## 1. Set up and generate what can be generated

1. Check the settings in `components_index.settings.json` beside the script:
   `package_dir` is the folder that holds the package (for example `src/myapp`), and
   `extra_source_dirs` lists other folders with source worth listing (scripts, tools).
   `docs_dir` is where the index is written (`docs/components` by default): if `docs/`
   is published as a site or scanned by documentation tests, put the index outside it or
   exclude it from the site. For a package of more than about 100 modules set
   `verb_list` to `shared`, so the generated verb list at the top of the catalog holds
   only the verbs two or more entries use.
2. Run `python3 scripts/components_index.py write`. The first run writes the starter
   catalog; every run writes `docs/components/modules/`, one page per top-level folder,
   with every public class and function, its signature and its first docstring line.
3. Run `python3 scripts/components_index.py stats`. The coverage line is your starting
   point (`0/N`), and the list under it is the work.

## 2. Read before you write

1. Read what the project says about itself: the README, any architecture or design
   document, the package's top-level `__init__.py`, the command-line entry points in
   `pyproject.toml`. Note the words the project uses for its own parts.
2. Run `python3 scripts/components_index.py draft > <scratch file>`. It prints one stub
   per module with its docstring summary, public names, what it imports, what imports it
   and which tests use it. `--by-importers` puts the most-imported modules first, and
   `--only <path>` prints one folder. Keep it outside `docs/components/`; it is working
   material, not a catalog.
3. Skim the `modules/` pages folder by folder. You are looking for the capabilities, not
   the files: "parse a config file", "retry a request", "render a report".

## 3. Decide the components

A component is one capability a planner would search for. It is not one file and not one
folder.

- **Group** the modules that together do one thing. A folder that does one thing is one
  entry with `modules: src/<package>/<folder>/` (the trailing `/` covers every file under
  it, including ones added later).
- **Split** a folder that does several unrelated things into several entries, each
  listing its own files. A single file is listed under one entry only: the entry for its
  main job, with its other jobs in that entry's `does` and `verbs` so a search still
  finds them; note it for the user as a file worth splitting. (For one file this rule
  wins over the "and" rule below, which is about separate files.)
- **A module that only re-exports** another under an old name goes with the component
  whose code it re-exports, with one sentence in `notes:`. It is not a component.
- **`__init__.py`.** One that defines names other modules import is its own entry, or
  goes with the component that owns those names. One that only re-exports goes with what
  it re-exports. One with a docstring only goes with the entry that holds the folder's
  public surface.
- **Examples and bundled scripts** inside the package are indexed like other code, with
  a `does` that starts "Example:", so a search hit is not mistaken for the real thing.
- **Name** each one `<area>.<capability>`: the area is the part of the system
  (`fs`, `report`, `cli`), the capability is what it does (`scan`, `rows`). Use the
  project's own words. The stub ids from `draft` are placeholders made from file names.
- **Size.** If you cannot say what an entry does in one sentence without "and", it is
  probably two entries. If you would write the same sentence for two entries, they are
  one. Two entries may share a verb ("sort by size" for the helper that sorts and for the
  report that uses it); give each the verbs that tell them apart as well.
- **Order.** Start with the modules the most other modules import (the `imported by`
  line in the draft): they are the shared code other work is most likely to rebuild.

For a package of more than about 40 modules, do not try to hold it all at once. Work one
top-level folder at a time, and see "Large codebases" below.

## 4. Write the entries, in batches

For each component:

1. **Open the code.** Read the module, not only its docstring: the docstring may be
   absent, out of date, or describe the intent rather than what the code does. Read the
   tests when there are any; they show how it is meant to be called.
2. Write the entry in the format in `SKILL.md` ("Entry format"):
   - `does`: one sentence saying what it does, in the words someone would search for.
     Name the main function or class in brackets when there is one obvious entry point.
   - `verbs`: every phrase a planner might type for this capability, synonyms included
     ("format size, humanize bytes, pretty print size"). The search matches whole words
     and knows only simple plurals, so write the other forms a searcher might use
     ("hidden files, dotfiles, skip hidden").
   - `status`: `canonical` unless you have evidence otherwise. Use `experimental` for
     code marked as such, `deprecated` for code the project says not to use, and
     `duplicate-of <id>` for the weaker of two implementations of one capability.
   - `modules`: the files or folders.
   - `tests`: the test files whose subject is this component, about six at most. Find
     them by the imports (the draft's "imported from tests and scripts" line), then by
     the function names, then by the command word for code that tests reach through the
     command line.
   - `checked: partial` (optional, free text) when you wrote the entry without reading
     all of its code; a later review starts with these.
   - Keep each line short: `does` about 120 characters, `notes` two sentences, `verbs`
     ten to twenty phrases. Function names belong in `verbs` or in brackets in `does`:
     only those two fields are searched. Underscores, hyphens and dots split words, so
     `run_bounded_process` is found by "run", "bounded" or "process".
3. After each batch (one folder, or about ten entries) run
   `python3 scripts/components_index.py write`. It refuses to write while an entry is
   invalid and prints why: a path that does not exist, a `TODO` left in `does` or
   `verbs`, an id used twice. Fix and rerun, then run `stats` and watch the number rise.

Do not write an entry from the file name alone. An entry that says what you guessed the
code does is worse than no entry: the search will send the next agent to the wrong place.

## 5. What you could not finish

Aim for every module to have a component. When the package is too large to finish in
one sitting, or a module is genuinely unclear:

```bash
python3 scripts/components_index.py stats --write-baseline
```

This records the modules still without a component in
`docs/components/unassigned-baseline.txt`. From then on `--check --strict` accepts those
and rejects any new one, and the list is only allowed to shrink. Tell the user how many
are in it and which folders they are in.

## 6. Add the end-to-end flows

When the components are in place, add a `### subsystem.<name>` entry for each main path
through the system: one for each main command or public entry point the README leads
with (usually one to eight). It says what happens, from input to output, when the
program does that job. `components:` lists the members; `flow:` gives them in call
order, joined by ` -> `. Write the flow from the code: start at the entry point and
follow the calls. The generated `uses:` lines and `graph.md` show which component
imports which, and are a check on your reading, not a substitute for it. When several
flows start at one shared entry point (a command-line dispatcher that imports every
command), the generated `members_uses:` of each subsystem lists the other flows'
components too; `flow:` is the line that says what this path reaches.

Then run `python3 scripts/components_index.py review` once. Two of its groups check the
build itself: a pair of components that import each other usually means a module was
put under the wrong entry, and a flow step that no earlier step imports means the order
is wrong or the step is reached through a component the flow leaves out.

## 7. Test the index by using it

1. Write down five to ten capabilities someone new to the project would ask for, in
   their words, not the code's. Take some from the README and from recent commit
   subjects.
2. Run `python3 scripts/components_index.py search --explain <words>` for each. The right
   component should be the first component in the list, and the words in brackets should
   show it matched on more than a word every entry shares (such as the project's main
   noun). A module listed above it is fine: modules are found by their docstrings.
3. When one misses, or is found on a common word only, fix the entry's `does` and
   `verbs`, never the query. Two limits are the tool's, not the entry's: several
   components that match the same number of words are listed in alphabetical order, so
   a short query may leave the right one below the fifth line (`--limit 20` shows it);
   and only whole words match ("look up" does not find "lookups"). Record those and
   move on; do not stuff an entry with verbs to win a tie.
4. Search for one thing the project does not do. The answer is `no component matched`,
   or hits that match one word of the query at most (`--explain` shows the count): some
   entry will share the project's main noun with almost any query. A component that matches most of the words claims too much in its `does` or
   `verbs`.

## 8. Finish

1. `python3 scripts/components_index.py write`, then
   `python3 scripts/components_index.py --check --strict`: both clean.
2. Write what you noticed in the code to `docs/components/REVIEW.md`, in the form
   [`review.md`](review.md) step 5 gives: capabilities written twice, modules nothing
   imports, files worth splitting, code with no tests. The groups that
   `python3 scripts/components_index.py review` prints are the starting list. These are
   suggestions; do not act on them here.
3. Show the user: the coverage line, the components by area
   (`python3 scripts/components_index.py list`), the baseline count, how many modules
   were read in full and how many in part, the searches you tried and what each
   returned, and the suggestions.
4. Commit the index files only (`docs/components/`), in one commit.
5. Propose, and make only with the user's go-ahead, in a second commit, what keeps the
   index current: `python3 scripts/components_index.py write` in the project's
   `after_apply` in `.devtools.toml` (check whether it is already there); the `changed`
   check in the project's CI or pre-PR routine (`SKILL.md`, "Before a PR"); and a line
   naming the index in the project's agent instructions (`CLAUDE.md`, `AGENTS.md`) so
   every session knows to search it first. These are the project's own files and may
   have rules of their own.

## Large codebases

Reading is the slow part, and it divides well. Writing does not.

- **Cost.** Every module is read by an agent. A trial on a package of 298 modules and
  130,000 lines used twelve readers and about three million tokens. Tell the user the
  size of the job before fanning out, and ask first when the project's rules require a
  go-ahead for parallel agents.
- **Decide the words first.** Before any reader starts, choose the area names and the
  recurring capability names (for example `<area>.command` for every command handler)
  and give the list to every reader. Otherwise each reader invents its own and you
  rename at the merge.
- **Cut the groups by size**, not by folder: about 10,000 lines (15 to 40 modules) per
  reader. Split a large folder, combine small ones, and cut the modules that sit
  directly in the package by subject (a layer map if the project has one, otherwise by
  what imports what). `draft --only <path>` prints one group's stubs.
- **Brief each reader** with [`reader-brief.md`](reader-brief.md), filled in. A reader
  writes its proposed entries to a scratch file outside `docs/components/` and returns
  a short summary; it does not edit the catalog.
- **One writer.** You merge the proposals into `COMPONENTS.md`, settle the names, and
  remove overlap between readers (two readers will both claim a shared helper). Every
  module ends under exactly one entry.
- **Check a sample.** A reader's entry is a claim about the code. A reader returns two
  lists: questions for the writer (a name, a placement, a merge) and claims it did not
  verify. Settle the first yourself. For the second, open the code when the claim is in
  `does`; beyond that, open the code for at least three entries per reader, weighted to
  the most-imported modules. Mark an entry you could not check `checked: partial`.
