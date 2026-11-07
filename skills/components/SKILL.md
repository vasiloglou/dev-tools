---
name: components
description: The project's component index (docs/components/), which says what already exists in the project and its dependencies. Consult mode searches it by capability (scripts/components_index.py search) and records a reuse / adapt / reject decision. Update mode edits entries, assigns new modules, marks duplicates, regenerates, and checks the index against the files a change touched before a PR (changed). Build mode writes the catalog for an existing codebase that has none. Review mode rereads every entry against the code, repairs the index and lists suggested code changes (duplicates, unused code, tangled components) without making them. Use before planning a phase, before writing any new module, class or function, before briefing a coder, whenever you add, move, retire or duplicate code, before opening a PR, when a project has no component index yet, and when asked to audit, refresh or clean up the index. Also use when asked "does the project already have X?".
---

# components

An agent that cannot search by capability rebuilds what the project, or one of its
dependencies, already has. The component index makes existing code findable by what it
does; this skill is how you use and maintain it. The entry format is defined in
"Entry format" below: it is exactly what the index script parses and validates.

| Mode | When | Where |
|---|---|---|
| **Consult** | Before planning or writing code | "Consult" below |
| **Update** | With every change that adds, moves or retires code, and before a PR | "Update" below |
| **Build** | The project has no catalog, or most modules have no component | [`references/build.md`](references/build.md) |
| **Project rules** (optional) | The project has rules of its own about what may use what | [`references/rules.md`](references/rules.md) |
| **Review** | Asked to audit the index; searches keep missing; before planning a large piece of work; after a large merge | [`references/review.md`](references/review.md) |

Paths below assume the default settings (`docs_dir` = `docs/components`, script at
`scripts/`). A project changes them in `components_index.settings.json` beside the script
(`package_dir`, `import_prefix`, `extra_source_dirs`, `docs_dir`, `script_path`, `verb_list`).

| File | What it is | Edit? |
|---|---|---|
| `docs/components/COMPONENTS.md` | Subsystems (end-to-end flows that combine components) and one entry per capability | By hand, except the generated verb block and the `uses`, `used_by`, `part_of` and `members_uses` lines |
| `docs/components/graph.md` | Every component's full `uses` / `used_by`, with up to three importer -> imported module pairs per edge | Never; generated |
| `docs/components/modules/<group>.md` | Every module, public class, function and method, with signature, line, first docstring line and the component ids that own the module. One page per top-level folder of the package (`_root.md` for modules directly in it) and one per extra source directory | Never; generated |
| `docs/components/external/<distribution>.md` | Public top-level classes and functions of the selected dependency modules, with the installed version | Never; generated from `external.toml` |
| `docs/components/external.toml` | Which dependency modules are listed. Optional: without it no dependency is indexed | By hand |
| `docs/components/layers.toml` | Which areas may use which: a rank for each area and forbidden pairs. Optional; `facts` reads it (see "Project rules" below) | By hand |
| `docs/components/unassigned-baseline.txt` | The package modules no component covers | Only with `stats --write-baseline` |

