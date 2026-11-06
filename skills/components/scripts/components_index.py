#!/usr/bin/env python3
"""Generate and search the component catalog using source ASTs, never package imports.

    components_index.py init                 write a starter catalog (never overwrites one)
    components_index.py write                regenerate the index from the catalog and the source
                                             (the first run writes the starter catalog too)
    components_index.py --check              fail if the index is stale
    components_index.py --check --strict     also fail if a module has no component
    components_index.py search <words>       find components, modules and external names by capability
    components_index.py stats [--write-baseline]
    components_index.py draft [--only PATH] [--by-importers]
                                             stub entries for the modules no component covers
    components_index.py list [AREA]          the component ids by area, each with its one-line description
    components_index.py changed --base REF   check the index against the files changed since REF
    components_index.py review [AREA ...]    list leads for a review of the index (all of it, or ids starting with AREA)
    components_index.py show ID              one component: its entry, its modules, what they import and what imports them

The catalog is ``<docs_dir>/COMPONENTS.md``, written by hand: one entry per component,

    ### area.name
    - does: one sentence
    - verbs: comma-separated capability phrases people search for
    - status: canonical | experimental | deprecated | external | duplicate-of <id>
    - modules: comma-separated source files, or directories ending in /
    - tests: comma-separated test paths (optional)

``write`` adds the ``uses`` / ``used_by`` lines and the verbs list. ``<docs_dir>/external.toml``
is optional; it lists installed libraries to index (``[name]`` with ``modules = [...]``).
Modules listed in ``<docs_dir>/unassigned-baseline.txt`` (``stats --write-baseline``) are
tolerated by ``--check --strict``; the baseline can only shrink. ``changed`` and ``review``
read the git history of the checkout. Needs Python 3.11 or newer.

A source file is parsed once for each content it has had: what was read from it is kept
outside the checkout (``$XDG_CACHE_HOME/components-index/``, by default under ``~/.cache``)
and found again by a digest of the content. ``--no-cache`` before the command ignores it.
"""
from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import functools
import hashlib
import io
import json
import os
from importlib import metadata, util
import re
import subprocess
import sys
import time
import tokenize
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python older than 3.11
    sys.exit('components_index.py needs Python 3.11 or newer (this is %d.%d)' % sys.version_info[:2])

# Project settings live beside this script, in components_index.settings.json.
DEFAULT_SETTINGS = {
    'package_dir': 'src',
    'import_prefix': '',
    'extra_source_dirs': [],
    'docs_dir': 'docs/components',
    'script_path': 'scripts/components_index.py',
    # Which verbs the generated list at the top of the catalog holds: 'all', 'shared'
    # (only those two or more entries use) or 'none'. A large catalog wants 'shared'.
    'verb_list': 'all',
}


def load_settings(path: Path) -> dict:
    settings = dict(DEFAULT_SETTINGS)
    if path.is_file():
        loaded = json.loads(path.read_text(encoding='utf-8'))
        unknown = sorted(set(loaded) - set(DEFAULT_SETTINGS))
        if unknown:
            raise SystemExit(f'{path}: unknown setting(s): {", ".join(unknown)}')
        settings.update(loaded)
    if settings['verb_list'] not in {'all', 'shared', 'none'}:
        raise SystemExit(f'{path}: verb_list must be all, shared or none')
    return settings


SETTINGS = load_settings(Path(__file__).resolve().with_suffix('.settings.json'))
PACKAGE_DIR = SETTINGS['package_dir'].strip('/')
PACKAGE = SETTINGS['import_prefix'] or PACKAGE_DIR.rsplit('/', 1)[-1]
SOURCE_ROOT = PACKAGE_DIR[:len(PACKAGE_DIR) - len(PACKAGE)]
EXTRA_DIRS = tuple(SETTINGS['extra_source_dirs'])
LABEL = SETTINGS['script_path']
ROOT = Path(__file__).resolve().parents[len(Path(LABEL).parts) - 1]
BASE = SETTINGS['docs_dir'].strip('/') + '/'
VERBS = re.compile(r'<!-- verbs:begin -->.*?<!-- verbs:end -->', re.S)
GENERATED = frozenset({'uses', 'used_by', 'part_of', 'members_uses'})
# Fields the script reads. One of these written twice in an entry is an error (the first would be lost).
CHECKED = frozenset({'does', 'verbs', 'status', 'modules', 'tests', 'components', 'flow',
                     'duplicates', 'external', 'distinct_from'})
LARGE = 12  # `review` names a component that covers more modules than this
STOPWORDS = frozenset('a an the to of for and or in on from with into by is it its end'.split())


STARTER = """# Components

What this project can already do, by capability. Search it before writing new code:

```bash
python3 {label} search <what you need, in plain words>
```

Each entry is written by hand (`does`, `verbs`, `status`, `modules`, `tests`). The
`uses` / `used_by` lines and the verbs list are generated by `python3 {label} write`.

Add one entry per component below this line, in this form (without the indentation):

    ### area.name
    - does: One sentence saying what it is for
    - verbs: phrase people would search for, another phrase
    - status: canonical
    - modules: {package_dir}/<file>.py
    - tests: tests/<test file>.py
"""


def catalog(root: Path) -> Path:
    path = root / BASE / 'COMPONENTS.md'
    if not path.is_file():
        raise ValueError(f'{BASE}COMPONENTS.md is missing: run `python3 {LABEL} init` to create a starter catalog')
    return path


def external_config(root: Path) -> dict:
    """Libraries to index, from the optional external.toml."""
    path = root / BASE / 'external.toml'
    return tomllib.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}


def read_components(root: Path) -> list[dict]:
    """Read component headings and single-line fields, retaining duplicate ids."""
    return parse_components(catalog(root).read_text(encoding='utf-8'))


def parse_components(text: str) -> list[dict]:
    entries = []
    for match in re.finditer(r'^### ([^\n]+)\n(.*?)(?=^### |\Z)', text, re.M | re.S):
        pairs = re.findall(r'^- ([a-z_]+):[ \t]*(.*)$', match[2], re.M)
        entry = dict(pairs)
        keys = [key for key, _ in pairs]
        repeated = sorted({key for key in keys if keys.count(key) > 1} & CHECKED)
        if repeated:
            entry['_repeated'] = ', '.join(repeated)
        entry['id'] = match[1].strip()
        entries.append(entry)
    return entries


def values(entry: dict, key: str) -> list[str]:
    return [s.strip() for s in entry.get(key, '').split(',') if s.strip()]


@functools.lru_cache(maxsize=None)
def module_paths(modules: str) -> tuple[frozenset, tuple]:
    """A `modules:` value as (the files it names, the folders it names)."""
    names = [s.strip() for s in modules.split(',') if s.strip()]
    return frozenset(n for n in names if not n.endswith('/')), tuple(n for n in names if n.endswith('/'))


def covers(entry: dict, path: str) -> bool:
    files, folders = module_paths(entry.get('modules', ''))
    return not subsystem(entry) and (path in files or path.startswith(folders))


def sources(root: Path, directory: str):
    for path in sorted((root / directory).rglob('*.py')):
        parts = path.relative_to(root / directory).parts
        if not any(p in {'tests', 'fixtures', '__pycache__'} or p.startswith('fake_')
                   for p in parts):
            yield path


def coverage(root: Path, entries: list[dict]) -> tuple[list[str], int]:
    paths = [p.relative_to(root).as_posix() for p in sources(root, PACKAGE_DIR)]
    return [p for p in paths if not any(covers(e, p) for e in entries)], len(paths)


