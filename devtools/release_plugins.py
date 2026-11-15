#!/usr/bin/env python3
"""Release the Claude Code plugins in plugins/ (dvt-phase, dvt-milestone).

Claude Code keeps an installed plugin until its version changes, so every change to the
skills ships under a new version. A release takes two steps, matching how changes land:

    python3 devtools/release_plugins.py status
        The released version, the version in the tree, and whether plugins/ changed since
        the last release (a release is due).

    python3 devtools/release_plugins.py bump [patch|minor|major|X.Y.Z]
        On the branch with the change: writes devtools/PLUGIN_VERSION and rebuilds plugins/.
        Commit the result with the change, so the pull request carries the new version.

    python3 devtools/release_plugins.py tag [--push] [--github] [--dry-run]
        On main, after the pull request is merged: checks the tree is clean, plugins/ is what
        a build writes and the version is not released yet, then creates the annotated tag
        plugins-vX.Y.Z with notes from the commits since the last release. --push pushes the
        tag to origin; --github also creates the GitHub release (needs gh). Without them
        nothing leaves this machine.

Exit codes: 0 ok; 1 status found a release is due; 2 the step cannot run.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_plugins", ROOT / "devtools" / "build_plugins.py")
build_plugins = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_plugins)
PREFIX = "plugins-v"
RELEASE_BRANCH = "main"
# What a plugin is built from: a change here changes plugins/.
SOURCES = ["plugins", "skills", "agents", "devtools/build_plugins.py", "devtools/PLUGIN_VERSION"]


class Stop(Exception):
    """The step cannot run; exit 2 with this message."""


def git(*args: str, check: bool = True) -> str:
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and done.returncode != 0:
        raise Stop(f"git {' '.join(args)}: {(done.stderr or done.stdout).strip()}")
    return done.stdout.strip() if done.returncode == 0 else ""


def released() -> list[tuple[tuple[int, int, int], str]]:
    """Every release tag, oldest first, as (version, tag)."""
    tags = []
    for tag in git("tag", "--list", PREFIX + "*").splitlines():
        match = build_plugins.SEMVER.match(tag[len(PREFIX):])
        if match:
            tags.append((tuple(int(n) for n in match.groups()), tag))
    return sorted(tags)


def parse(version: str) -> tuple[int, int, int]:
    match = build_plugins.SEMVER.match(version)
    if not match:
        raise Stop(f"{version!r} is not a version like 1.2.3")
    return tuple(int(n) for n in match.groups())


def next_version(current: str, part: str) -> str:
    if build_plugins.SEMVER.match(part):
        if parse(part) <= parse(current):
            raise Stop(f"{part} is not above the current version {current}")
        return part
    major, minor, patch = parse(current)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise Stop(f"bump takes patch, minor, major or a version, not {part!r}")


def only_version(tag: str, path: str) -> bool:
    """True when a plugin manifest differs from the tag's in its version alone."""
    if not path.endswith("/.claude-plugin/plugin.json") or not (ROOT / path).is_file():
        return False
    try:
        before = json.loads(git("show", f"{tag}:{path}", check=False) or "null")
        after = json.loads((ROOT / path).read_text(encoding="utf-8"))
    except ValueError:
        return False
    if not isinstance(before, dict) or not isinstance(after, dict):
        return False
    before.pop("version", None)
    after.pop("version", None)
    return before == after


def changed_since(tag: str) -> list[str]:
    """Files under plugins/ that differ between the tag and the working tree. A manifest whose
    version alone changed is not a change: a bump with nothing in it is no release."""
    paths = [line for line in git("diff", "--name-only", tag, "--", "plugins").splitlines() if line]
    return [path for path in paths if not only_version(tag, path)]


def cmd_status(args) -> int:
    tags = released()
    current = build_plugins.version()
    print(f"version in the tree: {current}")
    if not tags:
        print("released: none yet")
        print("a release is due: run `release_plugins.py tag` on main")
        return 1
    last = tags[-1][1]
    print(f"released: {last[len(PREFIX):]} ({last})")
    changed = changed_since(last)
    stale = build_plugins.stale(build_plugins.build())
    if stale:
        print(f"plugins/ is stale ({len(stale)} file(s)): run `python3 devtools/build_plugins.py`")
    if not changed and not stale:
        print("no change since the last release")
        return 0
    print(f"{len(changed)} plugin file(s) changed since {last}")
    if parse(current) <= tags[-1][0]:
        print("a release is due: run `release_plugins.py bump` on the branch with the change")
    else:
        print(f"{current} is ready: after the merge, run `release_plugins.py tag` on {RELEASE_BRANCH}")
    return 1


