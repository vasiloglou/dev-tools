#!/usr/bin/env python3
"""Copy dev-tools skills and scripts into a project and keep the copies honest.

Prototype. The project lists what it takes in ``.devtools.toml``::

    [[sync]]
    source = "skills/phase/process-phase"          # path in this repository (file or directory)
    dest = ".claude/skills/process-phase"          # path in the project
    exclude = ["scripts/gates.json"]               # optional: files in a directory the project keeps as its own
    values = { planning_dir = ".planning" }        # optional: fills {{devtools:planning_dir}} in shipped text
    [sync.settings."scripts/phase_tool.settings.json"]   # written inside dest (beside dest for a file)
    planning_dir = ".planning"

    replaces = ".claude/skills/acme-demo"          # optional: the project's old copy under another name;
                                                   # `compare` reads it, nothing deletes it

    after_apply = ["python3 scripts/components_index.py write"]  # optional, top level: run when apply changed a file
                                                   # (no shell: write `env NAME=value command` to set a variable)

``apply`` copies the files, writes the settings files and records every managed file in
``.devtools-receipt.json`` (sha256 and mode). It refuses to overwrite a file the project
changed by hand, or one it does not manage yet, unless told to (``--force``, ``--adopt``).
``check`` needs only the project: it compares the managed files with the receipt.

For a project that already has its own copies of these skills: ``survey`` finds them and can
print a starter ``.devtools.toml`` (``--toml``), and ``compare`` shows, before anything is
written, which files an apply would replace and which of the project's lines would be gone.
Neither writes anything. ``skills/adopt-devtools/SKILL.md`` is the guide that uses them.

Exit codes: 0 ok; 1 check found drift; 2 usage or configuration; 3 apply refused (nothing written);
4 files were written but an after_apply command failed.

Needs Python 3.11 or newer.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python older than 3.11
    sys.exit("sync.py needs Python 3.11 or newer (this is %d.%d)" % sys.version_info[:2])

SOURCE_ROOT = Path(__file__).resolve().parents[1]
CONFIG = ".devtools.toml"
RECEIPT = ".devtools-receipt.json"
JOURNAL = ".devtools-sync.journal"
SKIP_DIRS = {"__pycache__"}
TOKEN = re.compile(r"\{\{devtools:([a-z_]+)\}\}")
TODO = "TODO"  # a value the starter config could not know; apply and compare refuse it
# Read from this checkout, never copied into a project.
NOT_FOR_PROJECTS = {"skills/adopt-devtools", "skills/move-from-gsd"}
PRUNE = {".git", "node_modules", ".venv", "venv", "site-packages", ".tox", ".cache",
         ".mypy_cache", ".pytest_cache", ".ruff_cache"} | SKIP_DIRS


class SyncError(Exception):
    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inside(root: Path, relative: str) -> Path:
    """Resolve a configured relative path, refusing anything that leaves ``root``."""
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SyncError(f"path must be relative and stay inside {root}: {relative!r}")
    return root / relative


def fill_tokens(data: bytes, values: dict, origin: str, used: set) -> bytes:
    """Replace ``{{devtools:<key>}}`` in text files with the project's value; a missing value is an error."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    keys = set(TOKEN.findall(text))
    missing = sorted(keys - set(values))
    if missing:
        raise SyncError(f"{origin} needs values for: {', '.join(missing)}")
    used |= keys
    return TOKEN.sub(lambda match: str(values[match.group(1)]), text).encode("utf-8") if keys else data


def read_config(project: Path) -> dict:
    config_path = project / CONFIG
    if not config_path.is_file():
        raise SyncError(f"{config_path} not found")
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    unknown = sorted(set(config) - {"sync", "after_apply"})
    if unknown:
        raise SyncError(f"{config_path}: unknown top-level keys: {unknown}")
    return config


def desired_files(source_root: Path, config: dict, project: Path) -> dict[str, dict]:
    """Project-relative path -> {data, mode, origin} for everything the config asks for."""
    files: dict[str, dict] = {}

    def add(dest: str, data: bytes, mode: int, origin: str) -> None:
        inside(project, dest)
        if dest in files:
            raise SyncError(f"{dest} is produced twice ({files[dest]['origin']} and {origin})")
        files[dest] = {"data": data, "mode": mode, "origin": origin}

    for entry in config.get("sync", []):
        unknown = sorted(set(entry) - {"source", "dest", "settings", "exclude", "values", "replaces"})
        if unknown or "source" not in entry or "dest" not in entry:
            raise SyncError(f"[[sync]] needs source and dest; unknown keys: {unknown}")
        source = inside(source_root, entry["source"])
        dest = entry["dest"].rstrip("/")
        exclude = set(entry.get("exclude", []))
        values, used = entry.get("values", {}), set()
        unset = sorted(k for k, v in values.items() if v == TODO)
        unset += sorted(f"{name}: {k}" for name, block in entry.get("settings", {}).items()
                        for k, v in block.items() if v == TODO)
        if unset:
            raise SyncError(f"{entry['source']}: still {TODO} in {CONFIG}: {', '.join(unset)}")
        if source.is_file():
            if exclude:
                raise SyncError(f"exclude applies to a directory source, not {entry['source']}")
            add(dest, fill_tokens(source.read_bytes(), values, entry["source"], used),
                stat.S_IMODE(source.stat().st_mode), entry["source"])
            settings_base = Path(dest).parent
        elif source.is_dir():
            for path in sorted(p for p in source.rglob("*") if p.is_file() and not SKIP_DIRS & set(p.parts)):
                relative = path.relative_to(source).as_posix()
                if relative in exclude:
                    exclude.discard(relative)
                    continue
                add(f"{dest}/{relative}", fill_tokens(path.read_bytes(), values, f"{entry['source']}/{relative}", used),
                    stat.S_IMODE(path.stat().st_mode), f"{entry['source']}/{relative}")
            settings_base = Path(dest)
            if exclude:
                raise SyncError(f"exclude names files that {entry['source']} does not ship: {sorted(exclude)}")
        else:
            raise SyncError(f"source not found in dev-tools: {entry['source']}")
        if set(values) - used:
            raise SyncError(f"{entry['source']} has no token for values: {sorted(set(values) - used)}")
        for name, values in entry.get("settings", {}).items():
            data = (json.dumps(values, indent=2, sort_keys=True) + "\n").encode("utf-8")
            add((settings_base / name).as_posix(), data, 0o644, "settings")
    return files


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def source_identity(source_root: Path, config: dict | None = None) -> dict:
    """The dev-tools commit, and whether what the config takes from it has uncommitted changes."""
    def git(*args: str) -> str:
        done = subprocess.run(["git", "-C", str(source_root), *args], capture_output=True, text=True)
        return done.stdout.strip() if done.returncode == 0 else ""
    taken = [entry["source"] for entry in (config or {}).get("sync", []) if "source" in entry]
    return {"commit": git("rev-parse", "HEAD") or None, "dirty": bool(git("status", "--porcelain", "--", *taken))}


