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
| `.claude/skills/components/scripts/rules_check.settings.json` | `gnd_command` (how to run GND) and `index_script` (where the index script is) | In `.devtools.toml` |

Both files live beside the catalog, in the index script's `docs_dir`; a project that
moved the catalog finds them there.

## Set it up

1. Install GND where the check will run (Python 3.11 or newer). The check needs the
   rule-check flags (`--rule-ids`, `--baseline`, `--allow-vacuous`), which the published
   release 0.1.0 does not have; until the next release, install from the repository:

   ```bash
   uv tool install "get-nick-done @ git+https://github.com/vasiloglou/gnd-public@f4ce6992"
   ```

   That commit is the one this script was tried with. A project that would rather not
   install it sets `gnd_command` to a command that runs it, for example
   `uv run --project <a checkout of gnd-public> gnd`. The script stops (exit 2) when GND
   has no `--rule-ids`, and on a report of a version it does not know.
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
   error, so a misspelt name cannot pass quietly.
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
  it used to report: say in the PR body what changed and why.
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

After adding a rule, run `check --format json` with no base and read what it reports: a
rule that reports nothing may be right, or may name a fact that never matches, and one
that reports hundreds may say more than was meant.

## What a pass does not show

- **Only what the index script sees.** The facts come from the catalog and from `import`
  statements. An import made at run time from a name in a string breaks no rule. Neither
  does a call through a registry.
- **Component ids, not folders.** A module that sits in `tools/` and is listed under a
  `platform.*` component counts as `platform`. If a line looks wrong, check which entry
  owns the two files before changing the code.
- **A regrouping can look new.** Moving a module from one entry to another makes its old
  imports new facts. `changed` knows the file imported the same thing before; this check
  does not.
- **The rule is only as good as its sentence.** GND checks the facts against what was
  written, not against what was meant.
