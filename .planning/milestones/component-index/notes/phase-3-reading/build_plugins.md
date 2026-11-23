# Reading: devtools/build_plugins.py

## 1. Header

- Path: `devtools/build_plugins.py`
- Lines (`wc -l`): 243
- Blob SHA (`git hash-object`): `56096d56c256db3a586bd406b6895e1a67a8ca1b`
- Read at commit `3963a46`.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `version` | 44 | Reads `devtools/PLUGIN_VERSION`, strips it and raises `SystemExit` unless it matches `X.Y.Z`. |
| `note` | 123 | Returns the blockquote inserted after each SKILL.md frontmatter, naming `.devtools/project.md`, `.devtools/<script>.settings.json`, `${CLAUDE_PLUGIN_ROOT}` and the planning folder. |
| `rewrite` | 135 | Fills `{{devtools:<key>}}` tokens from `VALUES` (unknown key raises `SystemExit`), then applies `REWRITES` and the plugin's own rewrites, adding each pattern's match count to `hits`. |
| `fill` | 137 | Nested in `rewrite`: returns `VALUES[key]` for one token match or raises `SystemExit`. |
| `shipped` | 149 | Yields every file under a skill folder, sorted, leaving out `__pycache__`/`.DS_Store` anywhere and a top-level `evals/` or `agents/` subfolder. |
| `build_plugin` | 156 | Collects one plugin's files in memory: each skill's shipped files, its extra `files`, the repository `agents/*.md` when set, and a generated `.claude-plugin/plugin.json`. |
| `add` | 159 | Nested in `build_plugin`: reads a source's bytes, rewrites it when it is `.md` (inserting `note` after a SKILL.md frontmatter, failing on none), stores it and records the source's mode in `MODES`. |
| `build` | 186 | Builds both plugins, raises `SystemExit` listing every rewrite pattern that matched nothing across the whole build, and adds `.claude-plugin/marketplace.json`. |
| `stale` | 207 | Lists wanted files that are missing, differ in bytes or differ in mode, plus files under `plugins/` (outside `SKIP` names) that a build would not write. |
| `main` | 214 | With `--check` prints `stale:` lines and exits 1 on any; otherwise deletes unwanted files under `plugins/`, writes changed files, fixes modes, removes empty folders and prints a count. |

Counted with
`python3 -c "import ast,sys; t=ast.parse(open(sys.argv[1]).read()); print(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(t)))" devtools/build_plugins.py`:
10.

## 3. Commands

| Command | Reaches | Writes |
|---|---|---|
| `build_plugins.py` | `main` 214 -> `build` 186, `stale` 207 | `plugins/dvt-phase/**`, `plugins/dvt-milestone/**`, `.claude-plugin/marketplace.json`; deletes files under `plugins/` a build does not write (226-228) and empty folders (235-237); stdout `N file(s) written or removed` or `plugins are up to date`; exit 0. |
| `build_plugins.py --check` | `main` 220-225 | Nothing; stdout `stale: <path>` per file, stderr `run: python3 devtools/build_plugins.py`; exit 1 when stale, else 0. |
| any | `version` 47, `fill` 139, `add` 166, `build` 195 | A bad version, an unknown token, a SKILL.md without frontmatter or an unmatched rewrite raise `SystemExit(<message>)`: exit 1 with the message on stderr. |

Ran `python3 devtools/build_plugins.py --check` read-only at `3963a46`: exited 0, no output.

## 4. The entry, claim by claim

| Claim | Verdict | Settled by |
|---|---|---|
| does: Build the dvt-phase and dvt-milestone plugins in plugins/ | true | `build_plugins.py:55-91`, `:186-191` |
| does: and the marketplace | true | `build_plugins.py:196-203` |
| does: from skills/ | overstated | Also from `agents/` (`:68`, `:177-179`), `skills/phase/pytest/phase_selection.py` (`:67`) and `devtools/PLUGIN_VERSION` (`:180`). |
| does: --check finds a stale copy | true | `build_plugins.py:207-211`, `:220-225`; it also finds a mode difference and a file a build would not write. |
| verb: build plugins | true | `build_plugins.py:186` |
| verb: rebuild plugins | true | `build_plugins.py:226-238` |
| verb: generate plugins folder | true | `build_plugins.py:229-232` |
| verb: regenerate plugins | true | `build_plugins.py:226-238` |
| verb: marketplace json | true | `build_plugins.py:33`, `:203` |
| verb: plugin manifest | true | `build_plugins.py:180-182` |
| verb: check plugins stale | true | `build_plugins.py:207`, `:220` |
| verb: rewrite script paths | true | `build_plugins.py:109-116` (in Markdown only; scripts are not rewritten, `:160-169`). |
| verb: CLAUDE_PLUGIN_ROOT | true | `build_plugins.py:109-116`, `:129` |
| verb: devtools token | true | `build_plugins.py:119`, `:137-142` |
| verb: plugin copy of a skill | true | `build_plugins.py:172-174` |
| verb: dvt-phase | true | `build_plugins.py:56` |
| verb: dvt-milestone | true | `build_plugins.py:73` |
| notes: Read: the module docstring, the function list and the command line. | stale | A process note; this reading replaces it. |
| notes: Copies scripts byte for byte | true | `build_plugins.py:160-169`: only `.md` sources are decoded and rewritten. |
| notes: and fails the build when a rewrite stops matching | true | `build_plugins.py:192-195` |

