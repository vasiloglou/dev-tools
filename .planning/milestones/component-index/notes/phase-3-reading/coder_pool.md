# coder_pool.py

## 1. Header

- Path: `skills/phase/process-phase/scripts/coder_pool.py`
- Lines: 471 (`wc -l`)
- Blob: `921c53c7eae42615e91286d529289cb3e469175a` (`git hash-object`), unchanged from `3963a46`.
- Entry: `phase.coder_pool`.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `plugin_root` | 50 | Returns `parents[3]` when the script sits in `<x>/skills/<s>/scripts/` and `<x>/.claude-plugin/plugin.json` exists, else None. |
| `checkout_root` | 59 | Returns the first of cwd and its parents holding `.git`, else cwd. |
| `load_settings` | 78 | Overlays the JSON settings file on `DEFAULT_SETTINGS`; an unknown key raises `SystemExit` naming it. |
| `SubsetReader` | 105 | Recursive-descent reader for a TOML subset, used when `tomllib` is missing. |
| `SubsetReader.__init__` | 116 | Stores text, name, position, root table, current table and opened headers. |
| `SubsetReader.fail` | 122 | Raises `SystemExit("<file>:<line>: <message>")`. |
| `SubsetReader.peek` | 126 | Returns the next character or "". |
| `SubsetReader.skip` | 129 | Skips spaces, tabs and `#` comments, and line ends when asked. |
| `SubsetReader.expect` | 141 | Consumes a literal token or fails. |
| `SubsetReader.end_of_line` | 146 | Fails when anything but a comment follows a value on its line. |
| `SubsetReader.string` | 151 | Reads a one-line basic or literal string with basic-string escapes (incl. `\u`/`\U`); multi-line strings fail. |
| `SubsetReader.key` | 180 | Reads a bare, quoted or dotted key into its parts. |
| `SubsetReader.value` | 198 | Reads a string, array, inline table, boolean, decimal integer or float; anything else (dates, hex, inf) fails. |
| `SubsetReader.array` | 220 | Reads a bracketed array across lines and comments, trailing comma allowed. |
| `SubsetReader.inline_table` | 235 | Reads `{ k = v, ... }` into a dict. |
| `SubsetReader.pair` | 250 | Reads `key = value`, creating dotted-key tables and failing on a repeated key. |
| `SubsetReader.header` | 263 | Opens a `[table]` (failing if opened twice) or appends to an `[[array]]` of tables. |
| `SubsetReader.read` | 288 | Loops headers and pairs to end of text and returns the root table. |
| `load_toml` | 300 | `{}` for a missing file; else `tomllib.loads` (decode error becomes `SystemExit`) or `SubsetReader`. |
| `deep_merge` | 316 | Merges dicts recursively; any non-dict in the override replaces. |
| `find_root` | 327 | `--root` if given, else the first of cwd and parents holding `.git`, else cwd. |
| `local_config_path` | 338 | The checkout's local file, or for a linked worktree without one, the file beside `git rev-parse --git-common-dir`'s parent. |
| `load_config` | 354 | Deep-merges the team TOML with the local TOML. |
| `table` | 358 | Walks `config[a][b]...`, `{}` when absent, `SystemExit` when a step is not a table. |
| `detect` | 370 | Maps `claude`, `codex`, `gemini` to their `shutil.which` path or None. |
| `coder_accounts` | 375 | Builds one pool entry per `coders.<tool>.accounts` item (default one named "default") with env, model/effort (falling back to `tools.<tool>`), stuck_model and risk. |
| `resolve` | 400 | Picks `roles.coders` (or `[roles.implementer]`, or `["codex"]`), keeps those on PATH, falls back to `claude` if on PATH, reads the two limits (bad ones warn and become 4), and computes capacity and `effective_tracks`. |
| `render` | 437 | Prints the pool, each entry's model/effort/risk/stuck_model/env, the limits and the warnings as text. |
| `main` | 454 | Parses `show [--json] [--root]`, resolves the pool and prints JSON or text; returns 0. |

