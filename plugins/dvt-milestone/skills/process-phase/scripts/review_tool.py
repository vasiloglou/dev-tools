#!/usr/bin/env python3
"""review_tool.py: the independent review of the milestone workflow (process-phase skill).

Stdlib only; runs on the system python3 (3.9).

    review_tool.py brief DIR --subject plan|spec|phase|close|pr --question TEXT
                       [--file PATH ...] [--claim TEXT ...] [--base REF] [--pr N]
    review_tool.py run DIR [--reviewer codex|claude] [--wait] [--dry-run]
    review_tool.py status PATH [PATH ...] [--format json]
    review_tool.py post DIR [--pr N] [--yes] [--again]
    review_tool.py sanitize DIR

One review round is one folder, DIR, which ``brief`` creates and nothing rewrites:

- ``BRIEF.md`` states the question without the author's conclusion, lists every file to
  read with its SHA-256, and forbids opening credential files. ``brief.json`` holds the
  same in a form this script reads back. ``--base REF`` (a phase diff) adds the diff
  against REF as ``diff.patch`` and every changed or new file; ``--pr N`` adds the PR's
  diff at its head SHA, read with ``gh``. A file that looks like a credential file is
  refused when named, and left out (with a note) when a diff would have brought it in.
  The brief of a ``phase`` or ``pr`` subject also tells the reviewer to look for code fitted
  to its examples (references/standing-rules.md), whatever the question.
- ``FINDINGS.md`` is the findings ledger, filled in by whoever dispositions the review:
  reproduced or not, class, disposition, and for a fixed finding the commit or tag that
  holds the repaired bytes.

``run`` checks that every file still has the bytes the brief names, then starts the
reviewer in the other harness from the one running this script (``reviewer = "auto"``:
Codex read-only from Claude Code, ``claude -p`` in plan mode from Codex), in the
background, with stdin closed. The reviewer's answer is saved word for word in
``review.md`` and its log in ``review.log``; ``run.json`` records the command (with the
folder as ``{dir}``), the exit and the SHA-256 of the brief and of the review.

``status`` reports each round under the paths given: the run, the ledger, and every
reviewed file whose bytes changed after the last round that read them ("unreviewed"). A
repaired file stays unreviewed until a later round's brief lists its new bytes and that
round's review finishes.

``post`` shows the comment it would put on the PR (the review, its head SHA and the
ledger) and posts it only with ``--yes``, which the owner's approval supplies.
``sanitize`` replaces this machine's absolute paths in ``review.md`` and ``review.log``
before they are committed, and says so at the top of ``review.md``.

Exit codes: 0 ok, 1 a check found something (a changed file, an unfinished ledger, a
failed run, an unreviewed file), 2 the command could not run (usage, no brief, no git, a
settings file it cannot use).

Settings live beside this script, in review_tool.settings.json; when the script runs from a
plugin install, in the project's .devtools/review_tool.settings.json.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def plugin_root(script: Path):
    """The plugin install that holds this script, or None. A plugin keeps it in
    <plugin>/skills/<skill>/scripts/, beside <plugin>/.claude-plugin/plugin.json; a synced copy is
    in a project, under .claude/skills/ or scripts/."""
    folder = script.parents[3] if len(script.parents) > 3 else None
    return folder if folder and script.parent.parent.parent.name == "skills" \
        and (folder / ".claude-plugin" / "plugin.json").is_file() else None


def checkout_root() -> Path:
    """The git checkout that holds the working directory, or the working directory."""
    here = Path.cwd().resolve()
    return next((folder for folder in (here, *here.parents) if (folder / ".git").exists()), here)


# Settings live beside this script in a synced copy. A plugin install is shared by every
# project, so there they are the project's own, in .devtools/.
PLUGIN = plugin_root(Path(__file__).resolve())
SETTINGS_FILE = (checkout_root() / ".devtools" / "review_tool.settings.json" if PLUGIN
                 else Path(__file__).resolve().with_suffix(".settings.json"))
DEFAULT_SETTINGS = {
    # codex, claude, or auto: the other harness from the one this script runs under.
    "reviewer": "auto",
    # The Codex model; empty for Codex's own default.
    "codex_model": "",
    # Codex's model_reasoning_effort: low, medium, high or xhigh.
    "codex_effort": "high",
    # The Claude model for claude -p; an alias such as "opus" or a full model id.
    "claude_model": "opus",
    # A review still running after this many minutes is stopped and recorded as failed.
    "timeout_minutes": 60,
}
SUBJECTS = {
    "plan": "the milestone plan",
    "spec": "a phase spec",
    "phase": "a phase's diff",
    "close": "the milestone close",
    "pr": "a pull request",
}
# The subjects whose brief is a diff of code. Their brief carries FITTED_CHECK, whatever the
# question; the rule it serves is in references/standing-rules.md, "Code fitted to its examples".
DIFF_SUBJECTS = ("phase", "pr")
FITTED_CHECK = [
    "## A standing check: code fitted to its examples", "",
    "Whatever the question above, also look in the code this change adds or changes for a",
    "solution that handles the examples in its tests and fixtures, and not the whole class of",
    "input it is given:", "",
    "- a regular expression, string split, slice or index over structured text (JSON, YAML,",
    "  TOML, source code, paths, command lines) that a parser or an existing reader in this",
    "  repository already reads;",
    "- a pattern over output this project renders itself (a report, a table, a log line), where",
    "  the code could have been handed the data instead;",
    "- a pattern fitted to the fixtures: it matches every committed example and fails on a",
    "  legal input with other whitespace, quoting, casing, nesting, Unicode or a line break;",
    "- a branch on one literal name, file or message, added to make one case pass;",
    "- a second matcher for something an existing helper already does.", "",
    "A regular expression is not a finding in itself: one that states the whole grammar of a",
    "flat token (an identifier, a version number, a hex digest) is the right tool. For each",
    "suspect, build a legal input that the tests and fixtures lack and run the code on it.",
    "Report a finding only with that input: what the code returned and what it should have",
    "returned. A suspicion with no breaking input is style: label it so. In your list of what",
    "you checked, name each matcher you tried and the input you tried it with.", ""]
PROMPT = "Read {dir}/BRIEF.md and follow it."
CLASSES = ("blocking", "hardening", "completeness")
DISPOSITIONS = ("fixed", "deferred", "rejected", "open")
LEDGER_COLUMNS = ["Id", "Finding", "Reproduced", "Class", "Disposition", "Repaired at", "Notes"]
NO_FINDINGS = "No findings."
# Names that hold keys, tokens or passwords. A sample of one (.env.example) is not one.
CREDENTIAL = re.compile(
    r"(^|/)(\.env(\.[^/]*)?|\.envrc|\.netrc|\.npmrc|\.pypirc|\.git-credentials|auth\.json"
    r"|credentials(\.json|\.ya?ml|\.toml|\.ini)?|secrets?\.(json|ya?ml|toml|env)"
    r"|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?|[^/]*\.(pem|key|p12|pfx|jks|keystore))$",
    re.IGNORECASE)
SAMPLE = (".example", ".sample", ".template", ".dist")


class Stop(Exception):
    """The command cannot run; exit 2 with this message."""


def load_settings(path: Path = SETTINGS_FILE) -> dict:
    """The settings, or `Stop` (exit 2: the command could not run) for a file this script cannot use."""
    settings = dict(DEFAULT_SETTINGS)
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise Stop(f"{path}: not valid JSON: {exc}")
        if not isinstance(loaded, dict):
            raise Stop(f"{path}: the settings must be a JSON object")
        unknown = sorted(set(loaded) - set(DEFAULT_SETTINGS))
        if unknown:
            raise Stop("{}: unknown setting(s): {}".format(path, ", ".join(unknown)))
        for key, value in loaded.items():  # each value has its default's type; a list holds strings
            kind = type(DEFAULT_SETTINGS[key])
            if type(value) is not kind or (kind is list and not all(isinstance(item, str) for item in value)):
                raise Stop(f"{path}: {key} must be " + {str: "a string", bool: "true or false", int: "a whole number",
                                                          list: "a list of strings"}[kind])
        settings.update(loaded)
    if settings["reviewer"] not in ("auto", "codex", "claude"):
        raise Stop(f"{path}: reviewer must be auto, codex or claude")
    return settings


def now(precise: bool = False) -> str:
    # datetime.UTC is new in 3.11; this script runs on 3.9 (README).
    stamp = datetime.datetime.now(datetime.timezone.utc)  # noqa: UP017
    return (stamp if precise else stamp.replace(microsecond=0)).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=check,
                          encoding="utf-8", errors="replace")


def repo_root() -> Path:
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                          check=False)
    if proc.returncode != 0:
        raise Stop("not inside a git repository")
    return Path(proc.stdout.strip()).resolve()


def looks_secret(path: str) -> bool:
    return bool(CREDENTIAL.search(path)) and not path.lower().endswith(SAMPLE)


def write_json(path: Path, data: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def shown(root: Path, path: Path) -> str:
    """A path as a brief names it: relative to the repository when inside it."""
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path.resolve())


def unquote(path: str) -> str:
    """A path as git prints it in a diff header: C-quoted when it holds a special byte."""
    if not (len(path) >= 2 and path[0] == path[-1] == '"'):
        return path
    out, i, body = bytearray(), 0, path[1:-1]
    escapes = {"a": 7, "b": 8, "t": 9, "n": 10, "v": 11, "f": 12, "r": 13, '"': 34, "\\": 92}
    while i < len(body):
        if body[i] == "\\" and i + 1 < len(body):
            if body[i + 1] in "01234567" and re.match(r"[0-7]{3}", body[i + 1:i + 4]):
                out.append(int(body[i + 1:i + 4], 8))
                i += 4
                continue
            out.append(escapes.get(body[i + 1], ord(body[i + 1])))
            i += 2
            continue
        out += body[i].encode("utf-8")
        i += 1
    return out.decode("utf-8", errors="replace")


def strip_prefix(path: str) -> str:
    return re.sub(r"^[a-z]/", "", unquote(path))


def header_paths(line: str) -> list[str]:
    """Both paths of a 'diff --git' line, quoted or not."""
    rest = line[len("diff --git "):]
    quoted = re.match(r'("(?:[^"\\]|\\.)*"|\S+) ("(?:[^"\\]|\\.)*")$', rest) or \
        re.match(r'("(?:[^"\\]|\\.)*") (.*)$', rest)
    if quoted:
        return [strip_prefix(quoted.group(1)), strip_prefix(quoted.group(2))]
    half = len(rest) // 2
    if len(rest) % 2 == 1 and rest[half] == " " and rest[:half][2:] == rest[half + 1:][2:]:
        return [strip_prefix(rest[:half]), strip_prefix(rest[half + 1:])]  # a/x y b/x y
    return [strip_prefix(part) for part in rest.split(" ")]


def split_diff(text: str) -> list[tuple[list[str], str]]:
    """(paths, block) for each file of a unified git diff. The paths come from the block's
    header only, the lines before its first hunk, and name both sides of a rename or copy."""
    blocks, paths, lines, header = [], [], [], False
    for line in text.splitlines(keepends=True):
        bare = line.rstrip("\n")
        if line.startswith("diff --git "):
            if lines:
                blocks.append((paths, "".join(lines)))
            paths, lines, header = header_paths(bare), [line], True
            continue
        if header and line.startswith(("@@", "Binary files")):
            header = False
        elif header:
            side = re.match(r"(?:rename|copy) (?:from|to) (.*)$|(?:---|\+\+\+) (.*)$", bare)
            if side:
                path = unquote(side.group(1)) if side.group(1) else strip_prefix(side.group(2))
                if path != "dev/null":
                    paths.append(path)
        lines.append(line)
    if lines:
        blocks.append((paths, "".join(lines)))
    return blocks


def without_secrets(text: str) -> tuple[str, list[str]]:
    """The diff without any block that names a credential file on either side, and every
    path those blocks name: a credential renamed to an innocent name is still one."""
    kept, dropped = [], []
    for paths, block in split_diff(text):
        if any(looks_secret(p) for p in paths):
            dropped += [p for p in dict.fromkeys(paths) if p not in dropped]
        else:
            kept.append(block)
    return "".join(kept), dropped


# --- brief -----------------------------------------------------------------------------

def cmd_brief(args, settings) -> int:
    root = repo_root()
    out = Path(args.dir)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise Stop(f"{args.dir} already exists: a round is never rewritten; start the next round in a new folder")
    if not args.question.strip():
        raise Stop("--question is empty")
    if args.base and args.pr is not None:
        raise Stop("--base and --pr are two different diffs: pass one")
    if args.subject == "pr" and args.pr is None:
        raise Stop("--subject pr needs --pr N")
    if args.subject == "phase" and not args.base:
        raise Stop("--subject phase needs --base REF, the commit the phase began from")
    if args.subject in ("plan", "spec", "close") and not args.file:
        raise Stop(f"--subject {args.subject} needs --file for each file the reviewer must read")

    files, notes, deleted, left_out = [], [], [], []

    def add(rel: str, named: bool) -> None:
        path = (root / rel).resolve()
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            raise Stop(f"{rel} is outside the repository")
        if looks_secret(rel) or rel in tainted:
            if named:
                raise Stop(f"{rel} looks like a credential file; a brief never lists one")
            left_out.append(rel)
            return
        if out.resolve() in path.parents:
            return
        if path.is_dir():
            if named:
                raise Stop(f"{rel} is a folder: name its files")
            return
        if not path.is_file():
            if named:
                raise Stop(f"{rel} does not exist")
            deleted.append(rel)
            return
        if rel not in [f["path"] for f in files]:
            files.append({"path": rel, "sha256": sha256(path)})

    head = git(root, "rev-parse", "HEAD", check=False).stdout.strip()
    dirty = bool(git(root, "status", "--porcelain", "--untracked-files=no", check=False).stdout.strip())
    diff, pr, tainted = None, None, []
    if args.base:
        if git(root, "rev-parse", "--verify", "--quiet", args.base + "^{commit}", check=False).returncode:
            raise Stop(f"--base {args.base} is not a commit here")
        # Which files changed, from git itself (-z: no quoting), with renames found whatever
        # diff.renames says. An entry that names a credential file on either side is left out
        # whole, and only the other entries are diffed.
        fixed = ["-c", "diff.noprefix=false", "-c", "diff.mnemonicPrefix=false", "-c", "diff.renames=true"]
        fields = git(root, *fixed, "diff", "--name-status", "-z", "-M", args.base, "--").stdout.split("\0")
        entries, i = [], 0
        while i < len(fields) and fields[i]:
            width = 3 if fields[i][0] in "RC" else 2
            entries.append(fields[i + 1:i + width])
            i += width
        tainted = [p for entry in entries if any(looks_secret(q) for q in entry) for p in entry]
        kept = [p for entry in entries if not any(looks_secret(q) for q in entry) for p in entry]
        diff = ""
        if kept:
            diff = git(root, *fixed, "diff", "--no-color", "--no-ext-diff", "-M", "--src-prefix=a/",
                       "--dst-prefix=b/", args.base, "--", *[":(literal)" + p for p in kept]).stdout
            diff, more = without_secrets(diff)
            tainted += more
        untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z").stdout.split("\0")
        for rel in [p for p in kept + untracked if p]:
            add(rel, named=False)
        notes += [f"new: {p} (not tracked yet, so not in the diff: read it whole)"
                  for p in untracked if p and any(f["path"] == p for f in files)]
    if args.pr is not None:
        pr = pr_view(args.pr)
        diff, tainted = without_secrets(run_gh(["pr", "diff", str(args.pr)]))
        if pr_view(args.pr)["head"] != pr["head"]:
            raise Stop(f"PR #{args.pr} moved while the brief was written: write it again")
    for rel in args.file:
        add(rel, named=True)

    out.mkdir(parents=True, exist_ok=True)
    if diff is not None:
        left_out += [p for p in tainted if p not in left_out]
        (out / "diff.patch").write_text(diff, encoding="utf-8")
        files.insert(0, {"path": shown(root, out / "diff.patch"), "sha256": sha256(out / "diff.patch")})
    brief = {
        "version": 1,
        "subject": args.subject,
        "question": args.question.strip(),
        "claims": [c.strip() for c in args.claim if c.strip()],
        "created": now(precise=True),
        "head": head,
        "dirty": dirty,
        "base": args.base,
        "pr": pr,
        "files": files,
        "deleted": deleted,
        "left_out": left_out,
        "notes": notes,
    }
    (out / "BRIEF.md").write_text(brief_text(root, out, brief), encoding="utf-8")
    write_json(out / "brief.json", brief)
    (out / "FINDINGS.md").write_text(ledger_text(out), encoding="utf-8")
    for rel in left_out:
        print(f"left out: {rel} (a credential file, or a rename of one)")
    print(f"wrote {args.dir}/BRIEF.md: {len(files):d} files, SHA-256 {sha256(out / 'BRIEF.md')}")
    print(f"next: review_tool.py run {args.dir}")
    return 0


def brief_text(root: Path, out: Path, brief: dict) -> str:
    lines = ["# Review brief: {}".format(SUBJECTS[brief["subject"]]), "",
             "You are an independent reviewer, working in a different tool from the one that produced",
             "this work. Nothing here asks you to agree with it. Answer from the files themselves, not",
             "from any summary of them, including this brief's.", "",
             "## The question", "", brief["question"], ""]
    if brief["claims"]:
        lines += ["## Claims to test", "",
                  "The author claims what follows. For each, try to show where it is false: a claim is",
                  "met only if you looked for the case that breaks it and did not find one.", ""]
        lines += [f"- C{i:d}. {claim}" for i, claim in enumerate(brief["claims"], 1)] + [""]
    lines += ["## The change under review", ""]
    pr, diff = brief["pr"], shown(root, out / "diff.patch")
    if pr:
        lines.append("Pull request #{}, {}, at head `{}` (base `{}`). Its diff is `{}`.".format(pr["number"], pr["url"], pr["head"], pr["base"], diff))
        if brief["head"] == pr["head"] and not brief["dirty"]:
            lines.append("Your checkout is at that head, so the files in it are the PR's.")
        elif brief["head"] == pr["head"]:
            lines.append("Your checkout is at that head, with uncommitted changes. Read a file as the PR has "
                         "it with `git show {}:<path>`.".format(pr["head"]))
        elif git(root, "cat-file", "-e", pr["head"] + "^{commit}", check=False).returncode == 0:
            lines.append("Your checkout is not at that head. Read a file as the PR has it with "
                         "`git show {}:<path>`.".format(pr["head"]))
        else:
            lines.append("The head commit is not in your checkout: judge the diff, and say which "
                         "findings you could not check against the whole file.")
    elif brief["base"]:
        lines.append("The work from `{}` to the working tree at `{}`{}. Its diff is `{}`.".format(brief["base"], brief["head"][:12],
                        " with uncommitted changes" if brief["dirty"] else "", diff))
    else:
        lines.append("The files below, as they stand at `{}`{}.".format(brief["head"][:12], " with uncommitted changes" if brief["dirty"] else ""))
    lines += [f"- {note}" for note in brief["notes"]]
    lines += [f"- deleted: {rel}" for rel in brief["deleted"]]
    lines += [f"- left out: {rel} (a credential file, or a rename of one; do not open it)" for rel in brief["left_out"]]
    lines += ["", "## What to read", "",
              "Paths are relative to the repository root, the directory you start in. Before you rely",
              "on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in",
              "your answer: you are not reading the bytes this brief names.", "",
              "| File | SHA-256 |", "|---|---|"]
    lines += ["| `{}` | `{}` |".format(f["path"], f["sha256"]) for f in brief["files"]]
    lines += ["", "You may read anything else in the repository that helps you answer.", ""]
    if brief["subject"] in DIFF_SUBJECTS:
        lines += FITTED_CHECK
    lines += ["## Rules", "",
              "- Read only. Do not edit, create, stage, commit, push or post anything.",
              "- Do not open `.env` files, keys, tokens, `auth.json` or any other credential file, and do",
              "  not print environment variables. If you need one, name it and go on without it.",
              "- A finding names its file and line and the consequence someone would observe. Run what",
              "  you can to show it; where you only read, say so.", "",
              "## What to return", "",
              "1. Findings, each with an id (F1, F2, ...), file and line, what is wrong, the observable",
              "   consequence, and how to reproduce it. A finding with no observable consequence is",
              "   style: label it so.",
              "2. What you checked and found true.",
              "3. What you could not check, and why.",
              "4. A last line: `VERDICT: APPROVE` or `VERDICT: CHANGES_REQUESTED`.", ""]
    return "\n".join(lines)


def ledger_text(out: Path) -> str:
    return "\n".join([
        f"# Findings ledger: {out.name}", "",
        "One row per finding the review returned, under the reviewer's own id. Fill every cell:", "",
        "- Reproduced: yes or no. A finding is believed only once it is reproduced against the bytes.",
        "- Class: blocking, hardening or completeness, assigned here, not by the reviewer",
        "  (review-convergence.md).",
        "- Disposition: fixed, deferred, rejected or open.",
        "- Repaired at: for a fixed finding, the commit or tag that holds the repaired bytes. Those",
        "  bytes are unreviewed until a later round reads them; `review_tool.py status` says which.",
        "- Notes: the regression test for a fixed finding, the target for a deferred one, the reason",
        "  for a rejected one.", "",
        f"If the review returned no findings, replace the table with the line: {NO_FINDINGS}", "",
        "| " + " | ".join(LEDGER_COLUMNS) + " |",
        "|" + "---|" * len(LEDGER_COLUMNS), ""])


# --- run -------------------------------------------------------------------------------

def load_brief(path: str) -> tuple[Path, dict]:
    out = Path(path)
    brief = read_json(out / "brief.json")
    if not brief:
        raise Stop(f"{path} has no brief.json: write one with review_tool.py brief")
    return out, brief


def changed_files(root: Path, out: Path, brief: dict) -> list[str]:
    problems = []
    for f in brief["files"]:
        path = root / f["path"] if not os.path.isabs(f["path"]) else Path(f["path"])
        if not path.is_file():
            problems.append("missing: {}".format(f["path"]))
        elif sha256(path) != f["sha256"]:
            problems.append("changed since the brief: {}".format(f["path"]))
    return problems


def pick_reviewer(args, settings) -> str:
    name = args.reviewer or settings["reviewer"]
    if name != "auto":
        return name
    if os.environ.get("CLAUDECODE"):
        return "codex"
    if any(key.startswith("CODEX_") for key in os.environ):
        return "claude"
    raise Stop("reviewer = auto, and neither Claude Code nor Codex is running this: pass --reviewer")


def command(name: str, settings: dict) -> tuple[list[str], str]:
    """The reviewer's argv with the brief folder as {dir}, and the file its stdout goes to."""
    if name == "codex":
        argv = ["codex", "exec", "--ephemeral"]
        if settings["codex_model"]:
            argv += ["-m", settings["codex_model"]]
        argv += ["-c", 'model_reasoning_effort="{}"'.format(settings["codex_effort"]), "--sandbox", "read-only",
                 "--color", "never", "--skip-git-repo-check", "--add-dir", "{dir}",
                 "-o", "{dir}/review.md", PROMPT]
        return argv, "review.log"
    return ["claude", "-p", "--model", settings["claude_model"], "--permission-mode", "plan",
            "--add-dir", "{dir}", PROMPT], "review.md"


