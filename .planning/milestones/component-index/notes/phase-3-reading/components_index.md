# Reading: components_index.py

## 1. Header

- Path: `skills/components/scripts/components_index.py`
- Lines (`wc -l`): 1664
- Blob (`git hash-object`): `0679bdc45b749087633dbc1a4d82fd4a89281f12`
- Read at commit `3963a46`. The built copy `plugins/dvt-milestone/skills/components/scripts/components_index.py` is byte-identical (`diff` exited 0).

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `load_settings` | 79 | Merges a JSON settings file over `DEFAULT_SETTINGS`, exiting on an unknown key, a bad `verb_list` or a non-bool `count_extra_dirs`. |
| `plugin_root` | 94 | Returns `parents[3]` of the script when it sits in `<x>/skills/<skill>/scripts/` beside `<x>/.claude-plugin/plugin.json`, else None. |
| `checkout_root` | 103 | Returns the nearest folder at or above the cwd holding `.git`, else the cwd. |
| `catalog` | 158 | Returns `<docs_dir>/COMPONENTS.md` under root, raising ValueError that names `init` when it is missing. |
| `external_config` | 165 | Parses `<docs_dir>/external.toml` with tomllib, or returns `{}`. |
| `layers_config` | 171 | Parses `<docs_dir>/layers.toml` into area ranks and forbid pairs, raising on unknown keys, non-int ranks, malformed `[[forbid]]` rows or an area no component has. |
| `read_components` | 197 | Reads the catalog file and hands its text to `parse_components`. |
| `parse_components` | 202 | Splits text on `### ` headings into dicts of `- key: value` lines, recording checked keys written twice under `_repeated`. |
| `values` | 216 | Splits one field of an entry on commas into stripped, non-empty items. |
| `module_paths` | 221 | (lru-cached) Splits a `modules:` value into a frozenset of files and a tuple of folders ending in `/`. |
| `covers` | 227 | True when a non-subsystem entry names the path as a file or as a folder prefix. |
| `sources` | 232 | Yields sorted `*.py` under a folder, skipping parts named tests, fixtures, `__pycache__` or starting `fake_`. |
| `counted_modules` | 240 | Lists the package's source paths, plus the extra source dirs' when `count_extra_dirs` is on, deduplicated. |
| `counted_dirs` | 250 | Names the folders coverage counts, for the coverage line. |
| `coverage` | 254 | Returns the counted paths no entry covers and the total count. |
| `validate` | 259 | Collects catalog errors: duplicate or malformed ids, missing or repeated fields, TODO in does/verbs, bad status or duplicate-of target, missing or escaping paths, unknown distinct_from ids, external names absent from the inventory. |
| `validate_subsystem` | 305 | Errors when a subsystem has `modules`, or its `components`/`flow` name anything but an existing non-subsystem id. |
| `docstring` | 318 | Returns a node's stripped docstring or `''`. |
| `summary` | 323 | Returns the docstring's first line (or `(no docstring)`) cut to 120 characters. |
| `shorten` | 327 | Cuts text to a length with a trailing ellipsis. |
| `signature` | 331 | Renders a function's parameter names (with `/`, `*`, `**`) and its return annotation as source, cut to 100 characters. |
| `tool_kind` | 350 | Returns ` @tool <id>` when a decorator call named `tool` has a constant `id=` keyword, else `''`. |
| `symbols` | 359 | Yields a row per top-level class/function (and class methods), with label, kind, line, summary and docstring, private names only when asked and marked so. |
| `parse` | 387 | Reads a file's bytes and passes them to `parse_source`. |
| `parse_source` | 391 | Decodes bytes by their declared encoding, parses them, and stores each return annotation's exact source text on the node. |
| `cell` | 406 | Escapes `|` and turns newlines into spaces for a Markdown table cell. |
| `table` | 410 | Renders symbol rows as a Markdown table. |
| `module_inventory` | 417 | Builds the `modules/<group>.md` page texts and one search hit per source file (package and extra dirs), and with `cache` stores each hit's token list in the cache row and `SPLIT`. |
| `file_facts` | 457 | Returns cached `[summary, has docstring, public rows, imports, docstring, private rows]` keyed by a blake2b digest of the file, skipping the read when `trust` and the size/mtime match a trusted row. |
| `top_level` | 490 | Drops method rows (ids containing a dot). |
| `cache_path` | 495 | Returns `$XDG_CACHE_HOME` (or `~/.cache`)`/components-index/<sha256 of root>[:16].json`. |
| `cache_stamp` | 501 | Returns the cache key: format 7, the script's mtime and size, the settings and the Python minor version. |
| `cache_state` | 507 | Loads the saved cache once per root when the stamp matches, trusting rows whose mtime is over 2 s older than the write, swallowing read errors. |
| `save_caches` | 528 | Writes every dirty cache state when caching is on. |
| `write_cache` | 535 | Atomically writes the cache (keeping only files read this run or still present) and deletes any cache file in the folder older than 30 days, ignoring OSError. |
| `external_source` | 553 | Finds an external module's source from its distribution's file list, else from `find_spec` of the top-level package, raising ValueError when absent. |
| `external_inventory` | 575 | For each external.toml library, writes an `external/<name>.md` page of its top-level symbols and hits, reusing the recorded page when the installed version differs. |
| `verb_block` | 610 | Builds the `<!-- verbs:begin -->` list of lower-cased verbs to ids, filtered by `verb_list` (all, shared, none). |
| `subsystem` | 621 | True when an id starts with `subsystem.`. |
| `import_nodes` | 625 | Walks a tree yielding Import/ImportFrom nodes, skipping `if TYPE_CHECKING:` bodies but not their else arms. |
| `raw_imports` | 637 | Turns import nodes into `[level, module, names]` rows, level -1 for plain `import`. |
| `text_imports` | 645 | (lru-cached) Parses source text and returns its raw imports. |
| `resolve_imports` | 650 | Maps import rows to available project paths, only for names under the import prefix, handling relative levels inside the package. |
| `resolve` | 655 | (nested) Maps a dotted name under the prefix to an available `.py` or `__init__.py` path. |
| `module_graph` | 676 | Collects package files plus every file the entries' modules name (and base-revision overrides, None meaning deleted), then returns each file's owners and each owned file's resolved imports. |
| `component_graph` | 700 | Turns file imports into `(caller, callee)` component edges with their file-pair evidence, skipping imports inside the same component. |
| `private` | 713 | True when the file or a folder above it (inside the package) starts with one underscore. |
| `relations` | 720 | Computes uses, used_by and part_of per entry, and members_uses for subsystems. |
| `direct_edges` | 735 | Removes evidence pairs whose importer is a package `__init__.py`. |
| `cycle_groups` | 740 | Runs an iterative Tarjan SCC over edges and returns groups of two or more, largest first. |
| `enter` | 748 | (nested) Numbers a node, pushes it on the stack, and returns its sorted successor iterator. |
| `listing` | 775 | Joins sorted ids, capped with a `… +N more (graph.md)` tail, or `(none)`. |
| `rewrite` | 782 | Replaces every entry's generated lines (uses/used_by/part_of after `modules:`, members_uses after `components:`) leaving authored lines alone. |
| `section` | 787 | (nested) Rewrites one entry's body. |
| `graph_text` | 804 | Builds `graph.md`: each entry's uses/used_by and up to three import pairs per edge. |
| `components_text` | 822 | Returns the catalog with generated lines rewritten and the verbs block replaced, or inserted before the first entry. |
| `build_index` | 833 | Returns every generated file's text (module pages, external pages, COMPONENTS.md, graph.md) and the validation errors. |
| `tokens` | 843 | Lower-cases, splits on non-alphanumerics, drops stopwords and stems `-ies`/`-s`. |
| `stem` | 844 | (nested) Strips a plural ending. |
| `recorded_external` | 851 | Reads search hits and versions from the committed `external/*.md` tables, without the library installed. |
| `search` | 872 | Ranks component, subsystem, external and module hits by query-word overlap (then kind, retired last, id) and attaches matching symbols to module hits. |
| `coverage_line` | 912 | Formats `coverage: N/M <dirs> modules assigned…; external: …`. |
| `generated_paths` | 919 | Lists the `modules/*.md` and `external/*.md` files on disk. |
| `external_skips` | 924 | Maps external pages whose installed version differs from the recorded one to a skip message. |
| `stale_files` | 941 | Returns generated paths whose bytes differ from what `build_index` makes, or that should no longer exist, minus skipped externals. |
| `write_or_check` | 951 | With check, prints stale files, errors and (strict) unassigned modules not in the baseline and returns 1 if any; else writes all generated files and deletes orphaned pages, or prints errors to stderr and returns 1. |
| `git` | 980 | Runs `git -C root -c core.quotepath=off …`, raising ValueError on failure when `check`, else returning `''`. |
| `files_at` | 992 | Reads many paths at one commit through a single `git cat-file --batch`, raising when one is not a blob. |
| `package_imports` | 1014 | Maps each package source file to the package files it imports. |
| `draft` | 1020 | Prints a stub entry per unassigned module (derived id, TODO does, symbols, imports, package importers, test/script importers), optionally filtered by prefix and sorted by importer count. |
| `base_snapshot` | 1079 | Resolves REF (or `origin/REF`), takes the merge base with HEAD, and returns the changed paths (worktree diff plus untracked as A), the catalog there and the old text of each changed `.py`. |
| `exists` | 1086 | (nested) True when `git rev-parse --verify` names a commit. |
| `changed` | 1106 | Prints fail (validation, stale, new uncovered counted module), warn (new import of a deprecated/duplicate component already in the old catalog) and reread (unedited entries whose files or members changed) lines, returning 1 on a fail or a strict warn. |
| `imported_before` | 1125 | (nested) True when the file is unchanged or its base text already imported the target. |
| `authored` | 1140 | (nested) Drops generated fields from an entry. |
| `facts` | 1192 | Builds the `devtools-facts/1` document (types, fact rows, edge evidence, cycle groups) from the catalog, import graph and layers.toml, at HEAD or at the merge base, with optional module facts. |
| `entry_commits` | 1256 | Runs `git blame --line-porcelain` on the catalog and returns, per id, the newest commit and time of its does/verbs/flow lines (uncommitted counts as now). |
| `is_retired` | 1280 | True for status deprecated or `duplicate-of …`. |
| `outside_importers` | 1284 | Maps package files to the files in `tests/` and the extra dirs that import them, skipping unparsable files. |
| `some` | 1302 | Joins items up to a cap with a `+N more` tail. |
| `review` | 1307 | Builds 16 lead groups (17 when there are no subsystems and no area filter) from git history, the graph, symbols and tests, filtered by area and capped at 40 per group. |
| `callers` | 1340 | (nested) Lists a component's callers with up to two importing files each. |
| `places` | 1350 | (nested) Describes the import pairs between two components. |
| `wanted` | 1470 | (nested) True when no area filter is set or a lead names an id with that prefix. |
| `show` | 1488 | Prints one entry's fields and, for each counted module it covers, the line count, public symbols, private names and constants, package imports, package importers and outside importer count. |
| `owned` | 1508 | (nested) Lists paths with their owning components. |
| `main` | 1531 | Parses the command line, sets the cache switch, writes the starter catalog when needed, dispatches each command, maps OSError/ValueError/SyntaxError to exit 1 and always saves caches. |
| `why` | 1589 | (nested) Formats the `[n/total: words]` tail under `search --explain`. |

