#!/usr/bin/env python3
"""Check the project's own rules about its components. Optional: it needs GND installed.

    rules_check.py init [--print]     write a starter rules file and layers.toml (never overwrites one)
    rules_check.py check [--base REF] [--strict] [--require] [--format json]
    rules_check.py check --phase NN [--strict] [--require] [--format json]
    rules_check.py test [--format json]   judge each rule on the examples it carries
    rules_check.py suggest [--format json|toml]   which areas the code already keeps apart, and near misses

``check`` asks ``components_index.py facts`` for the catalog and the import graph as
facts, adds the rules in ``rules.json``, and has ``gnd check`` judge them
(https://github.com/vasiloglou/gnd-public). It prints ``fail:`` for a broken ``must``
rule and ``warn:`` for a broken ``should`` rule, each with the rule's id, the components
and one import behind them, and the rule's remedy on the next line. With ``--base`` GND
judges the merge base with REF as well, under today's rules, and only what the change
added is printed; a line ends in ``[new import]`` when the change added the import it
names, and for each rule those come first.

Exit 0 means no ``must`` rule is newly broken in the facts the index script extracted:
with ``--base``, what was broken before still is, and an import the script cannot see
(a dynamic import, a name built at run time) breaks no rule. Exit 1 when a ``fail:`` is
printed (with ``--strict`` also a ``warn:``), 2 when the check did not run. Without GND
it prints ``skip:`` and exits 0 (1 with ``--require``).

``check --phase NN`` judges the plans of one phase of the phase workflow, before they are
approved: the rules marked ``"about": "plans"``, over what ``phase_tool.py facts`` reads from
the plans and the component facts together. Plain ``check`` leaves those rules out. There is
no base to compare with: every line is about the plans as written.

GND 0.3.1 adds three ``reread:`` lines, and the script asks ``gnd check
--help`` whether it can: a rule whose antecedent matched nothing although every fact it
names has rows (``--guarded-diagnostics``); a literal in a rule that no fact of its kind can
hold, such as a misspelt status or area; and, when ``--base`` finds ``rules.json`` edited,
the findings the edit stops reporting on today's code (``--baseline-model``). Without
those flags the output is what it was.

``test`` judges each rule alone on the ``examples`` it carries: facts it must fail on and
facts it must pass on, written by the rule's author. With a GND whose ``gnd synth`` has
``--guarded-cases``, it also asks GND to build a failing and a passing case for each rule
from the rule as written, and reports a rule GND finds can never fail, or can never apply.

``suggest`` reads the code, not the rules: GND's ``guarded-join`` discovery (``gnd discover``,
0.3.1) over which component uses which and the area each is in. It prints the
near misses first, an area that uses another only a few times, often a layering mistake
nobody wrote down, and then the directions the code keeps: an area that never uses one
that uses it. ``--format toml`` prints those as ``[[forbid]]`` lines for ``layers.toml``.
Nothing is written: a pair the code keeps today is a rule only when someone means it.

``rules.json`` and ``layers.toml`` live beside the catalog, in the index script's
``docs_dir``. Settings live beside this script, in rules_check.settings.json. Needs
Python 3.11 or newer, and GND 0.2.0 or newer (get-nick-done on PyPI), the first release
with the rule-check flags (``--rule-ids``, ``--baseline``, ``--allow-vacuous``: report
version 15).
"""
from __future__ import annotations

import argparse
import datetime
import fnmatch
import importlib.util
import itertools
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

DEFAULT_SETTINGS = {
    'index_script': 'scripts/components_index.py',
    # The command that runs GND, for example "uvx --from get-nick-done==0.3.0 gnd"; 0.3.1, a git tag, also needs
    # its URL: "uvx --from 'get-nick-done[synth] @ git+https://github.com/vasiloglou/gnd-public@v0.3.1' gnd".
    'gnd_command': 'gnd',
    # The phase tool, for `check --phase`: it writes what the plans of a phase say, as facts.
    'phase_script': '.claude/skills/process-phase/scripts/phase_tool.py',
}
SHOWN = 10  # lines printed for one rule; --format json has them all
REPORT = 15  # the `gnd check --rule-ids` report: a rule's own id, its remedy, and new or standing
DIAGNOSED = 16  # the same report with `--guarded-diagnostics`: each guarded rule's antecedent bindings
COMPARISON = 'gnd-rule-edition-comparison/1'  # what `gnd check --baseline-model` writes
NEWER = ('--guarded-diagnostics', '--baseline-model')  # flags of GND 0.3.1, used when present
RESERVED = 'devtools_'  # the ids of the value lists the script adds; a rule's id may not start with it
OUTSIDE = 'semantic:guarded-literal-outside-domain'
CASES = 'gnd-guarded-cases/1'  # what `gnd synth --guarded-cases` writes
# Why GND could build no case for a rule, and what that says about the rule; other reasons
# (a shape it does not build cases for, a search that ran out) say nothing about it.
NO_CASE = {'antecedent-unreachable': ('wrong', 'can never apply: no facts can match its antecedent'),
           'no-failing-case': ('wrong', 'can never fail: whatever matches its antecedent already meets its consequent'),
           'no-passing-case': ('note', 'can never pass once it applies: right for a ban, else reread it')}
# `suggest`: the relation and the classifier GND's guarded-join family reads.
RELATION, CLASSIFIER = 'component_uses:caller:callee', 'component_in_area:component:area'
# The values a role can hold whatever the project: a literal outside them in a rule is a typo.
# PLAN_KEYS is `phase_tool.PLAN_KEYS`; a test keeps the two equal.
STATUSES = ['canonical', 'deprecated', 'duplicate-of', 'experimental', 'external']
TASK_TYPES = ['auto', 'checkpoint:decision', 'checkpoint:human-verify']
TEST_KINDS = ['contract', 'guard']
PLAN_KEYS = ['autonomous', 'gap_closure', 'golden_impact', 'llm_dependency', 'prove_method']
BANDS = {0, 1, 2, 4}  # exit codes of a check that ran: accepted, violated, vacuous rules, undecided
USES = ('component_uses', 'component_uses_in_cycle')
MODEL_ID = 'urn:devtools:component-rules@1'
GND_FROM = 'get-nick-done 0.2.0'  # the first release with the flags; 0.3.1 is the one this script was last tried with