def preconditions(name: str) -> list[str]:
    if not shutil.which(name):
        return [f"{name} is not on PATH"]
    if name == "codex":
        proc = subprocess.run(["codex", "login", "status"], stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, check=False)
        if proc.returncode != 0:
            return [f"codex login status exited {proc.returncode:d}: log in to Codex first"]
    return []


def cmd_run(args, settings) -> int:
    root = repo_root()
    out, brief = load_brief(args.dir)
    run = read_json(out / "run.json")
    if run and not args.dry_run:
        raise Stop("{} was already run ({}): a new round is a new brief".format(args.dir, run.get("state")))
    name = pick_reviewer(args, settings)
    argv, stdout = command(name, settings)
    if args.dry_run:
        print(shlex.join(part.replace("{dir}", shown(root, out)) for part in argv))
        return 0
    problems = changed_files(root, out, brief) or preconditions(name)
    if problems:
        print("\n".join(problems))
        print("not started: nothing was launched")
        return 1
    run = {"state": "starting", "reviewer": name, "argv": argv, "stdout": stdout,
           "model": settings["codex_model"] or "codex default" if name == "codex" else settings["claude_model"],
           "effort": settings["codex_effort"] if name == "codex" else "",
           "timeout_minutes": settings["timeout_minutes"],
           "brief_sha256": sha256(out / "BRIEF.md"), "started": now()}
    write_json(out / "run.json", run)
    if args.wait:
        return watch(root, out)
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_watch", str(out.resolve())],
                     cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    print(f"started {name} on {args.dir} in the background; review_tool.py status {args.dir}")
    return 0