def warn_if_dirty(source_root: Path, config: dict) -> None:
    if source_identity(source_root, config)["dirty"]:
        print("warning: the dev-tools files this project takes have uncommitted changes; "
              "the dev-tools commit does not identify what is delivered", file=sys.stderr)


def plan(project: Path, wanted: dict[str, dict]) -> tuple[list[dict], list[str]]:
    """Classify every wanted or previously managed file. Returns (actions, refusals)."""
    managed = read_json(project / RECEIPT).get("files", {})
    interrupted = read_json(project / JOURNAL).get("files", {})
    actions, refusals = [], []
    for dest in sorted(set(wanted) | set(managed)):
        path = project / dest
        current = digest(path.read_bytes()) if path.is_file() and not path.is_symlink() else None
        ours = {managed.get(dest, {}).get("sha256"), interrupted.get(dest)} - {None}
        if dest not in wanted:
            if current is None:
                actions.append({"dest": dest, "do": "forget"})
            elif current in ours:
                actions.append({"dest": dest, "do": "delete"})
            else:
                refusals.append(f"{dest}: no longer shipped, but changed in the project (--force deletes it)")
                actions.append({"dest": dest, "do": "delete", "needs": "force"})
            continue
        target = digest(wanted[dest]["data"])
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise SyncError(f"{dest} exists and is not a regular file")
        if current is None:
            actions.append({"dest": dest, "do": "create"})
        elif current == target:
            same_mode = stat.S_IMODE(path.stat().st_mode) == wanted[dest]["mode"]
            actions.append({"dest": dest, "do": "keep" if same_mode else "update"})
        elif current in ours:
            actions.append({"dest": dest, "do": "update"})
        elif dest in managed:
            refusals.append(f"{dest}: changed in the project since the last sync (--force overwrites it)")
            actions.append({"dest": dest, "do": "update", "needs": "force"})
        else:
            refusals.append(f"{dest}: exists and is not managed yet (--adopt overwrites it)")
            actions.append({"dest": dest, "do": "update", "needs": "adopt"})
    return actions, refusals