STARTER_RULES = {'rules': [
    {'id': 'no_forbidden_area_use', 'level': 'must',
     'remedy': 'This area must not use that one (a [[forbid]] pair in layers.toml): move the import, '
               'or the module to the component it belongs to',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'component_uses', 'bind': {'caller': '$a', 'callee': '$b'}},
                    {'fact_type': 'component_in_area', 'bind': {'component': '$a', 'area': '$from'}},
                    {'fact_type': 'component_in_area', 'bind': {'component': '$b', 'area': '$to'}}],
     'consequent': {'absence': {'fact_type': 'area_must_not_use', 'bind': {'source': '$from', 'target': '$to'}}},
     'examples': {'fails': {'component_uses': [{'caller': 'cli.run', 'callee': 'core.sizes'}],
                            'component_in_area': [{'component': 'cli.run', 'area': 'cli'},
                                                  {'component': 'core.sizes', 'area': 'core'}],
                            'area_must_not_use': [{'source': 'cli', 'target': 'core'}]},
                  'passes': {'component_uses': [{'caller': 'cli.run', 'callee': 'core.sizes'}],
                             'component_in_area': [{'component': 'cli.run', 'area': 'cli'},
                                                   {'component': 'core.sizes', 'area': 'core'}],
                             'area_must_not_use': [{'source': 'core', 'target': 'cli'}]}}},
    {'id': 'no_use_of_a_higher_rank', 'level': 'must',
     'remedy': 'A component uses one of a higher rank ([rank] in layers.toml): move what it needs down, '
               'or the caller up',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'component_uses', 'bind': {'caller': '$a', 'callee': '$b'}},
                    {'fact_type': 'component_in_area', 'bind': {'component': '$a', 'area': '$from'}},
                    {'fact_type': 'component_in_area', 'bind': {'component': '$b', 'area': '$to'}},
                    {'fact_type': 'area_has_rank', 'bind': {'area': '$from', 'rank': '$rank'}},
                    {'fact_type': 'area_has_rank', 'bind': {'area': '$to', 'rank': '$used'}}],
     'consequent': {'comparison': {'operator': '<=', 'left': '$used', 'right': '$rank'}},
     'examples': {'fails': {'component_uses': [{'caller': 'core.sizes', 'callee': 'cli.run'}],
                            'component_in_area': [{'component': 'cli.run', 'area': 'cli'},
                                                  {'component': 'core.sizes', 'area': 'core'}],
                            'area_has_rank': [{'area': 'core', 'rank': 0}, {'area': 'cli', 'rank': 1}]},
                  'passes': {'component_uses': [{'caller': 'cli.run', 'callee': 'core.sizes'}],
                             'component_in_area': [{'component': 'cli.run', 'area': 'cli'},
                                                   {'component': 'core.sizes', 'area': 'core'}],
                             'area_has_rank': [{'area': 'core', 'rank': 0}, {'area': 'cli', 'rank': 1}]}}},
    {'id': 'no_import_inside_a_loop', 'level': 'should',
     'remedy': 'This import is part of a loop of imports between components: move the shared code '
               'into a component both can use',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'component_uses_in_cycle', 'bind': {'caller': '$a', 'callee': '$b'}}],
     'consequent': {'absence': {'fact_type': 'component_uses', 'bind': {'caller': '$a', 'callee': '$b'}}},
     # Every import inside a loop is reported, so the passing example has no loop: it shows the rule is
     # quiet then, and `test` notes that it matched nothing.
     'examples': {'fails': {'component_uses': [{'caller': 'cli.run', 'callee': 'core.sizes'},
                                               {'caller': 'core.sizes', 'callee': 'cli.run'}],
                            'component_uses_in_cycle': [{'caller': 'cli.run', 'callee': 'core.sizes'},
                                                        {'caller': 'core.sizes', 'callee': 'cli.run'}]},
                  'passes': {'component_uses': [{'caller': 'cli.run', 'callee': 'core.sizes'}]}}},
    {'id': 'canonical_component_has_a_test', 'level': 'should',
     'remedy': 'A canonical component lists no test: add a tests: line to its entry, or write one',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'component_has_status', 'bind': {'component': '$a', 'status': 'canonical'}}],
     'consequent': {'exists': {'atoms': [{'fact_type': 'component_has_test',
                                          'bind': {'component': '$a', 'path': '$test'}}]}},
     'examples': {'fails': {'component_has_status': [{'component': 'core.sizes', 'status': 'canonical'}]},
                  'passes': {'component_has_status': [{'component': 'core.sizes', 'status': 'canonical'}],
                             'component_has_test': [{'component': 'core.sizes', 'path': 'tests/test_sizes.py'}]}}},
    {'id': 'private_module_stays_in_its_component', 'level': 'should',
     'remedy': 'A file imports a private file (its name starts with _) of another component: import what '
               'that component offers, or move the file to the component that uses it',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'module_imports', 'bind': {'importer': '$a', 'imported': '$b'}},
                    {'fact_type': 'module_is_private', 'bind': {'path': '$b'}},
                    {'fact_type': 'component_has_module', 'bind': {'component': '$c', 'path': '$b'}}],
     'consequent': {'atom': {'fact_type': 'component_has_module', 'bind': {'component': '$c', 'path': '$a'}}},
     'examples': {'fails': {'module_imports': [{'importer': 'src/app/cli.py', 'imported': 'src/app/_round.py'}],
                            'module_is_private': [{'path': 'src/app/_round.py'}],
                            'component_has_module': [{'component': 'cli.run', 'path': 'src/app/cli.py'},
                                                     {'component': 'core.sizes', 'path': 'src/app/_round.py'}]},
                  'passes': {'module_imports': [{'importer': 'src/app/sizes.py', 'imported': 'src/app/_round.py'}],
                             'module_is_private': [{'path': 'src/app/_round.py'}],
                             'component_has_module': [{'component': 'core.sizes', 'path': 'src/app/sizes.py'},
                                                      {'component': 'core.sizes', 'path': 'src/app/_round.py'}]}}},
    {'id': 'plan_names_the_components_it_touches', 'about': 'plans', 'level': 'should',
     'remedy': 'A task changes a file of a component the plan does not name: add the component to the '
               "plan's reuse: line, or to new_component: if the plan creates it",
     'type': 'guarded',
     'antecedent': [{'fact_type': 'task_touches_component', 'bind': {'task': '$task', 'component': '$component'}},
                    {'fact_type': 'task_in_plan', 'bind': {'task': '$task', 'plan': '$plan'}}],
     'consequent': {'atom': {'fact_type': 'plan_names_component',
                             'bind': {'plan': '$plan', 'component': '$component'}}},
     'examples': {'fails': {'task_touches_component': [{'task': '01-01-T1', 'component': 'core.sizes'}],
                            'task_in_plan': [{'task': '01-01-T1', 'plan': '01-01'}],
                            'plan_names_component': [{'plan': '01-01', 'component': 'cli.run'}]},
                  'passes': {'task_touches_component': [{'task': '01-01-T1', 'component': 'core.sizes'}],
                             'task_in_plan': [{'task': '01-01-T1', 'plan': '01-01'}],
                             'plan_names_component': [{'plan': '01-01', 'component': 'core.sizes'}]}}},
]}
# What `check --phase` adds to the plan facts and the component facts: each needs both.
JOINED = {
    'task_touches_component': ('{Task} names a file of {Component}', (('task', 'task'), ('component', 'component'))),
    'task_reads_component': ('{Task} reads a file of {Component} first', (('task', 'task'), ('component', 'component'))),
    'task_adds_file': ('{Task} names {Path}, which does not exist yet', (('task', 'task'), ('path', 'path'))),
    'plan_names_component': ('{Plan} names {Component} in its Reuse section', (('plan', 'plan'), ('component', 'component'))),
}

STARTER_LAYERS = """# Which areas may use which. An area is the first part of a component id: core.sizes is in core.
# `components_index.py facts` turns these lines into facts, and the rules in rules.json judge them.
#
# [rank]          # a component may use components of its own rank or a lower one
# core = 0
# cli = 1
#
# [[forbid]]      # one pair that is never allowed, whatever the ranks
# from = "core"
# to = "cli"
"""


class Problem(Exception):
    """The check could not run."""


