# phase_tool.py

## 1. Header

- Path: `skills/phase/process-phase/scripts/phase_tool.py`
- Lines: 2051 (`wc -l`)
- Blob: `dfc65f6f20a571c0af6fb8cdf95d0581467901a3` (`git hash-object`), unchanged from `3963a46`.
- Entry: `phase.state`.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `plugin_root` | 47 | Returns `parents[3]` when the script sits in `<x>/skills/<s>/scripts/` and `<x>/.claude-plugin/plugin.json` exists, else None. |
| `checkout_root` | 56 | Returns the first of cwd and its parents holding `.git`, else cwd. |
| `load_settings` | 99 | Overlays the JSON settings file on `DEFAULT_SETTINGS`; an unknown key raises `SystemExit` naming it. |
| `ToolError` | 172 | Exception carrying code, message, hint, exit code and envelope data. |
| `ToolError.__init__` | 175 | Stores the five fields, data defaulting to `{}`. |
| `Parser` | 181 | `ArgumentParser` subclass whose errors become `ToolError`. |
| `Parser.error` | 184 | Raises `ToolError("USAGE", ..., exit_code=2)`. |
| `today` | 191 | Returns today's ISO date. |
| `norm_phase` | 195 | Turns `6`, `"06"`, `6.1` into `06` / `06.1`; a non-number raises `BAD_PHASE` (exit 2). |
| `phase_key` | 204 | Sort key `(major, minor)` with a whole phase as minor -1. |
| `rel` | 210 | Path relative to root as posix, or the path itself when outside. |
| `issue` | 217 | Builds the `{file, line, rule, message}` dict every check returns. |
| `git` | 221 | Runs `git <args>` in root with a 30 s timeout; stdout on exit 0, else None. |
| `find_root` | 230 | `--root` if given, else the first of cwd and parents holding the planning dir, else cwd. |
| `split_frontmatter` | 243 | Splits a leading `---` block into lines and body; `(None, text)` when absent or unclosed. |
| `parse_frontmatter` | 255 | Reads flat `key: value` lines (skipping indented, comment and colon-less lines), stripping quotes. |
| `format_value` | 266 | Writes None as `null` and quotes `current_phase` / `completed_phases`. |
| `update_frontmatter` | 272 | Rewrites the given flat keys in place and appends missing ones; adds a block when there is none. |
| `phase_list` | 290 | Extracts every number in a string as normalised phase ids. |
| `Planning` | 297 | Wrapper over root and `root/<planning_dir>` with roadmap and state readers. |
| `Planning.__init__` | 300 | Stores root and planning dir. |
| `Planning.require` | 304 | Raises `NO_PLANNING` when the planning dir is missing. |
| `Planning.state` | 309 | Parses STATE.md frontmatter (`NO_STATE` if absent); a `complete` state with open roadmap phases is returned as the first open phase `not_started`, without writing. |
| `Planning.roadmap_text` | 324 | ROADMAP.md text or "". |
| `Planning.phases` | 328 | Parsed roadmap phases sorted by `phase_key`. |
| `Planning.phase` | 331 | The phase with a given id, or None. |
| `Planning.phase_dir` | 337 | First directory `phases/<nn>-*`, or None. |
| `Planning.ensure_phase_dir` | 342 | Returns the phase dir, creating `phases/<nn>-<slug>` when missing. |
| `parse_roadmap` | 353 | Parses `## Phase N[.M]: Title` blocks and their `- **Field:** value` bullets into dicts with line numbers. |
| `public_phase` | 382 | Drops the `_`-prefixed keys of a phase dict. |
| `parse_requirements` | 386 | Collects `| U.. |` row lines and first-seen `| REQ-X-N |` rows (U ids, phases, status in cell 4). |
| `load_gates` | 408 | Reads `gates.json` beside the script; `{}` on any read or JSON error. |
| `gates_for` | 415 | Gate names whose `from_phase` is at or below the phase's major number, sorted by their digits. |
| `missing_artifacts` | 425 | Lists the ARTIFACTS a status has reached that are absent, per-plan summaries once any summary exists, and `EVIDENCE/prove.md` at exactly `tests_approved` when CONTEXT says `evidence_gate: required`. |
| `finished_elsewhere` | 451 | True for a `complete` phase whose `Acceptance tests` field starts with "none". |
| `open_phases` | 458 | Incomplete roadmap phases, those with all dependencies done first. |
| `next_phase` | 465 | First open phase, else the STATE current phase. |
| `cmd_status` | 471 | Reports phase, status, steps; without `--brief` adds dir, title, missing artifacts, blockers, gates, git branch and dirty flag. |
| `cmd_setup` | 526 | Refuses a planning dir whose STATE/ROADMAP/REQUIREMENTS it cannot parse (`FOREIGN_PLAN`), then copies `templates/planning/*` with substitutions, keeping existing files. |
| `cmd_setup.text` | 538 | Reads a planning file's text or None. |
| `cmd_init` | 568 | Creates the phase dir and its CONTEXT, DISCUSSION-LOG, TESTS, DEFERRED files from templates (CONTEXT from a built-in skeleton when absent) and `EVIDENCE/.gitkeep`. |
| `cmd_roadmap` | 602 | `list` returns all phases; `get NN` returns one with its raw block. |
| `check_top_level` | 620 | One issue per missing `TOP_LEVEL` planning file. |
| `check_state` | 625 | Checks STATE.md has the `STATE_KEYS` and valid `phase_status` / `active_step`. |
| `check_roadmap` | 639 | Checks numbering (contiguous unless `phase_gaps`, unique ordered), parent of insertions, fields, slug not starting with a digit, status, dependencies earlier, and agreement with STATE. |
| `coverage` | 690 | Computes U-to-REQ coverage and REQs with no or unknown phase (known phases default to 00-06 when the roadmap is empty). |
| `check_requirements` | 704 | Issues for uncovered U, no U rows, unphased REQ, unknown U references and status not Planned/Validated. |
| `check_docs` | 725 | Each `<planning>/docs/*.md` needs `normative_for`, and no topic may have two owners. |
| `check_ignored` | 740 | Runs `git check-ignore --no-index` on `planned-paths.txt` entries and reports ignored ones. |
| `check_skill` | 757 | Checks a skill's SKILL.md frontmatter name/description, length under 500 lines and that backticked `references/` `templates/` `scripts/` files exist. |
| `check_skills` | 785 | Runs `check_skill` over every skill under `skill_roots` and checks agent name/description, limited to receipt files when `skill_check` is `synced`. |
| `hashable` | 808 | A file outside `__pycache__`/`.pytest_cache` and not `.pyc`/`.pyo`. |
| `acceptance_files` | 813 | sha256 of every file under `<acceptance_dir>/pNN_*`, skipping inserted-phase folders for a whole phase. |
| `fixture_files` | 825 | sha256 of declared fixture files, expanding directories; a missing one raises `NO_FIXTURE` (exit 2). |
| `current_fixture_hashes` | 840 | sha256 of the locked fixture paths that still exist. |
| `check_testlock` | 844 | Compares the TESTLOCK.json hashes with current tests and fixtures: removed, added, modified. |
| `check_all_testlocks` | 875 | Runs `check_testlock` for every `phases/*/*-TESTLOCK.json`. |
| `check_doc_file` | 883 | Flags `{{X}}` placeholders, files under 200 chars, a plan naming no test, and for plans the Reuse section. |
| `check_plan_reuse` | 899 | Requires `searched:`, `external:` and `reuse:` or `new_component:` lines in `## Reuse`, and reuse ids that are catalog headings. |
| `scalar` | 923 | A YAML-ish value: text inside quotes, or before a ` #` comment. |
| `frontmatter_list` | 932 | A frontmatter list written inline or as `- item` lines. |
| `listed` | 952 | Items of a task field: backticked ones, else comma/line separated, `./` stripped. |
| `parse_plan` | 964 | Parses wave, declared keys, reuse and new components, depends_on, turns_green claims, requirements, and each `### id` task's files, tests, read_first, type and verify. |
| `phase_plans` | 996 | Parses every `NN-*-PLAN.md` of a phase, id taken from the file name. |
| `overlap` | 1006 | Whether two `files` entries (path, folder, `*` pattern) can name the same file, erring towards yes. |
| `index_paths` | 1026 | The component catalog, the `INDEX_FILES` beside it, and its `modules/` and `external/` folders. |
| `inside` | 1033 | Whether an entry equals, sits under, or matches one of the given entries. |
| `track_cap` | 1039 | Runs `coder_pool.py show --json --root` and returns a positive int `effective_tracks`, else None. |
| `plan_order` | 1054 | Resolves each plan's depends_on (NN-MM, MM or file name) to ids, the transitive predecessors, and the unresolved entries. |
| `plan_order.reach` | 1073 | Depth-first transitive closure from one plan. |
| `check_plan_order` | 1088 | Issues for unknown/self deps, missing wave, loops, deps in later waves and same-wave unordered plans sharing non-shared files; a warning when a wave's free plans exceed `track_cap`. |
| `traceability` | 1142 | Reads `test_dir` and the rows of `## Traceability` naming tests, with a guard flag from the last cell. |
| `test_path` | 1155 | Prefixes a bare test file name with the test_dir. |
| `check_plans` | 1161 | Issues for plans with no task, no REQ, empty verify, contract tests no task turns green, frontmatter/task turns_green mismatch, REQs outside or unserved by the phase, plus `check_plan_order`. |
| `check_plans.full` | 1185 | `test_path` with the phase's folder. |
| `check_scope` | 1221 | Warns on changed files since the merge-base in no task's files nor a summary's Deviations row; issues for catalog components new since base on no `new_component:` line. |
| `check_capabilities` | 1274 | Executes the project's `capabilities_script` with runpy, calls `build_index(root)` and compares bytes with `capabilities_target`. |
| `heading_words` | 1305 | Lower-cased words of a heading with a trailing "s" stripped. |
| `template_sections` | 1309 | A template's numbered sections (number to title and words) and all heading titles. |
| `citation_words` | 1320 | The two words after a citation unless the first is a stopword or non-letter. |
| `check_template_citations` | 1329 | Checks every `templates/X.md §N` / `prove.md §N` / quoted heading in the skill's SKILL.md and references exists and the following words match the heading. |
| `check_template_citations.report` | 1336 | Appends a `citation` issue. |
| `merge_base` | 1359 | Merge-base of HEAD with STATE `base_branch` or `origin/<base>`; sha None when neither resolves. |
| `changed_paths` | 1372 | Yields paths of `git diff --name-status -z`, both sides of a rename or copy. |
| `check_rule_decs` | 1387 | When process-phase rule files changed since the merge-base, requires a DEC row new since base or a DEC id cited in a commit of the range. |
| `check_rule_decs.cannot` | 1395 | Builds the `rule-dec` issue for an unrunnable check. |
| `markdown_tables` | 1419 | Pipe tables as (line, cells) lists, separator dropped, only when line 2 is a separator. |
| `check_prove` | 1436 | Checks prove.md's `### Method record` table header equals PROVE.md's and rows are filled, and every Go/Pivot goal of CONTEXT's Goals table has a row. |
| `cmd_check` | 1470 | Runs the selected checks (all fixed checks when none or `--all`), adds `--plans`/`--scope` warnings, raises `CHECK_FAILED` on any issue. |
| `cmd_check.run` | 1477 | Records a check's name and extends the issues. |
| `cmd_req_coverage` | 1524 | Returns coverage, raising `COVERAGE` below 100 % or with unphased REQs. |
| `require_dec` | 1536 | Requires a `DEC-NNN` id (exit 2 otherwise) that is a row of DECISIONS.md (`UNKNOWN_DEC`). |
| `cmd_testlock` | 1549 | Hashes the phase's acceptance tests; with `--write` writes TESTLOCK.json, refusing an existing lock unless `--relock --dec`, which appends a relock entry. |
| `set_roadmap_status` | 1588 | Rewrites a phase's `**Status:**` line in ROADMAP.md; False when there is none. |
| `evidence_problems` | 1600 | Runs `cmd_evidence_check` and returns its error message as a problem. |
| `gate_problems` | 1608 | Collects a transition's blockers: prove table, parity files for `prove_method`, VERIFICATION for gaps_found, missing artifacts and dirty test lock (softer before `gated_from`), evidence for verified. |
| `cmd_advance` | 1642 | Checks the transition and dependencies, blocks on gate problems (missing artifacts waivable with `--override DEC`), then writes STATE.md and ROADMAP.md status. |
| `cmd_branch` | 1684 | Shows phase/base/git branch, or with `--set` validates the name and writes `phase_branch` to STATE.md. |
| `validate_requirements` | 1703 | Rewrites trailing `| Planned |` to `| Validated |` for REQs whose phases are all complete and writes the file. |
| `cmd_activate` | 1719 | Makes an incomplete, unblocked roadmap phase current `not_started`, given a DEC, when the current status is `not_started`/empty. |
| `cmd_complete` | 1737 | For a verified current phase, requires a DEFERRED ledger row if DISCUSSION-LOG/VERIFICATION say "deferred", then marks ROADMAP complete, moves STATE to the next open phase and validates REQs. |
| `module_name` | 1782 | Turns a path or module token into a dotted module name with `package_prefix`. |
| `cmd_migration_check` | 1792 | Finds modules marked deleted in MIGRATION.md and reports `src/**/*.py` lines importing them. |
| `golden_base` | 1821 | `--base`, else merge-base of STATE `base_branch` and HEAD, else HEAD. |
| `cmd_golden_diff` | 1832 | Lists changed and untracked files under `golden_dir` since the base and fails those whose path appears in no phase-dir `.md`. |
| `cmd_evidence_check` | 1852 | Requires VERIFICATION.md to cite backticked `-EVIDENCE/` paths that exist under root or the phase dir. |
| `cmd_facts` | 1897 | Emits a `devtools-facts/1` document of a phase's plans (waves, deps, reqs, components, declares, tasks, tests) with HEAD revision. |
| `build_parser` | 1958 | Builds the argparse tree with `--format`/`--root` accepted before or after the command. |
| `render_md` | 2005 | Renders the envelope as `tool: ok|FAILED`, error, issues/warnings lines and key/value lines. |
| `main` | 2025 | Parses, dispatches, wraps the result or any exception in one envelope, forces exit 0 for `status`, prints JSON or md. |

