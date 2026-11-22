# Reading: devtools/sync.py

## 1. Header

- Path: `devtools/sync.py`
- Lines (`wc -l`): 1098
- Blob (`git hash-object devtools/sync.py`): `6cd09db68e24c3a9b051cf67fd1bd294fd19dff5`
- Read at commit `3963a46` (HEAD; `git diff --stat 3963a46 -- devtools/` printed nothing).
- Entry: `sync.copies`.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `SyncError` | 71 | Exception carrying an exit code; `main` prints `error: <message>` and returns the code. |
| `__init__` | 72 | Method of `SyncError`: stores the message and `code` (default 2; no caller passes another). |
| `digest` | 77 | sha256 hex of bytes. |
| `inside` | 81 | Raises `SyncError` for an absolute path or one with `..`, else returns `root / relative`. |
| `fill_tokens` | 88 | Replaces `{{devtools:<key>}}` in UTF-8 text with the entry's values, raising on a missing value and recording used keys; binary passes through. |
| `read_config` | 102 | Loads `.devtools.toml` with `tomllib` and refuses top-level keys other than `sync` and `after_apply`. |
| `desired_files` | 113 | Builds dest -> {data, mode, origin} from every `[[sync]]` entry (file or directory source, `exclude`, `values`, `settings` JSON), refusing unknown keys, `TODO` values, unused values, stale excludes, duplicate dests, and dests that escape or alias through a symlink. |
| `add` | 117 | Nested in `desired_files`: checks the dest is relative and not produced twice, then records it. |
| `read_json` | 174 | JSON of a file, or `{}` when it is not a file. |
| `source_identity` | 178 | The dev-tools HEAD commit and whether `git status --porcelain` shows changes under the sources the config takes. |
| `git` | 180 | Nested in `source_identity`: `git -C <source>`; stripped stdout on exit 0, else `""`. |
| `warn_if_dirty` | 187 | Prints a stderr warning when the taken dev-tools sources have uncommitted changes. |
| `plan` | 193 | Classifies every wanted or previously managed file as create, keep, update, delete or forget, marking hand-edited (`force`) and unmanaged (`adopt`) ones, using the receipt and an interrupted run's journal; raises on a non-regular file. |
| `write_atomic` | 230 | Writes through a temp file in the same folder, sets the mode, and `os.replace`s it. |
| `ignored_by_git` | 243 | Asks `git check-ignore --stdin -z` which paths are ignored; warns on stderr when git fails inside a work tree. |
| `entry_paths` | 259 | The wanted paths under one entry's dest, the dest itself, or its settings files beside a file dest. |
| `warn_if_ignored` | 267 | Per entry, prints a stderr warning naming how many delivered files git ignores and how to find the rule. |
| `cmd_apply` | 281 | Refuses (exit 3) when any action needs an unpassed `--force`/`--adopt`; dry run lists actions; else writes a journal, creates/updates/deletes files, writes the receipt, removes the journal, warns on ignored files, and runs `after_apply` when anything changed (exit 4 on the first failure). |
| `cmd_check` | 340 | Compares every receipt file's presence, sha256 and mode, and reports an interrupted apply; exit 1 on any problem. |
| `kept_lines` | 368 | (line number, stripped text) for UTF-8 lines of at least 4 characters with a letter or digit. |
| `squeeze` | 378 | Collapses all whitespace runs to one space. |
| `shared` | 383 | Share of the shipped file's token-free kept lines that also appear in the local file. |
| `shipped_files` | 389 | Sorted files under a folder, skipping `__pycache__`. |
| `shipped_units` | 393 | Every skill folder (has SKILL.md), the `agents` folder, and every `.py` under `skills/` outside a skill folder, minus adopt-devtools and move-from-gsd. |
| `walk` | 406 | `os.walk` returning regular files and symlinked folders, pruning caches, symlinks and nested checkouts. |
| `walk_project` | 418 | Files from `git ls-files -co --exclude-standard` (falls back to `walk`), plus a full walk of `skills/` and `agents/` at the root and one level down. |
| `other_plans` | 459 | Globs `OTHER_PLANS` into `(sign, tool)` pairs and, given a planning folder, adds it when its STATE.md lacks `current_phase:` or its ROADMAP.md lacks `## Phase N`. |
| `related` | 481 | True when a name is `<shipped>-x` or `x-<shipped>`. |
| `literals` | 486 | Top-level `NAME = <literal>` assignments of a script, by `ast.parse` and `literal_eval`, without running it. |
| `survey` | 502 | Matches each project SKILL.md folder to the best shipped skill by line share, file presence and name, plus agents folders, standalone scripts, shipped files kept outside their skill copy, same-name clashes and symlinked skill folders. |
| `covered` | 566 | (config dests, receipt paths, `replaces` paths) for the survey's status marks; empty without a config. |
| `tracked` | 576 | False only when `git ls-files -- <path>` succeeds and prints nothing. |
| `survey_text` | 582 | Formats the survey report: GSD planning folder advice, other planning tools, counterparts with share and missing files, files kept apart, unmatched units, clashes, own skills, links, and a `git grep` command to find readers of the copies. |
| `state` | 585 | Nested in `survey_text`: a path's mark (old copy, synced, in config not applied, not in config, not tracked). |
| `by_folder` | 687 | Groups paths into one `folder/: names` line per parent. |
| `toml_value` | 695 | `json.dumps` of a value, used as its TOML spelling. |
| `token_values` | 699 | Infers each token's value from the project's copy by matching shipped single-token lines as patterns, keeping a value only when all matches agree. |
| `starter_config` | 727 | Prints a starter `.devtools.toml`: one `[[sync]]` per counterpart under the shipped name with `replaces`, inferred `values`, `exclude` for scripts kept elsewhere plus their own entries, settings blocks, and an example pointer when nothing matched. |
| `settings` | 744 | Nested in `starter_config`: a `[sync.settings]` block from the shipped script's `DEFAULT_SETTINGS`, filled from the project's settings JSON, the old script's constants, survey paths, or `TODO`. |
| `cmd_survey` | 841 | Runs `survey` and prints the report or, with `--toml`, the starter config; exit 0. |
| `headings` | 851 | Line number -> enclosing Markdown heading, skipping fenced code. |
| `compare_rows` | 863 | One row per planned action, excluded kept file and old-copy file, with the project's lines no delivered file has, where each such line now lives in a file the project owns (or CLAUDE.md/AGENTS.md), near shipped lines, and duplicate copies. |
| `only_here` | 869 | Nested in `compare_rows`: lines of a file absent from every delivered file, also tried joined with a neighbour for prose. |
| `row_note` | 942 | The short note after a compare row (twin, excluded, script diff, lines only here, close, carried). |
| `cmd_compare` | 959 | Without paths prints labelled rows, files beside the synced ones and totals; with paths prints lost lines, `--added` lines, or `--diff`; `--record` prints a migration-record table skeleton. |
| `main` | 1061 | Builds the four sub-commands and maps `SyncError` to its exit code. |

