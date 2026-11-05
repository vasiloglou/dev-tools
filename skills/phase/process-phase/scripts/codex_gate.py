#!/usr/bin/env python3
"""Check a coding round's changed paths and added-line budget.

``--ignore`` names paths the supervisor writes itself during a round (briefs, run logs);
they are neither checked against the allowlist nor counted.
"""

import argparse
import fnmatch
import subprocess
from pathlib import Path


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow", action="append", required=True)
    parser.add_argument("--max-added", type=int, required=True)
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--ignore", action="append", default=[])
    args = parser.parse_args()
    root = Path(git("rev-parse", "--show-toplevel").decode().strip())
    paths, added, counts = set(), 0, {}
    # Disable rename folding so each changed path is checked independently.
    records = iter(git("-C", str(root), "diff", "--numstat", "-z", "--no-renames", args.base, "--").split(b"\0"))
    for record in records:
        if not record:
            continue
        count, _, path = record.split(b"\t", 2)
        paths.add(path.decode())
        counts[path.decode()] = 0 if count == b"-" else int(count)
        added += counts[path.decode()]
    for raw in git("-C", str(root), "ls-files", "--others", "--exclude-standard", "-z").split(b"\0"):
        if raw:
            path = raw.decode()
            paths.add(path)
            counts[path] = len((root / path).read_bytes().splitlines())
            added += counts[path]
    for path in [p for p in paths if any(fnmatch.fnmatch(p, pattern) for pattern in args.ignore)]:
        paths.discard(path)
        added -= counts[path]
    violations = ["outside allowlist: " + p for p in sorted(paths)
                  if not any(fnmatch.fnmatch(p, pattern) for pattern in args.allow)]
    if added > args.max_added:
        violations.append("added %d lines exceeds max-added %d" % (added, args.max_added))
    if violations:
        print("\n".join(violations))
        return 1
    print("ok %d files, %d added" % (len(paths), added))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
