# Reading: rules_check.py

## 1. Header

- Path: `skills/components/scripts/rules_check.py`
- Lines (`wc -l`): 1068
- Blob (`git hash-object`): `4b0f8c3b919998bfb2f0e2ef6a7b54cafde07ccd`
- Read at commit `3963a46`. The built copy `plugins/dvt-milestone/skills/components/scripts/rules_check.py` is byte-identical (`diff` exited 0).
- Runs below were made on a temp copy of `plugins/dvt-milestone` and a temp project under `/private/tmp/claude-501/rc-read-98806`, with `gnd 0.4.0` on the path.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `Problem` | 215 | Exception class whose raise ends a command with exit 2. |
| `load_settings` | 219 | Merges a JSON settings file over `DEFAULT_SETTINGS`, exiting on an unknown key. |
| `plugin_root` | 230 | Returns `parents[3]` of the script when it sits in `<x>/skills/<skill>/scripts/` beside `<x>/.claude-plugin/plugin.json`, else None. |
| `checkout_root` | 239 | Returns the nearest folder at or above the cwd holding `.git`, else the cwd. |
| `places` | 260 | Reads `docs_dir` from the index script's settings file (beside it, or `.devtools/` in a plugin install) and returns the `rules.json` and `layers.toml` paths there. |
| `load_rules` | 273 | Reads `rules.json`'s `rules` list and raises one Problem listing bad ids, reserved or repeated ids, bad level/about, missing type, non-text remedy or malformed examples. |
| `example_sets` | 307 | Returns a rule's examples as `(kind, number, facts)` triples, or None when the shape is not `{fails, passes}` of fact sets. |
| `domains` | 323 | Builds advisory `value` constraints (reserved `devtools_` ids) fixing the allowed statuses, task types, test kinds, plan keys and the catalog's areas, for the roles present. |
| `model` | 347 | Builds the GND model (version 4): value and fact types from the facts doc, each rule as a constraint (must alethic, should deontic) and the domain lists. |
| `population` | 369 | Wraps a facts doc's rows as a GND population (format 2) with a producer header. |
| `named_facts` | 375 | Collects every `fact_type` string anywhere inside a rule structure. |
| `run` | 382 | Runs a command capturing text output, raising Problem when it cannot start. |
| `read_facts` | 389 | Runs the index script's `facts` (optionally `--base`, `--modules`) as a subprocess and checks the format is `devtools-facts/1`. |
| `features` | 403 | Runs `gnd <command> --help` and returns which of the given flags its output names. |
| `judge` | 409 | Writes head (and base) populations, runs `gnd check --rule-ids --allow-vacuous [--baseline] [--guarded-diagnostics] --format json`, and validates exit band and report version 15 or 16. |
| `findings` | 438 | Turns verdicts into broken rows `(level, rule, binding, new)` and undecided rows, skipping domain constraints, and raises if a rule got no verdict. |
| `silent` | 465 | Makes `reread:` notes for rules whose guarded antecedent had zero bindings at a named atom. |
| `outside` | 482 | Makes `reread:` notes from GND's literal-outside-domain warnings, walking the warning path into the model to name the rule, fact, role and allowed values. |
| `hidden` | 508 | Makes `reread:` notes from a `--baseline-model` comparison: removed rules, edited rules that stop reporting findings, must-to-should changes, and uncomparable editions. |
| `base_rules` | 535 | Reads the component rules of `rules.json` at a commit with `git show`, or None. |
| `compare` | 549 | Runs `gnd check … --baseline-model base-model.json` on today's facts and returns its JSON or a `reason`. |
| `used_pair` | 561 | Returns the `(caller, callee)` a binding gives the rule's first `component_uses`/`component_uses_in_cycle` atom. |
| `describe` | 570 | Renders a binding as `key=value …`, or a row as `a -> b`. |
| `changed_rules` | 576 | Lists the rules and layers files that differ from a commit or are untracked, via `git diff` and `git ls-files`. |
| `check` | 587 | Judges component rules over the head facts (with module facts only if a rule needs them), optionally against the base, adds reread notes, marks new imports, prints or emits JSON, and returns 1 on a new fail (or any new row with strict). |
| `read_plan_facts` | 660 | Runs the phase tool's `--format json facts --phase NN` as a subprocess and returns its `data` doc. |
| `names` | 680 | True when a task's file entry equals a path, is a folder prefix of it, or a glob matching it. |
| `plans_with_components` | 685 | Merges component facts and plan facts and adds the four JOINED fact types derived from which component holds each named file. |
| `components` | 694 | (nested) Maps a plan fact's task file entries to `(task, component)` pairs. |
| `bindings` | 724 | Returns `{rule id: antecedent binding count}` from a diagnosed report. |
| `check_phase` | 732 | Judges the `about: plans` rules over the joined plan and component facts of one phase, prints rows with the plan file, and returns 1 on a fail (or any row with strict). |
| `where` | 753 | (nested) Returns ` (<plan file>)` for the first bound value that is a plan or a task of one. |
| `vocabulary` | 786 | Returns every fact type a rule may name: the index's facts with modules, plus the phase tool's `FACT_VALUES`/`FACT_TYPES` and JOINED when the phase tool file exists, loaded with importlib. |
| `generated` | 804 | Runs `gnd synth --guarded-cases` and reports rules GND finds can never apply, never fail, or never pass. |
| `test` | 830 | Judges each rule alone on each example set, recording wrong results and notes, then adds `generated`'s findings when synth supports it; returns 1 if anything is wrong. |
| `joined` | 905 | Runs `gnd discover --families guarded-join` over component uses by area and returns its report. |
| `area_pair` | 928 | Extracts `(source area, target area)` from a proposed absence constraint, None for same-area or malformed ones. |
| `suggest` | 940 | Lists near misses and kept directions between areas that layers.toml does not already cover, as text, JSON or `[[forbid]]` TOML; exit 0. |
| `covered` | 957 | (nested) True when layers.toml forbids the pair or ranks the target above the source. |
| `init` | 1016 | Writes the starter `rules.json` and `layers.toml` unless each exists, or prints both with `--print`. |
| `main` | 1031 | Parses the command line, refuses `--phase` with `--base`, dispatches, and maps Problem to stderr and exit 2. |