def cmd_bump(args) -> int:
    current = build_plugins.version()
    tags = released()
    floor = max(parse(current), tags[-1][0] if tags else (0, 0, 0))
    new = next_version(".".join(map(str, floor)), args.part)
    build_plugins.VERSION_FILE.write_text(new + "\n", encoding="utf-8")
    build_plugins.main([])
    print(f"plugins: {current} -> {new}; commit devtools/PLUGIN_VERSION and plugins/ with the change")
    return 0


def notes(previous: str | None, version: str) -> str:
    """The commits since the last release that touched what the plugins are built from. The first
    release has no earlier one to count from, and its history predates the plugins, so it says so."""
    if not previous:
        return f"dvt plugins {version}\n\n- First release.\n"
    log = git("log", "--no-merges", "--format=- %s (%h)", f"{previous}..HEAD", "--", *SOURCES)
    return f"dvt plugins {version}\n\n" + (log or "- No commit message names the change.") + "\n"


def cmd_tag(args) -> int:
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != RELEASE_BRANCH and not args.any_branch:
        raise Stop(f"on {branch}: tag releases from {RELEASE_BRANCH} (--any-branch to override)")
    if git("status", "--porcelain"):
        raise Stop("the working tree has changes: commit or set them aside first")
    stale = build_plugins.stale(build_plugins.build())
    if stale:
        raise Stop(f"plugins/ is stale ({len(stale)} file(s)): run `python3 devtools/build_plugins.py` and commit")
    version = build_plugins.version()
    tag = PREFIX + version
    tags = released()
    if any(name == tag for _, name in tags):
        raise Stop(f"{tag} exists: run `release_plugins.py bump` on a branch first")
    if tags and parse(version) <= tags[-1][0]:
        raise Stop(f"{version} is not above the last release {tags[-1][1]}")
    previous = tags[-1][1] if tags else None
    if previous and not changed_since(previous):
        raise Stop(f"plugins/ has not changed since {previous}: nothing to release")
    text = notes(previous, version)
    if args.dry_run:
        print(f"would tag {tag} at {git('rev-parse', '--short', 'HEAD')}:\n\n{text}")
        return 0
    git("tag", "-a", tag, "-m", text)
    print(f"tagged {tag}")
    if args.push or args.github:
        git("push", "origin", tag)
        print(f"pushed {tag} to origin")
    if args.github:
        if not shutil.which("gh"):
            raise Stop("gh is not installed: the tag is pushed; create the release on GitHub by hand")
        done = subprocess.run(["gh", "release", "create", tag, "--title", f"dvt plugins {version}",
                               "--notes", text], cwd=ROOT, capture_output=True, text=True)
        if done.returncode != 0:
            raise Stop(f"gh release create: {(done.stderr or done.stdout).strip()}")
        print(done.stdout.strip())
    if not (args.push or args.github):
        print(f"not pushed: git push origin {tag} (or rerun with --push / --github)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="say whether a release is due")
    bump = sub.add_parser("bump", help="raise the version and rebuild plugins/")
    bump.add_argument("part", nargs="?", default="patch", help="patch (default), minor, major or X.Y.Z")
    tag = sub.add_parser("tag", help="tag the version in the tree as a release")
    tag.add_argument("--push", action="store_true", help="push the tag to origin")
    tag.add_argument("--github", action="store_true", help="push the tag and create the GitHub release")
    tag.add_argument("--dry-run", action="store_true", help="print the tag and its notes; change nothing")
    tag.add_argument("--any-branch", action="store_true", help=f"allow a branch other than {RELEASE_BRANCH}")
    args = parser.parse_args(argv)
    try:
        return {"status": cmd_status, "bump": cmd_bump, "tag": cmd_tag}[args.command](args)
    except Stop as exc:
        print(f"release_plugins.py {args.command}: {exc}", file=sys.stderr)
        return 2
    except SystemExit as exc:  # the build could not run
        if isinstance(exc.code, int):
            raise
        print(f"release_plugins.py {args.command}: {exc.code}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