Counted with `python3 -c "import ast,sys; t=ast.parse(open(sys.argv[1]).read()); print(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(t)))" skills/components/scripts/components_index.py`: 88 (76 top-level, 12 nested). 88 rows.

## 3. Commands

Global options (before the command): `--root PATH` (default: the checkout of the cwd in a plugin install, else derived from `script_path`, line 124), `--check`, `--strict`, `--no-cache`. Errors from OSError/ValueError/SyntaxError go to stderr, exit 1 (1656-1658). Caches are saved on every exit (1659-1660).

| Command | Reaches | Writes / exit |
|---|---|---|
| (none) or `write` | `write_or_check(check=False)` 1655 | Writes the starter catalog first if none (1578-1581); writes `modules/*.md`, `external/*.md`, `COMPONENTS.md`, `graph.md`, deletes orphaned pages; validation errors to stderr and exit 1, nothing written (967-977). |
| `--check` | `write_or_check(check=True)` | Prints `stale or missing:` lines and validation errors to stdout; exit 1 if any (956-966). Cannot combine with a command (1567). |
| `--check --strict` | same | Also prints `no component:` for unassigned counted modules not in `unassigned-baseline.txt`; exit 1 (961-965). `--strict` alone is an error (1569). |
| `init` | 1575-1583 | Writes the starter `COMPONENTS.md` unless one exists; exit 0 either way. |
| `search WORDS… [--limit N] [--explain] [--no-cache]` | `search` 1584-1610 | Prints up to N hits (default 5) within a 7000-character budget, up to 5 matched symbols per module hit, a "no component matched" note, and the coverage line; exit 0. |
| `stats [--write-baseline]` | 1611-1624 | Prints the coverage line and unassigned paths; with the flag writes `unassigned-baseline.txt`, refusing (exit 1) to add a path to an existing baseline. |
| `draft [--only PREFIX] [--by-importers]` | `draft` 1625-1628 | Prints stub entries to stdout; works with no catalog (1626); exit 0. |
| `list [AREA]` | 1629-1639 | Prints `## area (n)` and `id: does` lines for ids starting with AREA; exit 0. |
| `changed [--base REF] [--strict]` | `changed` 1640-1641 | Prints `fail:`/`warn:`/`reread:` lines and a summary; exit 1 on a fail, or a warn with `--strict`; REF defaults to `main`. |
| `facts [--base REF] [--modules] [--out FILE]` | `facts` 1642-1648 | Prints (or writes to FILE) the `devtools-facts/1` JSON, sorted keys; exit 0. |
| `review [AREA…] [--all]` | `review` 1649-1651 | Prints lead groups and a summary line; exit 0. |
| `show ID` | `show` 1652-1654 | Prints the entry and its modules; unknown id exits 1 with prefix suggestions (1492-1494). |