Count: `python3 -c "import ast; t=ast.parse(open('devtools/sync.py').read()); print(sum(isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for x in ast.walk(t)))"` printed 46 (1 class, 1 method, 39 top-level functions, 5 nested). The table has 46 rows.

## 3. Commands

| Command / option | Reaches | Writes |
|---|---|---|
| `apply --project P` (required) | `cmd_apply` 281 | project files, `.devtools-receipt.json`, transient `.devtools-sync.journal`; stdout `applied: {counts}`; stderr warnings; exit 0, 2 (config), 3 (refused, nothing written), 4 (after_apply failed). |
| `apply --source S` | `cmd_apply` 284 (default this checkout, 1066) | none extra. |
| `apply --adopt` | `cmd_apply` 288 | allows overwriting files present but not in the receipt. |
| `apply --force` | `cmd_apply` 287 | allows overwriting or deleting managed files changed by hand. |
| `apply --dry-run` | `cmd_apply` 298-304 | nothing; stdout one line per non-keep action and counts; refusals still exit 3 (293 precedes 298). |
| `check --project P` | `cmd_check` 340 | stdout problems and a count; exit 0, 1 (drift or interrupted apply), 2 (no receipt). |
| `survey --project P [--source S]` | `cmd_survey` -> `survey` -> `survey_text` | stdout report; exit 0, 2 when P is not a folder. |
| `survey --toml` | `cmd_survey` -> `starter_config` | stdout starter `.devtools.toml`. |
| `compare --project P [--source S]` | `cmd_compare` 959 | stdout rows and totals; exit 2 without `.devtools.toml`. |
| `compare <paths>` | `cmd_compare` 985-1037 | stdout the project's lines only it has, with heading, carried and close marks. |
| `compare <paths> --diff` | `cmd_compare` 1018-1023 | stdout unified diff project -> dev-tools. |
| `compare <paths> --added` | `cmd_compare` 1000-1017 | stdout lines only the shipped file has. |
| `compare --record [paths]` | `cmd_compare` 976-984 | stdout a Markdown table with only the file and line-count columns filled. |