def load_settings(path: Path) -> dict:
    settings = dict(DEFAULT_SETTINGS)
    if path.is_file():
        loaded = json.loads(path.read_text(encoding='utf-8'))
        unknown = sorted(set(loaded) - set(DEFAULT_SETTINGS))
        if unknown:
            raise SystemExit(f'{path}: unknown setting(s): {", ".join(unknown)}')
        settings.update(loaded)
    return settings


SETTINGS = load_settings(Path(__file__).resolve().with_suffix('.settings.json'))


def places(root: Path) -> tuple[str, str]:
    """The rules file and the layers file: beside the catalog, where the index script reads the layers."""
    settings = (root / SETTINGS['index_script']).with_suffix('.settings.json')
    try:
        folder = json.loads(settings.read_text(encoding='utf-8')).get('docs_dir') if settings.is_file() else None
    except (ValueError, AttributeError) as exc:
        raise Problem(f'{settings}: {exc}')
    folder = (folder or 'docs/components').strip('/')
    return f'{folder}/rules.json', f'{folder}/layers.toml'


def load_rules(root: Path) -> list[dict]:
    RULES = places(root)[0]
    path = root / RULES
    if not path.is_file():
        raise Problem(f'{RULES} is missing: run `python3 {Path(sys.argv[0]).as_posix()} init` to write the starter rules')
    try:
        rules = json.loads(path.read_text(encoding='utf-8')).get('rules')
    except (ValueError, AttributeError) as exc:
        raise Problem(f'{RULES}: not a JSON object with a "rules" list: {exc}')
    problems, seen = [], set()
    for number, rule in enumerate(rules if isinstance(rules, list) else [None], 1):
        name = rule.get('id') if isinstance(rule, dict) else None
        if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_]*', name):
            problems.append(f'rule {number}: needs an "id" of lower-case letters, digits and _')
            continue
        if name.startswith(RESERVED):
            problems.append(f'{name}: an id starting with {RESERVED} is kept for the value lists this script adds')
        if name in seen:
            problems.append(f'{name}: id used twice')
        seen.add(name)
        if rule.get('level', 'must') not in {'must', 'should'}:
            problems.append(f'{name}: "level" is must or should')
        if rule.get('about', 'components') not in {'components', 'plans'}:
            problems.append(f'{name}: "about" is components or plans')
        if not isinstance(rule.get('remedy', ''), str) or 'type' not in rule:
            problems.append(f'{name}: needs a "type", and "remedy" is text')
        if 'examples' in rule and example_sets(rule) is None:
            problems.append(f'{name}: "examples" is {{"fails": ..., "passes": ...}}, each a set of facts '
                            '({fact type: [rows]}) or a list of them')
    if problems:
        raise Problem(f'{RULES}: ' + '; '.join(problems))
    return rules


def example_sets(rule: dict):
    """A rule's examples as [(kind, number, facts)], or None when they are not written as `test` reads them."""
    found = []
    examples = rule.get('examples')
    if not isinstance(examples, dict) or not set(examples) <= {'fails', 'passes'}:
        return None
    for kind in ('fails', 'passes'):
        sets = examples.get(kind, [])
        for number, facts in enumerate(sets if isinstance(sets, list) else [sets], 1):
            if not isinstance(facts, dict) or not all(isinstance(rows, list) and all(isinstance(r, dict) for r in rows)
                                                       for rows in facts.values()):
                return None
            found.append((kind, number, facts))
    return found


def domains(types: dict, facts: dict | None = None) -> list[dict]:
    """The value lists the vocabulary fixes, for the roles the types have: a rule naming another value is a
    typo. Advisory constraints: GND warns about a literal outside them; their verdicts are not findings."""
    lists = []
    present = {(name, role) for name, spec in types['facts'].items() for role, _ in spec['roles']}
    for fact, role, values in (('component_has_status', 'status', STATUSES), ('task_has_type', 'type', TASK_TYPES),
                               ('test_is_in_contract', 'kind', TEST_KINDS), ('plan_declares', 'key', PLAN_KEYS)):
        if (fact, role) in present:
            lists.append((fact, role, values))
    areas = sorted({row['area'] for row in (facts or {}).get('component_in_area', [])})
    if areas and ('component_in_area', 'area') in present:
        lists.append((None, 'area', areas))  # every role an area plays: the catalog's areas are all there are
    found = []
    for fact, role, values in lists:
        kind = dict(types['facts'][fact]['roles'])[role] if fact else role
        body = {'id': f'{RESERVED}{(fact + "_") if fact else ""}{role}_values', 'type': 'value', 'object_type': kind,
                'allowed': values, 'modality': 'deontic', 'source': 'explicit', 'status': 'confirmed',
                'provenance': {'user_quote': 'the values this role can hold'}}
        if fact:
            body['role_ref'] = {'fact_type': fact, 'role': role}
        found.append(body)
    return found


def model(types: dict, rules: list[dict], facts: dict | None = None) -> dict:
    """The GND model: fact types as the facts file describes them, the project's rules, and the value
    lists of `domains` after them."""
    constraints = []
    for rule in rules:
        body = {key: value for key, value in rule.items()
                if key not in ('level', 'about', 'examples') and (key != 'remedy' or value)}
        body.update(modality='alethic' if rule.get('level', 'must') == 'must' else 'deontic', source='explicit',
                    status='confirmed', provenance={'user_quote': rule.get('remedy') or rule['id']})
        constraints.append(body)
    return {
        'version': 4, 'model_id': MODEL_ID, 'rejected_proposals': [],
        'source': {'kind': 'text-conversation', 'mode': 'one-shot', 'confidence': 'standard'},
        'object_types': [{'id': name, 'kind': 'value', 'name': name.capitalize(), 'primitive': primitive}
                         for name, primitive in types['values'].items()],
        'fact_types': [{'id': name, 'reading': spec['reading'],
                        'roles': [{'role_name': role, 'object_type': kind} for role, kind in spec['roles']]}
                       for name, spec in types['facts'].items()],
        'constraints': constraints + domains(types, facts),
    }


def population(doc: dict) -> dict:
    header = {'covers': sorted(doc['facts']), 'model': 'model.json', 'model_id': MODEL_ID, 'source': 'tool-output',
              'producer': f'{Path(SETTINGS["index_script"]).name} facts @ {doc.get("revision") or "no revision"}'[:200]}
    return {'format_version': 2, 'facts': doc['facts'], 'population': header}


def named_facts(value) -> set:
    """Every fact type a rule names, wherever in it."""
    if isinstance(value, dict):
        return {v for k, v in value.items() if k == 'fact_type' and isinstance(v, str)} | named_facts(list(value.values()))
    return set().union(*map(named_facts, value)) if isinstance(value, list) else set()


def run(command: list, what: str, **options) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(command, capture_output=True, text=True, **options)
    except OSError as exc:
        raise Problem(f'{what} could not start: {exc}')


def read_facts(root: Path, base: str = '', modules: bool = False) -> dict:
    script = root / SETTINGS['index_script']
    if not script.is_file():
        raise Problem(f'{SETTINGS["index_script"]} is missing (index_script in rules_check.settings.json)')
    done = run([sys.executable, str(script), '--root', str(root), 'facts', *(['--base', base] if base else []),
                *(['--modules'] if modules else [])], 'the index script')
    if done.returncode:
        raise Problem(f'{SETTINGS["index_script"]} facts: {(done.stderr or done.stdout).strip()}')
    doc = json.loads(done.stdout)
    if doc.get('format') != 'devtools-facts/1':
        raise Problem(f'{SETTINGS["index_script"]} facts wrote format {doc.get("format")!r}; this script reads devtools-facts/1')
    return doc