## 4. The entry, claim by claim

| Claim | Verdict | Settled by |
|---|---|---|
| does: "Generate … the component catalog" | overstated | The catalog's `does`/`verbs`/`status`/`modules` are hand-written; `write` only rewrites generated lines and writes pages (782-801, 833-840). |
| does: "and search the component catalog" | true | `search` 872. |
| does: "from source ASTs" | true | `parse_source` 391, `symbols` 359, `raw_imports` 637. |
| does: "write, check, search, stats, draft, changed, review, show, facts" | vague | All exist (1538-1565) but `init` (1540) and `list` (1564) are left out. |
| verbs: component index | true | Whole module. |
| verbs: component catalog | true | `catalog` 158. |
| verbs: search components | true | `search` 872. |
| verbs: find existing code | true | Module and symbol hits, private included (894-905). |
| verbs: does the project already have | true | `search` plus the not-proof note 1607-1608. |
| verbs: generate index | true | `write_or_check` 971-977. |
| verbs: check index stale | true | `stale_files` 941, 956-958. |
| verbs: strict check | true | 963-965. |
| verbs: unassigned modules | true | `coverage` 254, `stats` 1615. |
| verbs: coverage | true | `coverage_line` 912. |
| verbs: draft entries | true | `draft` 1020. |
| verbs: changed since base | true | `changed` 1106, `base_snapshot` 1079. |
| verbs: review the index | true | `review` 1307. |
| verbs: show component | true | `show` 1488. |
| verbs: import graph | true | `component_graph` 700, `graph_text` 804. |
| verbs: facts for rules | true | `facts` 1192. |
| verbs: unassigned baseline | true | 961-962, 1616-1623. |
| verbs: count extra dirs | true | Setting 70, used 244, 251. |
| uses / used_by: (none) | true | Imports are stdlib only (42-61). |
| part_of: subsystem.rule_check | true | rules_check.py runs `facts` (rules_check.py:393). |
| tests: tests/test_tools.py, tests/test_index_cache.py | true | Both exist; test_index_cache.py imports `INDEX` from test_tools (tests/test_index_cache.py:6). |
| notes: "Read: the module docstring, the command line and … The cache and search ranking were not reread." | superseded | This reading covers the cache (451-550) and ranking (872-909). |