A read-only check on a temp project under the scratchpad (`[[sync]] source = "agents"`, one agent file pre-existing): `apply` printed `refused: ... (needs --adopt)` and exited 3; `apply --adopt --dry-run` listed 4 create and 1 update and exited 0.

## 4. The entry, claim by claim

| Claim | Verdict | Settled by |
|---|---|---|
| does: "Copy dev-tools skills and scripts into a project from its .devtools.toml" | true; it also copies the agents folder and writes settings JSON files | `desired_files` 123-159, `shipped_units` 398. |
| does: "keep the copies honest with a receipt" | true | 314-319, `cmd_check` 340-359. |
| does: "(sync.py apply, check, survey, compare)" | true | `main` 1064-1088. |
| verb: sync skills | true | `cmd_apply` 281. |
| verb: copy skills into project | true | 308-311. |
| verb: install skills | true | 308-311. |
| verb: apply sync | true | 1064. |
| verb: devtools.toml | true | `read_config` 102. |
| verb: receipt | true | 314-319. |
| verb: devtools-receipt | true | 58. |
| verb: check copies | true | `cmd_check` 340. |
| verb: hand edit | true | `plan` 221-223. |
| verb: adopt existing copies | true | `plan` 225, `--adopt` 1067. |
| verb: survey project | true | `survey` 502. |
| verb: starter config | true | `starter_config` 727. |
| verb: compare before replacing | true | `cmd_compare` 959. |
| verb: settings files | true | 157-159. |
| verb: after_apply | true | 323-336. |
| verb: fill tokens | true | `fill_tokens` 88. |
| tests: tests/test_sync.py | true but incomplete: `tests/test_tools.py:64`, `tests/test_review_tool.py:68` and `tests/test_from_gsd.py:191` also run `sync.main(["apply", ...])` as a fixture | — |
| duplicates: devtools/from_gsd.py | overstated as a module duplicate: only `OTHER_PLANS` and the 4-line search loop repeat | see suggestion 1 below. |
| note: "Read: the module docstring, the documented functions and the four commands." | true of the first build, now superseded | — |
| note: "survey and compare write nothing" | true: they print only; their git calls are `ls-files` | `cmd_survey` 846, `cmd_compare` 959-1058, 427, 578. |
| note: "adopt-devtools is the skill that drives them" | true | `skills/adopt-devtools/SKILL.md:61`, `:126`, `:169`. |
| note: "from_gsd.py repeats its other_plans and OTHER_PLANS (REVIEW.md)" | true in part | below. |