Counted with `python3 -c "import ast,sys; t=ast.parse(open(sys.argv[1]).read()); print(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(t)))" skills/components/scripts/rules_check.py`: 41 (38 top-level, 3 nested). 41 rows.

## 3. Commands

Global option: `--root PATH`, default the cwd (1033), not the checkout root. A Problem prints `rules_check: …` to stderr and exits 2 (1062-1064). `check`, `test` and `suggest` print `skip: gnd not found …` and exit 0, or 1 with `--require`, when `gnd_command` is not on the path (589-592, 735-738, 835-838, 943-946).

| Command | Reaches | Writes / exit |
|---|---|---|
| `init [--print]` | `init` 1016 | Writes `<docs_dir>/rules.json` (six starter rules) and `<docs_dir>/layers.toml` (commented) unless present; `--print` prints both, writes nothing; exit 0. |
| `check [--base REF] [--strict] [--require] [--format text\|json]` | `check` 587 | Temp files only; prints `fail:`/`warn:` lines with remedies (10 per rule), `reread:` notes and a summary; JSON holds all rows (standing ones too), notes, baseline and binding counts; exit 1 on a new fail, or any new row with `--strict`, 0 otherwise. |
| `check --phase NN [--strict] [--require] [--format …]` | `check_phase` 732 | Same output form for plan rules; exit 1 on any fail, or any row with `--strict`; `--phase` with `--base` is an argparse error (1050-1051). |
| `test [--require] [--format text\|json]` | `test` 830 | Prints `wrong:`/`note:` lines, `no examples:` and a summary; exit 1 if any wrong. |
| `suggest [--require] [--format text\|json\|toml]` | `suggest` 940 | Prints `almost:` and `kept:` lines and a summary, or JSON, or `[[forbid]]` blocks; skip (exit 0/1) when `gnd discover` lacks `--joined-relation` (947-949); otherwise exit 0. |

## 4. The entry, claim by claim

### components.rules