## 5. What the entry leaves out

- Starter catalog (`init`, and first `write`): 1575-1583.
- List ids by area (`list`): 1629-1639.
- Catalog validation (duplicate id, invalid id, TODO drafts, repeated field, bad status, missing paths, unknown distinct_from/duplicate-of): 259-315.
- Third-party library index from `external.toml`, with version-skip: 553-607, 924-938.
- Layers file reading and validation (`[rank]`, `[[forbid]]`): 171-194.
- Parse cache outside the checkout and `--no-cache`: 451-550, 1536, 1572.
- New callers of deprecated or duplicate components (`changed --strict`): 1118-1138, 1553.
- Entries to reread because their files changed: 1140-1157.
- Import loops between components (cycle detection): 740-772, 1225, 1357-1359.
- Private module detection by underscore name: 713-717, 1238.
- Stale descriptions (commits to modules since does/verbs last edited, via blame): 1256-1277, 1321-1338.
- Duplicate public names across components: 1390-1421.
- Generated verbs list and its `verb_list` setting: 610-618, 75.
- Search `--explain` and symbol hits under a module: 1544, 1596-1602.

## 6. Docstring against body

- Module docstring lists `write` but not that no command at all also writes (1578, 1655).
- Module docstring: `changed --base REF` "files changed since REF"; the body diffs the working tree against the merge base, adds untracked files as A, and falls back to `origin/REF` (1089-1099).
- Module docstring on the cache does not say that each write deletes any cache file in that folder older than 30 days, including other checkouts' (546-548).
- Module docstring gives `--no-cache` only before the command; `search --no-cache` also exists (1545).
- `facts` docstring: "Module paths stay out of the facts"; `component_has_test` carries test file paths without `--modules` (1226).
- `module_graph` docstring: "The files of the package"; it also takes every file any entry's `modules` names, extra dirs included, and does not apply `sources`' tests/fixtures/`fake_` exclusion to the package rglob (680-687).
- `review` help says `--all` lifts the 40-per-group cap; an area filter lifts it too (1473).
- `review`'s symbol, docstring, size, multi-owner and same-name leads read only `PACKAGE_DIR` files (1317), so with `extra_source_dirs` (dev-tools' `skills/`) those modules are not examined even when `count_extra_dirs` is true; only the last group uses `counted_modules` (1467).
- `draft`'s "imports" and "imported by" lines come from `package_imports` (package only, 1023), so a stub for an extra-dir module always shows "(nothing in the package)".
- In a plugin install, settings are read from the checkout of the cwd (112), not from `--root`; `--root` moves the project but not its settings.
- `--check` prints validation errors to stdout, `write` to stderr (959-960, 968-969); not documented.