REVIEW.md suggestion 1, checked against both bodies: true in part. `diff` of `from_gsd.py:46-48` against `sync.py:454-456` printed nothing, and `diff` of the loops `from_gsd.py:492-495` against `sync.py:463-466` printed nothing. The functions differ after the loop: `from_gsd.py:496` returns `[{"tool", "sign"}]`, `sync.py:467` returns `(sign, tool)` tuples, and `sync.py:468-477` adds a planning folder in a foreign format. The review's "both run from a dev-tools checkout and are not shipped" is true: `shipped_units` takes only `skills/` and `agents` (393-403), and no file under `plugins/` is named `from_gsd.py` or `sync.py`.

## 5. What the entry leaves out

- Deletes managed files that are no longer shipped, refusing a hand-changed one without `--force` (202-209, 312).
- Journal: an interrupted apply is finished by the next apply, and `check` reports it (305-307, 320, 196, 346-347).
- `--dry-run` for apply (298-304).
- Records and checks each file's mode, not only its hash (217-218, 316, 354-355).
- Records the dev-tools commit in the receipt and warns when the taken sources are dirty (178-190, 315).
- Warns when git ignores delivered files (243-278).
- Path safety: refuses `..`, absolute paths, dests through a symlink out of the project, and two dests that are one file (81-85, 160-170).
- `exclude` keeps files of a directory source as the project's own (129, 143-152).
- `replaces` names an old copy that compare reads and nothing deletes (900-905, 785).
- Refuses `TODO` values and values with no token (131-135, 155-156).
- Survey reports a GSD planning folder and points to `from_gsd.py` or the milestone route (599-619).
- Survey reports other planning tools' plans and a planning folder in a foreign format (459-478, 620-625).
- Survey flags same-name, different-skill clashes and symlinked skill folders (531-532, 656-663).
- Survey prints a `git grep` that finds what reads the copies (664-683).
- Starter config infers token values from the project's copies (699-724, 737-742).
- Starter config fills settings from the shipped script's `DEFAULT_SETTINGS`, the project's settings JSON and the old script's constants (744-771).
- Compare shows where a lost line now lives in a file the project owns, CLAUDE.md or AGENTS.md (911-931).
- Compare `--diff`, `--added`, `--record` (1018-1023, 1000-1017, 976-984).
- Standalone scripts under `skills/` (the pytest plugin) are units of their own (400-402).
- adopt-devtools and move-from-gsd are never offered to a project (64, 403).
- Points a project with no counterparts at the example configs (827-834, 962-964).
- Other tests depend on `apply` as their fixture (section 4, tests row).

## 6. Docstring against body

- Module docstring line 4 calls the script a "Prototype"; the body has four commands and `tests/test_sync.py` has 43 tests. Whether it is still a prototype is the owner's word: not settled.
- Module docstring lines 20-22 do not say that apply deletes managed files no longer shipped (206, 312) or that it keeps a journal (305-320).
- Module docstring line 22: refuses to overwrite "unless told to"; it also refuses to delete a hand-changed file no longer shipped (208-209), and refuses in `--dry-run` too (293 before 298).
- Module docstring line 30: exit 1 is "check found drift"; the Python-version guard also exits 1 with a message (54).
- `plan` 194: "Returns (actions, refusals)". Both callers discard the refusals (286, 865), so the reason text ("changed in the project since the last sync") never reaches the user; checked on a temp project, see section 3.
- `survey` 503: "Reads only." True of files; it runs `git ls-files` (427) and `survey_text` runs it once per reported path (578).
- `starter_config` 728: "puts each shipped unit where the project keeps its own copy". It puts a skill under the shipped folder name beside the copy and names the copy under `replaces` (780-785), and gives scripts kept outside the copy entries of their own (817-823).
- `compare_rows` 864 does not say it also finds twin copies of one origin and counts them once (920-923).

## 7. Other scripts

Runs or loads:

