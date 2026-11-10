#!/usr/bin/env python3
"""Check the project's own rules about its components. Optional: it needs GND installed.

    rules_check.py init [--print]     write a starter rules file and layers.toml (never overwrites one)
    rules_check.py check [--base REF] [--strict] [--require] [--format json]

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

``rules.json`` and ``layers.toml`` live beside the catalog, in the index script's
``docs_dir``. Settings live beside this script, in rules_check.settings.json. Needs
Python 3.11 or newer, and GND 0.2.0 or newer (get-nick-done on PyPI), the first release
with the rule-check flags (``--rule-ids``, ``--baseline``, ``--allow-vacuous``: report
version 15).
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_SETTINGS = {
    'index_script': 'scripts/components_index.py',
    # The command that runs GND, for example "uvx --from get-nick-done==0.2.0 gnd".
    'gnd_command': 'gnd',
}
SHOWN = 10  # lines printed for one rule; --format json has them all
REPORT = 15  # the `gnd check --rule-ids` report: a rule's own id, its remedy, and new or standing
BANDS = {0, 1, 2, 4}  # exit codes of a check that ran: accepted, violated, vacuous rules, undecided
USES = ('component_uses', 'component_uses_in_cycle')
MODEL_ID = 'urn:devtools:component-rules@1'
GND_FROM = 'get-nick-done 0.2.0'  # the first release with the flags, and the one this script was tried with

STARTER_RULES = {'rules': [
    {'id': 'no_forbidden_area_use', 'level': 'must',
     'remedy': 'This area must not use that one (a [[forbid]] pair in layers.toml): move the import, '
               'or the module to the component it belongs to',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'component_uses', 'bind': {'caller': '$a', 'callee': '$b'}},
                    {'fact_type': 'component_in_area', 'bind': {'component': '$a', 'area': '$from'}},
                    {'fact_type': 'component_in_area', 'bind': {'component': '$b', 'area': '$to'}}],
     'consequent': {'absence': {'fact_type': 'area_must_not_use', 'bind': {'source': '$from', 'target': '$to'}}}},
    {'id': 'no_use_of_a_higher_rank', 'level': 'must',
     'remedy': 'A component uses one of a higher rank ([rank] in layers.toml): move what it needs down, '
               'or the caller up',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'component_uses', 'bind': {'caller': '$a', 'callee': '$b'}},
                    {'fact_type': 'component_in_area', 'bind': {'component': '$a', 'area': '$from'}},
                    {'fact_type': 'component_in_area', 'bind': {'component': '$b', 'area': '$to'}},
                    {'fact_type': 'area_has_rank', 'bind': {'area': '$from', 'rank': '$rank'}},
                    {'fact_type': 'area_has_rank', 'bind': {'area': '$to', 'rank': '$used'}}],
     'consequent': {'comparison': {'operator': '<=', 'left': '$used', 'right': '$rank'}}},
    {'id': 'no_import_inside_a_loop', 'level': 'should',
     'remedy': 'This import is part of a loop of imports between components: move the shared code '
               'into a component both can use',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'component_uses_in_cycle', 'bind': {'caller': '$a', 'callee': '$b'}}],
     'consequent': {'absence': {'fact_type': 'component_uses', 'bind': {'caller': '$a', 'callee': '$b'}}}},
    {'id': 'canonical_component_has_a_test', 'level': 'should',
     'remedy': 'A canonical component lists no test: add a tests: line to its entry, or write one',
     'type': 'guarded',
     'antecedent': [{'fact_type': 'component_has_status', 'bind': {'component': '$a', 'status': 'canonical'}}],
     'consequent': {'exists': {'atoms': [{'fact_type': 'component_has_test',
                                          'bind': {'component': '$a', 'path': '$test'}}]}}},
]}

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
        if name in seen:
            problems.append(f'{name}: id used twice')
        seen.add(name)
        if rule.get('level', 'must') not in {'must', 'should'}:
            problems.append(f'{name}: "level" is must or should')
        if not isinstance(rule.get('remedy', ''), str) or 'type' not in rule:
            problems.append(f'{name}: needs a "type", and "remedy" is text')
    if problems:
        raise Problem(f'{RULES}: ' + '; '.join(problems))
    return rules


def model(types: dict, rules: list[dict]) -> dict:
    """The GND model: fact types as the facts file describes them, and the project's rules."""
    constraints = []
    for rule in rules:
        body = {key: value for key, value in rule.items() if key != 'level' and (key != 'remedy' or value)}
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
        'constraints': constraints,
    }


