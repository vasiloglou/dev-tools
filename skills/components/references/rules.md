# Project rules: an optional check on the components

The index script checks the form of the index. It has no way to say "the core must not
import the command line" or "nothing new may join a loop of imports". A project that
wants such rules writes them down once, and `rules_check.py` checks them against the
catalog and the import graph before a PR.

The checker is [GND](https://github.com/vasiloglou/gnd-public), which judges a set of
facts against a set of rules. It is optional: without it `check` prints `skip:` and
exits 0, and nothing else in the workflow depends on it.

**Status: a trial.** It has been run on two codebases and not yet adopted by a project.
Use it where the user asked for it; do not add it to a project on your own.

It does not check the index itself. Run `components_index.py --check --strict` and
`changed` first: a module that no component covers has no facts, so its imports break
no rule.

| File | What it is | Edit? |
|---|---|---|
| `docs/components/layers.toml` | A rank for each area and the forbidden pairs of areas | By hand |
| `docs/components/rules.json` | The rules. `init` writes four starter rules | By hand |
| `.claude/skills/components/scripts/rules_check.settings.json` | `gnd_command` (how to run GND), `index_script` (where the index script is) and `phase_script` (where the phase tool is, for [rules about plans](#rules-about-plans)) | In `.devtools.toml` |

Both files live beside the catalog, in the index script's `docs_dir`; a project that
moved the catalog finds them there.

## Set it up

1. Install GND where the check will run (Python 3.11 or newer). The check needs release
   0.2.0 or newer, the first with the rule-check flags (`--rule-ids`, `--baseline`,
   `--allow-vacuous`):

   ```bash
   uv tool install "get-nick-done[synth] @ git+https://github.com/vasiloglou/gnd-public@v0.3.1"
   ```

   Release 0.3.1 is the one this script was last tried with. It is a tag on GitHub, not on
   PyPI, hence the install from git. It adds the checks of a rule itself in
   [Test a rule](#test-a-rule) and [`suggest`](#suggest-rules-from-the-code); the `synth`
   extra is needed only for the cases GND builds from a rule. The script asks each
   command's `--help` whether a check is there and works as before when it is not, so
   0.3.0 from PyPI (`get-nick-done==0.3.0`) still runs every rule. A project that would
   rather not install it sets
   `gnd_command = "uvx --from 'get-nick-done[synth] @ git+https://github.com/vasiloglou/gnd-public@v0.3.1' gnd"`. The script
   stops (exit 2) when GND has no `--rule-ids` (release 0.1.0), and on a report of a
   version it does not know.
2. Write the starter files (neither is overwritten if it exists):

   ```bash
   python3 .claude/skills/components/scripts/rules_check.py init
   ```

3. Say in `layers.toml` which areas may use which. An area is the first part of a
   component id: `core.sizes` is in `core`.

   ```toml
   [rank]            # a component may use components of its own rank or a lower one
   core = 0
   store = 1
   cli = 2

   [[forbid]]        # one pair that is never allowed, whatever the ranks
   from = "store"
   to = "report"
   ```

   An area with no rank is not judged by rank. An area that no component is in is an
   error, so a misspelt name cannot pass quietly. With a newer GND,
   [`suggest`](#suggest-rules-from-the-code) lists the directions the code already keeps,
   to start from.
4. Run the check on the whole project once and read what it prints:

   ```bash
   python3 .claude/skills/components/scripts/rules_check.py check
   ```

   An existing project will not be clean. That is expected: from here on the check runs
   against a base, and only what a change adds is reported.

## Before a PR

```bash
python3 .claude/skills/components/scripts/rules_check.py check --base <base branch>
```

- `fail: <rule id>: <the components> (<one import behind them>)`, then `remedy:` with
  the rule's advice. A `must` rule the change broke. Fix the import, or move the module
  to the component it belongs to. Do not edit the rule to make the line go away; a rule
  changes only with the user's go-ahead.
- `warn:` A `should` rule the change broke. Fix it, or say why not in the PR body.
- `[new import]` at the end of a line: the change added the import the line names. For
  each rule these come first, and they are where to start. A line without the mark is
  new for another reason: an import that was already there and that a new one pulled
  into a loop (one import that closes a loop puts every import of the loop on the list),
  a status or a rank that changed, a `tests:` line that was removed.
- `… +N more for <rule>, M of them through imports that were already there` Ten lines
  are printed for a rule; `--format json` has them all.
- `reread: rules changed in this change: <file>` The rules or the layers were edited in
  this change. Both revisions are judged by today's rules, so a loosened rule hides what
  it used to report: say in the PR body what changed and why. With a newer GND, the next
  lines say what the edit hides (see [Test a rule](#test-a-rule)).
- `reread: <rule> was removed in this change; …`, `reread: <rule> was edited in this change
  and no longer reports N finding(s) …`, `reread: <rule> went from must to should …`
  What an edit of `rules.json` stops reporting on today's code. Each needs the user's
  go-ahead, named in the PR body.
- `reread: <rule> matched nothing: …` and `reread: <rule>: '<value>' is not a value … can
  hold` A rule that judged nothing, or names a value no fact of its kind can hold: most
  often a typo. See [Test a rule](#test-a-rule).
- `reread: no catalog at <commit>` The base has no component index, so everything
  broken counts as new.

Exit 0 when no `must` rule is newly broken, 1 with a `fail:` (and with `--strict`, a
`warn:`), 2 when the check did not run: a line starting `rules_check:` says why, and it
is not a pass, though it prints no `fail:`. `--require` turns a missing GND from a skip
into a failure, for a CI job that must not pass by not running. With `--base`, exit 0
says nothing about what was already broken: the summary line counts it as `standing`.

## The starter rules

| Rule | Level | Says |
|---|---|---|
| `no_forbidden_area_use` | must | No component uses a component of an area its own area is forbidden to use |
| `no_use_of_a_higher_rank` | must | No component uses a component of a higher rank |
| `no_import_inside_a_loop` | should | No import between components is part of a loop of imports |
| `canonical_component_has_a_test` | should | Every `canonical` component lists a test |
| `private_module_stays_in_its_component` | should | No file imports a private file (its name, or a folder above it, starts with `_`) that another component holds |
| `plan_names_the_components_it_touches` | should | A [rule about plans](#rules-about-plans): only `check --phase` judges it |

The first two say nothing until `layers.toml` has pairs or ranks. Delete a rule the
project does not want, or change its `level`.

## Write a rule

A rule is one object in the `rules` list of `rules.json`:

```json
{
  "id": "canonical_does_not_use_experimental",
  "level": "must",
  "remedy": "A canonical component uses an experimental one: finish it first, or mark the caller experimental",
  "type": "guarded",
  "antecedent": [
    {"fact_type": "component_uses", "bind": {"caller": "$a", "callee": "$b"}},
    {"fact_type": "component_has_status", "bind": {"component": "$a", "status": "canonical"}}
  ],
  "consequent": {"absence": {"fact_type": "component_has_status", "bind": {"component": "$b", "status": "experimental"}}}
}
```

- `id`: lower-case letters, digits and `_`; unique, and not the name of a fact type.
- `level`: `must` (a `fail:`) or `should` (a `warn:`). Default `must`.
- `about`: `components` (the default) or `plans`. A rule about plans is judged by `check --phase NN` and
  left out of every other `check`; see [Rules about plans](#rules-about-plans).
- `remedy`: what to do when the rule is broken; printed under each line. GND keeps it
  on the rule and repeats it in its own reports.
- Everything else is a GND constraint as GND writes it, of a kind GND allows at the top
  level of a model (`guarded`, `subset`, `equality`, `value` and others). The kinds GND
  writes inside one fact type (a ring constraint such as acyclic, or a uniqueness or
  mandatory constraint on a single fact type) cannot be written here. A `guarded` rule reads "for
  every way the `antecedent` facts fit together, the `consequent` holds". A name
  starting with `$` stands for any value and means the same value wherever it appears;
  anything else is a literal. The `consequent` is one of:
  - `absence`: this fact must not exist;
  - `atom`: this fact must exist;
  - `exists`: some facts must exist, with names of their own (`{"atoms": [...]}`);
  - `comparison`: two values compared with `=`, `!=`, `<`, `<=`, `>`, `>=`.
- The script adds what GND also wants on a rule (its modality, source, status and
  provenance); do not write those.

What the script does itself is small: it turns the facts file into a GND model and
population, runs `gnd check` with `--rule-ids --allow-vacuous`, and with `--base` adds
`--baseline` so that GND marks each violation new or standing. GND's own account of
those flags: <https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/adopt-rules-with-a-baseline.md>.

An antecedent has no "not" and no "or": a rule that needs "unless both are in the same
area" has to be turned around until the exception is in the consequent, or split in two.
The component a line's import is read from is the first `component_uses` (or
`component_uses_in_cycle`) fact in the antecedent, so put it first.

The full constraint language is in GND's own reference, section "Guarded constraints":
<https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md>.

The facts a rule can name (`python3 scripts/components_index.py facts` prints them all):

| Fact | Roles | Meaning |
|---|---|---|
| `component_is_listed` | `component` | The catalog has this component (subsystems are not components) |
| `component_has_status` | `component`, `status` | `canonical`, `experimental`, `deprecated`, `external` or `duplicate-of` |
| `component_in_area` | `component`, `area` | The first part of its id |
| `component_uses` | `caller`, `callee` | A module of one imports a module of the other at run time |
| `component_uses_in_cycle` | `caller`, `callee` | That import lies inside a loop of imports (the imports a package `__init__` makes are not counted) |
| `component_has_test` | `component`, `path` | A path on its `tests:` line |
| `subsystem_has_member` | `subsystem`, `component` | A component on a subsystem's `components:` line |
| `area_has_rank` | `area`, `rank` | From `[rank]` in `layers.toml` |
| `area_must_not_use` | `source`, `target` | From a `[[forbid]]` in `layers.toml` |
| `component_has_module` | `component`, `path` | A package file the component holds |
| `module_imports` | `importer`, `imported` | One file imports another; a component holds each |
| `module_is_private` | `path` | The file's name, or a folder above it inside the package, starts with one `_` (`__init__.py` and `__main__.py` are not private) |

The last three are facts about files (`facts --modules` prints them). `check` asks for them
only when a rule it judges names one, so a project whose rules name no file is judged on
the component facts alone, as before.

After adding a rule, give it examples and run `test` ([Test a rule](#test-a-rule)), then run
`check --format json` with no base and read what it reports: one that reports hundreds may
say more than was meant.

## Test a rule

A rule that never fires looks exactly like a rule the code obeys. A misspelt value, a role
bound to the wrong name, an antecedent that cannot match: each gives a quiet pass for
ever. Five things catch it.

**Examples, written by the rule's author.** A rule may carry facts it must fail on and facts
it must pass on:

```json
"examples": {
  "fails":  {"component_has_status": [{"component": "core.sizes", "status": "canonical"}]},
  "passes": {"component_has_status": [{"component": "core.sizes", "status": "canonical"}],
             "component_has_test": [{"component": "core.sizes", "path": "tests/test_sizes.py"}]}
}
```

Each of `fails` and `passes` is one set of facts, `{fact type: [rows]}`, or a list of them.
A fact type the set leaves out has no rows. Then:

```bash
python3 .claude/skills/components/scripts/rules_check.py test
```

judges each rule alone on each set. `wrong:` a failing set that does not break the rule, a
passing set that does, or a set naming a fact type that does not exist. `note:` a passing set
the rule matched nothing in: it shows only that the rule is quiet with no subject, as for
`no_import_inside_a_loop`, which reports every import inside a loop. Exit 1 on a `wrong:`,
2 when it could not run. Rules without examples are listed. Every starter rule has one
example of each kind. This works with GND 0.3.0; the reason a rule matched nothing needs
0.3.1.

The next three need GND 0.3.1 and appear in `check` by themselves:

- **A rule that matched nothing** (`--guarded-diagnostics`). When every fact a rule names
  has rows and still no binding gets through its antecedent, the line names the first atom
  that emptied it. A rule can be right and have no subject today: read it, do not delete it.
- **A value nothing can hold.** The script adds the values the vocabulary fixes (the five
  statuses, the task types, the test kinds, the `plan_declares` keys, the areas the catalog
  has) as value lists with ids that start with `devtools_`, a prefix a rule's id may not use.
  GND then names a literal in a rule that lies outside them, in the antecedent or the
  consequent alike.
- **What an edit hides** (`--baseline-model`). With `--base`, when `rules.json` changed,
  today's facts are judged by the base edition of the rules and by today's, rule by rule,
  and the lines say what the edit stops reporting. A rule that was added, or that reports
  more, needs no line: the ordinary output shows it.

The fifth is in `test`, with GND 0.3.1 and its `synth` extra (`gnd synth --guarded-cases`). **Cases GND builds from the rule as written**, a failing one and a passing
one. Where it can build none, the rule itself is wrong:

- `wrong: <rule> can never fail` (`no-failing-case`): whatever matches the antecedent already
  meets the consequent, so the rule only ever passes.
- `wrong: <rule> can never apply` (`antecedent-unreachable`): no facts can match the
  antecedent. Not repeated for a rule already noted for a value nothing can hold.
- `note: <rule> can never pass once it applies` (`no-passing-case`): right for a ban, written
  as a guard whose consequent cannot hold; otherwise reread it.

A shape GND builds no cases for, or a search that ran out, says nothing about the rule and
prints nothing. The cases come from the rule, so they cannot show it means what its author
meant: the examples do that.

## Suggest rules from the code

```bash
python3 .claude/skills/components/scripts/rules_check.py suggest
```

It reads the code, not the rules: GND's `guarded-join` discovery (`gnd discover`, GND
0.3.1) over which component uses which and the area each is in. Nothing is written.

- `almost: <a> uses <b> in N of its M use(s)`, with one of the uses and its import. GND reports a
  pair as a near miss when the uses are at most 5% of the area's, and at most 32. Those
  that close a loop (`<b> uses <a> K time(s)`) come first: a low layer reaching up is the
  usual layering mistake. Read each one: fix the import, or decide the use is meant. A pair
  `layers.toml` already forbids is left out, since `check` reports it. An area with fewer
  than 20 uses has no near misses.
- `kept: <a> never uses <b>, … (each uses it)` Directions the code keeps that `layers.toml`
  does not say yet: `<b>` uses `<a>` and never the other way. A pair of areas that do not use
  each other at all is not listed. `--format toml` prints these as `[[forbid]]` lines: keep the
  ones the project means, with the user's go-ahead, and the starter rule
  `no_forbidden_area_use` holds them from then on.

A direction kept today is a fact about today's code, not a decision: a suggestion becomes a
rule only when someone means it. `--format json` lists every near miss with the uses behind
it. Exit 0 when it ran, 2 when it could not; without such a GND it prints `skip:` (exit 1 with
`--require`).

## Rules about plans

For a project that uses the phase workflow. The same rules file can hold rules about the
plans of a phase: which components a task may change, what a plan has to name, what kind
of task an area needs. They are judged while the plans can still be edited, before the
plan gate:

```bash
python3 .claude/skills/components/scripts/rules_check.py check --phase NN
```

- It judges the rules marked `"about": "plans"` and no others. There is no `--base`: a plan
  is judged as written, and every line is about it.
- A line reads `warn: <rule id>: <what the rule bound> (<the plan file>)`, then `remedy:`.
  Fix the plan, or say at the plan gate why the line stands. Exit codes are those of `check`.
- It is not `phase_tool.py check --plans NN`. That check holds the rules the workflow fixes
  for every project (two plans of one wave that name a file, a `depends_on` that cannot
  hold) and needs nothing installed. This one holds the rules a project writes for itself.
- **Status: a trial**, like the rest of this file. It has run on plans written to test it
  and on no real project's plans. No step of the workflow requires it.

`init` writes one such rule, `plan_names_the_components_it_touches` (should): a task that
names a file of a component, in a plan whose Reuse section names neither that component
nor a subsystem it belongs to.

The facts such a rule can name are the component facts above and these. The first group is
what the plans say (`phase_tool.py facts --phase NN` prints them); the second is added by
`check --phase`, from the plans and the index together.

| Fact | Roles | Meaning |
|---|---|---|
| `plan_in_wave` | `plan`, `wave` | The plan's `wave`, a whole number |
| `plan_depends_on` | `plan`, `earlier` | A plan its `depends_on` names |
| `plan_runs_after` | `plan`, `earlier` | Every plan before it through `depends_on` |
| `plan_names_requirement` | `plan`, `requirement` | A REQ id in its `requirements` |
| `plan_reuses_component` | `plan`, `component` | An id on the `reuse:` line of its Reuse section |
| `plan_adds_component` | `plan`, `component` | An id on a `new_component:` line |
| `plan_declares` | `plan`, `key`, `value` | `golden_impact`, `llm_dependency`, `gap_closure`, `autonomous` or `prove_method`, as written |
| `task_in_plan` | `task`, `plan` | The plan a task is in |
| `task_has_type` | `task`, `type` | `auto`, `checkpoint:decision` or `checkpoint:human-verify` |
| `task_turns_green` | `task`, `test` | A test id, with its folder |
| `task_names_file` | `task`, `path` | An entry of `files` or `unit_tests`, as written: a path, a folder ending in `/`, or a pattern with `*` |
| `task_reads_first` | `task`, `path` | An entry of `read_first`, as written |
| `test_is_in_contract` | `test`, `kind` | A test of the Traceability table: `contract` or `guard` |
| `task_touches_component` | `task`, `component` | An entry of the task's files names a file the component holds |
| `task_reads_component` | `task`, `component` | The same, for `read_first` |
| `task_adds_file` | `task`, `path` | A plain path among the task's files that does not exist yet |
| `plan_names_component` | `plan`, `component` | The plan reuses or adds the component, or reuses a subsystem it is in |
| `component_has_module` | `component`, `path` | A package file the component holds (`components_index.py facts --modules`) |

Three rules a project might write. Each was run through GND 0.3.0 before it was put here.

```json
{"id": "no_task_changes_a_retired_component", "about": "plans", "level": "should",
 "remedy": "A task changes a deprecated component: change the component that replaces it, or say in the plan why this one",
 "type": "guarded",
 "antecedent": [{"fact_type": "task_touches_component", "bind": {"task": "$task", "component": "$c"}}],
 "consequent": {"absence": {"fact_type": "component_has_status", "bind": {"component": "$c", "status": "deprecated"}}}}
```

```json
{"id": "billing_changes_are_checked_by_a_person", "about": "plans", "level": "must",
 "remedy": "A task changes the billing area: make it a checkpoint:human-verify task",
 "type": "guarded",
 "antecedent": [{"fact_type": "task_touches_component", "bind": {"task": "$task", "component": "$c"}},
                {"fact_type": "component_in_area", "bind": {"component": "$c", "area": "billing"}}],
 "consequent": {"atom": {"fact_type": "task_has_type", "bind": {"task": "$task", "type": "checkpoint:human-verify"}}}}
```

```json
{"id": "a_task_reads_the_callers_of_what_it_changes", "about": "plans", "level": "should",
 "remedy": "A task changes a component and does not read one that uses it: add a file of the caller to read_first",
 "type": "guarded",
 "antecedent": [{"fact_type": "task_touches_component", "bind": {"task": "$task", "component": "$c"}},
                {"fact_type": "component_uses", "bind": {"caller": "$d", "callee": "$c"}}],
 "consequent": {"atom": {"fact_type": "task_reads_component", "bind": {"task": "$task", "component": "$d"}}}}
```

The third is what the Plan step asks for in words. It is loud for a component many others
use, which is why it is an example and not a starter: add a rule only when its lines are
ones someone will act on.

What a pass here does not show, beside the limits below:
- **Only what the plan writes down.** A task that changes a file its `files` does not name
  breaks no rule here; `phase_tool.py check --scope NN` looks for that after the work.
- **Only files a component holds.** A file no component has claimed gives no
  `task_touches_component`, so run the index checks first, as for any rule.
- **A new file has no component yet.** It gives `task_adds_file` and nothing else.

## What a pass does not show

- **Only what the index script sees.** The facts come from the catalog and from `import`
  statements. An import made at run time from a name in a string breaks no rule. Neither
  does a call through a registry.
- **A renamed file is a new fact.** A rule that names a file fact sees a moved or renamed
  file as another file. Against a base, a line that was standing can come back as new
  after a rename; say so in the PR body and go on. Rules over components are not affected.
- **Component ids, not folders.** A module that sits in `tools/` and is listed under a
  `platform.*` component counts as `platform`. If a line looks wrong, check which entry
  owns the two files before changing the code.
- **A regrouping can look new.** Moving a module from one entry to another makes its old
  imports new facts. `changed` knows the file imported the same thing before; this check
  does not.
- **The rule is only as good as its sentence.** GND checks the facts against what was
  written, not against what was meant.