def watch(root: Path, out: Path) -> int:
    run = read_json(out / "run.json")
    run.update(state="running", pid=os.getpid())
    write_json(out / "run.json", run)
    changed = changed_files(root, out, read_json(out / "brief.json"))
    if changed:  # the bytes moved between run's check and this start
        run.update(state="failed", exit=None, finished=now(), review_sha256=None,
                   note="not started: " + "; ".join(changed))
        write_json(out / "run.json", run)
        return 1
    argv = [part.replace("{dir}", str(out.resolve())) for part in run["argv"]]
    note, code = "", None
    with contextlib.ExitStack() as files:
        log = files.enter_context(open(out / "review.log", "ab"))
        sink = log if run["stdout"] == "review.log" else files.enter_context(open(out / run["stdout"], "wb"))
        try:
            code = subprocess.run(argv, cwd=root, stdin=subprocess.DEVNULL, stdout=sink, stderr=log,
                                  timeout=run["timeout_minutes"] * 60, check=False).returncode
        except subprocess.TimeoutExpired:
            note = "stopped after {} minutes".format(run["timeout_minutes"])
        except OSError as error:
            note = str(error)
    review = out / "review.md"
    if code == 0 and not (review.is_file() and review.read_text(encoding="utf-8", errors="replace").strip()):
        note = "the reviewer exited 0 and wrote no review"
    run.update(state="done" if code == 0 and not note else "failed", exit=code, finished=now(),
               review_sha256=sha256(review) if review.is_file() else None)
    if note:
        run["note"] = note
    write_json(out / "run.json", run)
    return 0 if run["state"] == "done" else 1