Count: `python3 -c "import ast;t=ast.parse(open('skills/phase/process-phase/scripts/phase_tool.py').read());print(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(t)))"` printed 110; the table has 110 rows.

## 3. Commands

Global: `--format json|md` (default md), `--root DIR`, accepted before or after the command (1960-1965). Output: one envelope on stdout (2046). Exit: 0 ok, 1 `ToolError` or internal error, 2 usage; `status` always 0 (2044).

| Command | Reaches | Writes |
|---|---|---|
| `setup [--name] [--base-branch] [--release-branch]` | `cmd_setup` 526 | Planning files from `templates/planning/` that do not exist (560). |
| `status [--phase NN\|next] [--brief]` | `cmd_status` 471 | Nothing. |
| `init --phase NN` | `cmd_init` 568 | Phase dir, CONTEXT, DISCUSSION-LOG, TESTS, DEFERRED, `EVIDENCE/.gitkeep` (592, 597). |
| `activate --phase NN --dec DEC` | `cmd_activate` 1719 | STATE.md (1732). |
| `roadmap list\|get [NN]` | `cmd_roadmap` 602 | Nothing. |
| `check [--all] [--state] [--roadmap] [--requirements] [--docs] [--ignored]` | `cmd_check` 1470 | Nothing; exit 1 on any issue (1520). |
| `check --skill DIR / --context F / --plan F / --testlock NN / --prove NN` | `check_skill` / `check_doc_file` / `check_testlock` / `check_prove` | Nothing. |
| `check --plans NN` | `check_plans` 1161 | Nothing; warnings in `data.warnings`; may run `coder_pool.py`. |
| `check --scope NN [--base REF]` | `check_scope` 1221 | Nothing. |
| `req-coverage` | `cmd_req_coverage` 1524 | Nothing. |
| `testlock --phase NN [--write [--fixture P ...] [--relock --dec DEC]]` | `cmd_testlock` 1549 | `NN-TESTLOCK.json` with `--write` (1583). |
| `advance --to STATUS [--override DEC]` | `cmd_advance` 1642 | STATE.md (1670), ROADMAP.md Status (1675). |
| `complete --phase NN` | `cmd_complete` 1737 | ROADMAP.md, STATE.md, REQUIREMENTS.md (1758, 1765, 1715). |
| `branch [--set NAME]` | `cmd_branch` 1684 | STATE.md `phase_branch` with `--set` (1698). |
| `migration-check` | `cmd_migration_check` 1792 | Nothing. |
| `golden-diff [--base REF]` | `cmd_golden_diff` 1832 | Nothing. |
| `evidence-check [--phase NN]` | `cmd_evidence_check` 1852 | Nothing. |
| `facts --phase NN` | `cmd_facts` 1897 | Nothing; facts document in the envelope's `data`. |

