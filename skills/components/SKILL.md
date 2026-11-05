---
name: components
description: The project's component index (docs/components/), which says what already exists in the project and in its dependencies before you plan or write code. Consult mode searches it by capability (scripts/components_index.py search), reads the matching COMPONENTS.md entries, the generated per-package symbol inventory and the recorded dependency capabilities, and records a reuse / adapt / reject decision. Update mode adds or edits a component entry, assigns new modules, marks duplicates, adds a dependency module to external.toml and regenerates the index. Use before planning a phase (Discuss and Plan), before writing any new module, class or function, before briefing a coder, and whenever you add, move, retire or duplicate code. Also use when asked "does the project already have X?".
---

# components

An agent that cannot search by capability rebuilds what the project, or one of its
dependencies, already has. The component index makes existing code findable by what it
does; this skill is how you use and maintain it. The entry format is defined in
"Entry format" below: it is exactly what the index script parses and validates.

Paths below assume the default settings (`docs_dir` = `docs/components`, script at
`scripts/`). A project changes them in `components_index.settings.json` beside the script
(`package_dir`, `import_prefix`, `extra_source_dirs`, `docs_dir`, `script_path`).

| File | What it is | Edit? |
|---|---|---|
| `docs/components/COMPONENTS.md` | Subsystems (end-to-end flows that combine components) and one entry per capability | By hand, except the generated verb block and the `uses`, `used_by`, `part_of` and `members_uses` lines |
| `docs/components/graph.md` | Every component's full `uses` / `used_by`, with up to three importer -> imported module pairs per edge | Never; generated |
| `docs/components/modules/<group>.md` | Every module, public class, function and method, with signature, line, first docstring line and the component ids that own the module. One page per top-level folder of the package (`_root.md` for modules directly in it) and one per extra source directory | Never; generated |
| `docs/components/external/<distribution>.md` | Public top-level classes and functions of the selected dependency modules, with the installed version | Never; generated from `external.toml` |
| `docs/components/external.toml` | Which dependency modules are listed. Optional: without it no dependency is indexed | By hand |
| `docs/components/unassigned-baseline.txt` | The package modules no component covers | Only with `stats --write-baseline` |

