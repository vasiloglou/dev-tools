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

    after_apply = ["python scripts/components_index.py"]  # optional, top level: run when apply changed a file

``apply`` copies the files, writes the settings files and records every managed file in
``.devtools-receipt.json`` (sha256 and mode). It refuses to overwrite a file the project
changed by hand, or one it does not manage yet, unless told to (``--force``, ``--adopt``).
``check`` needs only the project: it compares the managed files with the receipt.

Exit codes: 0 ok; 1 check found drift; 2 usage or configuration; 3 apply refused (nothing written);
4 files were written but an after_apply command failed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
CONFIG = ".devtools.toml"
RECEIPT = ".devtools-receipt.json"
JOURNAL = ".devtools-sync.journal"
SKIP_DIRS = {"__pycache__"}
TOKEN = re.compile(r"\{\{devtools:([a-z_]+)\}\}")


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
        unknown = sorted(set(entry) - {"source", "dest", "settings", "exclude", "values"})
        if unknown or "source" not in entry or "dest" not in entry:
            raise SyncError(f"[[sync]] needs source and dest; unknown keys: {unknown}")
        source = inside(source_root, entry["source"])
        dest = entry["dest"].rstrip("/")
        exclude = set(entry.get("exclude", []))
        values, used = entry.get("values", {}), set()
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


def source_identity(source_root: Path) -> dict:
    def git(*args: str) -> str:
        done = subprocess.run(["git", "-C", str(source_root), *args], capture_output=True, text=True)
        return done.stdout.strip() if done.returncode == 0 else ""
    return {"commit": git("rev-parse", "HEAD") or None, "dirty": bool(git("status", "--porcelain"))}


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
        "source": source_identity(args.source.resolve()),
        "files": {dest: {"sha256": digest(item["data"]), "mode": oct(item["mode"]), "origin": item["origin"]}
                  for dest, item in sorted(wanted.items())},
    }
    write_atomic(project / RECEIPT, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"), 0o644)
    (project / JOURNAL).unlink()
    print("applied:", json.dumps(counts, sort_keys=True))
    if set(counts) - {"keep"}:
        for command in config.get("after_apply", []):
            print("after_apply:", command)
            if subprocess.run(shlex.split(command), cwd=project).returncode != 0:
                print(f"after_apply failed: {command}", file=sys.stderr)
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
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except SyncError as error:
        print(f"error: {error}", file=sys.stderr)
        return error.code


if __name__ == "__main__":
    sys.exit(main())