def features(gnd: list, command: str = 'check', flags: tuple = NEWER) -> set:
    """Which flags of GND 0.3.1 this one has, read from `gnd <command> --help`."""
    done = run([*gnd, command, '--help'], 'gnd')
    return {flag for flag in flags if not done.returncode and flag in done.stdout}


def judge(gnd: list, folder: Path, head: dict, base: dict | None, diagnose: bool = False) -> dict:
    """The report of `gnd check` on the head facts, against the base facts when given. With `diagnose`,
    each guarded verdict also says how many bindings its antecedent had."""
    for name, doc in (('head', head), ('base', base)):
        if doc is not None:
            (folder / f'{name}.pop.json').write_text(json.dumps(population(doc)), encoding='utf-8')
    command = [*gnd, 'check', str(folder / 'model.json'), str(folder / 'head.pop.json'), '--rule-ids',
               '--allow-vacuous', *(['--guarded-diagnostics'] if diagnose else []), '--format', 'json']
    if base is not None:
        command[-2:-2] = ['--baseline', str(folder / 'base.pop.json')]
    done = run(command, 'gnd')
    if done.returncode == 64 and 'unrecognized arguments' in done.stderr:
        raise Problem(f'this GND has no --rule-ids: install {GND_FROM} or newer')
    try:
        report = json.loads(done.stdout)
    except ValueError:
        raise Problem(f'gnd check failed (exit {done.returncode}): {(done.stderr or done.stdout).strip()[:600]}')
    if not isinstance(report, dict):
        raise Problem(f'gnd check wrote no report (exit {done.returncode})')
    if report.get('exit_code') not in BANDS or not isinstance(report.get('verdicts'), list):
        issues = '; '.join(f'{i.get("path")}: {str(i.get("message"))[:200]}' for i in (report.get('issues') or [])[:5])
        raise Problem(f'gnd did not judge the rules ({report.get("outcome")}, exit {report.get("exit_code")}): '
                      f'{issues or report.get("error")}')
    wanted = DIAGNOSED if diagnose else REPORT
    if report.get('schema_version') != wanted:
        raise Problem(f'gnd wrote report version {report.get("schema_version")}; this script reads version {wanted} here')
    return report


def findings(report: dict, rules: list[dict]) -> tuple[list, list]:
    """What is broken, as (level, rule, binding, new), and the rules gnd could not decide, as (level, rule, why)."""
    by_id = {rule['id']: rule for rule in rules}
    broken, undecided, judged = [], [], set()
    try:
        for verdict in report['verdicts']:
            if verdict['address'].removeprefix('constraint:').startswith(RESERVED):
                continue  # a value list of `domains`, not a rule
            rule = by_id[verdict['address'].removeprefix('constraint:')]  # every rule has an id
            judged.add(rule['id'])
            level = 'fail' if rule.get('level', 'must') == 'must' else 'warn'
            if verdict['verdict'] in {'fail', 'warning'}:
                rows = verdict.get('offending_facts') or [None]
                marks = verdict.get('row_novelty') or [verdict.get('novelty')] * len(rows)
                broken.extend((level, rule, row, mark != 'standing') for row, mark in zip(rows, marks))
            elif verdict['verdict'] == 'unchecked':
                undecided.append((level, rule, verdict.get('reason_code') or verdict.get('message', '')))
            elif verdict['verdict'] not in {'pass', 'vacuous'}:
                raise ValueError(f'unknown verdict {verdict["verdict"]!r}')
    except (KeyError, TypeError, IndexError, ValueError, AttributeError) as exc:
        raise Problem(f'gnd wrote a report this script cannot read: {type(exc).__name__}: {exc}')
    unjudged = [rule['id'] for rule in rules if rule['id'] not in judged]
    if unjudged:
        raise Problem(f'gnd gave no verdict for: {", ".join(unjudged)}')
    return broken, undecided


def silent(report: dict, rules: list[dict]) -> list[str]:
    """`reread:` notes for the rules a report shows judged nothing: an antecedent that no binding gets
    through although every fact it names has rows (GND says so only with --guarded-diagnostics)."""
    by_id = {rule['id']: rule for rule in rules}
    notes = []
    for verdict in report.get('verdicts', []):
        rule = by_id.get(verdict.get('address', '').removeprefix('constraint:'))
        seen = verdict.get('guarded_antecedent') or {}
        index = seen.get('first_empty_atom_index')
        if rule and seen.get('binding_count') == 0 and isinstance(index, int):
            atoms = rule.get('antecedent') or []
            fact = atoms[index].get('fact_type', '?') if 0 <= index < len(atoms) and isinstance(atoms[index], dict) else '?'
            notes.append(f'{rule["id"]} matched nothing: no binding gets past atom {index} ({fact}) of its antecedent, '
                         f'though every fact it names has rows')
    return notes


def outside(report: dict, built: dict, rules: list[dict]) -> list[str]:
    """`reread:` notes for a literal in a rule that no fact of its kind can hold, from GND's warnings."""
    notes = []
    for warning in report.get('warnings') or []:
        if not isinstance(warning, dict) or warning.get('rule_id') != OUTSIDE:
            continue
        path = str(warning.get('path', ''))
        steps = re.findall(r'\.([A-Za-z_]+)|\[(\d+)\]|\[([^\]]+)\]', path)
        node, trail = built, []
        try:
            for key, index, name in steps:
                trail.append(node)
                node = node[int(index)] if index else node[key or name]
        except (KeyError, IndexError, TypeError, ValueError):
            notes.append(f'a literal lies outside the values its role can hold, at {path}')
            continue
        owner = trail[2] if len(trail) > 2 and isinstance(trail[2], dict) else {}  # model, constraints, the rule
        atom = next((step for step in reversed(trail) if isinstance(step, dict) and 'fact_type' in step), {})
        role = (steps[-1][2] or steps[-1][0]) if steps else '?'
        found = re.search(r'constraints\[(\d+)\]', str(warning.get('message', '')))
        allowed = built['constraints'][int(found.group(1))].get('allowed', []) if found else []
        notes.append(f'{owner.get("id", "a rule")}: {node!r} is not a value {atom.get("fact_type", "?")}.{role} '
                     f'can hold' + (f' ({", ".join(map(str, allowed))})' if allowed else ''))
    return notes