def write_atomic(path: Path, data: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=".devtools-")
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def cmd_apply(args) -> int:
    project = args.project.resolve()
    config = read_config(project)
    wanted = desired_files(args.source.resolve(), config, project)
    warn_if_dirty(args.source.resolve(), config)
    actions, _ = plan(project, wanted)
    allowed = {"force"} if args.force else set()
    allowed |= {"adopt"} if args.adopt else set()
    blocked = [a for a in actions if a.get("needs") and a["needs"] not in allowed]
    counts: dict[str, int] = {}
    for action in actions:
        counts[action["do"]] = counts.get(action["do"], 0) + 1
    if blocked:
        for action in blocked:
            print(f"refused: {action['dest']} (needs --{action['needs']})", file=sys.stderr)
        print(f"nothing written; {len(blocked)} file(s) refused", file=sys.stderr)
        return 3
    if args.dry_run:
        for action in actions:
            if action["do"] != "keep":
                print(f"{action['do']}: {action['dest']}")
        print("dry run:", json.dumps(counts, sort_keys=True))
        return 0
    # The journal names what this run intends, so an interrupted run can be finished by running apply again.
    journal = {"files": {dest: digest(item["data"]) for dest, item in wanted.items()}}
    write_atomic(project / JOURNAL, json.dumps(journal).encode("utf-8"), 0o644)
    for action in actions:
        path = project / action["dest"]
        if action["do"] in ("create", "update"):
            write_atomic(path, wanted[action["dest"]]["data"], wanted[action["dest"]]["mode"])
        elif action["do"] == "delete":
            path.unlink()
    receipt = {
        "source": source_identity(args.source.resolve(), config),
        "files": {dest: {"sha256": digest(item["data"]), "mode": oct(item["mode"]), "origin": item["origin"]}
                  for dest, item in sorted(wanted.items())},
    }
    write_atomic(project / RECEIPT, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"), 0o644)
    (project / JOURNAL).unlink()
    print("applied:", json.dumps(counts, sort_keys=True))
    if set(counts) - {"keep"}:
        for command in config.get("after_apply", []):
            print("after_apply:", command, flush=True)
            try:
                code = subprocess.run(shlex.split(command), cwd=project).returncode
            except OSError as error:  # the command itself could not be started
                print(error, file=sys.stderr)
                code = 1
            if code != 0:
                print(f"after_apply failed: {command}", file=sys.stderr)
                print("the files and the receipt are written; run the command by hand once it works", file=sys.stderr)
                return 4
    return 0


def cmd_check(args) -> int:
    project = args.project.resolve()
    receipt = read_json(project / RECEIPT)
    if not receipt:
        raise SyncError(f"{project / RECEIPT} not found; run apply first")
    problems = []
    if (project / JOURNAL).is_file():
        problems.append("an apply was interrupted; run apply again")
    for dest, recorded in sorted(receipt["files"].items()):
        path = project / dest
        if not path.is_file() or path.is_symlink():
            problems.append(f"{dest}: missing")
        elif digest(path.read_bytes()) != recorded["sha256"]:
            problems.append(f"{dest}: differs from the receipt")
        elif oct(stat.S_IMODE(path.stat().st_mode)) != recorded["mode"]:
            problems.append(f"{dest}: mode differs from the receipt")
    for problem in problems:
        print(problem)
    print(f"{len(receipt['files'])} managed file(s), {len(problems)} problem(s)")
    return 1 if problems else 0


# --------------------------------------------------------------------------- survey and compare

PROSE = {".md", ".txt", ".rst", ""}  # read line by line; any other file is a script or data, read as a diff
COMMON = {"SKILL.md", "README.md", "__init__.py", "conftest.py", "openai.yaml"}  # names too common to look for


def kept_lines(data: bytes) -> list[tuple[int, str]]:
    """(line number, stripped text) for the lines that say something; nothing for a binary file."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    return [(number, line.strip()) for number, line in enumerate(text.splitlines(), 1)
            if len(line.strip()) >= 4 and any(c.isalnum() for c in line)]


def squeeze(text: str) -> str:
    """The text with every run of spaces and line breaks as one space, so a re-wrapped sentence still matches."""
    return " ".join(text.split())


def shared(shipped: bytes, local: bytes) -> float:
    """The share of the shipped file's lines that the local file also has (lines with a token left out)."""
    want = {line for _, line in kept_lines(shipped) if not TOKEN.search(line)}
    return len(want & {line for _, line in kept_lines(local)}) / len(want) if want else 0.0


def shipped_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.rglob("*") if p.is_file() and not SKIP_DIRS & set(p.parts))


def shipped_units(source_root: Path) -> list[dict]:
    """What a project can take: each skill directory, the agents directory, and the scripts that stand alone."""
    skills = source_root / "skills"
    folders = sorted(p.parent for p in skills.rglob("SKILL.md"))
    units = [{"source": d.relative_to(source_root).as_posix(), "kind": "skill"} for d in folders]
    if (source_root / "agents").is_dir():
        units.append({"source": "agents", "kind": "agents"})
    for path in sorted(skills.rglob("*.py")):
        if not SKIP_DIRS & set(path.parts) and not any(d in path.parents for d in folders):
            units.append({"source": path.relative_to(source_root).as_posix(), "kind": "file"})
    return [unit for unit in units if unit["source"] not in NOT_FOR_PROJECTS]


def walk_project(project: Path):
    """(regular files, symlinked directories), skipping caches and checkouts nested in the project."""
    files, links = [], []
    for current, folders, names in os.walk(project):
        here = Path(current)
        links.extend(here / d for d in folders if (here / d).is_symlink())
        folders[:] = sorted(d for d in folders if d not in PRUNE and not (here / d).is_symlink()
                            and not (here / d / ".git").exists())
        files.extend(here / name for name in sorted(names) if not (here / name).is_symlink())
    return files, links


def related(name: str, shipped: str) -> bool:
    """`acme-components` and `components-acme` are other names for `components`."""
    return name != shipped and (name.startswith(shipped + "-") or name.endswith("-" + shipped))


