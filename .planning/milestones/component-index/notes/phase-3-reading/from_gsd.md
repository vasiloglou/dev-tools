# Reading: devtools/from_gsd.py

## 1. Header

- Path: `devtools/from_gsd.py`
- Lines (`wc -l`): 1410
- Blob (`git hash-object devtools/from_gsd.py`): `83289e5c8b5af2cf2ce0af2e9da4d240fcb88a0d`
- Read at commit `3963a46` (HEAD; `git diff --stat 3963a46 -- devtools/` printed nothing).
- Entry: `migrate.from_gsd`.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `Stop` | 71 | Bare `Exception` subclass; `main` prints it to stderr and exits 2. |
| `norm` | 75 | Zero-pads a phase number to `NN` or `NN.m`. |
| `key` | 80 | Sort key `(major, minor or -1)` for a normalised phase id. |
| `shown` | 85 | Writes an id as a roadmap heading does (`7`, `7.1`), dropping the padding. |
| `read` | 91 | File text as UTF-8, or `""` when the path is not a file. |
| `frontmatter` | 95 | Reads top-level `key: value` lines between leading `---` markers into a dict, quotes stripped. |
| `plain` | 107 | Drops `(INSERTED)`, `**`, backticks, collapses spaces and trims dashes, colons, stars and tick marks. |
| `slugify` | 112 | Lowercase hyphen slug, at most 60 characters, `phase` when empty. |
| `cell` | 116 | Replaces `\|` with `/` and collapses whitespace so text fits one table cell. |
| `sections` | 121 | `{heading: body}` for headings of one Markdown level. |
| `parked` | 136 | Returns the put-off word (paused, deferred, backlog...) found in any case for a section, or in capitals/brackets for a phase line. |
| `phase_numbers` | 147 | Every phase number after "Phase(s)", expanding whole-number ranges up to 200 wide, normalised and sorted. |
| `dependencies` | 163 | Splits a "Depends on" text into the numbers of its first clause (brackets and "independent of"/"in parallel with" tails removed) and the other numbers it names. |
| `same_phase` | 179 | True when two titles are equal ignoring case or share at least half the words (longer than 2 letters) of the shorter. |
| `words` | 182 | Nested in `same_phase`: the set of lowercase words longer than 2 characters. |
| `runs` | 188 | Splits roadmap entries in file order into runs, starting a new run when a number repeats with a different title. |
| `one_run` | 201 | Merges all runs into one dict, first entry wins, `done` OR-ed across repeats. |
| `read_roadmap` | 212 | Parses GSD ROADMAP.md into checklist items and `Phase N:` detail sections (fields, success criteria, plan count, milestone version, parked word), each split into runs. |
| `read_folders` | 261 | Lists `phases/NN-slug/` folders with their CONTEXT, PLAN, SUMMARY and VERIFICATION files and the verification's frontmatter status, and notes misnamed or duplicate folders. |
| `left_by_gsd` | 287 | One phrase saying what GSD left in an unfinished phase's folder. |
| `read_requirements` | 298 | Parses REQUIREMENTS.md into checkbox (current) and non-checkbox (later) requirements with groups and continuation lines, traceability-table phases, archived definitions from `milestones/*REQUIREMENTS.md`, and the out-of-scope list. |
| `out_of_scope` | 330 | Rows or bullets of the "Out of Scope" section as strings, header and rule rows skipped. |
| `named_ids` | 344 | Requirement ids in a line that are defined somewhere or look like GSD ids, expanding `X-01 through X-03` ranges up to 50 wide. |
| `add` | 350 | Nested in `named_ids`: appends a name once if defined or GSD-shaped. |
| `row_cells` | 366 | Splits a Markdown table row on `\|`, keeping pipes inside backticks or escaped. |
| `read_decisions` | 386 | Reads the Key Decisions table, finding decision, rationale, outcome and date columns by header words, falling back to fixed positions. |
| `column` | 393 | Nested in `read_decisions`: index of the first header containing any given word. |
| `read_project` | 409 | Reads PROJECT.md (the root's for a workstream) into name, what-this-is, core value, constraints and decisions. |
| `part` | 418 | Nested in `read_project`: body of the first section whose heading starts with a name. |
| `git` | 428 | Runs `git <args>` in the project with a 30 s timeout; stripped stdout on exit 0, else `""`. |
| `tool_folders` | 436 | The fixed runtime folders plus every other top-level dot-folder not in `NOT_A_TOOL`. |
| `gsd_entries` | 450 | Counts GSD-named strings in a settings JSON outside and inside the top-level `permissions` block; non-JSON counts as calls. |
| `walk` | 460 | Nested in `gsd_entries`: recursive JSON walk that tallies the counts. |
| `hook_files` | 473 | For each tool folder's `settings.json`, `settings.local.json`, `hooks.json` naming GSD, reports counts and whether git tracks it. |
| `other_plans` | 489 | Globs `OTHER_PLANS` and returns `[{"tool", "sign"}]`, first hit per tool. |
| `gsd_pointer` | 499 | The current phase from STATE.md's `current_phase` frontmatter or a `Phase: N` line, normalised. |
| `installed` | 506 | Per tool folder, GSD's files from its manifest plus every file matching the `INSTALLED` name patterns, with the manifest's version. |
| `default_branch` | 531 | Base branch from `origin/HEAD`, else a local main/master/develop; `("main", "not a git repository")` outside git; `("", "")` otherwise. |
| `plan_ignored` | 547 | Whether `git check-ignore` ignores `<planning_dir>/MANIFESTO.md`; None outside a work tree or on git failure. |
| `read_workstreams` | 559 | Lists `workstreams/*` folders that hold phases, a STATE frontmatter or a ROADMAP, with last activity, status and the active one. |
| `code_summary` | 577 | Top three tracked file suffixes (skipping runtime and planning folders), Python file count, Python setup files, and whether the project is Python; None when `git ls-files` prints nothing. |
| `map_ids` | 598 | Maps GSD ids to `REQ-<LETTERS>-<digits>`, giving letter-suffixed or colliding ids the next free number in their family. |
| `build` | 621 | Reads the whole GSD project into one model dict (phases, status, current phase, requirements, notes, workstreams, branch, installs, hooks), raising `Stop` on a non-GSD, already-moved, half-moved or ambiguous project. |
| `roadmap_text` | 932 | Writes the dev-tools ROADMAP.md: one `## Phase` block per phase, a placeholder block for missing whole numbers, and a "Put off under GSD" list. |
| `requirements_text` | 986 | Writes REQUIREMENTS.md: U rows per GSD group, the requirement table with phases and Planned/Validated, plus loose, put-off and out-of-scope sections. |
| `state_text` | 1027 | Writes STATE.md frontmatter (current phase, status, branches, completed phases) and its where/next/lessons/from-GSD sections. |
| `decisions_text` | 1064 | Writes DECISIONS.md with DEC-001/002 for the move and one row per carried PROJECT.md decision. |
| `manifesto_text` | 1086 | Appends PROJECT.md constraints as `T3...` rules and its what-this-is and core value to the MANIFESTO template. |
| `readme_text` | 1098 | Appends a "History from GSD" table of the archive and kept GSD folders to the README template. |
| `record_text` | 1115 | Writes CONVERSION.md: owner to-dos, files table, phases table, put-off table, workstreams table, id map, and the dev-tools commit. |
| `convert` | 1165 | Refuses on missing templates, unchosen workstreams, git-ignored plan, unknown base or a half run; then (unless dry run) moves GSD files, writes templates and drafts, the record, and STATE.md last. |
| `template` | 1193 | Nested in `convert`: a template file with `{{NAME}}`, `{{DATE}}`, `{{BASE}}`, `{{RELEASE}}`, `{{TOOL}}` filled. |
| `survey_lines` | 1254 | Formats the model as the survey report, ending with suggested `.devtools.toml` settings and the to-settle notes. |
| `plan_line` | 1265 | Nested in `survey_lines`: one aligned line per GSD plan (root or workstream). |
| `main` | 1351 | Parses `survey`/`convert`, builds the model, dispatches, prints text or JSON, maps `Stop` to exit 2. |

Count: `python3 -c "import ast; t=ast.parse(open('devtools/from_gsd.py').read()); print(sum(isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for x in ast.walk(t)))"` printed 55 (1 class, 54 functions, 7 of them nested). The table has 55 rows.

## 3. Commands

| Command / option | Reaches | Writes |
|---|---|---|
| `survey` | `main` -> `build` -> `survey_lines` (1383-1391) | stdout report; exit 0, or 2 with `from_gsd: <message>` on stderr from `Stop`. |
| `survey --format json` | `main` 1384-1388 | stdout JSON of 23 model keys (`signs` ... `elsewhere`). |
| `survey --installed` | `main` 1380-1382 | stdout, one path per GSD file inside the project; `--format` ignored. |
| `--project` (both, default `.`) | `build` 1379 | none. |
| `--planning-dir` (both) | `build` 623-627 | none; a `workstreams/<name>` path is read as a workstream. |
| `--numbering first\|last\|same` (both) | `build` 657-676 | none; picks or merges runs when GSD restarted numbering, else `Stop`. |
| `--complete N,N` (both) | `build` 624, 715-716 | none; marks phases complete, `Stop` on an unknown number (698-702). |
| `--open N,N` (both) | `build` 625, 717 | none; keeps put-off phases in the roadmap, `Stop` on an unknown number. |
| `convert` | `main` -> `build` -> `convert` (1392) | `.planning/archive/gsd/` (moved STATE, ROADMAP, REQUIREMENTS, PROJECT.md, config.json, plus CONVERSION.md), `phases/<NN-slug>/gsd/` (moved PLAN/SUMMARY/VERIFICATION of open phases), every template under `skills/phase/process-phase/templates/planning/` not already present, `archive/gsd/<NAME>-to-merge.md` drafts, and the three files; stdout list; exit 0 or 2. |
| `convert --dry-run` | `convert` 1228-1229 | nothing; still runs every refusal; prints "would write". |
| `convert --format json` | `main` 1397-1399 | stdout `{"written", "kept", "dry_run"}`. |
| `--owner` | `decisions_text` 1066 | approver name on DEC rows. |
| `--base-branch` | `convert` 1180 | STATE.md `base_branch`/`phase_branch`; `Stop` when absent and undetectable. |
| `--release-branch` | `convert` 1190, 1207 | STATE.md `release_branch` (defaults to base). |
| `--tool` | `convert` 1191 | `{{TOOL}}` in README.md (default `.claude/skills/process-phase/scripts/phase_tool.py`). |
| `--root-plan` | `convert` 1171, 1184-1187 | allows moving the root plan beside workstreams; rewrites the note. |
| `--ignored-plan` | `convert` 1177 | allows moving a git-ignored planning folder. |

`survey --help` and `convert --help` were run read-only to confirm `--dry-run` through `--ignored-plan` attach to `convert` only (the loop variable `p` is the convert parser at 1369).

## 4. The entry, claim by claim

| Claim | Verdict | Settled by |
|---|---|---|
| does: "Move a project's planning folder from GSD to the dev-tools phase workflow" | true | `convert` 1165-1248. |
| does: "survey reads it" | true | `main` 1383-1391 calls only `build` and prints; `git` calls are read-only (430, 552). |
| does: "convert rewrites STATE, ROADMAP and REQUIREMENTS" | overstated in scope, true as far as it goes: it also moves PROJECT.md and config.json to the archive, moves open phases' GSD files into `gsd/`, writes DECISIONS, MANIFESTO, README, every other template, `-to-merge` drafts and CONVERSION.md | 1200, 1233-1236, 1209-1214, 1240-1242. |
| verb: move from gsd | true | 1165. |
| verb: migrate gsd | true | 1165. |
| verb: convert planning folder | true | 1165. |
| verb: gsd roadmap | true | `read_roadmap` 212. |
| verb: gsd requirements | true | `read_requirements` 298. |
| verb: gsd state | true | `build` 628, `gsd_pointer` 499. |
| verb: archive gsd files | true | 1230-1232. |
| verb: map requirement ids | true | `map_ids` 598. |
| verb: workstreams | true | `read_workstreams` 559, `convert` 1171. |
| verb: unfinished phase | true | 796-798, 1233-1236. |
| verb: survey gsd | true | 1383. |
| verb: dry run conversion | true | 1228. |
| distinct_from: plugins.release, plugins.build | true: `Stop` is the same bare-Exception shape as `release_plugins.py:44` but its own; `build` makes the model, not plugins | 71, 621; `devtools/build_plugins.py:186`. |
| note: "Read: the module docstring and the documented functions." | true of the first build, now superseded by this reading | — |
| note: "It never calls git to change anything" | true: every call is `rev-parse`, `symbolic-ref`, `ls-files` or `check-ignore` | 483, 485, 536, 538, 542, 549, 552, 579, 1117. |
| note: "move-from-gsd is the skill that drives it" | true | `skills/move-from-gsd/SKILL.md:89`, `:219`. |
| note: "Its Stop and git are its own, as each script's are" | true | 71, 428; seven other `git` definitions, none imported (section 7). |
| note: "its build makes the conversion plan, not plugins" | true, though "plan" is the model dict both commands read | 621-926. |
| tests: tests/test_from_gsd.py | true (40 tests; runs the script at `tests/test_from_gsd.py:180`) | — |

## 5. What the entry leaves out

- Refuses a project already moved, half moved, or not GSD, and points a non-GSD plan at adopt-devtools (636-654).
- Detects a restarted phase numbering and asks `--numbering first|last|same` (657-674).
- Owner overrides: `--complete` marks phases done, `--open` keeps put-off phases (698-718).
- Put-off (parked) phases are taken out of the roadmap and listed at its end (739-740, 974-982).
- Placeholder "Not used" phases for a missing whole number, and the `phase_gaps` hint (743-756).
- Picks the current phase from readiness and GSD's STATE pointer, carrying a discussed phase as `context_approved` (778-795).
- Parses "Depends on" lines and drops dependencies on parked or later phases (163-176, 764-774).
- Carries PROJECT.md key decisions into DECISIONS.md and constraints into MANIFESTO.md (1076-1082, 1089-1091).
- Carries GSD's out-of-scope list (330, 1021-1023).
- Never overwrites an existing file: writes `archive/gsd/<NAME>-to-merge.md` instead (1217-1219, 1240-1241).
- Writes STATE.md last so a stopped run is detected as half made (1243-1246, 639-644).
- Finds GSD installed inside the project (`survey --installed`) by manifest and by name (506-528, 1380).
- Finds settings/hook files that still name GSD and whether git tracks them (450-486).
- Counts GSD mentions in CLAUDE.md, AGENTS.md, GEMINI.md (903-904).
- Detects Spec Kit, OpenSpec, Kiro, BMAD, Task Master, Agent OS plans (489-496).
- Detects the base branch and refuses without one (531-544, 1180-1183).
- Refuses a git-ignored planning folder without `--ignored-plan` (547-556, 1177-1179).
- Warns when the project is not Python (577-592, 896-901).
- Suggests `skill_check = "synced"` from skill/agent files not in the sync receipt (905-913, 1343-1345).
- Writes CONVERSION.md, the record of the move (1115-1162, 1242).
- JSON output for both commands (1384-1388, 1397-1399).

## 6. Docstring against body

- Module docstring line 17: "It never calls git." False: it runs git through `subprocess` at 430 and 552 (read-only; the entry's note says it right).
- Module docstring lines 12-15 do not say that `convert` writes `-to-merge` drafts for DECISIONS, MANIFESTO and README that exist (1219, 1240-1241), nor its five refusals (1167-1206).
- `installed` 507-508: "without one they are found by name". The name patterns are applied whether or not a manifest exists (521-524).
- `default_branch` 532: "("", "") when it cannot be told". Outside a git work tree it returns `("main", "not a git repository")` (536-537).
- `plan_ignored` 548: "a file the move writes". It asks git about `<planning_dir>/MANIFESTO.md` only (552).
- `code_summary` 578: "None outside a git work tree". It is also None in a repository with no tracked files or when git fails (579-581).
- `phase_numbers` 148-149 and `named_ids` 345-347 hide their range caps (200 at 157, 50 at 358).
- `build` and `convert`, the two largest functions, have no docstring.

## 7. Other scripts

Runs or loads:

- `subprocess.run(["git", ...])` in `git` (430) and `plan_ignored` (552); `record_text` runs `git rev-parse --short HEAD` in the dev-tools checkout (1117).
- No `runpy`, no `importlib`, no import of another repository module.
- Path to another part of the repository: `TEMPLATES = SOURCE_ROOT / "skills/phase/process-phase/templates/planning"` (32), read at 1194 and listed at 1213; `convert` refuses without it (1167-1168).
- Reads sync.py's receipt `.devtools-receipt.json` and its `files` keys (906): coupled to `devtools/sync.py:58` and the receipt shape at `devtools/sync.py:314-318`.
- Names `phase_tool.py` only as text (default `{{TOOL}}` at 1191, messages at 652, 1405).

Same name defined in another shipped script (`ast` over `skills/` and `devtools/`):

| Here | Elsewhere | Same body? |
|---|---|---|
| `Stop` 71 | `skills/milestone/process-phase/scripts/review_tool.py:117`, `devtools/release_plugins.py:44` | Same shape (bare `Exception` subclass, exit 2); docstrings differ. |
| `git` 428 | `devtools/sync.py:180` (nested), `skills/components/scripts/components_index.py:980`, `skills/milestone/process-phase/scripts/review_tool.py:143`, `skills/phase/process-phase/scripts/codex_gate.py:14`, `skills/phase/process-phase/scripts/phase_tool.py:221`, `devtools/release_plugins.py:48` | No; closest is `phase_tool.py:221` (same timeout and except, returns unstripped stdout or None instead of stripped `""`). |
| `other_plans` 489 | `devtools/sync.py:459` | Partly: list and loop identical, return shape differs (REVIEW.md suggestion 1, settled in `sync.md` section 4). |
| `key` 80 | `skills/phase/process-phase/scripts/coder_pool.py:180` | No (a TOML parser method). |
| `shown` 85 | `review_tool.py:169` | No (path display). |
| `read` 91 | `coder_pool.py:288` | No (a TOML parser method). |
| `cell` 116 | `components_index.py:406` | No (that one escapes the pipe with a backslash; this one replaces it with `/`). |
| `build` 621 | `devtools/build_plugins.py:186` | No. |
| `roadmap_text` 932 | `phase_tool.py:324` | No (a method that reads ROADMAP.md). |
| `walk` 460 (nested) | `devtools/sync.py:406` | No (JSON walk vs directory walk). |
| `add` 350 (nested) | `review_tool.py:271`, `handoff.py:818`, `devtools/sync.py:117`, `devtools/build_plugins.py:159` | No. |
| `main` 1351 | every other script | No (each its own command line). |

Searched for `plugin_root`, `checkout_root`, `load_settings`: not defined here.

## 8. Proposed entry

- does: Move a project's planning folder from GSD to the dev-tools phase workflow: survey reports what a move would do and what to settle; convert archives GSD's files, rewrites STATE, ROADMAP and REQUIREMENTS, adds the other planning files without overwriting any, and records the move in CONVERSION.md (from_gsd.py)
- verbs: move from gsd, migrate gsd, convert planning folder, gsd roadmap, gsd requirements, gsd state, archive gsd files, map requirement ids, workstreams, unfinished phase, survey gsd, dry run conversion, restarted phase numbering, put off phases, parked phases, mark phase complete, current phase after move, gsd installed files, gsd hooks in settings, key decisions to decisions md, constraints to manifesto, conversion record, to-merge drafts, base branch detection, other planning tools
- notes: Read in full at 3963a46. Its git calls only read (rev-parse, symbolic-ref, ls-files, check-ignore); the module docstring's "never calls git" is wrong. Refuses a non-GSD, already-moved or half-moved folder, unchosen workstreams, a git-ignored plan and an unknown base branch; --dry-run runs the same refusals. Reads the templates under skills/phase/process-phase/templates/planning and sync.py's .devtools-receipt.json. move-from-gsd is the skill that drives it. Its OTHER_PLANS list and search loop are the same as sync.py's (REVIEW.md suggestion 1).