def hidden(comparison: dict) -> list[str]:
    """`reread:` notes from `gnd check --baseline-model`: what the edited rules stop reporting on this code."""
    notes = []
    if comparison.get('schema_version') != COMPARISON:
        return [f'the rules were edited, and gnd wrote no comparison this script reads '
                f'({comparison.get("schema_version")!r})']
    for row in comparison.get('rules') or []:
        name = str(row.get('address', '')).removeprefix('constraint:')
        if name.startswith(RESERVED):
            continue
        delta, before, after = row.get('delta') or {}, row.get('base') or {}, row.get('head') or {}
        gone = delta.get('base_only') or []
        shown = ''.join(f'; {describe(binding)}' for binding in gone[:3]) + ('; …' if len(gone) > 3 else '')
        if row.get('pairing') == 'removed':
            notes.append(f'{name} was removed in this change; on this code it reported {len(gone)} finding(s){shown}')
        elif row.get('pairing') == 'paired' and gone:
            notes.append(f'{name} was edited in this change and no longer reports {len(gone)} finding(s) it '
                         f'reported before{shown}')
        if row.get('pairing') == 'paired' and before.get('modality') == 'alethic' and after.get('modality') == 'deontic':
            notes.append(f'{name} went from must to should in this change')
        if row.get('reason'):
            notes.append(f'{name}: the two editions could not be compared ({row["reason"]})')
    if comparison.get('reason'):
        notes.append(f'the two editions of the rules could not be compared ({comparison["reason"]})')
    return notes


def base_rules(root: Path, revision: str) -> list[dict] | None:
    """The rules about components as `rules.json` held them at a commit, or None when it had none."""
    RULES = places(root)[0]
    done = run(['git', '-C', str(root), 'show', f'{revision}:{RULES}'], 'git')
    if done.returncode:
        return None
    try:
        rules = json.loads(done.stdout).get('rules')
    except (ValueError, AttributeError):
        return None
    return [rule for rule in rules if isinstance(rule, dict) and rule.get('about', 'components') == 'components'
            and isinstance(rule.get('id'), str)] if isinstance(rules, list) else None


def compare(gnd: list, folder: Path, head_model: dict, base_model: dict) -> dict:
    """`gnd check` of today's facts under today's rules, against the base edition of the rules."""
    (folder / 'base-model.json').write_text(json.dumps(base_model), encoding='utf-8')
    done = run([*gnd, 'check', str(folder / 'model.json'), str(folder / 'head.pop.json'),
                '--baseline-model', str(folder / 'base-model.json'), '--format', 'json'], 'gnd')
    try:
        found = json.loads(done.stdout)
    except ValueError:
        return {'reason': f'gnd check --baseline-model exited {done.returncode}: {(done.stderr or done.stdout).strip()[:300]}'}
    return found if isinstance(found, dict) else {'reason': 'gnd wrote no comparison'}


def used_pair(rule: dict, binding) -> tuple | None:
    """The (caller, callee) a broken rule is about: what its first `component_uses` atom binds."""
    atoms = rule.get('antecedent') if isinstance(binding, dict) else None
    for atom in atoms if isinstance(atoms, list) else []:
        if isinstance(atom, dict) and atom.get('fact_type') in USES and isinstance(atom.get('bind'), dict):
            return tuple(binding.get(atom['bind'].get(role), atom['bind'].get(role)) for role in ('caller', 'callee'))
    return None


def describe(binding) -> str:
    if isinstance(binding, dict):
        return ' '.join(f'{key.lstrip("$")}={value}' for key, value in binding.items())
    return ' -> '.join(str(value) for value in binding or [])


def changed_rules(root: Path, commit: str) -> list[str]:
    """The rules files that differ from a commit, untracked ones included."""
    RULES, LAYERS = places(root)
    names = []
    for command in (['diff', '--name-only', commit, '--', RULES, LAYERS],
                    ['ls-files', '--others', '--exclude-standard', '--', RULES, LAYERS]):
        done = run(['git', '-C', str(root), *command], 'git')
        names.extend(done.stdout.split() if not done.returncode else [])
    return sorted(set(names))


def check(root: Path, base: str, strict: bool, require: bool, as_json: bool) -> int:
    gnd = shlex.split(SETTINGS['gnd_command'])
    if not gnd or not shutil.which(gnd[0]):
        print(f'skip: gnd not found ({SETTINGS["gnd_command"]!r}; install GND or set gnd_command in '
              f'rules_check.settings.json)')
        return int(require)
    rules = [rule for rule in load_rules(root) if rule.get('about', 'components') == 'components']
    has = features(gnd)
    head = read_facts(root)
    # The facts about files are asked for only when a rule names one: a file path in a fact
    # makes a renamed file a new fact, which a project whose rules name no file is spared.
    modules = bool(named_facts(rules) - set(head['types']['facts']))
    if modules:
        head = read_facts(root, modules=True)
    notes, before, old = [], None, None
    if base:
        before = read_facts(root, base, modules)
        if before['facts']['component_is_listed']:
            old = {(row['caller'], row['callee']): row['imports'] for row in before['evidence']['component_uses']}
        else:
            notes.append(f'no catalog at {before["revision"][:7]}: everything broken counts as new')
        edited = changed_rules(root, before['revision'])
        notes.extend(f'rules changed in this change: {path}' for path in edited)
    built = model(head['types'], rules, head['facts'])
    with tempfile.TemporaryDirectory() as name:
        folder = Path(name)
        (folder / 'model.json').write_text(json.dumps(built), encoding='utf-8')
        report = judge(gnd, folder, head, before if old is not None else None, '--guarded-diagnostics' in has)
        earlier = base_rules(root, before['revision']) if base and places(root)[0] in edited else None
        if earlier is not None and '--baseline-model' in has:
            notes.extend(hidden(compare(gnd, folder, built, model(head['types'], earlier, head['facts']))))
    notes.extend(silent(report, rules) + outside(report, built, rules))
    broken, undecided = findings(report, rules)
    edges = {(row['caller'], row['callee']): row['imports'] for row in head['evidence']['component_uses']}
    rows = []
    for level, rule, binding, new in broken:
        imports = edges.get(used_pair(rule, binding), [])
        added = [pair for pair in imports if pair not in old.get(used_pair(rule, binding), [])] if old is not None else []
        shown = ''.join(f' ({" -> ".join(pair)})' for pair in (added or imports)[:1])
        rows.append({'rule': rule['id'], 'level': level, 'remedy': rule.get('remedy', ''), 'binding': binding,
                     'text': describe(binding) + shown + (' [new import]' if added else ''),
                     'new': new, 'new_import': bool(added), 'old_import': bool(imports) and not added})
    order = [rule['id'] for rule in rules]
    rows.sort(key=lambda row: (order.index(row['rule']), not row['new_import'], row['text']))
    rows.extend({'rule': rule['id'], 'level': level, 'remedy': f'gnd could not decide this rule ({why})',
                 'binding': None, 'text': '', 'new': True, 'new_import': False, 'old_import': False}
                for level, rule, why in undecided)
    new = [row for row in rows if row['new']]
    fails = sum(row['level'] == 'fail' for row in new)
    against = f' against {base} ({before["revision"][:7]})' if old is not None else ''
    summary = (f'rules{against}: {len(rules)} rule(s); {fails} to fix, {len(new) - fails} warning(s)'
               + (f', {len(rows) - len(new)} standing' if old is not None else ''))
    if as_json:
        print(json.dumps({'rows': rows, 'notes': notes, 'summary': summary, 'baseline': report.get('baseline'),
                          'bindings': bindings(report)}, indent=1))
    else:
        for name, group in itertools.groupby(new, key=lambda row: row['rule']):
            group = list(group)
            for row in group[:SHOWN]:
                print(f'{row["level"]}: {name}' + (f': {row["text"]}' if row['text'] else ''))
                if row['remedy']:
                    print(f'  remedy: {row["remedy"]}')
            if len(group) > SHOWN:
                old_ones = sum(row['old_import'] for row in group[SHOWN:])
                print(f'… +{len(group) - SHOWN} more for {name}'
                      + (f', {old_ones} of them through imports that were already there' if old is not None else '')
                      + ' (--format json lists them all)')
        for note in notes:
            print(f'reread: {note}')
        print(summary)
    return int(bool(fails or (strict and new)))