Commands are written `python3 scripts/components_index.py …`. Any Python 3.11 or newer
runs it; the script parses source files and never imports the project's package. A
project that lists libraries in `external.toml` runs it with the interpreter those
libraries are installed in (usually `.venv/bin/python`; in a worktree without `.venv`,
the main checkout's), because writing and checking read their installed versions.
`search`, `stats`, `draft` and `review` need no dependency installed. `write` and
`--check` print nothing when all is well; `stats` prints the coverage line.

| Command | What it does |
|---|---|
| no command, or `write` | Validates the catalog, then writes `modules/`, `external/`, `graph.md` and the generated parts of `COMPONENTS.md`, and deletes generated pages it no longer produces. An invalid entry prints the errors, writes nothing and exits 1 |
| `init` | Writes a starter `COMPONENTS.md` with the entry format; never overwrites one. `write` does the same on its first run in a project that has no catalog |
| `--check` | Writes nothing. Prints `stale or missing: <path>` for each generated file that differs, plus every validation error; exits 1 if there is any. With `--strict` it also prints `no component: <path>` for each package module that no entry covers and is not in `unassigned-baseline.txt`, and exits 1; use `--check --strict` when closing a phase. Cannot be combined with a command |
| `search <words> [--limit N] [--explain] [--no-cache]` | Ranks subsystems, components, recorded dependency names and modules by the number of query words they share (5 hits by default). Prints `<kind> <id>: <summary>` (a retired component shows its status after the id and, on a tie, comes after the others), a `flow:` line under a subsystem, under a module hit one indented `symbol <module>.<name> (line N): <summary>` line for each class, function or method whose name, signature or docstring shares a word with the query, a private one marked `(line N, private)` (those sharing the most words first, the first 5, then `+N more symbol(s)`), `no component matched: …` when no component or subsystem matched, and the coverage line. `--explain` adds the matched words after the id (`component fs.scan [file, hidden]: …`, also on symbol lines), which shows a hit that matched on one common word only |
| `stats [--write-baseline]` | Prints the coverage line, then each package module no component covers. `--write-baseline` records that list in `unassigned-baseline.txt` and refuses when it holds a module the recorded list did not. Files under a `tests` or `fixtures` folder and files named `fake_*` are not counted as package modules |
| `list [<area>]` | Prints the ids by area, each with its `does` |
| `draft [--only <path>] [--by-importers]` | Prints one stub entry for each package module no component covers: an id, the module's docstring summary after `TODO`, the test file of the same name when there is one, and indented lines with its public names, what it imports, what imports it and the tests and scripts that import it. `--only` keeps the modules under one path; `--by-importers` puts the most-imported first. Writes nothing. A `does` or `verbs` that still contains `TODO` is a validation error, so a stub cannot be kept as it is |
| `changed [--base <ref>] [--strict]` | Compares the working tree with its merge base with `<ref>` (default `main`), untracked files included. Prints `fail:` for every validation error, every stale generated file and every new package module with no component (the baseline does not excuse a new file); `warn:` for a new import of a `deprecated` or `duplicate-of` component; `reread:` for each entry whose modules changed while its hand-written fields did not, and each subsystem with such a member; then a summary line. Exits 1 on any `fail`, and with `--strict` on any `warn`. Needs git |
| `facts [--base <ref>] [--out <file>]` | Prints the catalog and the import graph as one JSON document of facts, for a rule checker (see "Project rules" below): which components are listed, their status, area and tests, which component uses which, which of those imports lie inside a loop, the members of each subsystem, and the ranks and forbidden pairs of `layers.toml`. With `--base` the catalog and the code are those of the merge base with `<ref>`; the layers are always today's. Needs no checker installed |
| `show <id>` | Prints one component as a reader needs it: the entry, then each of its modules with its length, public names and their lines, the private names and constants it also defines, the package modules it imports and is imported by (each with its component), and the files in `tests/` and the extra source directories that import it |
| `review [<area> …] [--all]` | Prints leads for a review, in groups: descriptions older than their code (commits to the modules since the entry's `does` and `verbs` last changed, with the commit to compare from), retired components that are still called, retired components nothing calls, components that import each other, loops of imports through three or more components, flow steps that no earlier step imports, entries marked `checked: partial`, components nothing imports, modules nothing imports inside a component that is used, the same public name in two or three components (pairs recorded under `duplicates:` or `distinct_from:` are left out), modules under more than one component, components over 12 modules, components with no tests listed, test files that import one component only and are not in its `tests:`, modules with no docstring, modules with no component, and a line when the catalog has no subsystem. Every group is printed with its count, the first 40 leads of each; `--all` prints them all, and `review <area>` (an id or the start of one, such as `datasets`) prints every lead that names a component of that area. Writes nothing and always exits 0. The first group needs git |
| `--root <dir>` | Runs against another checkout |
| `--no-cache` | Before the command: parses every source file and ignores what earlier runs kept. After `search` it means the same |

The search compares whole words (lower case, stop words dropped, a final "s" removed and
a final "ies" read as "y"), not meanings. A component is matched on its id, `does` and `verbs`; a module on its name,
its whole docstring and the signatures and whole docstrings of its symbols, the private
ones too (every line, not only the summary the pages show, so a capability named deep in
the docstring of a helper is found); a dependency name on its own summary plus the `does` and `verbs` of any component
that lists it under `external:`.

Every command keeps what it read from each source file in a cache outside the checkout
(`$XDG_CACHE_HOME/components-index/`, by default under `~/.cache`) and parses a file
again only when its content changed. `write`, `--check`, `changed`, `review`, `show`
and `draft` read every file and look it up by a digest of its content, so they print
what a full parse would print; `search` also skips reading a file whose size and time
are unchanged. `--no-cache` before the command ignores the cache and saves nothing;
the result is the same.

## Entry format

`COMPONENTS.md` is a list of `###` sections; a `##` heading between entries is kept and can group them. Each field is one line, `- <key>: <value>`;
a value never continues on a second line, and list values are comma-separated. A field
is written once: a validated field that appears twice is an error, and of a free-text
field written twice only the last is kept.

```markdown
### <area>.<capability>
- does: <one sentence saying what it does>
- verbs: <words and short phrases a planner would search for>
- in: <what it takes>
- out: <what it returns>
- status: canonical
- modules: src/<package>/<module>.py, src/<package>/<folder>/
- tests: tests/unit/<package>/test_<topic>.py
```

The id is two lower-case parts joined by one dot (each `[a-z][a-z0-9_]*`) and is unique.

| Field | Required | Content |
|---|---|---|
| `does` | yes | One sentence; searched |
| `verbs` | yes | Comma-separated; searched, and collected into the verb block |
| `status` | yes | `canonical`, `experimental`, `deprecated`, `external`, or `duplicate-of <existing id>` |
| `modules` | yes for a component | Repo-relative paths that exist: a `.py` file, or a folder ending in `/`, which covers everything under it. The value is empty only with `status: external`; the line stays |
| `tests` | no | Repo-relative paths that exist: the test files whose subject is this component (those named for its modules), about six at most, or a folder ending in `/` that holds only this component's tests. It tells a reader where to see the component used; it is not a coverage record |
| `duplicates` | no | Repo-relative paths, which must exist, of the modules that duplicate this component, in whole or in one function |
| `distinct_from` | no | Ids of existing components that look like this one and are separate on purpose (a reference implementation beside the production one, a fallback). `review` stops reporting a name the two share; say why in `notes` |
| `checked` | no | `partial` when the entry was written without reading all of its code. `review` lists these first for rereading; remove the line once it is checked |
| `external` | with `status: external`; otherwise optional | Dotted names `<module>.<name>` that appear in an `external/` page, so the module must be listed in `external.toml` |
| `in`, `out`, `notes`, any other key | no | Free text: kept as written, not validated, not searched |
| `uses`, `used_by`, `part_of` | generated | Written after the `modules:` line from the runtime imports between component modules (imports under `TYPE_CHECKING` are ignored). `used_by` shows at most 12 names here; the full list is in `graph.md` |

A **subsystem** is an entry whose id is `subsystem.<name>`. It requires `does`, `verbs`,
`status` and `components` (ids of existing components, never subsystems). `flow` is
optional: component ids in the order they are first reached, joined by ` -> `; describe
loops and conditions in `notes`. A subsystem has no `modules`
line. `members_uses` (what its members use outside the subsystem) is generated after the
`components:` line.

The verb block sits between `<!-- verbs:begin -->` and `<!-- verbs:end -->`; the script
inserts it before the first entry when it is absent and replaces it on every run. The
`verb_list` setting chooses what it holds: `all` verbs (the default), only those
`shared` by two or more entries (for a large catalog), or `none`.

`external.toml` has one table per installed distribution:

```toml
[<distribution-name>]
modules = ["<package>.<module>", "<package>.<other_module>"]
```

The generated `external/<distribution-name>.md` records the installed version. When the
installed version differs from the recorded one, the script prints
`skipped external/<name>.md: installed <x> != recorded <y>` and keeps the recorded page;
it writes a new page only when the recorded one is absent.

## Consult: before planning or writing code

Do this for every capability you are about to build, not once per phase.

1. **Name the capability by what it does**, as verbs and data: "format a byte count for
   display", "read orders from a file". Not by the name you would give your new class.
2. **Search, twice with different words.**
   `python3 scripts/components_index.py search format size human readable` and again with
   synonyms (`render`, `humanize`, `display`). Read the top component entries in full.
3. **Check the dependencies explicitly.** Read the external hits, and grep
   `docs/components/external/` for your verbs. The external list is a selection, not the
   whole dependency: when the capability belongs to a dependency's domain, also grep that
   dependency's installed source in `.venv` for the verbs.
4. **Read the composition.** A component's `uses:` says what it is built from and
   `used_by:` says what calls it inside the package (full list and import evidence in
   `graph.md`; `show <id>` adds the tests and scripts that import it); `part_of:`
   names the subsystem it runs in. For broad work, start from the `subsystem.*` hit: its
   `flow:` is the call order, and `members_uses:` shows what the subsystem depends on
   outside itself. Before changing a component, read its `used_by:`: those are the callers
   your change can break.
5. **Open the code.** For each candidate, read the module and its tests; the index tells
   you where to look, not whether it fits.
6. **A miss is not proof.** When the search prints `no component matched`, also
   `git grep` the verbs in the project's source directories and in earlier phase branches
   (`git grep <pattern> <branch> -- <paths>`). Check the coverage line: an unassigned
   module may hold what you need.
7. **Decide and record**: `reuse` (call it), `adapt` (extend it in place), or `reject`
   (with the reason: wrong layer, measured worse, different cost). Never build beside a
   `canonical` component without a reject reason; never add a caller to a
   `duplicate-of` module.

Record the decision where the work is planned:

- **Phase plans** (`NN-MM-PLAN.md`): the `## Reuse` section, which `phase_tool.py check --plan` checks:
  ```markdown
  ## Reuse
  searched: "format size human readable", "render humanize display" (scripts/components_index.py search); git grep format_ src/<package>
  external: <package>.<module>.<name> (<version>) checked
  reuse: format.sizes (adapt: add binary units), fs.scan
  new_component: report.rows because no entry builds report rows
  ```
  `searched:` and `external:` are required. `reuse:` must name an id that exists in
  `COMPONENTS.md`, or the plan has a `new_component:` line with a reason.
- **Coder briefs**: list the component ids and module paths the coder must call instead of
  rewriting, and the `duplicate-of` modules it must not import.
- **Ad-hoc fixes and PRs**: one line in the PR body: what you searched, what you reused.

## Update: when you add, move or retire code

The index must change in the same commit as the code.

- **New module in the project's source package.** Add its path to the `modules:` of the
  component it belongs to. If none fits, add a new entry. `stats` names every module no
  component covers, and `stats --write-baseline` refuses to record a longer list.
- **New component entry.** Add a `### <area>.<capability>` section in the format above.
  Write `does` as one sentence a planner would search for; put every synonym you can think
  of in `verbs`. One entry per capability: split a package that does several things, and
  group the classes that together do one thing.
- **New or changed end-to-end flow.** Add or edit a `### subsystem.<name>` entry near the
  top of `COMPONENTS.md`. A subsystem lists component ids, never modules. Write `flow:`
  from the code's real call order, not from names.
- **Generated composition lines.** Never edit `uses:`, `used_by:`, `part_of:` or
  `members_uses:`; they come from the imports. If an edge looks wrong, the code imports
  the wrong thing, or a module sits in the wrong component: fix that instead.
- **Duplicate found.** Keep both listed. When a whole module duplicates a component, the
  loser gets its own entry with `status: duplicate-of <winner id>`, and the winner lists
  the loser's module paths under `duplicates:`. When the duplicate is one function in a
  module that also does something else, leave that module's entry as it is: add the
  module path to the winner's `duplicates:` and name the function in the `notes:` of both
  entries. Record the consolidation where the project keeps follow-up work (a todo in
  `.planning/todos/` in the phase workflow) and name it in `notes:`; during a Review the
  record is `REVIEW.md` instead. Do not delete the loser in an unrelated change.
- **Retired code.** Set `status: deprecated` and a `notes:` line with the replacement;
  remove the entry when the module is deleted.
- **Dependency capability worth knowing.** Add the module to `external.toml`, regenerate,
  and add or extend a component with `external:` (use `status: external` when the project
  has no implementation of its own). Do this even if the project does not import it yet.
- **A planner missed something.** Fix the entry's `does` and `verbs` until the words that
  should have found it do. The shipped script has no retrieval-case file or check; a
  project that keeps one (for example `retrieval-cases.toml`) describes it in its
  `.claude/skills/process-phase/references/project.md`.
- **Regenerate** after any change: `python3 scripts/components_index.py` (writes the module
  inventory, external pages, graph, generated lines and verb block), then
  `python3 scripts/components_index.py --check`. After a dependency upgrade the recorded
  external page is kept (see `external.toml` above): remove it, regenerate, and review the
  diff for removed or renamed names.
- **Before a PR.** Run the check against the branch the change will merge into:

  ```bash
  python3 scripts/components_index.py changed --base <base branch>
  ```

  - `fail:` Fix each one: regenerate, correct the entry, or give the new module a
    component.
  - `warn: new caller of <id>` You added an import of a retired component. Call its
    replacement instead (the entry's `status` or `notes` names it). If the import must
    stay, say why in the PR body.
  - `reread: <id>` The code of that component changed and its entry did not. Open the
    entry and the diff of the listed files. If the change added, removed or altered what
    the component does, edit `does`, `verbs`, `modules` or `tests`; if it did not, leave
    the entry and say so in the PR body ("fs.scan reread, still accurate"). A `reread:`
    line never fails the check: the script cannot tell whether a sentence is still true.

  The PR body gets one line: what you searched before writing, what you reused, and the
  summary line the check printed. A project can run the same command in its CI
  (`examples/components-check.yml` in the dev-tools repository is a GitHub Actions job).

## Build: a project with no catalog

Follow [`references/build.md`](references/build.md). In short: generate the module
inventory, print stubs with `draft`, read the code, write one entry per capability in
batches, record what is left in the baseline, add the end-to-end flows, and test the
result by searching for capabilities a newcomer would ask for. The build commits the
index only; it changes no code.

## Review: the whole index against the code

Follow [`references/review.md`](references/review.md). In short: run `review` for the
leads, reread every entry against its modules, repair the index, and write the code
changes you would suggest to `REVIEW.md` in `docs/components/`. The review changes no code;
the user decides which suggestions become work.

## Project rules: an optional check

Follow [`references/rules.md`](references/rules.md). In short: a project that wants rules
the index script cannot state ("the core must not import the command line", "nothing new
joins a loop of imports") writes them in `docs/components/rules.json`, with the ranks and
forbidden pairs of its areas in `docs/components/layers.toml`. Where the project has a
`rules.json`, run this before a PR, after `changed`:

```bash
python3 .claude/skills/components/scripts/rules_check.py check --base <base branch>
```

It reports only what the change added: fix each `fail:`, and fix or justify each `warn:`.
Exit 2 means the check did not run, which is not a pass. The checker is GND, which the
project installs separately; without it the command prints `skip:` and exits 0. Never
edit a rule to make a line go away. This check is a trial: use it where the user asked
for it.

## Rules

- The index tells you where to look; read the code before you decide.
- Never hand-edit `modules/`, `external/`, `graph.md`, the verb block or the generated lines.
- The unassigned baseline only shrinks. Never add a path to it.
- Build and Review commit index files only. A code change they suggest is a suggestion
  until the user turns it into work.
- Keep entries short: one line per field, a `does` of about 120 characters (the search
  prints it whole for every hit), `notes` of two sentences at most. Details belong in the code's docstrings, which the
  inventory picks up.