def literals(script: Path) -> dict:
    """The top-level `NAME = <literal>` assignments of a script, read without running it."""
    try:
        tree = ast.parse(script.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {}
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                found[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                pass
    return found


def survey(source_root: Path, project: Path) -> dict:
    """Match what the project has against what dev-tools ships. Reads only."""
    files, links = walk_project(project)
    units = shipped_units(source_root)
    relative = lambda path: path.relative_to(project).as_posix()
    local_skills = sorted(p.parent for p in files if p.name == "SKILL.md")
    found = {unit["source"]: [] for unit in units}
    own, clashes = [], []
    for folder in local_skills:
        local = (folder / "SKILL.md").read_bytes()
        best = None
        for unit in (u for u in units if u["kind"] == "skill"):
            source = source_root / unit["source"]
            others = [p.relative_to(source).as_posix() for p in shipped_files(source) if p.name != "SKILL.md"]
            missing = [name for name in others if not (folder / name).is_file()]
            match = {"unit": unit["source"], "share": shared((source / "SKILL.md").read_bytes(), local),
                     "present": len(others) - len(missing), "of": len(others), "missing": missing,
                     "same_name": folder.name == source.name, "related": related(folder.name, source.name)}
            match["score"] = match["share"] + (0.5 * match["present"] / len(others) if len(others) >= 3 else 0)
            named = match["same_name"] or match["related"]
            match["counterpart"] = match["share"] >= 0.2 or (named and match["score"] >= 0.08)
            key = (match["counterpart"], match["score"] + 0.2 * named)
            if best is None or key > best[0]:
                best = (key, match)
        match = best[1] if best else None
        if match and match["counterpart"]:
            found[match["unit"]].append({"path": relative(folder), **match})
        else:
            own.append(relative(folder))
            if match and match["same_name"]:
                clashes.append({"path": relative(folder), "unit": match["unit"]})
    taken = [project / hit["path"] for hits in found.values() for hit in hits]
    for unit in units:
        source = source_root / unit["source"]
        if unit["kind"] == "agents":
            names = {p.name for p in shipped_files(source)}
            for folder in sorted({p.parent for p in files if p.name in names and p.parent.name == "agents"}):
                have = [name for name in sorted(names) if (folder / name).is_file()]
                found[unit["source"]].append({"path": relative(folder), "present": len(have), "of": len(names)})
        elif unit["kind"] == "file":
            found[unit["source"]].extend({"path": relative(p)} for p in files if p.name == source.name)
    # A file that a skill ships, kept by the project somewhere outside its copy of that skill: every
    # script, and any other file its copy lacks. Templates are left out (the project has files of the
    # same names that were made from them).
    apart = {}
    for unit in (u for u in units if u["kind"] == "skill" and found[u["source"]]):
        source = source_root / unit["source"]
        lacking = {name for hit in found[unit["source"]] for name in hit["missing"]}
        for shipped in shipped_files(source):
            inner = shipped.relative_to(source).as_posix()
            if shipped.name in COMMON or inner.startswith("templates/"):
                continue
            if shipped.suffix != ".py" and inner not in lacking:
                continue
            places = [relative(p) for p in files if p.name == shipped.name
                      and not any(folder in p.parents for folder in taken)
                      and (shipped.suffix == ".py" or shared(shipped.read_bytes(), p.read_bytes()) >= 0.2)]
            if places:
                apart[f"{unit['source']}/{inner}"] = places
    in_skill = lambda place: any(folder in (project / place).parents for folder in local_skills)
    return {"units": units, "found": found, "apart": apart, "own": own, "clashes": clashes, "in_skill": in_skill,
            "links": sorted(relative(p) for p in links if p.parent.name == "skills")}


def covered(project: Path) -> tuple[set[str], set[str], set[str]]:
    """(paths the config delivers to, paths in the receipt, old copies it names); empty without a config."""
    wanted, old = set(), set()
    if (project / CONFIG).is_file():
        for entry in read_config(project).get("sync", []):
            wanted.add(str(entry.get("dest", "")).rstrip("/"))
            old.add(str(entry.get("replaces", "")).rstrip("/"))
    return wanted, set(read_json(project / RECEIPT).get("files", {})), old - {""}


def tracked(project: Path, path: str) -> bool:
    """False only when git answers and knows no file at or under the path."""
    done = subprocess.run(["git", "-C", str(project), "ls-files", "--", path], capture_output=True, text=True)
    return done.returncode != 0 or bool(done.stdout.strip())


def survey_text(source_root: Path, project: Path, result: dict) -> list[str]:
    wanted, managed, old = covered(project)

    def state(path: str) -> str:
        known = tracked(project, path)
        if path in old:
            return f"  [the old copy that {CONFIG} names under replaces]"
        if any(m == path or m.startswith(path + "/") for m in managed):
            return "  [synced]" if known else "  [synced; not added to git yet]"
        untracked = "" if known else "  [not tracked by git]"
        if path in wanted:
            return f"  [in {CONFIG}, not applied yet]" + untracked
        return (f"  [not in {CONFIG}]" if wanted else "") + untracked

    lines = []
    have = [unit for unit in result["units"] if result["found"][unit["source"]]]
    lines.append(f"dev-tools ships {len(result['units'])} unit(s); {len(have)} have a counterpart in this project.")
    lines += ["", "## Counterparts: the project's copy of something dev-tools ships"]
    for unit in have:
        lines.append(unit["source"])
        name = Path(unit["source"]).name
        for hit in result["found"][unit["source"]]:
            if unit["kind"] != "skill":
                if unit["kind"] == "agents":
                    note = f"{hit['present']} of {hit['of']} shipped files present"
                else:
                    same = (project / hit["path"]).read_bytes() == (source_root / unit["source"]).read_bytes()
                    note = "identical" if same else "differs"
                lines.append(f"  {hit['path']}  ({note}){state(hit['path'])}")
                continue
            lines.append(f"  {hit['path']}{state(hit['path'])}")
            if not hit["same_name"]:
                lines.append(f"      dev-tools names it `{name}`")
            lines.append(f"      {round(100 * hit['share'])}% of the shipped SKILL.md lines; "
                         f"{hit['present']} of {hit['of']} other shipped files present")
            if hit["missing"]:
                more = f" and {len(hit['missing']) - 3} more" if len(hit["missing"]) > 3 else ""
                lines.append(f"      not here: {', '.join(hit['missing'][:3])}{more}")
    if not have:
        lines.append("(none)")
    if result["apart"]:
        lines += ["", "## Shipped files the project keeps outside its copy of the skill"]
        for inner, places in result["apart"].items():
            lines += [inner] + [f"  {place}{state(place)}" for place in places]
    missing = [unit["source"] for unit in result["units"] if not result["found"][unit["source"]]]
    if missing:
        lines += ["", "## Shipped, with no counterpart here"] + missing
    if result["clashes"]:
        lines += ["", "## Same name, different skill: a sync to this path would replace the project's own skill"]
        lines += [f"{clash['path']}  (dev-tools ships {clash['unit']})" for clash in result["clashes"]]
    if result["own"]:
        lines += ["", "## The project's own skills: no counterpart, the sync never touches them"] + by_folder(result["own"])
    if result["links"]:
        lines += ["", "## Symlinked skill folders: not read"]
        lines += [line.split(": ")[0] + f" {line.count(',') + 1} folder(s)" for line in by_folder(result["links"])]
    if have:
        # Names that point at the copies: the folder with its parent, each shipped script as a module
        # name, each shipped data file with its folder.
        names, folders = [], []
        for unit in have:
            source = source_root / unit["source"]
            for hit in result["found"][unit["source"]]:
                path = Path(hit["path"])
                folders.append(hit["path"])
                names.append(f"{path.parent.name}/{path.name}" if unit["kind"] != "file" else path.stem)
            if unit["kind"] == "skill":
                for shipped in shipped_files(source):
                    if shipped.suffix == ".py":
                        names.append(shipped.stem)
                    elif shipped.suffix in (".json", ".toml", ".yaml", ".yml") and shipped.parent.name == "scripts":
                        names.append(f"{shipped.parent.name}/{shipped.name}")
        names = list(dict.fromkeys(names))
        lines += ["", "## To find what reads these copies (tests, scripts, CI, other skills)",
                  "git grep -l " + " ".join(f"-e '{name}'" for name in names) + " -- . "
                  + " ".join(f"':!{folder}'" for folder in dict.fromkeys(folders))]
    return lines


def by_folder(paths: list[str]) -> list[str]:
    """One line per parent folder, with the names inside it."""
    groups: dict[str, list[str]] = {}
    for path in paths:
        groups.setdefault(str(Path(path).parent), []).append(Path(path).name)
    return [f"{folder}/: {', '.join(names)}" for folder, names in sorted(groups.items())]


def toml_value(value) -> str:
    return json.dumps(value)  # strings, booleans, numbers and lists of them read the same in TOML


def token_values(source: Path, copy: Path) -> dict[str, tuple[str, str]]:
    """Token -> (value, where it was read), for the tokens whose value the project's copy shows.

    A shipped line with one token is matched against the lines of the project's file of the same
    name; a value is taken only when every line that matches gives the same one.
    """
    seen: dict[str, dict[str, str]] = {}
    for shipped in shipped_files(source):
        local = copy / shipped.relative_to(source)
        if not local.is_file():
            continue
        try:
            lines = local.read_text(encoding="utf-8").splitlines()
            text = shipped.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line in text.splitlines():
            keys = TOKEN.findall(line)
            if len(set(keys)) != 1 or len(line.strip()) < 12:
                continue
            pattern = re.compile(r"([^\s`'\"()<>]+?)".join(re.escape(part) for part in TOKEN.split(line.strip())[::2]))
            for number, candidate in enumerate(lines, 1):
                match = pattern.fullmatch(candidate.strip())
                if match and len(set(match.groups())) == 1:
                    seen.setdefault(keys[0], {}).setdefault(match.group(1), f"{local.name} line {number}")
    return {key: next(iter(values.items())) for key, values in seen.items() if len(values) == 1}


def starter_config(source_root: Path, project: Path, result: dict) -> list[str]:
    """A .devtools.toml that puts each shipped unit where the project keeps its own copy."""
    lines = [f"# Starter {CONFIG}, written by `sync.py survey --toml`. Nothing is copied until `sync.py apply`.",
             f"# The sync refuses to run while a \"{TODO}\" is left. A value marked \"from the survey\" or",
             "# \"read from\" is a reading, not a decision: check it against how the project works.", ""]
    skill_roots = sorted({str(Path(hit["path"]).parent) for unit in result["units"] if unit["kind"] == "skill"
                          for hit in result["found"][unit["source"]]})
    agents = [hit["path"] for hit in result["found"].get("agents", [])]
    delivered: set[str] = set()
    # A token's value read in one of the project's copies serves the copies that do not show it.
    readings = {(unit["source"], hit["path"]): token_values(source_root / unit["source"], project / hit["path"])
                for unit in result["units"] if unit["kind"] == "skill" for hit in result["found"][unit["source"]]}
    agreed: dict[str, set] = {}
    for read in readings.values():
        for name, (value, _) in read.items():
            agreed.setdefault(name, set()).add(value)

    def settings(script: Path, name: str, old_script: str, dest_script: str, dest_folder: str) -> list[str]:
        defaults = literals(script).get("DEFAULT_SETTINGS")
        if not isinstance(defaults, dict):
            return []
        current = read_json(project / Path(dest_script).with_suffix(".settings.json"))
        constants = literals(project / old_script)
        block = [f"# Each {TODO} shows the shipped default. Read what {old_script} did, and the comment on the",
                 f"# setting in the shipped {script.relative_to(source_root).as_posix()}.",
                 f'[sync.settings."{name}"]']
        for key, default in defaults.items():
            if key in current:
                value, why = current[key], "the project's settings file"
            elif key.upper() in constants and type(constants[key.upper()]) is type(default):
                value, why = constants[key.upper()], f"read from {key.upper()} in {old_script}"
            elif key == "script_path":
                value, why = dest_script, "from the survey"
            elif key == "process_skill":
                value, why = dest_folder, "from the survey"
            elif key == "skill_roots" and skill_roots:
                value, why = skill_roots, "from the survey: add the other skill folders the project's check covered"
            elif key == "agents_dir" and agents:
                value, why = agents[0], "from the survey"
            else:
                value, why = TODO, f"default {toml_value(default)}"
                if value == TODO and not default:
                    why += " (an empty value is valid)"
            block.append(f"{key} = {toml_value(value)}  # {why}")
        return block + [""]

    for unit in result["units"]:
        source = source_root / unit["source"]
        for hit in result["found"][unit["source"]]:
            path = hit["path"]
            if unit["kind"] != "skill":
                lines += ["[[sync]]", f'source = "{unit["source"]}"', f'dest = "{path}"', ""]
                continue
            dest = (Path(path).parent / source.name).as_posix()
            if not tracked(project, path):
                lines.append(f"# {path} is not tracked by git: remove this entry unless the copy should be committed.")
            lines += ["[[sync]]", f'source = "{unit["source"]}"', f'dest = "{dest}"']
            if dest != path:
                lines.append(f'replaces = "{path}"  # the old copy: `compare` reads it; delete the folder after the apply')
            names = sorted({key for p in shipped_files(source) for key in TOKEN.findall(p.read_text(errors="ignore"))})
            if names:
                read = dict(readings[(unit["source"], path)])
                for name in names:
                    if name not in read and len(agreed.get(name, ())) == 1:
                        read[name] = (next(iter(agreed[name])), "")
                lines += [f"# {name}: " + (f"read from {where} of the project's copy" if where else
                                           "the value the project's other copies show")
                          for name, (_, where) in read.items()]
                lines.append("values = { %s }" % ", ".join(
                    f"{name} = {toml_value(read[name][0] if name in read else TODO)}" for name in names))
            scripts = {inner: places for inner, places in result["apart"].items()
                       if inner.startswith(unit["source"] + "/") and inner.endswith(".py")}
            moved = {inner[len(unit["source"]) + 1:]: [place for place in places if not result["in_skill"](place)]
                     for inner, places in scripts.items()}
            moved = {inner: places for inner, places in moved.items() if places}
            if moved:
                lines.append(f"exclude = {toml_value(sorted(moved))}")
            data = [p.relative_to(source).as_posix() for p in shipped_files(source)
                    if p.suffix in (".json", ".toml", ".yaml", ".yml")
                    and (project / path / p.relative_to(source)).is_file()
                    and (project / path / p.relative_to(source)).read_bytes() != p.read_bytes()]
            if data:
                lines.append(f"# Data files that differ from the shipped ones (add to exclude to keep the project's): "
                             f"{', '.join(data)}")
            lines.append("")
            for script in (p for p in shipped_files(source) if p.suffix == ".py"):
                inner = script.relative_to(source).as_posix()
                if inner not in moved:
                    lines += settings(script, str(Path(inner).with_suffix(".settings.json")),
                                      f"{path}/{inner}", f"{dest}/{inner}", dest)
            for inner, places in moved.items():
                for place in places:
                    if place not in delivered:  # one delivery of the script serves every copy of the skill
                        delivered.add(place)
                        lines += ["[[sync]]", f'source = "{unit["source"]}/{inner}"', f'dest = "{place}"', ""]
                        lines += settings(source / inner, Path(place).with_suffix(".settings.json").name,
                                          place, place, dest)
    if delivered or any(".settings.json" in line for line in lines):
        lines[3:3] = ["", "# If a synced script generates files, run it after a sync (no shell: `env NAME=value command`):",
                      '# after_apply = ["<interpreter> <script> write"]']
    missing = [unit["source"] for unit in result["units"] if not result["found"][unit["source"]]]
    if missing:
        lines.append("# Shipped, with no counterpart found here (add an entry to take one):")
        lines += [f"#   {source}" for source in missing]
    return lines


def cmd_survey(args) -> int:
    project, source_root = args.project.resolve(), args.source.resolve()
    if not project.is_dir():
        raise SyncError(f"{project} is not a directory")
    result = survey(source_root, project)
    print("\n".join(starter_config(source_root, project, result) if args.toml
                    else survey_text(source_root, project, result)))
    return 0


def headings(text: str) -> dict[int, str]:
    """Line number -> the Markdown heading it sits under (its own text for a heading); code fences are skipped."""
    under, current, fenced = {}, "", False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and re.match(r"#{1,6} \S", line):
            current = line.strip()
        under[number] = current
    return under


def compare_rows(project: Path, source_root: Path, config: dict, wanted: dict) -> tuple[list[dict], list[str]]:
    """One row per file an apply would touch, per file of an old copy, and per excluded file the project keeps."""
    actions, _ = plan(project, wanted)
    exact = {line for item in wanted.values() for _, line in kept_lines(item["data"])}
    running = squeeze(" ".join(item["data"].decode("utf-8", errors="ignore") for item in wanted.values()))

    def only_here(data: bytes, path: Path | None = None) -> list[tuple[int, str]]:
        """The lines no delivered file has, alone or joined with a neighbour (a sentence wrapped elsewhere)."""
        raw = [""] + data.decode("utf-8", errors="ignore").splitlines() + [""]
        prose = path is None or path.suffix in PROSE
        found = []
        for n, line in kept_lines(data):
            if line in exact or (len(line) >= 12 and squeeze(line) in running):
                continue
            joined = [squeeze(raw[n - 1] + " " + raw[n]), squeeze(raw[n] + " " + raw[n + 1])] if prose else []
            if not any(len(text) > len(line) + 8 and text in running for text in joined):
                found.append((n, line))
        return found

    rows = []
    for action in actions:
        dest, path = action["dest"], project / action["dest"]
        row = {"dest": dest, "lost": [], "origin": wanted.get(dest, {}).get("origin", "")}
        if action["do"] in ("create", "keep", "delete", "forget"):
            row["label"] = {"create": "new", "keep": "same"}.get(action["do"], "remove")
        else:
            row["label"] = {"adopt": "replace", "force": "edited"}.get(action.get("needs"), "update")
            row["lost"] = only_here(path.read_bytes(), path)
        rows.append(row)
    kept, beside = [], []
    for entry in config.get("sync", []):
        dest, source = entry["dest"].rstrip("/"), source_root / entry["source"]
        for name in entry.get("exclude", []):
            if (project / dest / name).is_file():
                kept.append(f"{dest}/{name}")
                rows.append({"dest": f"{dest}/{name}", "label": "kept", "origin": f"{entry['source']}/{name}",
                             "lost": only_here((project / dest / name).read_bytes(), project / dest / name)})
        old = project / inside(project, entry["replaces"]) if entry.get("replaces") else None
        if old and old.is_dir():
            for path in shipped_files(old):
                rows.append({"dest": path.relative_to(project).as_posix(), "label": "old copy", "origin": "",
                             "against": f"{dest}/{path.relative_to(old).as_posix()}",
                             "lost": only_here(path.read_bytes(), path)})
        if source.is_dir() and (project / dest).is_dir():
            beside += [p.relative_to(project).as_posix() for p in shipped_files(project / dest)
                       if p.relative_to(project).as_posix() not in wanted]
    beside = sorted(set(beside) - set(kept))
    # What the project owns and an apply leaves alone: where a carried rule would now be.
    owned = [project / name for name in beside]
    owned += [project / name for name in ("CLAUDE.md", "AGENTS.md") if (project / name).is_file()]
    owned_text = {path.relative_to(project).as_posix(): squeeze(path.read_text(encoding="utf-8", errors="ignore"))
                  for path in owned}
    owned_lines = {name: [line for _, line in kept_lines((project / name).read_bytes())] for name in owned_text}
    first: dict[tuple, str] = {}
    for row in rows:
        row["prose"] = Path(row["dest"]).suffix in PROSE
        row["twin"] = None
        if row["label"] in ("replace", "edited", "update") and row["origin"]:
            key = (row["origin"], digest((project / row["dest"]).read_bytes()))
            row["twin"] = first.get(key)
            first.setdefault(key, row["dest"])
        row["carried"], row["close"] = {}, {}
        if row["lost"] and row["prose"] and not row["twin"]:
            for number, line in row["lost"]:
                home = next((name for name, text in owned_text.items() if len(line) >= 12 and squeeze(line) in text), None)
                home = home or next((name for name, lines in owned_lines.items()
                                     if difflib.get_close_matches(line, lines, n=1, cutoff=0.8)), None)
                if home:
                    row["carried"][number] = home
            against = row.get("against", row["dest"])
            if against in wanted:
                shipped = [line for _, line in kept_lines(wanted[against]["data"])]
                for number, line in row["lost"]:
                    near = difflib.get_close_matches(line, shipped, n=1, cutoff=0.65)
                    if near:
                        row["close"][number] = near[0]
    return rows, beside


def row_note(row: dict) -> str:
    if row["twin"]:
        return f"  same as {row['twin']}: counted there"
    if row["label"] == "kept":
        return "  excluded: stays as it is"
    if row["label"] not in ("replace", "edited", "old copy"):
        return ""
    if not row["prose"]:
        return f"  script or data, {len(row['lost'])} line(s) differ: read it with --diff"
    if not row["lost"]:
        return "  every line is in a shipped file"
    note = f"  {len(row['lost'])} line(s) only the project's copy has"
    extra = [f"{len(row['close'])} close to a shipped line"] if row["close"] else []
    extra += [f"{len(row['carried'])} now in a file the project owns"] if row["carried"] else []
    return note + (f" ({', '.join(extra)})" if extra else "")


def cmd_compare(args) -> int:
    project, source_root = args.project.resolve(), args.source.resolve()
    config = read_config(project)
    wanted = desired_files(source_root, config, project)
    warn_if_dirty(source_root, config)
    rows, beside = compare_rows(project, source_root, config, wanted)
    counted = [row for row in rows if row["label"] in ("replace", "edited", "old copy") and not row["twin"]]
    chosen = [p.rstrip("/") for p in args.paths]
    if (args.diff or args.added) and not chosen:
        raise SyncError("--diff and --added need the path of a file or folder the sync delivers")
    picked = [row for row in rows if any(row["dest"] == p or row["dest"].startswith(p + "/") for p in chosen)]
    if chosen and not picked:
        raise SyncError(f"no file the sync delivers, keeps or replaces is at or under: {', '.join(chosen)}")
    if args.record:
        print("| File | Lines only here | Stated | Carried | Kept file | Changed | Gap | Candidate | Dropped |")
        print("|---|---|---|---|---|---|---|---|---|")
        listed = [row for row in picked or counted + [row for row in rows if row["label"] == "kept"]
                  if row["lost"] and not row["twin"]]
        for row in listed:
            print(f"| `{row['dest']}` | {len(row['lost'])} | | | | | | | |")
        print(f"| Total | {sum(len(row['lost']) for row in listed)} | | | | | | | |")
        return 0
    if chosen:
        for row in picked:
            label, dest = row["label"], row["dest"]
            if row["twin"]:
                print(f"{label:8} {dest}: the same file as {row['twin']}, listed there")
                continue
            if label == "new":
                size = len(wanted[dest]["data"].decode("utf-8", errors="replace").splitlines())
                print(f"{label:8} {dest}: nothing of the project's is replaced. Read the shipped file, "
                      f"{row['origin']} ({size} lines), against how the project works today")
                continue
            if label not in ("replace", "edited", "update", "old copy", "kept"):
                print(f"{label:8} {dest}")
                continue
            old = (project / dest).read_text(encoding="utf-8", errors="replace")
            if args.added:
                against = row.get("against", dest)
                if against not in wanted:
                    continue
                have = {line for _, line in kept_lines(old.encode("utf-8"))}
                flat = squeeze(old)
                new = wanted[against]["data"].decode("utf-8", errors="replace")
                arrives = [(n, line) for n, line in kept_lines(new.encode("utf-8"))
                           if line not in have and not (len(line) >= 12 and squeeze(line) in flat)]
                print(f"{label:8} {dest}: {len(arrives)} line(s) only the shipped file has")
                under, last, raw = (headings(new) if against.endswith(".md") else {}), None, new.splitlines()
                for number, line in arrives:
                    heading = under.get(number, "")
                    if under and heading != last and heading != line:
                        print(f"  under: {heading or '(no heading)'}")
                    last = heading
                    print(f"  {number:>5}: {line if row['prose'] else raw[number - 1].rstrip()}")
                continue
            if args.diff and dest in wanted:
                new = wanted[dest]["data"].decode("utf-8", errors="replace")
                sys.stdout.writelines(difflib.unified_diff(
                    old.splitlines(keepends=True), new.splitlines(keepends=True),
                    f"{dest} (the project's)", f"{dest} (dev-tools)"))
                continue
            print(f"{label:8} {dest}:{row_note(row).removeprefix(' ')}")
            raw = old.splitlines()
            under = headings(old) if dest.endswith(".md") else {}
            last = None
            for number, line in row["lost"]:
                heading = under.get(number, "")
                if under and heading != last and heading != line:
                    print(f"  under: {heading or '(no heading)'}")
                last = heading
                mark = f"   [in {row['carried'][number]}]" if number in row["carried"] else ""
                print(f"  {number:>5}: {line if row['prose'] else raw[number - 1].rstrip()}{mark}")
                if number in row["close"]:
                    print(f"       ~ shipped: {row['close'][number]}")
        return 0
    for row in rows:
        if row["label"] != "same":
            print(f"{row['label']:8} {row['dest']}{row_note(row)}")
    if beside:
        print("\nonly in the project, inside a synced folder (an apply leaves these as they are):")
        for dest in beside:
            print(f"  {dest}")
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["label"]] = counts.get(row["label"], 0) + 1
    order = ["replace", "edited", "update", "old copy", "new", "remove", "kept", "same"]
    summary = ", ".join(f"{counts[label]} {label}" for label in order if label in counts)
    prose = [row for row in counted if row["prose"]]
    text = sum(len(row["lost"]) for row in prose)
    close, carried = sum(len(row["close"]) for row in prose), sum(len(row["carried"]) for row in prose)
    code = sum(len(row["lost"]) for row in counted if not row["prose"])
    print(f"\n{summary}")
    print(f"{text} line(s) of the project's text are in no file the sync delivers"
          f" ({close} close to a shipped line, {carried} now in a file the project owns)"
          + (f"; {code} line(s) differ in scripts and data files" if code else ""))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    apply = sub.add_parser("apply", help="copy the configured files into the project")
    apply.add_argument("--project", type=Path, required=True)
    apply.add_argument("--source", type=Path, default=SOURCE_ROOT, help="dev-tools checkout (default: this one)")
    apply.add_argument("--adopt", action="store_true", help="overwrite existing files that are not managed yet")
    apply.add_argument("--force", action="store_true", help="overwrite managed files changed in the project")
    apply.add_argument("--dry-run", action="store_true")
    apply.set_defaults(run=cmd_apply)
    check = sub.add_parser("check", help="compare the project's managed files with its receipt")
    check.add_argument("--project", type=Path, required=True)
    check.set_defaults(run=cmd_check)
    survey_ = sub.add_parser("survey", help="find the project's own copies of what dev-tools ships")
    survey_.add_argument("--project", type=Path, required=True)
    survey_.add_argument("--source", type=Path, default=SOURCE_ROOT, help="dev-tools checkout (default: this one)")
    survey_.add_argument("--toml", action="store_true", help=f"print a starter {CONFIG} instead of the report")
    survey_.set_defaults(run=cmd_survey)
    compare = sub.add_parser("compare", help="show what an apply would replace, and what the project would lose")
    compare.add_argument("--project", type=Path, required=True)
    compare.add_argument("--source", type=Path, default=SOURCE_ROOT, help="dev-tools checkout (default: this one)")
    compare.add_argument("paths", nargs="*", help="synced files or folders: list the lines only the project has")
    compare.add_argument("--diff", action="store_true", help="with paths: print the full difference instead")
    compare.add_argument("--added", action="store_true",
                         help="with paths: print the lines only the shipped file has (what arrives)")
    compare.add_argument("--record", action="store_true",
                         help="print one table row per file with lines of its own, for the migration record")
    compare.set_defaults(run=cmd_compare)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except SyncError as error:
        print(f"error: {error}", file=sys.stderr)
        return error.code


if __name__ == "__main__":
    sys.exit(main())