def read_plan_facts(root: Path, phase: str) -> dict:
    """What the plans of a phase say, from the phase tool."""
    name = SETTINGS['phase_script']
    if not (root / name).is_file():
        raise Problem(f'{name} is missing (phase_script in rules_check.settings.json): check --phase is for a '
                      f'project that uses the phase workflow')
    done = run([sys.executable, str(root / name), '--format', 'json', '--root', str(root), 'facts', '--phase', phase],
               'the phase tool')
    try:
        answer = json.loads(done.stdout)
        if not answer['ok']:
            raise Problem(f'{name} facts: {answer["error"]["message"]}')
        doc = answer['data']
        if doc['format'] != 'devtools-facts/1':
            raise Problem(f'{name} facts wrote format {doc["format"]!r}; this script reads devtools-facts/1')
    except (ValueError, KeyError, TypeError):
        raise Problem(f'{name} facts: {(done.stderr or done.stdout).strip()[:600]}')
    return doc


def names(entry: str, path: str) -> bool:
    """Whether an entry of a task's files (a path, a folder ending in /, or a pattern with *) names a file."""
    return entry == path or (entry.endswith('/') and path.startswith(entry)) or ('*' in entry and fnmatch.fnmatch(path, entry))


def plans_with_components(root: Path, code: dict, plans: dict) -> dict:
    """One set of facts from the two: the component facts, the plan facts, and the JOINED ones."""
    holders = {}
    for row in code['facts']['component_has_module']:
        holders.setdefault(row['path'], []).append(row['component'])
    members = {}
    for row in code['facts']['subsystem_has_member']:
        members.setdefault(row['subsystem'], []).append(row['component'])

    def components(fact: str) -> set:
        return {(row['task'], component) for row in plans['facts'][fact]
                for path, held in holders.items() if names(row['path'], path) for component in held}

    named = {(row['plan'], component) for fact in ('plan_reuses_component', 'plan_adds_component')
             for row in plans['facts'][fact] for component in [row['component'], *members.get(row['component'], [])]}
    found = {
        'task_touches_component': components('task_names_file'),
        'task_reads_component': components('task_reads_first'),
        'task_adds_file': {(row['task'], row['path']) for row in plans['facts']['task_names_file']
                           if '*' not in row['path'] and not row['path'].endswith('/')
                           and not (root / row['path']).exists()},
        'plan_names_component': named,
    }
    values = dict(code['types']['values'])
    for name, primitive in plans['types']['values'].items():
        if values.setdefault(name, primitive) != primitive:
            raise Problem(f'the index script and the phase tool disagree about the value type {name}')
    return {
        'revision': plans.get('revision') or code.get('revision'),
        'types': {'values': values,
                  'facts': {**code['types']['facts'], **plans['types']['facts'],
                            **{name: {'reading': reading, 'roles': [list(role) for role in roles]}
                               for name, (reading, roles) in JOINED.items()}}},
        'facts': {**code['facts'], **plans['facts'],
                  **{name: [dict(zip((role for role, _ in JOINED[name][1]), row)) for row in sorted(rows)]
                     for name, rows in found.items()}},
    }


def bindings(report: dict) -> dict:
    """{rule id: how many bindings its antecedent had}, for the guarded rules GND counted."""
    return {verdict['address'].removeprefix('constraint:'): verdict['guarded_antecedent'].get('binding_count')
            for verdict in report.get('verdicts', [])
            if isinstance(verdict.get('guarded_antecedent'), dict)
            and not verdict['address'].removeprefix('constraint:').startswith(RESERVED)}


def check_phase(root: Path, phase: str, strict: bool, require: bool, as_json: bool) -> int:
    """Judge the rules about plans over the plans of one phase. No base: a plan is judged as written."""
    gnd = shlex.split(SETTINGS['gnd_command'])
    if not gnd or not shutil.which(gnd[0]):
        print(f'skip: gnd not found ({SETTINGS["gnd_command"]!r}; install GND or set gnd_command in '
              f'rules_check.settings.json)')
        return int(require)
    rules = [rule for rule in load_rules(root) if rule.get('about') == 'plans']
    has = features(gnd)
    plans = read_plan_facts(root, phase)
    doc = plans_with_components(root, read_facts(root, modules=True), plans)
    built = model(doc['types'], rules, doc['facts'])
    with tempfile.TemporaryDirectory() as name:
        folder = Path(name)
        (folder / 'model.json').write_text(json.dumps(built), encoding='utf-8')
        report = judge(gnd, folder, doc, None, '--guarded-diagnostics' in has)
    notes = silent(report, rules) + outside(report, built, rules)
    broken, undecided = findings(report, rules)
    files = plans['evidence']['plans']
    plan_of = {row['task']: row['plan'] for row in plans['facts']['task_in_plan']}

    def where(binding) -> str:
        """The plan file a line is about: the first plan, or task of a plan, among the values it binds."""
        for value in binding.values() if isinstance(binding, dict) else []:
            if plan_of.get(value, value) in files:
                return f' ({files[plan_of.get(value, value)]})'
        return ''

    rows = [{'rule': rule['id'], 'level': level, 'remedy': rule.get('remedy', ''), 'binding': binding,
             'text': describe(binding) + where(binding)} for level, rule, binding, _ in broken]
    order = [rule['id'] for rule in rules]
    rows.sort(key=lambda row: (order.index(row['rule']), row['text']))
    rows.extend({'rule': rule['id'], 'level': level, 'remedy': f'gnd could not decide this rule ({why})',
                 'binding': None, 'text': ''} for level, rule, why in undecided)
    fails = sum(row['level'] == 'fail' for row in rows)
    summary = (f'plan rules for phase {plans["phase"]}: {len(rules)} rule(s); {fails} to fix, '
               f'{len(rows) - fails} warning(s)')
    if as_json:
        print(json.dumps({'rows': rows, 'notes': notes, 'summary': summary, 'bindings': bindings(report)}, indent=1))
    else:
        for name, group in itertools.groupby(rows, key=lambda row: row['rule']):
            group = list(group)
            for row in group[:SHOWN]:
                print(f'{row["level"]}: {name}' + (f': {row["text"]}' if row['text'] else ''))
                if row['remedy']:
                    print(f'  remedy: {row["remedy"]}')
            if len(group) > SHOWN:
                print(f'… +{len(group) - SHOWN} more for {name} (--format json lists them all)')
        for note in notes:
            print(f'reread: {note}')
        print(summary)
    return int(bool(fails or (strict and rows)))


def vocabulary(root: Path) -> dict:
    """Every fact type a rule can name: the component facts, the file facts, and, where the phase tool is
    here, the plan facts and the ones `check --phase` joins."""
    types = read_facts(root, modules=True)['types']
    script = root / SETTINGS['phase_script']
    if script.is_file():
        spec = importlib.util.spec_from_file_location('phase_tool', script)
        tool = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(tool)
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - a broken phase tool leaves its facts out
            raise Problem(f'{SETTINGS["phase_script"]} could not be read for its fact types: {exc}')
        types = {'values': {**types['values'], **tool.FACT_VALUES},
                 'facts': {**types['facts'], **{name: {'reading': reading, 'roles': [list(role) for role in roles]}
                                                for name, (reading, roles) in {**tool.FACT_TYPES, **JOINED}.items()}}}
    return types