## 4. The entry, claim by claim

| Claim | Verdict | Settled by |
|---|---|---|
| does: "Own the phase workflow's state" | true | `setup` creates STATE.md from a template (560); only advance, activate, branch, complete rewrite it (1670, 1732, 1698, 1765). |
| does: "and planning checks" | true | `cmd_check` 1470-1521. |
| does: "setup, status, activate, check, testlock, advance, complete, facts" | true but partial | Omits `init`, `roadmap`, `req-coverage`, `branch`, `migration-check`, `golden-diff`, `evidence-check` (1950-1955). |
| verb: phase state | true | `Planning.state` 309. |
| verb: phase status | true | `cmd_status` 471. |
| verb: next phase | true | `status --phase next` 474, `next_phase` 465. |
| verb: roadmap | true | `cmd_roadmap` 602, `check_roadmap` 639. |
| verb: advance phase | true | `cmd_advance` 1642. |
| verb: complete phase | true | `cmd_complete` 1737. |
| verb: activate phase | true | `cmd_activate` 1719. |
| verb: gate problems | true, vague | Internal name `gate_problems` 1608; a searcher would say "transition gate" or "phase gate". |
| verb: check plans | true | `check --plans` 1512, `check_plans` 1161. |
| verb: plan order | true | `plan_order` 1054, `check_plan_order` 1088. |
| verb: requirements coverage | true | `cmd_req_coverage` 1524, `coverage` 690. |
| verb: test lock | true | `cmd_testlock` 1549, `check_testlock` 844. |
| verb: golden diff | true | `cmd_golden_diff` 1832. |
| verb: evidence check | true | `cmd_evidence_check` 1852. |
| verb: phase branch | true | `cmd_branch` 1684; records the name only, git is not touched (1698). |
| verb: plan facts | true | `cmd_facts` 1897. |
| verb: state md | true | STATE.md read 309, written 272. |
| notes: "Read: the module docstring, the command list and the documented functions." | superseded | This file reads every line. |
| notes: "It asks coder_pool.py for the track cap (subsystem.phase_status)" | true, overstated in reach | Only `check --plans`, only for a wave of more than one plan, only to add a warning (1134-1138, 1039-1051). |
| notes: "and runs a project's generator with runpy" | true | 1281; only in `check`/`check --all`, only when `capabilities_script` is set (1277, 1496). |
| field tests: `tests/test_tools.py` | incomplete | Also exercised by `tests/test_plugins.py:95`, `tests/test_sync.py:444,588`, `tests/test_from_gsd.py:195`. |