def validate(root: Path, entries: list[dict], external_names: set[str]) -> list[str]:
    errors, seen = [], set()
    ids = {e['id'] for e in entries}
    for entry in entries:
        name = entry['id']
        if name in seen:
            errors.append(f'{name}: duplicate id')
        seen.add(name)
        if not re.fullmatch(r'[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*', name):
            errors.append(f'{name}: invalid component id')
        required = ('does', 'verbs', 'status', 'components' if subsystem(entry) else 'modules')
        for key in required:
            if key not in entry or (not entry[key] and key != 'modules'):
                errors.append(f'{name}: missing {key}')
        for key in values(entry, '_repeated'):
            errors.append(f'{name}: {key} appears twice')
        for key in ('does', 'verbs'):
            if 'TODO' in entry.get(key, ''):
                errors.append(f'{name}: {key} is still a draft (TODO)')
        status = entry.get('status', '')
        if status.startswith('duplicate-of '):
            if status.removeprefix('duplicate-of ') not in ids:
                errors.append(f'{name}: unknown duplicate-of id')
        elif status not in {'canonical', 'experimental', 'deprecated', 'external'}:
            errors.append(f'{name}: invalid status {status}')
        if subsystem(entry):
            errors.extend(validate_subsystem(entry, entries))
        elif not entry.get('modules') and status != 'external':
            errors.append(f'{name}: modules may be empty only for external status')
        if status == 'external' and not entry.get('external'):
            errors.append(f'{name}: external status needs external names')
        for key in ('modules', 'duplicates', 'tests'):
            for path in values(entry, key):
                target = root / path
                if (Path(path).is_absolute() or '..' in Path(path).parts
                        or not target.exists() or (path.endswith('/') and not target.is_dir())):
                    errors.append(f'{name}: {key} path missing or invalid: {path}')
        for other in values(entry, 'distinct_from'):
            if other not in ids:
                errors.append(f'{name}: unknown distinct_from id: {other}')
        for dotted in values(entry, 'external'):
            if dotted not in external_names:
                errors.append(f'{name}: external name missing: {dotted}')
    return errors


def validate_subsystem(entry: dict, entries: list[dict]) -> list[str]:
    errors = []
    if 'modules' in entry:
        errors.append(f'{entry["id"]}: modules not allowed on subsystem')
    ids = {e['id'] for e in entries if not subsystem(e)}
    for key in ('components', 'flow'):
        members = values(entry, key) if key == 'components' else entry.get(key, '').split('->')
        for member in (m.strip() for m in members if m.strip()):
            if member not in ids:
                errors.append(f'{entry["id"]}: {key} requires existing component, not subsystem: {member}')
    return errors


def summary(node: ast.AST) -> str:
    doc = (ast.get_docstring(node) or '').strip() or '(no docstring)'  # a docstring of spaces is none
    return shorten(doc.splitlines()[0], 120)


def shorten(text: str, length: int) -> str:
    return text if len(text) <= length else text[:length - 1] + '…'


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> str:
    args = node.args
    parts = [a.arg for a in args.posonlyargs]
    if parts:
        parts.append('/')
    parts.extend(a.arg for a in args.args)
    if args.vararg:
        parts.append('*' + args.vararg.arg)
    elif args.kwonlyargs:
        parts.append('*')
    parts.extend(a.arg for a in args.kwonlyargs)
    if args.kwarg:
        parts.append('**' + args.kwarg.arg)
    result = f'{name}({", ".join(parts)})'
    if node.returns:
        result += ' -> ' + getattr(node, '_return_source', ast.unparse(node.returns))
    return shorten(result, 100)


def tool_kind(node: ast.AST) -> str:
    for dec in node.decorator_list:
        if isinstance(dec, ast.Call) and ast.unparse(dec.func).split('.')[-1] == 'tool':
            for kw in dec.keywords:
                if kw.arg == 'id' and isinstance(kw.value, ast.Constant):
                    return f' @tool {kw.value.value}'
    return ''


def symbols(tree: ast.AST, prefix: str = '', methods: bool = True):
    """Public definitions in source order; never descend into function bodies."""
    for node in tree.body:
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith('_'):
            continue
        name = prefix + node.name
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases if ast.unparse(b) != 'object']
            kind = 'class' + (f'({", ".join(bases)})' if bases else '')
            label = name
        else:
            kind = 'method' if prefix else ('async function' if isinstance(node, ast.AsyncFunctionDef) else 'function')
            label = signature(node, name)
        yield {'id': name, 'label': label, 'kind': kind + tool_kind(node),
               'line': node.lineno, 'summary': summary(node)}
        if isinstance(node, ast.ClassDef) and methods:
            yield from symbols(node, name + '.')


def parse(path: Path) -> ast.Module:
    return parse_source(path.read_bytes(), str(path))


def parse_source(data: bytes, name: str) -> ast.Module:
    encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
    source = io.TextIOWrapper(io.BytesIO(data), encoding, line_buffering=True).read()  # as tokenize.open reads it
    tree = ast.parse(source, filename=name)
    lines = source.encode('utf-8').splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
            annotation = node.returns
            span = lines[annotation.lineno - 1:annotation.end_lineno]
            span[-1] = span[-1][:annotation.end_col_offset]
            span[0] = span[0][annotation.col_offset:]
            node._return_source = b''.join(span).decode('utf-8')
    return tree


def cell(text: str) -> str:
    return text.replace('|', r'\|').replace('\n', ' ')


def table(rows: list[dict]) -> list[str]:
    lines = ['| Symbol | Kind | Line | Summary |', '| --- | --- | --- | --- |']
    for row in rows:
        lines.append(f'| `{cell(row["label"])}` | {cell(row["kind"])} | {row["line"]} | {cell(row["summary"])} |')
    return lines


def module_inventory(root: Path, entries: list[dict], cache: bool = False) -> tuple[dict, list[dict]]:
    """The generated module pages and one search hit per module.

    With ``cache`` (only `search` asks for it) a file whose size and time are unchanged
    is not read again, and the words of its hit are kept for the next search.
    """
    groups, hits = {}, []
    state = cache_state(root)
    for directory in (PACKAGE_DIR, *EXTRA_DIRS):
        for path in sources(root, directory):
            relative = path.relative_to(root).as_posix()
            parts = path.relative_to(root / directory).parts
            group = (parts[0] if len(parts) > 1 else '_root') if directory == PACKAGE_DIR else directory
            dotted = relative.removesuffix('.py').removeprefix(SOURCE_ROOT).replace('/', '.')
            about, _, rows, _ = file_facts(root, relative, cache)
            owners = ', '.join(e['id'] for e in entries if covers(e, relative)) or 'unassigned'
            lines = groups.setdefault(group, [f'# {group} symbol inventory', '', f'Generated by `{LABEL}`.', ''])
            lines.extend([f'## {dotted} — `{relative}`', f'Components: {owners}', about, '', *table(rows), ''])
            text = ' '.join([dotted, about, *(r['label'] + ' ' + r['summary'] for r in rows)])
            hits.append({'kind': 'module', 'id': relative, 'summary': about, 'text': text})
            if cache:  # the words of the text are saved too, so a search does not split it again
                row = state['files'][relative]
                if not row[3]:
                    row[3], state['dirty'] = sorted(tokens(text)), True
                SPLIT[text] = row[3]
    return {BASE + f'modules/{k}.md': '\n'.join(v) for k, v in sorted(groups.items())}, hits


FACTS: dict[str, list] = {}   # content digest -> [summary, has a docstring, symbol rows, imports]
STATE: dict[Path, dict] = {}  # checkout -> what this run knows of its files (see cache_state)
CACHE = {'on': True}          # off under --no-cache: nothing saved by an earlier run is read, nothing is saved
SPLIT: dict[str, list[str]] = {}  # text -> its words, for the texts a cached inventory has already split