Run the script with the project's venv Python: `.venv/bin/python scripts/components_index.py …`
(in a worktree without `.venv`, use the main checkout's `.venv/bin/python`). It parses
source files and never imports the project's package. Writing and checking read the
installed dependencies' metadata, so they need the environment those are installed in;
`search` and `stats` need no dependency installed.

| Command | What it does |
|---|---|
| no command, or `write` | Validates the catalog, then writes `modules/`, `external/`, `graph.md` and the generated parts of `COMPONENTS.md`, and deletes generated pages it no longer produces. An invalid entry prints the errors, writes nothing and exits 1 |
| `init` | Writes a starter `COMPONENTS.md` with the entry format; never overwrites one. `write` does the same on its first run in a project that has no catalog |
| `--check` | Writes nothing. Prints `stale or missing: <path>` for each generated file that differs, plus every validation error; exits 1 if there is any. With `--strict` it also prints `no component: <path>` for each package module that no entry covers and is not in `unassigned-baseline.txt`, and exits 1; use `--check --strict` when closing a phase. Cannot be combined with a command |
| `search <words> [--limit N]` | Ranks subsystems, components, recorded dependency names and modules by the number of query words they share (5 hits by default). Prints `<kind> <id>: <summary>`, a `flow:` line under a subsystem, `no component matched: …` when no component or subsystem matched, and the coverage line |
| `stats [--write-baseline]` | Prints the coverage line, then each package module no component covers. `--write-baseline` records that list in `unassigned-baseline.txt` and refuses when it has grown |
| `--root <dir>` | Runs against another checkout |

The search compares whole words (lower case, stop words dropped, a final "s" removed),
not meanings. A component is matched on its id, `does` and `verbs`; a module on its name,
docstring summaries and symbol names; a dependency name on its own summary plus the
`does` and `verbs` of any component that lists it under `external:`.

## Entry format

`COMPONENTS.md` is a list of `###` sections. Each field is one line, `- <key>: <value>`;
a value never continues on a second line, and list values are comma-separated.

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
| `tests` | no | Repo-relative paths that exist |
| `duplicates` | no | Repo-relative paths, which must exist, of the modules that duplicate this component |
| `external` | with `status: external`; otherwise optional | Dotted names `<module>.<name>` that appear in an `external/` page, so the module must be listed in `external.toml` |
| `in`, `out`, `notes`, any other key | no | Free text: kept as written, not validated, not searched |
| `uses`, `used_by`, `part_of` | generated | Written after the `modules:` line from the runtime imports between component modules (imports under `TYPE_CHECKING` are ignored). `used_by` shows at most 12 names here; the full list is in `graph.md` |

A **subsystem** is an entry whose id is `subsystem.<name>`. It requires `does`, `verbs`,
`status` and `components` (ids of existing components, never subsystems). `flow` is
optional: component ids in call order, joined by ` -> `. A subsystem has no `modules`
line. `members_uses` (what its members use outside the subsystem) is generated after the
`components:` line.

The verb block sits between `<!-- verbs:begin -->` and `<!-- verbs:end -->`; the script
inserts it before the first entry when it is absent and replaces it on every run.

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
   `python scripts/components_index.py search format size human readable` and again with
   synonyms (`render`, `humanize`, `display`). Read the top component entries in full.
3. **Check the dependencies explicitly.** Read the external hits, and grep
   `docs/components/external/` for your verbs. The external list is a selection, not the
   whole dependency: when the capability belongs to a dependency's domain, also grep that
   dependency's installed source in `.venv` for the verbs.
4. **Read the composition.** A component's `uses:` says what it is built from and
   `used_by:` says what calls it (full list and import evidence in `graph.md`); `part_of:`
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
- **Duplicate found.** Keep both listed. The loser gets its own entry with
  `status: duplicate-of <winner id>`, and the winner lists the loser's module paths under
  `duplicates:`. Add the consolidation to a todo (`.planning/todos/`) and name it in
  `notes:`. Do not delete the loser in an unrelated change.
- **Retired code.** Set `status: deprecated` and a `notes:` line with the replacement;
  remove the entry when the module is deleted.
- **Dependency capability worth knowing.** Add the module to `external.toml`, regenerate,
  and add or extend a component with `external:` (use `status: external` when the project
  has no implementation of its own). Do this even if the project does not import it yet.
- **A planner missed something.** Fix the entry's `does` and `verbs` until the words that
  should have found it do. The shipped script has no retrieval-case file or check; a
  project that keeps one (for example `retrieval-cases.toml`) describes it in its
  `.claude/skills/process-phase/references/project.md`.
- **Regenerate** after any change: `python scripts/components_index.py` (writes the module
  inventory, external pages, graph, generated lines and verb block), then
  `python scripts/components_index.py --check`. After a dependency upgrade the recorded
  external page is kept (see `external.toml` above): remove it, regenerate, and review the
  diff for removed or renamed names.
- **Before a PR.** Run `--check` and `stats`, reread the entries of the components whose
  modules your diff changed, and fix anything stale. A PR-time component check (unassigned
  new modules, new callers of a `deprecated` or `duplicate-of` component) is not part of
  the shipped script; a project that has one names its command in
  `.claude/skills/process-phase/references/project.md`.

## Rules

- The index tells you where to look; read the code before you decide.
- Never hand-edit `modules/`, `external/`, `graph.md`, the verb block or the generated lines.
- The unassigned baseline only shrinks. Never add a path to it.
- Keep entries short (about 12 lines). Details belong in the code's docstrings, which the
  inventory picks up.