## 5. What the entry leaves out

- Create a phase folder and its starter files: `init` 568.
- Start a new project's planning folder, refusing a foreign (e.g. GSD) plan: `setup` 526, 543-549.
- Roadmap lint: numbering, insertions, slugs, dependency order, STATE agreement: `check_roadmap` 639.
- Skill and agent frontmatter lint (name, description, length, referenced files): `check_skill` 757, `check_skills` 785.
- Template citation check (`§N` against headings): `check_template_citations` 1329.
- Rule text change needs a DEC: `check_rule_decs` 1387.
- Planned paths not git-ignored: `check_ignored` 740.
- Normative docs ownership: `check_docs` 725.
- Prove method record and parity evidence: `check_prove` 1436, `gate_problems` 1619-1622.
- Plan reuse section (`searched:`, `external:`, `reuse:`/`new_component:`): `check_plan_reuse` 899.
- Scope drift of a phase branch against its plans: `check --scope` 1221.
- Fixture locking and re-lock by DEC: `cmd_testlock` 1576-1582.
- Gate override by DEC (missing artifacts only): `cmd_advance` 1661-1664.
- Deferred-work ledger check at complete: 1746-1753.
- Requirements marked Validated at complete: `validate_requirements` 1703.
- Imports of deleted modules: `migration-check` 1792.
- Capabilities file stale check: `check_capabilities` 1274.
- Phase plan parser (waves, tasks, files, turns_green): `parse_plan` 964.
- Same-wave file conflicts between plans: `check_plan_order` 1118-1133.
- JSON envelope / md output for every command: `main` 2025, `render_md` 2005.