def file_facts(root: Path, relative: str, trust: bool = False) -> list:
    """[summary, has a docstring, symbol rows, imports] of one source file. Do not change the result.

    The file is parsed only when no run has seen this content before: what is kept is found
    by a digest of the content, so a kept answer is the answer a parse would give. With
    ``trust`` (only `search` asks for it) an unchanged size and time are enough to skip
    reading the file.
    """
    state = cache_state(root)
    row = state['files'].get(relative)
    state['read'].add(relative)
    if trust and relative in state['trusted'] and row[2] in FACTS:
        stat = (root / relative).stat()
        if row[:2] == [stat.st_mtime_ns, stat.st_size]:
            return FACTS[row[2]]
    with open(root / relative, 'rb') as stream:
        stat = os.fstat(stream.fileno())
        data = stream.read()
    key = hashlib.blake2b(data, digest_size=16).hexdigest()
    if key not in FACTS:
        tree = parse_source(data, str(root / relative))
        FACTS[key] = [summary(tree), bool(ast.get_docstring(tree)), list(symbols(tree)), raw_imports(tree)]
    fresh = [stat.st_mtime_ns, stat.st_size, key]
    if not row or row[:3] != fresh:
        state['files'][relative] = fresh + [row[3] if row and row[2] == key else None]
        state['trusted'].discard(relative)  # a size and time seen in this run are not old enough to trust
        state['dirty'] = True
    return FACTS[key]


def top_level(rows: list[dict]) -> list[dict]:
    """The symbol rows without the methods: what `symbols(tree, methods=False)` gives."""
    return [row for row in rows if '.' not in row['id']]


def cache_path(root: Path) -> Path:
    """Where the facts read from the source files are kept: outside the checkout, one file per checkout."""
    home = Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache')
    return home / 'components-index' / (hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:16] + '.json')


def cache_stamp() -> list:
    """What the kept facts depend on besides the content of a file."""
    script = Path(__file__).stat()
    return [5, script.st_mtime_ns, script.st_size, SETTINGS, list(sys.version_info[:2])]


def cache_state(root: Path) -> dict:
    """What earlier runs kept for this checkout, read once per run.

    `files` maps a path to [time, size, content digest, search words]; `trusted` holds the
    paths whose size and time are safe to compare; `read` the paths this run asked for.
    """
    state = STATE.get(root)
    if state is None:
        state = STATE[root] = {'files': {}, 'trusted': set(), 'read': set(), 'dirty': False}
        try:
            saved = json.loads(cache_path(root).read_text(encoding='utf-8')) if CACHE['on'] else {}
            if saved.get('stamp') == cache_stamp():
                # A file changed in the same instant the cache was written could keep its size and time.
                trusted = {k for k, v in saved['files'].items() if v[0] < saved['written'] - 2_000_000_000}
                FACTS.update(saved['facts'])
                state.update(files=saved['files'], trusted=trusted)
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError):
            pass  # a cache that cannot be read only costs time
    return state


def save_caches() -> None:
    for root, state in STATE.items():
        if state['dirty'] and CACHE['on']:
            write_cache(root, state)
            state['dirty'] = False


def write_cache(root: Path, state: dict) -> None:
    path = cache_path(root)
    try:
        # A file that is gone leaves the cache; one this run did not ask for (a test file, on a search) stays.
        files = {k: v for k, v in state['files'].items() if k in state['read'] or (root / k).is_file()}
        facts = {v[2]: FACTS[v[2]] for v in files.values() if v[2] in FACTS}
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f'.{os.getpid()}.tmp')
        temporary.write_text(json.dumps({'stamp': cache_stamp(), 'written': time.time_ns(),
                                         'files': files, 'facts': facts}), encoding='utf-8')
        os.replace(temporary, path)
        for other in path.parent.glob('*.json'):  # checkouts that are gone leave a file behind
            if time.time() - other.stat().st_mtime > 30 * 86400:
                other.unlink()
    except OSError:
        pass  # a cache that cannot be written only costs time


def external_source(dist, dotted: str) -> Path:
    """Locate metadata-owned source first, or probe only the top-level package spec."""
    relative = dotted.replace('.', '/')
    candidates = (relative + '.py', relative + '/__init__.py')
    files = {str(p): p for p in (dist.files or [])}
    for name in candidates:
        if name in files:
            path = Path(dist.locate_file(files[name]))
            if not path.is_file():
                raise ValueError(f'{dotted}: listed external module source missing: {path}')
            return path
    top, *rest = dotted.split('.')
    spec = util.find_spec(top)  # Dotted find_spec would import parent packages.
    if spec and spec.origin:
        base = Path(spec.origin).parent
        target = base.joinpath(*rest)
        for path in (target.with_suffix('.py'), target / '__init__.py'):
            if path.is_file():
                return path
    raise ValueError(f'{dotted}: listed external module source missing')


def external_inventory(root: Path) -> tuple[dict, list[dict], dict, list[str]]:
    config = external_config(root)
    files, hits, versions, errors = {}, [], {}, []
    skipped = external_skips(root)
    recorded, _ = recorded_external(root)
    for name, settings in sorted(config.items()):
        path = BASE + f'external/{name}.md'
        if path in skipped:
            files[path] = (root / path).read_text(encoding='utf-8')
            hits.extend(h for h in recorded if h['id'].startswith(tuple(m + '.' for m in settings['modules'])))
            continue
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            errors.append(f'{name}: distribution not installed')
            continue
        versions[name] = dist.version
        lines = [f'# {name} external capabilities', '', f'Version: {dist.version}', '', f'Generated by `{LABEL}`.', '']
        for dotted in sorted(settings['modules']):
            try:
                tree = parse(external_source(dist, dotted))
            except (OSError, ValueError, SyntaxError) as exc:
                errors.append(f'{dotted}: {exc}')
                continue
            rows = list(symbols(tree, methods=False))
            for row in rows:
                full = dotted + '.' + row['id']
                row['label'] = dotted + '.' + row['label']
                hits.append({'kind': 'external', 'id': full, 'summary': row['summary'],
                             'text': full + ' ' + row['summary']})
            lines.extend([f'## {dotted}', summary(tree), '', *table(rows), ''])
        files[BASE + f'external/{name}.md'] = '\n'.join(lines)
    return files, hits, versions, errors


def verb_block(entries: list[dict]) -> str:
    verbs = {}
    for entry in entries:
        for verb in values(entry, 'verbs'):
            verbs.setdefault(verb.lower(), set()).add(entry['id'])
    least = {'all': 1, 'shared': 2, 'none': len(entries) + 1}[SETTINGS['verb_list']]
    lines = ['<!-- verbs:begin -->', '## Verbs', '']
    lines.extend(f'- {verb}: {", ".join(sorted(ids))}' for verb, ids in sorted(verbs.items()) if len(ids) >= least)
    return '\n'.join([*lines, '<!-- verbs:end -->'])


def subsystem(entry: dict) -> bool:
    return entry['id'].startswith('subsystem.')


def import_nodes(tree: ast.AST):
    """Walk runtime imports, excluding TYPE_CHECKING bodies but retaining else arms."""
    if isinstance(tree, ast.If) and ast.unparse(tree.test) in {'TYPE_CHECKING', 'typing.TYPE_CHECKING'}:
        for child in tree.orelse:
            yield from import_nodes(child)
        return
    if isinstance(tree, (ast.Import, ast.ImportFrom)):
        yield tree
    for child in ast.iter_child_nodes(tree):
        yield from import_nodes(child)


def raw_imports(tree: ast.AST) -> list:
    """The runtime imports of a module as [level, module, names]; level -1 is a plain `import`."""
    return [[-1, '', [alias.name for alias in node.names]] if isinstance(node, ast.Import)
            else [node.level, node.module or '', [alias.name for alias in node.names]]
            for node in import_nodes(tree)]