# --- status ----------------------------------------------------------------------------

def rounds(paths: list[str]) -> list[Path]:
    found = []
    for path in map(Path, paths):
        if (path / "brief.json").is_file():
            found.append(path)
        elif path.is_dir():
            found += sorted(p.parent for p in path.rglob("brief.json"))
        else:
            raise Stop(f"{path} is not a review round or a folder of them")
    return found


def alive(pid) -> bool:
    try:
        os.kill(int(pid), 0)
    except (OSError, TypeError, ValueError):
        return False
    return True


def run_state(run: dict) -> str:
    state = run.get("state", "not run")
    if state in ("starting", "running") and not alive(run.get("pid")):
        return "stopped" if run.get("pid") else state
    return state


def split_row(line: str) -> list[str]:
    """The cells of a table row, with or without its outer pipes."""
    line = line.strip()
    line = line.removeprefix("|")
    line = line[:-1] if line.endswith("|") and not line.endswith("\\|") else line
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def ledger_rows(text: str) -> list[dict]:
    """The rows of the findings table: from its Id header to the next heading or table,
    blank lines and rows written without their outer pipes included."""
    rows, header, separators = [], None, 0
    for line in text.splitlines():
        bare = line.strip()
        if header is None:
            if bare.startswith("|") and split_row(bare)[:1] == ["Id"]:
                header = split_row(bare)
            continue
        if bare.startswith("#"):
            break
        if "|" not in bare:
            continue
        cells = split_row(bare)
        if all(c and set(c) <= set("-: ") for c in cells):
            separators += 1
            if separators > 1:  # a new table began: the row before this line was its header
                rows.pop()
                break
            continue
        rows.append(dict(zip(header, cells + [""] * (len(header) - len(cells)))))
    return rows