## 6. Docstring against body

- Module docstring (4-5): "Every command prints exactly one JSON envelope". A bad settings file raises `SystemExit` at import (105, 147, 149, 151): plain text on stderr, exit 1, no envelope. Ran `status --format json` on a copy under `/private/tmp` with `{"bogus":1}` settings: stderr message, exit 1.
- Module docstring (24): "`status` always exits 0" is true even for `NO_PLANNING` (2044); ran on a copy without a planning dir: `ok: false`, exit 0.
- `Planning` (298): "the .planning/ directory" is the `planning_dir` setting (302, 111).
- `Planning.state` (309): returns a synthesized next-phase state when STATE says `complete` and the roadmap has open phases (318-321); no docstring says so, only a comment.
- `check_capabilities` (1275): "without loading the product or writing files". The body executes the project's script with runpy (1281), which can do either; and it reports against a fixed `docs/CAPABILITIES.md` (1288), not `capabilities_target`. A `KeyError` (no `build_index`) escapes the caught set (1286) to `INTERNAL` (2040).
- `cmd_golden_diff` (1833) and its hint (1848) say a changed golden is declared "with a DEC id"; the body only checks the path is a substring of the phase dir's `.md` text (1843-1844).
- `missing_artifacts`: `prove.md` is reported only when the status is exactly `tests_approved` (443), not at later statuses.
- `coverage`: with an empty roadmap the known phases default to `00`-`06` (694); undocumented.
- `check_roadmap` message "phases not contiguous from 0" also fires for a roadmap starting at 1 with a gap; a roadmap starting at 1 is accepted (648, 651).
- `validate_requirements`: counts a REQ as validated even when `Planned` is not the last cell and the substitution does nothing (1711-1714); rewrites REQUIREMENTS.md even with no change (1715).
- `check_prove`: the issue says "11-column table" (1448) while the header is read from PROVE.md (1444); a PROVE.md without a `| Goal |` line raises `StopIteration` to `INTERNAL`.
- `check --skill`, `--context`, `--plan` resolve against the working directory, not `--root` (1502, 1506, 1510).
- Module docstring (24): "2 usage error" does not hold for `status`: `main` takes the command from an argv scan before parsing (2029) and forces exit 0 for it (2044), so `status --bogus` prints a USAGE error and exits 0 (ran on the `/private/tmp` copy).
- The same scan takes the first argv token equal to a command name, so an option value placed before the command (e.g. `--root status ...`) names the envelope of a usage error.
- `check_plans` (1168) and `check_scope` (1223): "Advisory: no step of the workflow requires it yet" is not settled from this module; it is a claim about the skill text.