def population(doc: dict) -> dict:
    header = {'covers': sorted(doc['facts']), 'model': 'model.json', 'model_id': MODEL_ID, 'source': 'tool-output',
              'producer': f'{Path(SETTINGS["index_script"]).name} facts @ {doc.get("revision") or "no revision"}'[:200]}
    return {'format_version': 2, 'facts': doc['facts'], 'population': header}


def run(command: list, what: str, **options) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(command, capture_output=True, text=True, **options)
    except OSError as exc:
        raise Problem(f'{what} could not start: {exc}')


def read_facts(root: Path, base: str = '') -> dict:
    script = root / SETTINGS['index_script']
    if not script.is_file():
        raise Problem(f'{SETTINGS["index_script"]} is missing (index_script in rules_check.settings.json)')
    done = run([sys.executable, str(script), '--root', str(root), 'facts', *(['--base', base] if base else [])],
               'the index script')
    if done.returncode:
        raise Problem(f'{SETTINGS["index_script"]} facts: {(done.stderr or done.stdout).strip()}')
    doc = json.loads(done.stdout)
    if doc.get('format') != 'devtools-facts/1':
        raise Problem(f'{SETTINGS["index_script"]} facts wrote format {doc.get("format")!r}; this script reads devtools-facts/1')
    return doc


def judge(gnd: list, folder: Path, head: dict, base: dict | None) -> dict:
    """The report of `gnd check` on the head facts, against the base facts when given."""
    for name, doc in (('head', head), ('base', base)):
        if doc is not None:
            (folder / f'{name}.pop.json').write_text(json.dumps(population(doc)), encoding='utf-8')
    command = [*gnd, 'check', str(folder / 'model.json'), str(folder / 'head.pop.json'), '--rule-ids',
               '--allow-vacuous', '--format', 'json']
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
    if report.get('schema_version') != REPORT:
        raise Problem(f'gnd wrote report version {report.get("schema_version")}; this script reads version {REPORT}')
    return report


def findings(report: dict, rules: list[dict]) -> tuple[list, list]:
    """What is broken, as (level, rule, binding, new), and the rules gnd could not decide, as (level, rule, why)."""
    by_id = {rule['id']: rule for rule in rules}
    broken, undecided, judged = [], [], set()
    try:
        for verdict in report['verdicts']:
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
    rules = load_rules(root)
    head = read_facts(root)
    notes, before, old = [], None, None
    if base:
        before = read_facts(root, base)
        if before['facts']['component_is_listed']:
            old = {(row['caller'], row['callee']): row['imports'] for row in before['evidence']['component_uses']}
        else:
            notes.append(f'no catalog at {before["revision"][:7]}: everything broken counts as new')
        notes.extend(f'rules changed in this change: {path}' for path in changed_rules(root, before['revision']))
    with tempfile.TemporaryDirectory() as name:
        folder = Path(name)
        (folder / 'model.json').write_text(json.dumps(model(head['types'], rules)), encoding='utf-8')
        report = judge(gnd, folder, head, before if old is not None else None)
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
        print(json.dumps({'rows': rows, 'notes': notes, 'summary': summary, 'baseline': report.get('baseline')}, indent=1))
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
    run_check.add_argument('--strict', action='store_true', help='also fail on a warning')
    run_check.add_argument('--require', action='store_true', help='fail when GND is not installed')
    run_check.add_argument('--format', choices=('text', 'json'), default='text')
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            return init(args.root, args.show)
        return check(args.root, args.base, args.strict, args.require, args.format == 'json')
    except Problem as exc:
        print(f'rules_check: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