def says_none(text: str) -> bool:
    return any(line.strip() == NO_FINDINGS for line in text.splitlines())


def ledger_problems(root: Path, out: Path, finished: bool) -> tuple[list[dict], list[str]]:
    path = out / "FINDINGS.md"
    if not path.is_file():
        return [], ["no FINDINGS.md"] if finished else []
    text = path.read_text(encoding="utf-8")
    rows, problems = ledger_rows(text), []
    if finished and not rows and not says_none(text):
        problems.append(f"the ledger has no rows: fill it, or write the line '{NO_FINDINGS}'")
    for row in rows:
        fid = row.get("Id") or "a row with no id"
        blank = [c for c in LEDGER_COLUMNS[:5] if not row.get(c)]
        if blank:
            problems.append("{}: fill {}".format(fid, ", ".join(blank)))
            continue
        reproduced, kind, disposition = (row["Reproduced"].lower(), row["Class"].lower(),
                                         row["Disposition"].lower())
        if reproduced not in ("yes", "no"):
            problems.append("{}: Reproduced is yes or no, not {!r}".format(fid, row["Reproduced"]))
        if kind not in CLASSES:
            problems.append("{}: Class is one of {}, not {!r}".format(fid, ", ".join(CLASSES), row["Class"]))
        if disposition not in DISPOSITIONS:
            problems.append("{}: Disposition is one of {}, not {!r}".format(fid, ", ".join(DISPOSITIONS), row["Disposition"]))
        elif disposition == "open":
            problems.append(f"{fid}: still open")
        elif disposition == "fixed":
            if reproduced == "no":
                problems.append(f"{fid}: fixed, but not reproduced")
            where = row.get("Repaired at", "").strip("` ")
            if not where:
                problems.append(f"{fid}: fixed, with no commit or tag for the repaired bytes")
            elif git(root, "rev-parse", "--verify", "--quiet", where + "^{commit}", check=False).returncode:
                problems.append(f"{fid}: Repaired at {where!r} is not a commit or tag here")
            if not row.get("Notes"):
                problems.append(f"{fid}: fixed, with no regression test in Notes")
        elif disposition in ("deferred", "rejected") and not row.get("Notes"):
            problems.append("{}: {}, with no {} in Notes".format(fid, disposition,
                                                            "target" if disposition == "deferred" else "reason"))
    return rows, problems