## 7. Other scripts

Runs or loads:
- `git` subprocess: `git` 983 (rev-parse, merge-base, diff, ls-files, show, blame, rev-list); `files_at` 998 (`git cat-file --batch`).
- `importlib.util.find_spec` 565 and `importlib.metadata` 587, 931: locate installed third-party libraries named in `external.toml`, not repository scripts.
- No subprocess, runpy or importlib use of another script of this repository; `script_path`/`LABEL` (73, 117, 123) names this script itself in messages and generated text.
- Contract shared with other scripts: the `devtools-facts/1` format (1240) is read by rules_check.py (rules_check.py:398) and also written by phase_tool.py (phase_tool.py:1935).

Same names defined in other shipped scripts:
- `plugin_root` 94: AST-identical in rules_check.py:230, handoff.py:45, coder_pool.py:50, phase_tool.py:47, review_tool.py:64.
- `checkout_root` 103: AST-identical in rules_check.py:239, handoff.py:54, coder_pool.py:59, phase_tool.py:56, review_tool.py:73.
- `load_settings` 79: also rules_check.py:219, handoff.py:86, coder_pool.py:78, phase_tool.py:99, review_tool.py:121; this copy differs (adds the `verb_list` and `count_extra_dirs` checks, 87-90).
- `git` 980: also codex_gate.py:14, phase_tool.py:221, review_tool.py:143, release_plugins.py:48, sync.py:180 (nested), from_gsd.py:428; signatures and return types differ.
- `main` 1531: every shipped script has one.
- `cell` 406: from_gsd.py:116 (different: replaces `|` with `/` and collapses whitespace).
- `coverage` 254: phase_tool.py:690 (different: requirement coverage of a plan).
- `parse` 387: release_plugins.py:65 (different: parses a version string).
- `table` 410: coder_pool.py:358 (different: reads a TOML table).
- `resolve` 655 (nested): coder_pool.py:400 (different).
- `rewrite` 782: build_plugins.py:135 (different: rewrites script paths for a plugin).
- `places` 1350 (nested): rules_check.py:260 (different: locates rules.json and layers.toml).

## 8. Proposed entry

- does: Generate and check the component index from the hand-written catalog and source ASTs, and search it by capability: init, write, --check [--strict], search, stats, draft, list, changed, facts, review, show (components_index.py)
- verbs: component index, component catalog, search components, find existing code, does the project already have, generate index, check index stale, strict check, validate catalog, starter catalog, list components by area, unassigned modules, coverage, unassigned baseline, count extra dirs, draft entries, changed since base, new caller of deprecated component, entries to reread, review the index, stale descriptions, duplicate names, import loops, show component, import graph, facts for rules, private modules, layers toml, external libraries, parse cache, no-cache
- notes: Read in full at 3963a46 (phase 3 of component-index). Search and `--check` read the parse cache in `$XDG_CACHE_HOME/components-index/`, outside the checkout; each write there deletes cache files older than 30 days. `review`'s per-module leads see only `package_dir`, not `extra_source_dirs`. In a plugin install the settings come from the cwd's checkout, whatever `--root` says.