def generated(gnd: list, types: dict, rules: list[dict], noted: set) -> list[tuple]:
    """What `gnd synth --guarded-cases` finds about the rules as written: a rule it could build no failing,
    or no passing, case for. Those cases come from the rule itself, so they cannot say the rule means what
    its author meant; the examples do that. A rule already noted for a literal outside its values is not
    noted again for applying to nothing."""
    with tempfile.TemporaryDirectory() as name:
        folder = Path(name)
        (folder / 'model.json').write_text(json.dumps(model(types, rules)), encoding='utf-8')
        done = run([*gnd, 'synth', str(folder / 'model.json'), '--guarded-cases', '--out', str(folder / 'cases'),
                    '--seed', '0'], 'gnd')
        try:
            manifest = json.loads((folder / 'cases' / 'guarded-cases.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return [('note', f'gnd synth --guarded-cases built no cases (exit {done.returncode}): '
                             f'{(done.stderr or done.stdout).strip()[:300]}')]
    if manifest.get('schema_version') != CASES:
        return [('note', f'gnd synth --guarded-cases wrote {manifest.get("schema_version")!r}; this script reads {CASES}')]
    found = []
    for entry in manifest.get('rules') or []:
        name, reason = entry.get('rule_id'), entry.get('reason')
        if reason in NO_CASE and not (reason == 'antecedent-unreachable' and name in noted):
            level, says = NO_CASE[reason]
            found.append((level, f'{name} {says} (gnd synth --guarded-cases: {reason})'))
    return found


def test(root: Path, require: bool, as_json: bool) -> int:
    """Judge each rule alone on the examples it carries: each `fails` set must break it, each `passes` set
    must not. A passing set the rule matched nothing in is noted: it shows only that the rule is quiet
    with no subject (GND 0.3.1 says so; 0.3.0 only when no fact the rule names has rows)."""
    gnd = shlex.split(SETTINGS['gnd_command'])
    if not gnd or not shutil.which(gnd[0]):
        print(f'skip: gnd not found ({SETTINGS["gnd_command"]!r}; install GND or set gnd_command in '
              f'rules_check.settings.json)')
        return int(require)
    rules = load_rules(root)
    diagnose = '--guarded-diagnostics' in features(gnd)
    types = vocabulary(root)
    results, without, count, typos = [], [], 0, set()
    for rule in rules:
        sets = example_sets(rule) or []
        if not sets:
            without.append(rule['id'])
        for kind, number, facts in sets:
            count += 1
            label = f'{rule["id"]}: the {"failing" if kind == "fails" else "passing"} example {number}'
            unknown = sorted(set(facts) - set(types['facts']))
            if unknown:
                results.append(('wrong', f'{label} names {", ".join(unknown)}, which no fact type of this project is'))
                continue
            doc = {'facts': {name: facts.get(name, []) for name in types['facts']}, 'revision': 'examples'}
            built = model(types, [rule])
            with tempfile.TemporaryDirectory() as name:
                folder = Path(name)
                (folder / 'model.json').write_text(json.dumps(built), encoding='utf-8')
                try:
                    report = judge(gnd, folder, doc, None, diagnose)
                except Problem as exc:
                    results.append(('wrong', f'{label} could not be judged: {exc}'))
                    continue
            verdict = next((v for v in report['verdicts'] if v.get('address') == 'constraint:' + rule['id']), {})
            seen = verdict.get('guarded_antecedent') or {}
            empty = verdict.get('verdict') == 'vacuous' or seen.get('binding_count') == 0
            why = ''
            if isinstance(seen.get('first_empty_atom_index'), int):
                atoms = rule.get('antecedent') or []
                index = seen['first_empty_atom_index']
                fact = atoms[index].get('fact_type', '?') if 0 <= index < len(atoms) else '?'
                why = f': no binding gets past atom {index} ({fact})'
            literals = outside(report, built, [rule])
            results.extend(('note', note) for note in literals)
            typos.update([rule['id']] if literals else [])
            broke = verdict.get('verdict') in {'fail', 'warning'}
            if verdict.get('verdict') == 'unchecked':
                results.append(('wrong', f'{label}: gnd could not decide the rule ({verdict.get("reason_code")})'))
            elif kind == 'fails' and not broke:
                results.append(('wrong', f'{label} does not break the rule' + (f'; it matched nothing{why}' if empty else '')))
            elif kind == 'passes' and broke:
                first = (verdict.get('offending_facts') or [None])[0]
                results.append(('wrong', f'{label} breaks the rule: {describe(first)}'))
            elif kind == 'passes' and empty:
                results.append(('note', f'{label} matched nothing{why}, so it shows only that the rule is quiet '
                                        f'with no subject'))
    if '--guarded-cases' in features(gnd, 'synth', ('--guarded-cases',)):
        results.extend(generated(gnd, types, rules, typos))
    results = list(dict.fromkeys(results))  # a note about a rule's literal comes once, not once per example
    wrong = sum(level == 'wrong' for level, _ in results)
    summary = (f'rules test: {len(rules)} rule(s), {count} example(s); {wrong} wrong'
               + (f'; {len(without)} rule(s) without examples' if without else ''))
    if as_json:
        print(json.dumps({'results': [{'level': level, 'text': text} for level, text in results],
                          'without_examples': without, 'summary': summary}, indent=1))
    else:
        for level, text in results:
            print(f'{level}: {text}')
        if without:
            print(f'no examples: {", ".join(without)}')
        print(summary)
    return int(bool(wrong))