def cmd_status(args, settings) -> int:
    root = repo_root()
    found = rounds(args.paths)
    if not found:
        raise Stop("no review rounds under {}".format(", ".join(args.paths)))
    home = str(Path.home())
    report, latest = [], {}
    # Oldest first, ties by folder name, so the order the paths were given never matters.
    found = sorted({p.resolve() for p in found},
                   key=lambda p: (read_json(p / "brief.json").get("created", ""), p.as_posix()))
    for out in found:
        brief, run = read_json(out / "brief.json"), read_json(out / "run.json")
        state = run_state(run)
        rows, problems = ledger_problems(root, out, state == "done")
        if state == "not run":
            problems.insert(0, f"not run yet: review_tool.py run {shown(root, out)}")
        elif state in ("starting", "running"):
            problems.insert(0, f"still {state}")
        elif state in ("failed", "stopped"):
            problems.insert(0, "the review {}{}: see review.log".format(
                state, " ({})".format(run.get("note")) if run.get("note") else
                " (exit {})".format(run.get("exit")) if run.get("exit") is not None else ""))
        review = out / "review.md"
        if state == "done":
            if not review.is_file() or not review.read_text(encoding="utf-8", errors="replace").strip():
                problems.append("review.md is missing or empty")
            elif sha256(review) not in (run.get("review_sha256"), run.get("sanitized_sha256")):
                problems.append("review.md is not the reviewer's output: its SHA-256 matches neither run.json "
                                "digest")
            if not (out / "BRIEF.md").is_file() or sha256(out / "BRIEF.md") != run.get("brief_sha256"):
                problems.append("BRIEF.md changed after the review read it")
        if review.is_file() and home in review.read_text(encoding="utf-8", errors="replace"):
            problems.append(f"review.md names this machine's home folder: review_tool.py sanitize {out}")
        report.append({"round": shown(root, out), "subject": brief.get("subject"), "state": state,
                       "reviewer": run.get("reviewer"), "model": run.get("model"),
                       "findings": len(rows), "problems": problems})
        own = [f for f in brief.get("files", []) if (root / f["path"]).resolve().parent == out.resolve()]
        problems += changed_files(root, out, {"files": own})  # the round's own diff.patch
        for f in brief.get("files", []):
            if f["path"] not in latest or brief["created"] >= latest[f["path"]][0]:
                latest[f["path"]] = (brief["created"], shown(root, out), f["sha256"], state)
    coverage = []
    for rel, (_, where, digest, state) in sorted(latest.items()):
        path = root / rel
        if not path.is_file():
            coverage.append({"path": rel, "state": "missing", "round": where})
        elif sha256(path) != digest:
            coverage.append({"path": rel, "state": "unreviewed", "round": where,
                             "why": f"changed since {where} read {digest[:12]}"})
        elif state != "done":
            coverage.append({"path": rel, "state": "unreviewed", "round": where,
                             "why": f"{where} has no finished review"})
        else:
            coverage.append({"path": rel, "state": "reviewed", "round": where})
    bad = any(r["problems"] for r in report) or any(c["state"] != "reviewed" for c in coverage)
    if args.format == "json":
        print(json.dumps({"rounds": report, "coverage": coverage, "ok": not bad}, indent=2))
        return 1 if bad else 0
    for r in report:
        who = " by {} ({})".format(r["reviewer"], r["model"]) if r["reviewer"] else ""
        print(f"{r['round']}: {r['subject']} review{who}, {r['state']}, "
              f"{r['findings']:d} finding(s) in the ledger")
        for problem in r["problems"]:
            print(f"  problem: {problem}")
    for c in coverage:
        print("{}: {}{}".format(c["state"], c["path"], " ({})".format(c["why"]) if c.get("why") else
                            " ({})".format(c["round"])))
    return 1 if bad else 0