- `subprocess.run` of git: `source_identity` (181: `rev-parse HEAD`, `status --porcelain`), `ignored_by_git` (247 `check-ignore`, 251 `rev-parse`), `walk_project` (427 `ls-files`), `tracked` (578 `ls-files`).
- `subprocess.run(shlex.split(command), cwd=project)` for each `after_apply` line of the project's config (327): it runs whatever the project lists, typically a synced script such as `components_index.py write`.
- `ast.parse` of shipped scripts and of the project's old scripts to read `DEFAULT_SETTINGS` and constants without running them (486-499, 745, 749).
- No `runpy`, no `importlib`, no import of another repository module.
- Paths to other parts of the repository: `skills/` (395), `agents` (398), `EXAMPLES` (66), `NOT_FOR_PROJECTS` (64); `from_gsd.py` and `phase_tool.py setup` named only in printed text (614-618, 624).
- Its receipt (58, 314-318) is read by `devtools/from_gsd.py:906`.

Same name defined in another shipped script (`ast` over `skills/` and `devtools/`):

| Here | Elsewhere | Same body? |
|---|---|---|
| `other_plans` 459 | `devtools/from_gsd.py:489` | Partly (section 4). |
| `read_json` 174 | `skills/milestone/process-phase/scripts/review_tool.py:165` | Yes, the same one line. |
| `git` 180 (nested) | `devtools/from_gsd.py:428`, `skills/components/scripts/components_index.py:980`, `skills/milestone/process-phase/scripts/review_tool.py:143`, `skills/phase/process-phase/scripts/codex_gate.py:14`, `skills/phase/process-phase/scripts/phase_tool.py:221`, `devtools/release_plugins.py:48` | No; closest is `from_gsd.py:428` (stripped stdout or `""`, but no timeout or `OSError` catch here). |
| `inside` 81 | `skills/phase/process-phase/scripts/phase_tool.py:1033` | No (that one tests whether entries cover an entry). |
| `walk` 406 | `devtools/from_gsd.py:460` (nested) | No. |
| `covered` 566 | `skills/components/scripts/rules_check.py:957` (nested) | No. |
| `cmd_check` 340 | `phase_tool.py:1470` | No. |
| `state` 585 (nested) | `phase_tool.py:309` (method) | No. |
| `add` 117 (nested) | `review_tool.py:271`, `handoff.py:818`, `devtools/build_plugins.py:159`, `devtools/from_gsd.py:350` | No. |
| `__init__` 72 | `coder_pool.py:116`, `phase_tool.py:175`, `phase_tool.py:300` | No. |
| `main` 1061 | every other script | No. |

Searched for `plugin_root`, `checkout_root`, `load_settings`, `Stop`: not defined here.

## 8. Proposed entry

- does: Copy dev-tools skills, agents and standalone scripts into a project from its .devtools.toml and keep the copies honest with a receipt: apply writes, updates and deletes them, check finds drift, survey finds a project's own copies and prints a starter config, compare shows what an apply would replace and lose (sync.py)
- verbs: sync skills, copy skills into project, install skills, apply sync, devtools.toml, receipt, devtools-receipt, check copies, hand edit, adopt existing copies, survey project, starter config, compare before replacing, settings files, after_apply, fill tokens, delete files no longer shipped, interrupted apply journal, dry run sync, force overwrite, file mode drift, exclude files, replaces old copy, git ignores delivered files, dirty dev-tools source, infer token values, default settings, lines only the project has, diff against shipped, added lines, migration record table, gsd planning folder in survey, other planning tools
- notes: Read in full at 3963a46. Exit codes 0 ok, 1 drift, 2 configuration, 3 refused (nothing written), 4 after_apply failed. A refusal names only the flag it needs; plan's reason text is dropped. after_apply runs the project's own commands, without a shell, only when a file changed. survey and compare write nothing (git ls-files only); adopt-devtools is the skill that drives them. tests/test_tools.py, test_review_tool.py and test_from_gsd.py use apply as a fixture. Its OTHER_PLANS list and search loop are the same as from_gsd.py's; its other_plans also flags a planning folder the phase tool cannot read (REVIEW.md suggestion 1).