@functools.lru_cache(maxsize=None)
def text_imports(text: str, name: str) -> list:
    """The imports of source that is not a file here (a file as it was at another commit)."""
    return raw_imports(ast.parse(text, filename=name))


def resolve_imports(tree: ast.AST | list, path: str, available: set[str]) -> set[str]:
    """Resolve only the project's own modules; from-import symbols fall back to their base.

    `tree` is a module, or the rows `raw_imports` made of one.
    """
    def resolve(dotted):
        if dotted != PACKAGE and not dotted.startswith(PACKAGE + '.'):
            return None
        stem = SOURCE_ROOT + dotted.replace('.', '/')
        return next((p for p in (stem + '.py', stem + '/__init__.py') if p in available), None)

    package = path.removeprefix(SOURCE_ROOT).split('/')[:-1]
    imported = set()
    for level, base, names in tree if isinstance(tree, list) else raw_imports(tree):
        if level < 0:
            targets = [resolve(name) for name in names]
        else:
            if level:
                if not path.startswith(PACKAGE_DIR + '/') or level > len(package):
                    continue
                base = '.'.join(package[:len(package) - level + 1] + ([base] if base else []))
            targets = [resolve(base + '.' + name) or resolve(base) for name in names]
        imported.update(p for p in targets if p)
    return imported


def component_graph(root: Path, entries: list[dict], overrides=None) -> dict:
    """Map component pairs to sorted module evidence, optionally at a base revision."""
    overrides = overrides or {}
    paths = {p.relative_to(root).as_posix() for p in (root / PACKAGE_DIR).rglob('*.py')}
    for entry in entries:
        for name in values(entry, 'modules') if not subsystem(entry) else []:
            if Path(name).is_absolute() or '..' in Path(name).parts:
                continue
            target = root / name
            members = target.rglob('*.py') if target.is_dir() else [target]
            paths.update(p.relative_to(root).as_posix() for p in members if p.suffix == '.py' and p.is_file())
    paths.update(overrides)
    paths = {p for p in paths if overrides.get(p, '') is not None}
    owners = {p: {e['id'] for e in entries if covers(e, p)} for p in paths}
    edges = {}
    for path in sorted(paths):
        if not owners[path]:
            continue
        rows = text_imports(overrides[path], path) if path in overrides else file_facts(root, path)[3]
        for target in sorted(resolve_imports(rows, path, paths)):
            for caller in sorted(owners[path] - owners[target]):
                for callee in sorted(owners[target]):
                    edges.setdefault((caller, callee), []).append((path, target))
    return {edge: sorted(set(pairs)) for edge, pairs in sorted(edges.items())}


def relations(entries: list[dict], edges: dict) -> dict:
    result = {e['id']: {'uses': set(), 'used_by': set(), 'part_of': set()} for e in entries}
    for caller, callee in edges:
        result[caller]['uses'].add(callee)
        result[callee]['used_by'].add(caller)
    for entry in entries:
        if not subsystem(entry):
            continue
        members = set(values(entry, 'components')) & result.keys()
        result[entry['id']]['members_uses'] = set().union(*(result[m]['uses'] for m in members)) - members
        for member in members:
            result[member]['part_of'].add(entry['id'])
    return result


def listing(ids, cap=None) -> str:
    names = sorted(ids)
    if cap and len(names) > cap:
        names = names[:cap] + [f'… +{len(names) - cap} more (graph.md)']
    return ', '.join(names) or '(none)'


def rewrite(text: str, entries: list[dict], edges: dict) -> str:
    """Replace only generated fields, preserving the authored catalog content."""
    links = relations(entries, edges)
    by_id = {e['id']: e for e in entries}

    def section(match):
        name, body = match[1].strip(), match[2]
        body = re.sub(r'^- (?:uses|used_by|part_of|members_uses):[^\n]*\n?', '', body, flags=re.M)
        data = links[name]
        if subsystem(by_id[name]):
            line = '- members_uses: ' + listing(data['members_uses'], 12) + '\n'
            body = re.sub(r'(^- components:[^\n]*)(?:\n|$)', lambda m: m[1] + '\n' + line, body, flags=re.M)
        else:
            lines = f'- uses: {listing(data["uses"])}\n- used_by: {listing(data["used_by"], 12)}\n'
            if data['part_of']:
                lines += '- part_of: ' + listing(data['part_of']) + '\n'
            body = re.sub(r'(^- modules:[^\n]*)(?:\n|$)', lambda m: m[1] + '\n' + lines, body, flags=re.M)
        return '### ' + match[1] + '\n' + body

    return re.sub(r'^### ([^\n]+)\n(.*?)(?=^### |\Z)', section, text, flags=re.M | re.S)


def graph_text(entries: list[dict], edges: dict) -> str:
    links = relations(entries, edges)
    lines = ['# Component import graph', '', f'Generated by `{LABEL}`.', '']
    for entry in sorted(entries, key=lambda e: e['id']):
        name = entry['id']
        lines.extend(['### ' + name])
        if subsystem(entry):
            lines.extend(['- members_uses: ' + listing(links[name]['members_uses']), ''])
            continue
        lines.extend(['- uses: ' + listing(links[name]['uses']),
                      '- used_by: ' + listing(links[name]['used_by']), ''])
        for callee in sorted(links[name]['uses']):
            lines.append(f'#### {name} -> {callee}')
            lines.extend(f'- `{source} -> {target}`' for source, target in edges[name, callee][:3])
            lines.append('')
    return '\n'.join(lines)


def components_text(root: Path, entries: list[dict], edges: dict | None = None) -> str:
    text = catalog(root).read_text(encoding='utf-8')
    text = rewrite(text, entries, component_graph(root, entries) if edges is None else edges)
    block = verb_block(entries)
    if VERBS.search(text):
        return VERBS.sub(lambda _: block, text)
    match = re.search(r'^### ', text, re.M)
    offset = match.start() if match else len(text)
    return text[:offset].rstrip() + '\n\n' + block + '\n\n' + text[offset:]


def build_index(root: Path) -> tuple[dict[str, str], list[str]]:
    entries = read_components(root)
    external, hits, _, errors = external_inventory(root)
    errors.extend(validate(root, entries, {h['id'] for h in hits}))
    modules, _ = module_inventory(root, entries)
    edges = component_graph(root, entries)
    return {**modules, **external, BASE + 'COMPONENTS.md': components_text(root, entries, edges),
            BASE + 'graph.md': graph_text(entries, edges)}, errors


def tokens(text: str) -> set[str]:
    def stem(word):
        if len(word) > 4 and word.endswith('ies'):
            return word[:-3] + 'y'
        return word[:-1] if len(word) > 3 and word.endswith('s') else word
    return {stem(word) for word in re.findall(r'[a-z0-9]+', text.lower()) if word not in STOPWORDS}