# --- post and sanitize -----------------------------------------------------------------

def run_gh(args: list[str]) -> str:
    if not shutil.which("gh"):
        raise Stop("gh is not on PATH")
    proc = subprocess.run(["gh", *args], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                          check=False)
    if proc.returncode != 0:
        raise Stop(f"gh {' '.join(args[:2])} exited {proc.returncode:d}: {proc.stderr.strip()}")
    return proc.stdout


def pr_view(number) -> dict:
    data = json.loads(run_gh(["pr", "view", str(number), "--json", "number,url,title,headRefOid,baseRefOid"]))
    return {"number": data["number"], "url": data["url"], "title": data["title"],
            "head": data["headRefOid"], "base": data["baseRefOid"]}


def cmd_post(args, settings) -> int:
    repo_root()
    out, brief = load_brief(args.dir)
    run = read_json(out / "run.json")
    if run_state(run) != "done":
        raise Stop(f"{args.dir} has no finished review to post")
    number = args.pr if args.pr is not None else (brief.get("pr") or {}).get("number")
    if number is None:
        raise Stop("pass --pr N: this round is not a PR review")
    if (out / "posted.json").is_file() and not args.again:
        raise Stop("already posted ({}): pass --again to post once more".format(read_json(out / "posted.json").get("url")))
    review = sha256(out / "review.md") if (out / "review.md").is_file() else None
    if review not in (run.get("review_sha256"), run.get("sanitized_sha256")):
        raise Stop("review.md is not the reviewer's output (see review_tool.py status): nothing posted")
    reviewed = (brief.get("pr") or {}).get("head") or brief.get("head")
    current = pr_view(number)["head"]
    lines = ["**Independent review** by {} ({}) of `{}`.".format(run["reviewer"], run["model"], reviewed),
             "Brief SHA-256 `{}`, review SHA-256 `{}`{}.".format(
                 run["brief_sha256"], run["review_sha256"],
                 f" (sanitized, SHA-256 `{review}`)" if review != run["review_sha256"] else "")]
    if current != reviewed:
        lines.append(f"> The PR head is now `{current}`. This review did not read it.")
    lines += ["", (out / "review.md").read_text(encoding="utf-8").rstrip(), ""]
    ledger = (out / "FINDINGS.md").read_text(encoding="utf-8") if (out / "FINDINGS.md").is_file() else ""
    if ledger_rows(ledger) or says_none(ledger):
        lines += ["<details><summary>Findings ledger</summary>", "", ledger.rstrip(), "", "</details>", ""]
    body = "\n".join(lines)
    if len(body) > 60000:
        raise Stop(f"the comment would be {len(body):d} characters, over GitHub's limit: "
                   "post a shorter one by hand")
    if not args.yes:
        print(body)
        print(f"\nnot posted: run again with --yes once the owner approves posting this to PR #{number}")
        return 0
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as handle:
        handle.write(body)
    try:
        url = run_gh(["pr", "comment", str(number), "--body-file", handle.name]).strip()
    finally:
        os.unlink(handle.name)
    write_json(out / "posted.json", {"pr": number, "url": url, "posted": now(), "head": current})
    print(f"posted: {url}")
    return 0