| Claim | Verdict | Settled by |
|---|---|---|
| does: "Check the project's own rules about which components may use which" | overstated | Rules are any GND rule over the facts: also canonical-has-test, private modules and plan rules (154-192); "which may use which" is two of six starters. |
| does: "with GND" | true | `judge` 415. |
| does: "init" | true | `init` 1016. |
| does: "check" | true | `check` 587. |
| does: "check --phase" | true | `check_phase` 732. |
| does: "test the rules on their examples" | true | `test` 830-886. |
| does: "suggest rules" | true | `suggest` 940; it prints candidates and writes nothing (990-1013). |
| verbs: rule check | true | `check` 587. |
| verbs: component rules | true | `load_rules` 273. |
| verbs: layers | true | `STARTER_LAYERS` 202, `init` 1018. |
| verbs: forbidden imports | overstated | The starter forbids component uses between areas named in layers.toml, not single imports (107-114). |
| verbs: which areas may import which | true | 107-140. |
| verbs: gnd check | true | 415. |
| verbs: guarded rules | true | Starters are `type: guarded` (110), diagnostics 416. |
| verbs: rules json | true | 273-304. |
| verbs: layers toml | true | 1018, 993-997. |
| verbs: test rules on examples | true | 830. |
| verbs: suggest rules | true | 940. |
| verbs: near misses | true | 969-983. |
| verbs: check plans of a phase | true | 732. |
| verbs: new violation since base | true | 602-609, 634. |
| verbs: remedy | true | 647-648. |
| notes: "Without GND it prints skip: and exits 0." | true | 589-592; exit 1 with `--require` (592); a GND without `--rule-ids` is a Problem, exit 2 (420-421). |
| notes: "It runs components_index.py and phase_tool.py (subsystem.rule_check)." | true | Subprocess 393, 666; importlib load 792-795. |
| uses / used_by: (none) | true | Imports are stdlib only (57-70). |
| tests: tests/test_tools.py | true | It drives rules_check (5 mentions; also tests/test_plugins.py has 4). |

### subsystem.rule_check

| Claim | Verdict | Settled by |
|---|---|---|
| does: "rules_check.py reads the catalog and import graph from components_index.py facts" | true | 389-400. |
| does: "and the plans and fact types of the phase workflow from phase_tool.py" | true | Plans 660-677, fact types 786-801. |
| flow: components.rules -> components.index -> phase.state | false | components_index.py never reaches phase_tool.py; rules_check.py calls each itself (742 after 741; 789 then 792), so the flow is two branches from components.rules. |
| notes: "check and test run components_index.py facts as a subprocess" | true | check 595/600/603, test via `vocabulary` 789; `suggest` does too (950) and is not named. |
| notes: "test then loads phase_tool.py with importlib for its fact types" | true | 791-800, only when the file exists (791). |
| notes: "check --phase runs phase_tool.py facts first, then components_index.py facts" | true | 741-742. |

## 5. What the entry leaves out

- `reread:` notes: rules that matched nothing (465-479), literals outside a role's values such as a misspelt status or area (482-505, 323-344), and what an edited `rules.json` stops reporting (508-532, 549-558).
- Edited-rules comparison against the base edition (`--baseline-model`): 615-617.
- `[new import]` marking and new-import-first ordering under `--base`: 624-630.
- GND-built failing/passing cases per rule (`gnd synth --guarded-cases`): 804-827, 887-888.
- Starter rules: forbidden area use, no use of a higher rank, import inside a loop, canonical component has a test, private module stays in its component, plan names the components it touches: 106-193.
- Joined plan facts (task touches component, task reads component, task adds file, plan names component): 195-200, 685-721.
- `--format json`, `--strict`, `--require` and exit code 2: 1038-1048, 1062-1064.
- `[[forbid]]` TOML output for kept directions: 993-998.
- Settings `gnd_command` (for example a `uvx` command), `index_script`, `phase_script`: 72-79.

## 6. Docstring against body

- In a dvt-milestone plugin install, the default `phase_script` is `PLUGIN/skills/process-phase/scripts/phase_tool.py` (256), but dvt-milestone ships no phase_tool.py (only dvt-phase does). Run on a temp copy: `check --phase 01` exited 2 ("phase_tool.py is missing"), and `test` on the starter rules exited 1 with two `wrong:` lines for `plan_names_the_components_it_touches` ("names … which no fact type of this project is"), because `vocabulary` silently drops the plan facts when the file is absent (791). The docstring does not say either.
- Docstring: GND 0.3.1's three reread lines are used only when `gnd check --help` names the flags; the literal-outside-domain note does not depend on that check, since `domains` constraints are always put in the model (365) and `outside` always reads warnings (618). Whether an older GND accepts those constraints: not settled (no older GND run).
- Docstring: "Exit 1 when a `fail:` is printed"; an undecided `must` rule is also counted as a fail and is always new, even under `--base` (631-635).
- Docstring: "with `--base` … only what the change added is printed"; with `--format json` the standing rows are included (`rows`, 640), and when the base has no catalog everything counts as new (607).
- Docstring: "Settings live beside this script, in rules_check.settings.json"; in a plugin install they are `.devtools/rules_check.settings.json` of the cwd's checkout (249), and `index_script`/`phase_script` default to the plugin's copies (252-257).
- `--root` defaults to the cwd (1033), while the index script's default root is the checkout root (components_index.py:124) and, in a plugin install, its settings come from the cwd's checkout whatever `--root` says (components_index.py:112); run from a subfolder, `places` looks for settings under the subfolder and falls back to `docs/components` (262-269).
- `vocabulary` executes the whole phase tool module (795); a phase tool lacking `FACT_VALUES` or `FACT_TYPES` raises AttributeError outside the `except` (798-800), which `main` does not catch (1062), so it ends in a traceback with exit 1, not 2.
- `check_phase` docstring "No base": its exit counts every row, not only new ones (783), unlike `check` (657).
- `PLAN_KEYS` comment says a test keeps it equal to phase_tool's: true (tests/test_tools.py:1202); `STATUSES` (97) repeats components_index.py's status list (components_index.py:282) with no such test found.