Count: `python3 -c "import ast;t=ast.parse(open('skills/phase/process-phase/scripts/coder_pool.py').read());print(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(t)))"` printed 29; the table has 29 rows.

## 3. Commands

| Command | Reaches | Writes |
|---|---|---|
| `show [--json] [--root DIR]` (options before or after `show`, 459-463) | `main` 454 -> `find_root` 327, `load_config` 354, `detect` 370, `resolve` 400, `render` 437 | stdout: JSON `{installed, coders{pool, fallback, max_tracks, max_sessions_per_account, capacity, effective_tracks}, warnings}` (466) or text; no files. |

Exit: 0 always from `main` (467), an empty pool too; 1 from `SystemExit(<message>)` for a bad settings file (84, at import), unparseable TOML (124, 310) or a wrongly typed `roles.coders`, `coders.<t>.accounts` or table (363, 384, 407); 2 from argparse usage errors.

## 4. The entry, claim by claim

| Claim | Verdict | Settled by |
|---|---|---|
| does: "Say which coding assistants Implement may use" | true | `resolve` 403-422 keeps the configured coders found on PATH. |
| does: "and how many at once" | true | `effective_tracks = min(max_tracks, len(pool) * max_sessions_per_account)` 430-432. |
| does: "from the team's and the developer's TOML files" | true | `load_config` 355; paths are settings 70-75. |
| does: "(coder_pool.py show)" | true | Only command, 457. |
| verb: coder pool | true | 422, 431. |
| verb: coding assistants | true | `KNOWN_TOOLS` 94. |
| verb: how many coders | vague | The number is tracks, not coders: 432. |
| verb: parallel tracks | true | 425-432. |
| verb: max tracks | true | `LIMITS` 99, 432. |
| verb: sessions per account | true | 430. |
| verb: codex accounts | overstated | Accounts are read for any coder, not codex alone (378-380). |
| verb: gemini coder | true, thin | `gemini` is a known tool (94); no gemini-specific handling. |
| verb: coder model | true | 391. |
| verb: coder effort | true | 392. |
| verb: merge toml settings | true | `deep_merge` 316, `load_config` 355. |
| verb: which coders are on path | true | `detect` 370, 410-415. |
| notes: "Read: the module docstring and the documented functions." | superseded | This file reads every line. |
| notes: "It carries its own small TOML reader for a Python without tomllib." | true | 45-48, `SubsetReader` 105, used at 305-306. |

## 5. What the entry leaves out

- Fallback to the Claude Code coder (`claude -p`) when no configured coder is on PATH: 416-419.
- Empty pool with `effective_tracks` 0 when nothing is on PATH, still exit 0: 420-421, 467.
- A linked worktree reads the main checkout's local file: `local_config_path` 338-351.
- Per-account environment (e.g. `CODEX_HOME`) for several accounts of one coder: 390.
- `stuck_model` and `risk` per coder: 393-394.
- Model and effort defaults from a `[tools.<name>]` table: 379, 391-392.
- Legacy single `roles.implementer` key: 404-405.
- Defaults when nothing is configured: `["codex"]`, limits 4: 96-98.
- Paths of the two files are settings in `coder_pool.settings.json` (or `.devtools/` in a plugin install): 68-75.
- Capacity (pool size times sessions per account): 430.
- Prints each account's env values in text and JSON: 441, 390.

## 6. Docstring against body