def recorded_external(root: Path) -> tuple[list[dict], dict[str, str]]:
    """Search the recorded catalog even without the dependency installed."""
    hits, versions = [], {}
    for path in sorted((root / BASE / 'external').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        version = re.search(r'^Version: (.+)$', text, re.M)
        if version:
            versions[path.stem] = version[1]
        for line in text.splitlines():
            if not line.startswith('| `'):
                continue
            columns = [v.strip() for v in re.split(r'(?<!\\)\|', line)[1:-1]]
            if len(columns) != 4:
                continue
            name = columns[0].strip('`').split('(', 1)[0]
            description = columns[3].replace(r'\|', '|')
            hits.append({'kind': 'external', 'id': name, 'summary': description,
                         'text': name + ' ' + description})
    return hits, versions


def search(root: Path, query: str, limit: int | None = 5, *,
           entries=None, modules=None, external=None, cache: bool = True) -> list[dict]:
    entries = read_components(root) if entries is None else entries
    external = recorded_external(root)[0] if external is None else external
    modules = module_inventory(root, entries, cache)[1] if modules is None else modules
    external = [dict(hit) for hit in external]
    hits = [{'kind': 'subsystem' if subsystem(e) else 'component', 'retired': is_retired(e),
             'id': e['id'] + (f' ({e["status"]})' if is_retired(e) else ''),
             'summary': e.get('does', ''), 'flow': e.get('flow', ''),
             'text': ' '.join(e.get(k, '') for k in ('id', 'does', 'verbs'))} for e in entries]
    # Component context also makes dependency names discoverable by capability vocabulary.
    for hit in external:
        hit['text'] += ' ' + ' '.join(e.get('does', '') + ' ' + e.get('verbs', '')
                                     for e in entries if hit['id'] in values(e, 'external'))
    words = tokens(query)
    ranked = []
    for hit in hits + external + modules:
        hit['matched'] = sorted(words.intersection(SPLIT.get(hit['text']) or tokens(hit['text'])))
        overlap = len(hit['matched'])
        if overlap:
            ranked.append((overlap, hit))
    order = {'subsystem': 0, 'component': 1, 'external': 2, 'module': 3}
    # On a tie a retired component comes after the others: the first hit is the one to call.
    ranked.sort(key=lambda pair: (-pair[0], order[pair[1]['kind']], pair[1].get('retired', False), pair[1]['id']))
    return [h for _, h in ranked[:None if limit is None else max(0, limit)]]


def coverage_line(root: Path, entries: list[dict]) -> str:
    unassigned, total = coverage(root, entries)
    _, versions = recorded_external(root)
    external = ', '.join(f'{k} {v}' for k, v in versions.items()) or 'none'
    return f'coverage: {total - len(unassigned)}/{total} {PACKAGE_DIR} modules assigned to components; external: {external}'


def generated_paths(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for folder in ('modules', 'external')
            for p in (root / BASE / folder).glob('*.md')}


def external_skips(root: Path) -> dict[str, str]:
    """Explain recorded inventories that cannot be reproduced by this installation."""
    config = external_config(root)
    _, versions = recorded_external(root)
    skipped = {}
    for name in sorted(config.keys() & versions.keys()):
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            installed = None
        if installed != versions[name]:
            relative = f'external/{name}.md'
            skipped[BASE + relative] = (
                f'skipped {relative}: installed {installed or "none"} != recorded {versions[name]}')
    return skipped


def stale_files(root: Path, files: dict[str, str] | None = None) -> list[str]:
    """Return sorted stale or missing index paths without writing or printing."""
    if files is None:
        files, _ = build_index(root)
    stale = generated_paths(root) - files.keys()
    different = [name for name, text in files.items()
                 if not (root / name).is_file() or (root / name).read_bytes() != text.encode('utf-8')]
    return sorted((set(different) | stale) - external_skips(root).keys())


def write_or_check(root: Path, check: bool, strict: bool = False) -> int:
    files, errors = build_index(root)
    for message in external_skips(root).values():
        print(message)
    if check:
        stale = stale_files(root, files)
        for name in stale:
            print(f'stale or missing: {name}')
        for error in errors:
            print(error)
        baseline = root / BASE / 'unassigned-baseline.txt'
        tolerated = set(baseline.read_text(encoding='utf-8').split()) if baseline.is_file() else set()
        unassigned = [p for p in coverage(root, read_components(root))[0] if p not in tolerated] if strict else []
        for path in unassigned:
            print(f'no component: {path} (add it to the modules of an entry in {BASE}COMPONENTS.md)')
        return int(bool(stale or errors or unassigned))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    for name, text in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode('utf-8'))
    for name in generated_paths(root) - files.keys():
        (root / name).unlink()
    return 0


def git(root: Path, *args: str, check: bool = True) -> str:
    """Output of a git command run in `root`; '' when it fails and `check` is off."""
    try:
        done = subprocess.run(['git', '-C', str(root), '-c', 'core.quotepath=off', *args],
                              capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f'git is not available: {exc}')
    if done.returncode and check:
        raise ValueError(f'git {" ".join(args)}: {done.stderr.strip() or "failed"}')
    return '' if done.returncode else done.stdout


def files_at(root: Path, commit: str, paths: list[str]) -> dict[str, str]:
    """The text each path (relative to `root`) had at a commit, read with one git process."""
    if not paths:
        return {}
    prefix = git(root, 'rev-parse', '--show-prefix').strip()
    try:
        done = subprocess.run(['git', '-C', str(root), 'cat-file', '--batch'], capture_output=True,
                              input=''.join(f'{commit}:{prefix}{p}\n' for p in paths).encode('utf-8'))
    except OSError as exc:
        raise ValueError(f'git is not available: {exc}')
    out, at, texts = done.stdout, 0, {}
    for path in paths:
        end = out.find(b'\n', at)
        head = out[at:end].split()
        if done.returncode or end < 0 or len(head) != 3 or head[1] != b'blob':
            raise ValueError(f'git cannot read {path} at {commit[:7]}: {done.stderr.decode(errors="replace").strip()}')
        size = int(head[2])
        texts[path] = out[end + 1:end + 1 + size].decode('utf-8', errors='replace')
        at = end + size + 2
    return texts


def package_imports(root: Path) -> dict[str, set[str]]:
    """Each package module -> the package modules it imports at run time."""
    available = {p.relative_to(root).as_posix() for p in sources(root, PACKAGE_DIR)}
    return {p: resolve_imports(file_facts(root, p)[3], p, available) for p in sorted(available)}


def draft(root: Path, entries: list[dict], only: str = '', by_importers: bool = False) -> list[str]:
    """Stub entries for the modules no component covers: a starting point, never a catalog."""
    unassigned = [p for p in coverage(root, entries)[0] if p.startswith(only)]
    imports = package_imports(root)
    importers = {}
    for path, targets in imports.items():
        for target in targets:
            importers.setdefault(target, set()).add(path)
    if by_importers:
        unassigned.sort(key=lambda p: (-len(importers.get(p, ())), p))
    folder = root / 'tests'
    tests = {}
    for path in sorted(folder.rglob('test_*.py')) if folder.is_dir() else []:
        tests.setdefault(path.name, path.relative_to(root).as_posix())
    testers = outside_importers(root, sorted(imports))
    lines = [f'# Draft entries for {len(unassigned)} module(s) that no component covers.',
             '# One stub per module. Merge the stubs that are one capability (a path ending in /',
             '# covers a whole folder), rewrite every TODO after reading the code, drop the',
             f'# indented lines, then add the entries to {BASE}COMPONENTS.md.']
    taken = {e['id'] for e in entries}
    for path in unassigned:
        tree = parse(root / path)
        parts = [p for p in Path(path).relative_to(PACKAGE_DIR).with_suffix('').parts if p != '__init__']
        words = [re.sub(r'[^a-z0-9_]', '_', p.lower()).strip('_') or 'x' for p in parts]
        area = words[0] if len(words) > 1 else PACKAGE.lower()
        name = '_'.join(words[1:] if len(words) > 1 else words) or 'package'
        ident = '.'.join(w if w[0].isalpha() else 'x' + w for w in (area, name))
        while ident in taken:
            ident += '_2'
        taken.add(ident)
        names = [row['label'] for row in symbols(tree, methods=False)]
        private = [n.name for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                   and n.name.startswith('_')]
        if names:
            shown = '; '.join(names[:8]) + (f'; +{len(names) - 8} more' if len(names) > 8 else '')
        elif private:
            shown = f'(none public; {len(private)} private: {some(private, 6)})'
        elif imports.get(path):
            shown = '(defines nothing: it re-exports, or only imports)'
        else:
            shown = '(none)'
        lines.extend(['', f'### {ident}', f'- does: TODO {summary(tree)}', '- verbs: TODO',
                      '- status: canonical', f'- modules: {path}'])
        test = tests.get('test_' + Path(path).name)
        if test:
            lines.append(f'- tests: {test}')
        users = sorted(importers.get(path, ()))
        outside = testers.get(path, [])
        lines.append(f'  symbols: {shown}')
        lines.append(f'  imports: {", ".join(sorted(imports.get(path, ()))) or "(nothing in the package)"}')
        lines.append(f'  imported by ({len(users)}): {some(users, 8) or "nothing in the package"}')
        lines.append(f'  imported from tests and scripts ({len(outside)}): {some(outside, 3) or "none"}')
    return lines