## 7. Other scripts

Runs or loads:
- components_index.py `facts` as a subprocess: 393 (from `check` 595, 600, 603; `check_phase` 742; `vocabulary` 789; `suggest` 950).
- phase_tool.py `--format json --root … facts --phase NN` as a subprocess: 666.
- phase_tool.py loaded and executed with `importlib.util.spec_from_file_location` / `exec_module`: 792-795.
- Paths built to other scripts: `Path(__file__).with_name('components_index.py')` 255; `PLUGIN/skills/process-phase/scripts/phase_tool.py` 256; defaults `scripts/components_index.py` and `.claude/skills/process-phase/scripts/phase_tool.py` 73, 78.
- Reads the index script's settings file for `docs_dir`: `(root/index_script).with_suffix('.settings.json')` 262, or `.devtools/components_index.settings.json` 264.
- `git` subprocess: `git show` 538, `git diff --name-only` and `git ls-files --others` 580-582.
- `gnd` subprocess (external tool): `--help` 405, `check` 419 and 552, `synth` 812, `discover` 913.

Same names defined in other shipped scripts:
- `plugin_root` 230: AST-identical in components_index.py:94, handoff.py:45, coder_pool.py:50, phase_tool.py:47, review_tool.py:64.
- `checkout_root` 239: AST-identical in components_index.py:103, handoff.py:54, coder_pool.py:59, phase_tool.py:56, review_tool.py:73.
- `load_settings` 219: also components_index.py:79, handoff.py:86, coder_pool.py:78, phase_tool.py:99, review_tool.py:121; none AST-identical to this one.
- `places` 260: components_index.py:1350 (nested; different).
- `run` 382: phase_tool.py:1477 (nested; different).
- `covered` 957 (nested): sync.py:566 (different).
- `main` 1031: every shipped script has one.

## 8. Proposed entry

### components.rules
- does: Judge the project's own rules about its components and plans with GND, over the facts components_index.py extracts: init writes starter rules and layers, check (against a base, or --phase NN for plans), test judges each rule on its examples, suggest proposes area layers and near misses (rules_check.py)
- verbs: rule check, component rules, layers, forbidden area use, which areas may import which, rank of an area, gnd check, guarded rules, rules json, layers toml, starter rules, test rules on examples, suggest rules, near misses, check plans of a phase, new violation since base, new import, remedy, rules matched nothing, misspelt literal in a rule, edited rules hide findings, import loop rule, canonical component has a test, private module rule, gnd synth cases
- notes: Read in full at 3963a46 (phase 3 of component-index). Without GND, check, test and suggest print skip: and exit 0 (1 with --require); a check that could not run exits 2. It runs components_index.py facts and phase_tool.py facts as subprocesses and loads phase_tool.py with importlib (subsystem.rule_check). In a dvt-milestone install its default phase_script does not exist, so check --phase cannot run and test reports the starter plan rule wrong.

### subsystem.rule_check
- flow: components.rules -> phase.state -> components.index (the order of the calls in check --phase; `flow` is one `->` chain, components_index.py:311, so the two branches go in notes)
- notes: Run-time calls, which the import graph cannot see; components_index.py and phase_tool.py never call each other, rules_check.py calls each. check, test and suggest run components_index.py facts as a subprocess; test then loads phase_tool.py with importlib for its fact types; check --phase runs phase_tool.py facts first, then components_index.py facts --modules.