## 7. Other scripts

Runs or loads:

- `track_cap` 1042-1047: builds `SCRIPT_DIR / "coder_pool.py"` and runs `sys.executable coder_pool.py show --json --root <root>` with `subprocess.run`; reads `coders.effective_tracks`.
- `check_capabilities` 1281: `runpy.run_path(<root>/<capabilities_script>)`, then calls its `build_index(root)`.
- `git` 224 and `check_ignored` 749: `subprocess.run(["git", ...])` (not a repository script).
- Data paths: `gates.json` beside the script (43, 410); `templates/` beside the skill (42, 533, 579, 1443); `.devtools-receipt.json` written by `devtools/sync.py` (96, 789); the component catalog and `INDEX_FILES` that `components_index.py` writes (1218, 1026-1030).
- Text only: the setup hint names `devtools/from_gsd.py` (547); `PLUGIN_TOOL` names this script's plugin path for templates (67, 532).

Loaded by others: `skills/components/scripts/rules_check.py:792` loads this file with importlib for its fact types; `rules_check.py:100` keeps its own copy of `PLAN_KEYS` (this file 961); `FACT_TYPES` follows the shape `components_index.py facts` writes (1877).

Same names in other shipped scripts (`def`/`class` in `skills/`, `devtools/`):

| Name | Here | Also | Same body |
|---|---|---|---|
| `plugin_root` | 47 | `coder_pool.py:50`, `handoff.py:45`, `review_tool.py:64`, `rules_check.py:230`, `components_index.py:94` | yes, all (ast compare, docstring dropped) |
| `checkout_root` | 56 | `coder_pool.py:59`, `handoff.py:54`, `review_tool.py:73`, `rules_check.py:239`, `components_index.py:103` | yes, all |
| `load_settings` | 99 | `coder_pool.py:78`, `handoff.py:86`, `review_tool.py:121`, `rules_check.py:219`, `components_index.py:79` | same as `coder_pool.py` only |
| `find_root` | 230 | `coder_pool.py:327` | no: here the planning dir marks the root, there `.git` |
| `git` | 221 | `codex_gate.py:14`, `review_tool.py:143`, `components_index.py:980`, `release_plugins.py:48`, `sync.py:180` (nested), `from_gsd.py:428` | no: signatures and failure handling differ |
| `main` | 2025 | every other shipped script | no |
| `cmd_status` | 471 | `review_tool.py:669`, `release_plugins.py:110` | no |
| `cmd_check` | 1470 | `sync.py:340` | no |
| `coverage` | 690 | `components_index.py:254` | no |
| `inside` | 1033 | `sync.py:81` | no |
| `Planning.state` | 309 | `sync.py:585` (`def state`) | no |
| `Planning.roadmap_text` | 324 | `from_gsd.py:932` | no |
| `cmd_check.run` | 1477 | `rules_check.py:382` (`def run`) | no |