def changed(root: Path, base: str, strict: bool) -> int:
    """Check the index against the files that differ from the merge base with `base`."""
    def exists(ref):
        return bool(git(root, 'rev-parse', '--verify', '--quiet', ref + '^{commit}', check=False).strip())

    if not exists(base):
        if not exists('origin/' + base):
            raise ValueError(f'no branch or commit named {base}: pass --base <the branch this change will merge into>')
        base = 'origin/' + base
    anchor = git(root, 'merge-base', base, 'HEAD').strip()
    status = {}
    for line in git(root, 'diff', '--name-status', '--no-renames', '--relative', anchor).splitlines():
        code, path = line.split('\t', 1)
        status[path] = code
    for path in git(root, 'ls-files', '--others', '--exclude-standard').splitlines():
        status.setdefault(path, 'A')
    entries = read_components(root)
    files, fails = build_index(root)
    fails = list(fails)
    fails.extend(f'stale or missing: {name} (run `python3 {LABEL} write`)' for name in stale_files(root, files))
    package = {p.relative_to(root).as_posix() for p in sources(root, PACKAGE_DIR)}
    for path in sorted(status):
        if status[path] == 'A' and path in package and not any(covers(e, path) for e in entries):
            fails.append(f'no component: {path} (new file; add it to the modules of an entry in {BASE}COMPONENTS.md)')

    old_entries = parse_components(git(root, 'show', f'{anchor}:./{BASE}COMPONENTS.md', check=False))
    overrides = {p: None for p, code in status.items() if p.endswith('.py')}
    overrides.update(files_at(root, anchor, [p for p in overrides if status[p] != 'A']))
    old_edges = component_graph(root, old_entries, overrides)
    retired = {e['id']: e['status'] for e in entries
               if e.get('status') == 'deprecated' or e.get('status', '').startswith('duplicate-of ')}
    known = {e['id'] for e in old_entries}  # a component first described in this change has no "before"
    existed = {p.relative_to(root).as_posix() for p in (root / PACKAGE_DIR).rglob('*.py')}
    existed |= {p for p, text in overrides.items() if text is not None}

    def imported_before(path, target):
        """Whether the file already imported the target at the base (so a regrouping of entries is not news)."""
        if path not in status:
            return True
        text = overrides.get(path)
        return bool(text) and target in resolve_imports(text_imports(text, path), path, existed)

    warns = []
    for (caller, callee), pairs in component_graph(root, entries).items():
        added = sorted(pair for pair in set(pairs) - set(old_edges.get((caller, callee), []))
                       if not imported_before(*pair))
        if callee in retired and callee in known and added:
            evidence = ', '.join(f'{a} -> {b}' for a, b in added[:3])
            warns.append(f'new caller of {callee} ({retired[callee]}): {caller}: {evidence}')

    def authored(entry):
        return {k: v for k, v in entry.items() if k not in GENERATED}

    before = {e['id']: authored(e) for e in old_entries}
    touched = {e['id']: sorted(p for p in status if covers(e, p)) for e in entries if not subsystem(e)}
    rereads = []
    for entry in entries:
        name = entry['id']
        if before.get(name) != authored(entry):
            continue  # written or edited in this change
        if subsystem(entry):
            members = [m for m in values(entry, 'components') if touched.get(m)]
            if members:
                rereads.append(f'{name} (entry not edited): its members changed: {", ".join(members)}')
        elif touched[name]:
            paths = touched[name]
            more = f', +{len(paths) - 5} more' if len(paths) > 5 else ''
            rereads.append(f'{name} (entry not edited): {", ".join(paths[:5])}{more}')

    for prefix, rows in (('fail', fails), ('warn', warns), ('reread', rereads)):
        for row in rows:
            print(f'{prefix}: {row}')
    print(f'changed against {base} ({anchor[:7]}): {len(status)} file(s) differ; '
          f'{len(fails)} to fix, {len(warns)} warning(s), {len(rereads)} to reread')
    return int(bool(fails or (strict and warns)))


def entry_commits(root: Path) -> dict[str, tuple[str, int]]:
    """Component id -> (commit, time) of the newest line of its description (does, verbs, flow)."""
    blame = git(root, 'blame', '--line-porcelain', '--', BASE + 'COMPONENTS.md', check=False)
    newest, commit, stamp, current = {}, '', 0, None
    for line in blame.splitlines():
        head = re.fullmatch(r'([0-9a-f]{40}) \d+ \d+(?: \d+)?', line)
        if head:
            commit = head[1]
        elif line.startswith('committer-time '):
            stamp = int(line.split()[1])
        elif line.startswith('\t'):
            text = line[1:]
            if text.startswith('### '):
                current = text[4:].strip()
            field = re.match(r'- ([a-z_]+):', text)
            if not current or not (field and field[1] in {'does', 'verbs', 'flow'}):
                continue
            if set(commit) == {'0'}:  # not committed yet: the entry counts as edited now
                newest[current] = ('', float('inf'))
            elif stamp > newest.get(current, ('', -1))[1]:
                newest[current] = (commit, stamp)
    return newest


def is_retired(entry: dict) -> bool:
    return entry.get('status') == 'deprecated' or entry.get('status', '').startswith('duplicate-of ')


def outside_importers(root: Path, package: list[str]) -> dict[str, list[str]]:
    """Package module -> the files in tests/ and the extra source directories that import it."""
    available, found = set(package), {}
    for folder in dict.fromkeys(('tests', *EXTRA_DIRS)):
        base = root / folder
        for path in sorted(base.rglob('*.py')) if base.is_dir() else []:
            relative = path.relative_to(root).as_posix()
            if relative in available:
                continue
            try:
                targets = resolve_imports(file_facts(root, relative)[3], relative, available)
            except (SyntaxError, UnicodeDecodeError):
                continue
            for target in targets:
                found.setdefault(target, []).append(relative)
    return found


def some(items, cap: int) -> str:
    items = list(items)
    return ', '.join(items[:cap]) + (f', +{len(items) - cap} more' if len(items) > cap else '')