- Module docstring (11-12): "with none left the pool is the Claude Code coder". Only when `claude` is on PATH (416); otherwise the pool is empty and `effective_tracks` is 0. Ran `show --json` on a copy under `/private/tmp` with `PATH=/usr/bin:/bin`: `pool: []`, `effective_tracks: 0`, exit 0.
- Module docstring (31-32): "1 a settings or configuration file cannot be used". A bad `max_tracks` / `max_sessions_per_account` only warns and uses 4 (426-428; same run: `max_tracks=0` gave a warning and 4); an unknown coder name only warns (415).
- Module docstring (29): "Other tables and keys are ignored, so the files may hold more than the pool". On Python before 3.11 the whole file must fit the TOML subset (217, 154), so a date or multi-line string anywhere exits 1.
- Module docstring (25): `risk = "medium"` describes a meaning; the body passes `risk` through unvalidated and unused (394).
- Module docstring omits `roles.implementer` (404) and the `tools.<name>` fallback for `stuck_model` is absent although it exists for model and effort (393 against 391-392).
- `SubsetReader` docstring (106-108) lists "decimal numbers"; the body also reads exponents and `_` separators (113) and does not forbid extending an inline table later, which TOML does.
- `find_root` (328): true; `.git` as a file still marks the worktree as the root (333).
- `local_config_path` (339-340): for a submodule `.git` is also a file, and the common dir's parent is then `.git/modules/`, not a checkout (342, 350); not exercised by any caller here.

## 7. Other scripts

Runs or loads:

- `local_config_path` 345: `subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"])` (not a repository script).
- `detect` 372: `shutil.which` for `claude`, `codex`, `gemini`; nothing is run.
- No runpy or importlib use.

Run by others: `phase_tool.py:1042-1047` (`track_cap`) runs `coder_pool.py show --json --root` and reads `coders.effective_tracks`. `references/implement.md:26` tells the Implement step to run `show`.

Same names in other shipped scripts (`def`/`class` in `skills/`, `devtools/`):

| Name | Here | Also | Same body |
|---|---|---|---|
| `plugin_root` | 50 | `phase_tool.py:47`, `handoff.py:45`, `review_tool.py:64`, `rules_check.py:230`, `components_index.py:94` | yes, all (ast compare, docstring dropped) |
| `checkout_root` | 59 | `phase_tool.py:56`, `handoff.py:54`, `review_tool.py:73`, `rules_check.py:239`, `components_index.py:103` | yes, all |
| `load_settings` | 78 | `phase_tool.py:99`, `handoff.py:86`, `review_tool.py:121`, `rules_check.py:219`, `components_index.py:79` | same as `phase_tool.py` only |
| `find_root` | 327 | `phase_tool.py:230` | no: here `.git` marks the root, there the planning dir; and `checkout_root` 59 is the same search as this one without `--root` |
| `table` | 358 | `components_index.py:410` | no |
| `resolve` | 400 | `components_index.py:655` (nested) | no |
| `main` | 454 | every other shipped script | no |
| `SubsetReader.key` | 180 | `from_gsd.py:80` (`def key`) | no |
| `SubsetReader.read` | 288 | `from_gsd.py:91` (`def read`) | no |

TOML: `components_index.py:59` and `sync.py:52` import `tomllib` with no subset fallback; this is the only shipped TOML reader for Python 3.9-3.10.

## 8. Proposed entry

- does: Say which coding assistants Implement may use and how many tracks at once: merge the team's and the developer's TOML files, keep the coders found on PATH, fall back to claude, and give each account's model, effort, risk and env (coder_pool.py show)
- verbs: coder pool, coding assistants, parallel tracks, effective tracks, track cap, max tracks, sessions per account, coder accounts, account env, codex home, gemini coder, claude fallback, coder model, coder effort, stuck model, coder risk, merge toml settings, local coder config, worktree reads main checkout config, which coders are on path, toml without tomllib
- notes: `show` exits 0 even with an empty pool (nothing on PATH gives `effective_tracks` 0; read the warnings); bad limits warn and use 4, bad TOML or wrongly typed tables exit 1. phase_tool.py runs `show --json` for the track cap (subsystem.phase_status). Its `SubsetReader` reads only a TOML subset on Python before 3.11. `plugin_root`, `checkout_root` and `load_settings` are the same code as in phase_tool.py.