## 5. What the entry leaves out

- Inserts the "Installed from the plugin" note after every SKILL.md frontmatter (`:123-132`, `:163-167`).
- Rewrites project-rule and settings paths (`references/project.md` -> `.devtools/project.md`, `scripts/<x>.settings.json` -> `.devtools/<x>.settings.json`) (`:95-108`).
- Renames agent references to `dvt-phase:<agent>` in dvt-phase only (`:70-71`).
- Ships `agents/*.md` into dvt-phase (`:68`, `:177-179`).
- Leaves a skill's own `evals/` and `agents/` folders out (`:52`, `:152`).
- Keeps each file's permission bits from its source and checks them (`:170`, `:210`, `:233-234`).
- Deletes files under `plugins/` that no source produces, and empty folders (`:226-228`, `:235-237`).
- Writes the version from `devtools/PLUGIN_VERSION` into each manifest and refuses a non-semver version (`:40-48`, `:180`).
- Fails on an unknown `{{devtools:<key>}}` token and on a SKILL.md without frontmatter (`:139`, `:166`).
- Both plugins ship components, handle-issue, dev-handoff and dev-takeover (`:61-66`, `:79-86`).
- `SEMVER`, `VERSION_FILE`, `version`, `build`, `stale` and `main` are the interface `release_plugins.py` uses (`release_plugins.py:59`, `:112`, `:121`, `:140-141`).

## 6. Docstring against body

- Module docstring (`:7-9`) says dvt-phase is "the phase workflow, its agents and the component index" and dvt-milestone "the milestone workflow and the component index"; the body also puts handle-issue, dev-handoff and dev-takeover in both (`:61-66`, `:79-86`), and review-pr in dvt-milestone (`:82`).
- Module docstring (`:4`) says a build writes `plugins/` and the marketplace; it hides that the build also deletes files under `plugins/` it would not write (`:226-228`) and empty folders (`:235-237`).
- Module docstring (`:16-17`) describes how the shipped scripts find settings; build_plugins.py does none of that itself, it only rewrites the Markdown that says so (`:107-108`).
- `main` deletes `__pycache__`/`.DS_Store` files under `plugins/` (`:226` does not filter `SKIP`) while `stale` ignores them (`:208`), so such a deletion is not counted and the run can print "plugins are up to date" after deleting (`:238`).
- `--check` also reports a file whose mode differs (`:210`); the docstring (`:5`) says only "differ".

## 7. Other scripts

- Runs or loads no other script: no `subprocess`, `runpy` or `importlib`; it reads files under `skills/`, `agents/` and `devtools/PLUGIN_VERSION` as data (`:160`, `:45`).
- Loaded by `devtools/release_plugins.py:35-37` with `importlib.util.spec_from_file_location`, at that module's import.
- Same-named helpers in other shipped scripts (searched top-level `def` under `skills/` and `devtools/`):
  - `rewrite` (`:135`): also `skills/components/scripts/components_index.py:782`.
  - `build` (`:186`): also `devtools/from_gsd.py:621` (a conversion plan, not plugins).
  - `main` (`:214`): every shipped script has one.

## 8. Proposed entry

```
- does: Build the dvt-phase and dvt-milestone plugins in plugins/ and .claude-plugin/marketplace.json from skills/, agents/ and devtools/PLUGIN_VERSION, rewriting paths in Markdown only; --check exits 1 on a stale, extra or wrong-mode file (build_plugins.py)
- verbs: build plugins, rebuild plugins, generate plugins folder, regenerate plugins, marketplace json, plugin manifest, check plugins stale, rewrite script paths, CLAUDE_PLUGIN_ROOT, devtools token, plugin copy of a skill, dvt-phase, dvt-milestone, installed from plugin note, project rules path, settings json path, plugin agents, file modes, remove stale plugin files
- notes: Copies every non-Markdown file byte for byte with its mode; fails the build when a rewrite matches nothing, a token has no value or a SKILL.md has no frontmatter. A build deletes files under plugins/ that no source makes. release_plugins.py loads it with importlib (subsystem.release).
```