def review(root: Path, areas: tuple = (), everything: bool = False) -> list[str]:
    """Leads for a review of the index. Each one is a place to look, not a finding.

    Every group is a list of (component ids, text); `areas` keeps the leads that name a
    component whose id starts with one of them.
    """
    entries = read_components(root)
    components = [e for e in entries if not subsystem(e)]
    edges = component_graph(root, entries)
    links = relations(entries, edges)
    package = [p.relative_to(root).as_posix() for p in sources(root, PACKAGE_DIR)]
    owners = {p: sorted(e['id'] for e in components if covers(e, p)) for p in package}
    groups = []

    stale, dated, asked = [], entry_commits(root), []
    for name, (commit, stamp) in dated.items():
        entry = next((e for e in components if e['id'] == name), None)
        paths = [p for p in values(entry, 'modules') if (root / p).exists()] if entry else []
        if commit and paths:
            asked.append((name, commit, stamp, paths))
    with ThreadPoolExecutor(8) as pool:  # one git call per entry; no call needs another's answer
        counts = list(pool.map(lambda row: int(git(root, 'rev-list', '--count', f'{row[1]}..HEAD', '--', *row[3],
                                                   check=False) or 0), asked))
    for (name, commit, stamp, _), count in zip(asked, counts):
        if count:
            day = time.strftime('%Y-%m-%d', time.gmtime(stamp))
            stale.append((-count, [name], f'{name}: {count} commit(s) to its modules since {commit[:7]} ({day}), '
                                          f'when its does and verbs were last edited'))
    title = 'Descriptions older than their code'
    if not dated:
        title += ' (not computed: the catalog has no git history here)'
    groups.append((title, [row[1:] for row in sorted(stale)]))

    def callers(name):
        return ', '.join(f'{caller} ({some(dict.fromkeys(a for a, _ in edges[caller, name]), 2)})'
                         for caller in sorted(links[name]['used_by']))

    groups.append(('Retired components that are still called', [
        ([e['id'], *links[e['id']]['used_by']], f'{e["id"]} ({e["status"]}): used by {callers(e["id"])}')
        for e in components if is_retired(e) and links[e['id']]['used_by']]))

    # A package __init__ that re-exports its own modules is not a tangle.
    direct = {edge: [pair for pair in pairs if not pair[0].endswith('/__init__.py')]
              for edge, pairs in edges.items()}

    def places(a, b):
        pairs = direct[a, b]
        return f'{a} imports {b} in {len(pairs)} place(s): ' + some((f'{x} -> {y}' for x, y in pairs), 3)

    groups.append(('Components that import each other', [
        ([a, b], f'{a} <-> {b}: {places(a, b)}; {places(b, a)}')
        for a, b in sorted(direct) if a < b and direct[a, b] and direct.get((b, a))]))

    names, undocumented, public, mains, entry_points = {}, [], {}, set(), set()
    for path in package:
        _, described, rows, _ = file_facts(root, path)
        public[path] = rows = top_level(rows)
        if rows and not described:
            undocumented.append(path)
        if path.endswith('/__main__.py') or any(row['id'] == 'main' for row in rows):
            mains.update(owners[path])
            entry_points.add(path)
        for row in rows:
            if row['id'] != 'main':
                names.setdefault(row['id'], []).append((path, row['label']))

    groups.append(('Retired components nothing calls (ready to remove?)', [
        ([e['id']], f'{e["id"]} ({e["status"]})') for e in components
        if is_retired(e) and e.get('modules') and not links[e['id']]['used_by']]))

    groups.append(('Components nothing in the package imports (an entry point, or unused?)', [
        ([e['id']], e['id'] + (' (defines main)' if e['id'] in mains else '')) for e in components
        if e.get('status') in {'canonical', 'experimental'} and e.get('modules') and not links[e['id']]['used_by']]))

    imports = package_imports(root)
    imported = set().union(*imports.values()) if imports else set()
    unused = {e['id'] for e in components if not links[e['id']]['used_by']}
    groups.append(('Modules nothing in the package imports, inside a component that is used', [
        (owners[p], f'{p} ({", ".join(owners[p])})') for p in package
        if p not in imported and p not in entry_points and not p.endswith('/__init__.py')
        and owners[p] and not set(owners[p]) & unused]))

    # Two or three definitions of one name suggest a copy; more suggest a shared convention.
    # Not news: a pair the catalog already records (retired, `duplicates:`, `distinct_from:`),
    # and a definition whose module imports the other one (a wrapper).
    retired = {e['id'] for e in components if is_retired(e)}
    settled = set()
    for entry in components:
        for path in package:
            if any(path == d or (d.endswith('/') and path.startswith(d)) for d in values(entry, 'duplicates')):
                settled.update((entry['id'], other) for other in owners[path])
        settled.update((entry['id'], other) for other in values(entry, 'distinct_from'))
    settled |= {(b, a) for a, b in settled}
    same, conventions = [], 0
    for name, found in names.items():
        found = [(p, label) for p, label in found if not set(owners[p]) & retired]
        ids = sorted({i for p, _ in found for i in owners[p]})
        if ids and all((a, b) in settled for a in ids for b in ids if a != b) and all(owners[p] for p, _ in found):
            continue
        if len({tuple(owners[p]) for p, _ in found}) < 2:
            continue
        if len(found) > 3:
            conventions += 1
            continue
        paths = [p for p, _ in found]
        if any(q in imports.get(p, ()) for p in paths for q in paths if p != q):
            continue
        alike = len({label for _, label in found}) == 1 and '(' in found[0][1]
        where = ', '.join(f'{p} ({", ".join(owners[p]) or "no component"})' for p in paths)
        same.append((not alike, name, ids, f'{name}{" (same signature)" if alike else ""}: {where}'))
    title = 'The same public name in two or three components (a duplicate?)'
    if conventions:
        title += f'; {conventions} name(s) defined in four or more modules are left out'
    groups.append((title, [row[2:] for row in sorted(same)]))

    groups.append(('Modules listed under more than one component', [
        (ids, f'{p}: {", ".join(ids)}') for p, ids in owners.items() if len(ids) > 1]))

    large = []
    for entry in components:
        covered = [p for p in package if covers(entry, p)]
        if len(covered) > LARGE:
            count = sum(len(public[p]) for p in covered)
            large.append((-len(covered), [entry['id']],
                          f'{entry["id"]}: {len(covered)} modules, {count} public classes and functions'))
    groups.append((f'Components that cover more than {LARGE} modules (more than one capability?)',
                   [row[1:] for row in sorted(large)]))

    groups.append(('Components with no tests listed', [
        ([e['id']], e['id']) for e in components if e.get('modules') and not values(e, 'tests')]))

    unlisted = {}
    by_test = {}
    for target, files in outside_importers(root, package).items():
        for name in files:
            by_test.setdefault(name, set()).update(owners[target])
    for relative, ids in sorted(by_test.items()):
        name = Path(relative).name
        if len(ids) != 1 or not relative.startswith('tests/') or not (name.startswith('test_') or name.endswith('_test.py')):
            continue  # a test of several components belongs to none of them in particular
        entry = next(e for e in components if e['id'] in ids)
        if not any(relative == t or (t.endswith('/') and relative.startswith(t)) for t in values(entry, 'tests')):
            unlisted.setdefault(entry['id'], []).append(relative)
    groups.append(('Test files that import one component only and are not in its tests', [
        ([name], f'{name}: {some(paths, 4)}') for name, paths in sorted(unlisted.items())]))
    wrong = []
    for entry in entries:
        steps = [m.strip() for m in entry.get('flow', '').split('->') if m.strip()] if subsystem(entry) else []
        for position, step in enumerate(steps[1:], 1):
            if step not in steps[:position] and not any((earlier, step) in edges for earlier in steps[:position]):
                wrong.append(([entry['id'], step],
                              f'{entry["id"]}: no earlier step of the flow imports {step}'))
    groups.append(('Flow steps that no earlier step imports (wrong order, or reached another way?)', wrong))
    groups.append(('Entries marked as checked in part', [
        ([e['id']], e['id']) for e in entries if e.get('checked', '').startswith('partial')]))
    if components and len(components) == len(entries) and not areas:
        groups.append(('No subsystem entries', [([], 'the main paths through the system are not described')]))
    groups.append(('Modules with no docstring (the search cannot describe them)',
                   [(owners[p], p) for p in undocumented]))
    groups.append(('Modules with no component', [([], p) for p in package if not owners[p]]))

    def wanted(ids):
        return not areas or any(i.startswith(area) for i in ids for area in areas)

    cap = None if everything or areas else 40
    lines, total, filled = [], 0, 0
    for title, rows in groups:
        rows = [text for ids, text in rows if wanted(ids)]
        total, filled = total + len(rows), filled + bool(rows)
        lines.extend([f'## {title} ({len(rows)})', *rows[:cap]])
        if cap and len(rows) > cap:
            lines.append(f'… +{len(rows) - cap} more (review --all prints every lead; review <area> prints one area)')
        lines.append('')
    scope = f' for {", ".join(areas)}' if areas else ''
    lines.append(f'review{scope}: {total} lead(s) in {filled} group(s), from {len(components)} component(s) and '
                 f'{len(package)} module(s); each is a place to look in the code, not a finding')
    return lines