No `Stop` class here; errors are `ToolError` (172).

## 8. Proposed entry

- does: Own a phase's state in `.planning/` (STATE.md, ROADMAP.md status, REQUIREMENTS.md validation) and its planning checks: setup, init, status, roadmap, activate, advance, complete, branch, check, req-coverage, testlock, golden-diff, evidence-check, migration-check, facts (phase_tool.py)
- verbs: phase state, phase status, next phase, roadmap, roadmap lint, start planning folder, init phase folder, advance phase, complete phase, activate phase, transition gate, gate override, check plans, plan order, wave file conflict, plan scope drift, plan reuse section, requirements coverage, validate requirements, test lock, relock, lock fixtures, golden diff, evidence check, prove method record, deferred ledger, migration check, deleted module imports, skill lint, template citations, rule change needs dec, capabilities stale, phase branch, plan facts, state md, json envelope
- notes: Every command prints one envelope (`--format json|md`); `status` always exits 0, a usage error included, and a bad `phase_tool.settings.json` exits 1 at import with no envelope. `check --plans` runs coder_pool.py show --json for the track cap, only to warn (subsystem.phase_status); `check` runs the project's `capabilities_script` with runpy and calls its `build_index`. rules_check.py loads this file with importlib for its fact types and copies `PLAN_KEYS` (subsystem.rule_check). `plugin_root` and `checkout_root` are the same code as in five other scripts.