def cmd_sanitize(args, settings) -> int:
    root = repo_root()
    out, _ = load_brief(args.dir)
    places = [(str(root), "<repo>"), (str(Path.home()), "<home>")]
    for name in ("review.md", "review.log"):
        path = out / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        count = 0
        for real, placeholder in places:
            count += text.count(real)
            text = text.replace(real, placeholder)
        if not count:
            print(f"{name}: nothing to replace")
            continue
        if name == "review.md":
            text = (f"<!-- Edited by review_tool.py sanitize: {count:d} absolute path(s) replaced with <repo> "
                    "or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of "
                    "the original. -->\n") + text
        path.write_text(text, encoding="utf-8")
        if name == "review.md":
            run = read_json(out / "run.json")
            if run:
                run["sanitized_sha256"] = sha256(path)
                write_json(out / "run.json", run)
        print(f"{name}: replaced {count:d} absolute path(s)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    brief = sub.add_parser("brief", help="write a round's brief and ledger")
    brief.add_argument("dir")
    brief.add_argument("--subject", choices=sorted(SUBJECTS), required=True)
    brief.add_argument("--question", required=True)
    brief.add_argument("--file", action="append", default=[])
    brief.add_argument("--claim", action="append", default=[])
    brief.add_argument("--base")
    brief.add_argument("--pr", type=int)
    run = sub.add_parser("run", help="start the reviewer in the other harness")
    run.add_argument("dir")
    run.add_argument("--reviewer", choices=("codex", "claude"))
    run.add_argument("--wait", action="store_true", help="run in the foreground")
    run.add_argument("--dry-run", action="store_true", help="print the command and start nothing")
    status = sub.add_parser("status", help="report rounds, ledgers and unreviewed files")
    status.add_argument("paths", nargs="+")
    status.add_argument("--format", choices=("text", "json"), default="text")
    post = sub.add_parser("post", help="post a round's review on its PR")
    post.add_argument("dir")
    post.add_argument("--pr", type=int)
    post.add_argument("--yes", action="store_true", help="post: the owner approved it")
    post.add_argument("--again", action="store_true")
    sanitize = sub.add_parser("sanitize", help="replace this machine's paths in the saved review")
    sanitize.add_argument("dir")
    watch_parser = sub.add_parser("_watch")
    watch_parser.add_argument("dir")
    args = parser.parse_args(argv)
    try:
        if args.command == "_watch":
            return watch(repo_root(), Path(args.dir))
        settings = load_settings()
        return {"brief": cmd_brief, "run": cmd_run, "status": cmd_status, "post": cmd_post,
                "sanitize": cmd_sanitize}[args.command](args, settings)
    except Stop as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