def show(root: Path, name: str) -> list[str]:
    """One component as a reviewer needs it: the entry, then each module with its names and its imports."""
    entries = read_components(root)
    entry = next((e for e in entries if e['id'] == name), None)
    if entry is None:
        close = [e['id'] for e in entries if e['id'].startswith(name)]
        raise ValueError(f'no component {name}' + (f'; did you mean: {", ".join(close[:8])}' if close else ''))
    lines = [f'### {name}'] + [f'- {key}: {value}' for key, value in entry.items() if key not in {'id', '_repeated'}]
    if subsystem(entry):
        return lines
    components = [e for e in entries if not subsystem(e)]
    package = [p.relative_to(root).as_posix() for p in sources(root, PACKAGE_DIR)]
    owners = {p: [e['id'] for e in components if covers(e, p)] for p in package}
    imports = package_imports(root)
    importers = {}
    for path, targets in imports.items():
        for target in targets:
            importers.setdefault(target, []).append(path)
    outside = outside_importers(root, package)

    def owned(paths):
        return ', '.join(f'{p} ({", ".join(owners.get(p, [])) or "no component"})' for p in sorted(paths))

    for path in [p for p in package if covers(entry, p)]:
        text = (root / path).read_text(encoding='utf-8', errors='replace')
        tree = parse(root / path)
        private = [n.name for n in tree.body
                   if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('_')]
        constants = [t.id for n in tree.body if isinstance(n, (ast.Assign, ast.AnnAssign))
                     for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                     if isinstance(t, ast.Name) and t.id.isupper()]
        elsewhere = outside.get(path, [])
        lines.extend(['', f'## {path} ({len(text.splitlines())} lines): {summary(tree)}'])
        lines.extend(f'  {row["line"]}: {row["label"]}: {row["summary"]}' for row in symbols(tree, methods=False))
        if private or constants:
            lines.append(f'  also defines: {some(private + constants, 16)}')
        lines.append(f'  imports: {owned(imports.get(path, ())) or "(nothing in the package)"}')
        lines.append(f'  imported by: {owned(importers.get(path, ())) or "(nothing in the package)"}')
        lines.append(f'  imported from tests and scripts: {len(elsewhere)} file(s)'
                     + (f': {some(elsewhere, 6)}' if elsewhere else ''))
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--strict', action='store_true', help='with --check: also fail on a module with no component')
    parser.add_argument('--no-cache', dest='fresh', action='store_true',
                        help='parse every source file, ignoring what earlier runs kept')
    commands = parser.add_subparsers(dest='command')
    commands.add_parser('write')
    commands.add_parser('init')
    find = commands.add_parser('search')
    find.add_argument('words', nargs='+')
    find.add_argument('--limit', type=int, default=5)
    find.add_argument('--explain', action='store_true', help='show the query words each hit matched')
    find.add_argument('--no-cache', action='store_true', help='the same as --no-cache before the command')
    stats = commands.add_parser('stats')
    stats.add_argument('--write-baseline', action='store_true')
    stubs = commands.add_parser('draft')
    stubs.add_argument('--only', default='', help='only modules whose path starts with this')
    stubs.add_argument('--by-importers', action='store_true', help='most-imported modules first')
    diff = commands.add_parser('changed')
    diff.add_argument('--base', default='main', help='branch or commit the change will merge into')
    diff.add_argument('--strict', dest='strict_changed', action='store_true',
                      help='also fail on a new caller of a deprecated or duplicate component')
    look = commands.add_parser('review')
    look.add_argument('areas', nargs='*', help='only leads that name a component whose id starts with one of these')
    look.add_argument('--all', action='store_true', help='print every lead instead of the first 40 of each group')
    one = commands.add_parser('show')
    one.add_argument('id')
    names = commands.add_parser('list')
    names.add_argument('area', nargs='?', default='')
    args = parser.parse_args(argv)
    if args.check and args.command:
        parser.error('--check cannot be combined with a subcommand')
    if args.strict and not args.check:
        parser.error('--strict goes with --check (for the changed command, write it after: changed --strict)')
    STATE.clear()
    CACHE['on'] = not (args.fresh or getattr(args, 'no_cache', False))
    try:
        target = args.root / BASE / 'COMPONENTS.md'
        if args.command == 'init' and target.exists():
            print(f'{BASE}COMPONENTS.md exists; left as it is')
            return 0
        if args.command == 'init' or (not target.exists() and not args.check and args.command in (None, 'write')):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(STARTER.format(label=LABEL, package_dir=PACKAGE_DIR), encoding='utf-8')
            print(f'wrote {BASE}COMPONENTS.md: add one entry per component, then run `python3 {LABEL} write`')
            if args.command == 'init':
                return 0
        if args.command == 'search':
            hits = search(args.root, ' '.join(args.words), None, cache=not args.no_cache)
            budget = 7000
            for hit in hits[:max(0, args.limit)]:
                total = len(tokens(' '.join(args.words)))
                why = f' [{len(hit["matched"])}/{total}: {", ".join(hit["matched"])}]' if args.explain else ''
                line = f'{hit["kind"]} {hit["id"]}{why}: {hit["summary"]}'
                if hit.get('flow'):
                    line += '\nflow: ' + hit['flow']
                if len(line) > budget:
                    break
                print(line)
                budget -= len(line) + 1
            if not any(h['kind'] in {'component', 'subsystem'} for h in hits):
                print('no component matched: this is not proof that nothing exists; search modules/ and git grep')
            print(coverage_line(args.root, read_components(args.root)))
            return 0
        if args.command == 'stats':
            entries = read_components(args.root)
            unassigned, _ = coverage(args.root, entries)
            print(coverage_line(args.root, entries))
            print('\n'.join(unassigned))
            if args.write_baseline:
                target = args.root / BASE / 'unassigned-baseline.txt'
                known = set(target.read_text(encoding='utf-8').split()) if target.is_file() else None
                added = [p for p in unassigned if known is not None and p not in known]
                if added:
                    raise ValueError('unassigned baseline cannot grow; assign new modules to components: '
                                     + some(added, 5))
                target.write_text(''.join(p + '\n' for p in unassigned), encoding='utf-8')
            return 0
        if args.command == 'draft':
            found = read_components(args.root) if target.is_file() else []
            print('\n'.join(draft(args.root, found, args.only, args.by_importers)))
            return 0
        if args.command == 'list':
            areas = {}
            for entry in read_components(args.root):
                if entry['id'].startswith(args.area):
                    areas.setdefault(entry['id'].split('.')[0], []).append(entry)
            for area, members in areas.items():
                print(f'## {area} ({len(members)})')
                for entry in members:
                    print(f'{entry["id"]}: {entry.get("does", "")}')
                print()
            return 0
        if args.command == 'changed':
            return changed(args.root, args.base, args.strict_changed)
        if args.command == 'review':
            print('\n'.join(review(args.root, tuple(args.areas), args.all)))
            return 0
        if args.command == 'show':
            print('\n'.join(show(args.root, args.id)))
            return 0
        return write_or_check(args.root, args.check, args.strict)
    except (OSError, ValueError, SyntaxError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        save_caches()


if __name__ == '__main__':
    sys.exit(main())