def joined(gnd: list, head: dict) -> dict:
    """GND's guarded-join discovery over the component facts: the report of `gnd discover`."""
    areas = {row['area'] for row in head['facts']['component_in_area']}
    stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    with tempfile.TemporaryDirectory() as name:
        folder = Path(name)
        (folder / 'model.json').write_text(json.dumps(model(head['types'], [])), encoding='utf-8')
        (folder / 'pop.json').write_text(json.dumps(population(head)), encoding='utf-8')
        done = run([*gnd, 'discover', str(folder / 'model.json'), str(folder / 'pop.json'), '--families', 'guarded-join',
                    '--joined-relation', RELATION, '--joined-classifier', CLASSIFIER,
                    '--max-directed-pairs', str(max(1, len(areas) ** 2)),  # every ordered pair, an area with itself too
                    '--actor', 'rules_check.py', '--requested-at', stamp,
                    '--out', str(folder / 'proposal.json'), '--report', str(folder / 'report.json')], 'gnd')
        try:
            report = json.loads((folder / 'report.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            raise Problem(f'gnd discover failed (exit {done.returncode}): {(done.stderr or done.stdout).strip()[:600]}')
    reason = (report.get('joined_rules') or {}).get('reason')
    if reason:
        raise Problem(f'gnd discover could not look for rules over the areas: {reason}')
    return report


def area_pair(constraint: dict) -> tuple | None:
    """(source area, target area) of a forbidden pair GND proposes: a use from the one never reaches the other."""
    try:
        atoms, target = constraint['antecedent'], constraint['consequent']['absence']
        source = next(atom['bind']['area'] for atom in atoms if atom['fact_type'] == 'component_in_area')
        if target['fact_type'] != 'component_in_area' or target['bind']['area'] == source:
            return None  # a use inside one area is not a layer
        return source, target['bind']['area']
    except (KeyError, TypeError, StopIteration):
        return None


def suggest(root: Path, require: bool, form: str) -> int:
    """Rules about areas the code already keeps, and the near misses, from GND's guarded-join discovery."""
    gnd = shlex.split(SETTINGS['gnd_command'])
    if not gnd or not shutil.which(gnd[0]):
        print(f'skip: gnd not found ({SETTINGS["gnd_command"]!r}; install GND or set gnd_command in '
              f'rules_check.settings.json)')
        return int(require)
    if '--joined-relation' not in features(gnd, 'discover', ('--joined-relation',)):
        print('skip: suggest needs a GND whose `gnd discover` has the guarded-join family (GND 0.3.1)')
        return int(require)
    head = read_facts(root)
    facts = head['facts']
    area = {row['component']: row['area'] for row in facts['component_in_area']}
    uses = Counter((area.get(row['caller']), area.get(row['callee'])) for row in facts['component_uses'])
    rank = {row['area']: row['rank'] for row in facts['area_has_rank']}
    banned = {(row['source'], row['target']) for row in facts['area_must_not_use']}

    def covered(pair: tuple) -> bool:
        """Whether layers.toml already says so: a [[forbid]] pair, or a target of a higher rank."""
        return pair in banned or (pair[0] in rank and pair[1] in rank and rank[pair[1]] > rank[pair[0]])

    report = joined(gnd, head) if facts['component_uses'] else {'emitted': [], 'near_misses': []}
    imports = {(row['caller'], row['callee']): row['imports'] for row in head['evidence']['component_uses']}
    names = [spec for spec in head['types']['facts']]
    kept, almost = [], []
    for entry in report.get('emitted') or []:
        pair = area_pair(entry.get('constraint') or {})
        if pair and uses[pair[::-1]] and not covered(pair):  # the other way is used: the code keeps a direction
            kept.append({'from': pair[0], 'to': pair[1], 'used_the_other_way': uses[pair[::-1]]})
    for entry in report.get('near_misses') or []:
        pair = area_pair(entry.get('constraint') or {})
        if not pair or covered(pair):  # what layers.toml forbids, `check` reports
            continue
        rows = []
        for ref in entry.get('counterexamples') or []:
            found = re.fullmatch(r'ft(\d+)#(\d+)', str(ref))
            fact = names[int(found.group(1))] if found and int(found.group(1)) < len(names) else None
            table = facts.get(fact) or []
            if fact == 'component_uses' and int(found.group(2)) < len(table):
                row = table[int(found.group(2))]
                rows.append({'caller': row['caller'], 'callee': row['callee'],
                             'imports': imports.get((row['caller'], row['callee']), [])})
        almost.append({'from': pair[0], 'to': pair[1], 'uses': entry.get('violations'), 'of': entry.get('subjects'),
                       'used_the_other_way': uses[pair[::-1]], 'rows': rows})
    kept.sort(key=lambda row: (row['from'], row['to']))
    almost.sort(key=lambda row: (not row['used_the_other_way'], (row['uses'] or 0) / max(row['of'] or 1, 1),
                                 row['from'], row['to']))
    summary = (f'suggest: {len(area)} component(s) in {len(set(area.values()))} area(s), '
               f'{len(facts["component_uses"])} use(s); {len(almost)} near miss(es), '
               f'{len(kept)} direction(s) the code keeps that layers.toml does not say')
    if form == 'json':
        print(json.dumps({'near_misses': almost, 'kept': kept, 'summary': summary}, indent=1))
        return 0
    if form == 'toml':
        print('# Directions the code keeps today (rules_check.py suggest). Keep the ones you mean.')
        for row in kept:
            print(f'\n[[forbid]]  # {row["to"]} uses {row["from"]} {row["used_the_other_way"]} time(s)\n'
                  f'from = "{row["from"]}"\nto = "{row["to"]}"')
        return 0
    for row in almost[:SHOWN]:
        first = row['rows'][0] if row['rows'] else None
        through = ''
        if first:
            through = f': {first["caller"]} -> {first["callee"]}' + ''.join(
                f' ({" -> ".join(pair)})' for pair in first['imports'][:1])
        back = (f'; {row["to"]} uses {row["from"]} {row["used_the_other_way"]} time(s), so this closes a loop'
                if row['used_the_other_way'] else '')
        print(f'almost: {row["from"]} uses {row["to"]} in {row["uses"]} of its {row["of"]} use(s){back}{through}')
    if len(almost) > SHOWN:
        print(f'… +{len(almost) - SHOWN} more near misses (--format json lists them all)')
    for source, group in itertools.groupby(kept, key=lambda row: row['from']):
        print(f'kept: {source} never uses ' + ', '.join(row['to'] for row in group) + ' (each uses it)')
    print(summary + ('; --format toml prints them as [[forbid]] lines' if kept else ''))
    return 0


def init(root: Path, show: bool) -> int:
    RULES, LAYERS = places(root)
    starters = {RULES: json.dumps(STARTER_RULES, indent=2) + '\n', LAYERS: STARTER_LAYERS}
    for name, text in starters.items():
        if show:
            print(f'# {name}\n{text}')
        elif (root / name).exists():
            print(f'{name} exists; left as it is')
        else:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text, encoding='utf-8')
            print(f'wrote {name}')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='the project (default: the current folder)')
    commands = parser.add_subparsers(dest='command', required=True)
    start = commands.add_parser('init')
    start.add_argument('--print', dest='show', action='store_true', help='print the starter files, write nothing')
    run_check = commands.add_parser('check')
    run_check.add_argument('--base', default='', help='report only what is new since the merge base with this branch')
    run_check.add_argument('--phase', default='', help='judge the plans of this phase by the rules about plans')
    run_check.add_argument('--strict', action='store_true', help='also fail on a warning')
    run_check.add_argument('--require', action='store_true', help='fail when GND is not installed')
    run_check.add_argument('--format', choices=('text', 'json'), default='text')
    try_examples = commands.add_parser('test')
    try_examples.add_argument('--require', action='store_true', help='fail when GND is not installed')
    try_examples.add_argument('--format', choices=('text', 'json'), default='text')
    find = commands.add_parser('suggest')
    find.add_argument('--require', action='store_true', help='fail when GND, or its guarded-join family, is missing')
    find.add_argument('--format', choices=('text', 'json', 'toml'), default='text')
    args = parser.parse_args(argv)
    if args.command == 'check' and args.phase and args.base:
        parser.error('--phase judges the plans as written: leave out --base')
    try:
        if args.command == 'init':
            return init(args.root, args.show)
        if args.command == 'test':
            return test(args.root, args.require, args.format == 'json')
        if args.command == 'suggest':
            return suggest(args.root, args.require, args.format)
        if args.phase:
            return check_phase(args.root, args.phase, args.strict, args.require, args.format == 'json')
        return check(args.root, args.base, args.strict, args.require, args.format == 'json')
    except Problem as exc:
        print(f'rules_check: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
