#!/usr/bin/env python3
"""coder_pool.py: the coding assistants Implement may use, and how many at once (process-phase skill).

Stdlib only; runs on the system python3 (3.9).

    coder_pool.py show [--json] [--root DIR]

The pool comes from two TOML files of the same shape: the team's, checked in, and the
developer's own, gitignored. Tables merge; a scalar or a list in the developer's file
replaces the team's. A linked git worktree with no file of its own reads the main
checkout's. Only coders found on PATH are kept, and with none left the pool is the
Claude Code coder.

    [roles]
    coders = ["codex", "gemini"]     # in preference order

    [parallel]
    max_tracks = 4
    max_sessions_per_account = 4

    [coders.codex]                   # every key is optional
    model = "<model id>"
    effort = "medium"
    risk = "any"                     # "medium": medium-risk tracks only
    accounts = [{ name = "A" }, { name = "B", env = { CODEX_HOME = "~/.codex-b" } }]

A coder with no model or effort takes them from a [tools.<name>] table when the files
have one. Other tables and keys are ignored, so the files may hold more than the pool.

Exit codes: 0 ok (an empty pool too: read the warnings), 1 a settings or configuration
file cannot be used, 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.9 and 3.10
    tomllib = None

# Project settings live beside this script, as for phase_tool.py.
SETTINGS_FILE = Path(__file__).resolve().with_suffix(".settings.json")
DEFAULT_SETTINGS = {
    # The team's file, checked in. Never put keys, tokens or personal paths in it.
    "team_config": ".devtools/coders.toml",
    # The developer's file, same shape, gitignored. Accounts and their homes go here.
    "local_config": ".devtools/coders.local.toml",
}


def load_settings(path: Path = SETTINGS_FILE) -> dict:
    settings = dict(DEFAULT_SETTINGS)
    if path.is_file():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        unknown = sorted(set(loaded) - set(DEFAULT_SETTINGS))
        if unknown:
            raise SystemExit("%s: unknown setting(s): %s" % (path, ", ".join(unknown)))
        settings.update(loaded)
    return settings


SETTINGS = load_settings()
TEAM_CONFIG = SETTINGS["team_config"]
LOCAL_CONFIG = SETTINGS["local_config"]

# The coders references/implement.md has a command line for.
KNOWN_TOOLS = ("claude", "codex", "gemini")
FALLBACK_TOOL = "claude"
# What a project gets when neither file names a coder or a limit.
DEFAULT_CODERS = ["codex"]
DEFAULT_LIMIT = 4
LIMITS = ("max_tracks", "max_sessions_per_account")


# --------------------------------------------------------------------------- reading TOML


class SubsetReader:
    """Reads the part of TOML these files use, for a Python with no tomllib (before 3.11):
    tables, arrays of tables, one-line strings, decimal numbers, booleans, arrays and inline
    tables. Anything else is an error that names the line."""

    BARE_KEY = re.compile(r"[A-Za-z0-9_-]+")
    WORD = re.compile(r"[A-Za-z0-9_+.:-]+")
    INTEGER = re.compile(r"[+-]?(0|[1-9](_?[0-9])*)")
    FLOAT = re.compile(r"[+-]?(0|[1-9](_?[0-9])*)(\.[0-9](_?[0-9])*)?([eE][+-]?[0-9](_?[0-9])*)?")
    ESCAPES = {'"': '"', "\\": "\\", "b": "\b", "t": "\t", "n": "\n", "f": "\f", "r": "\r"}

    def __init__(self, text: str, name: str):
        self.text, self.name, self.pos = text, name, 0
        self.root: dict = {}
        self.table = self.root
        self.headers: list = []  # tables a [header] has opened; a second one is an error

    def fail(self, message: str):
        line = self.text.count("\n", 0, self.pos) + 1
        raise SystemExit("%s:%d: %s" % (self.name, line, message))

    def peek(self) -> str:
        return self.text[self.pos:self.pos + 1]

    def skip(self, newlines: bool = False) -> None:
        """Move past blanks and comments, and past line ends when asked."""
        while self.peek():
            char = self.peek()
            if char in " \t" or (newlines and char in "\r\n"):
                self.pos += 1
            elif char == "#":
                end = self.text.find("\n", self.pos)
                self.pos = len(self.text) if end < 0 else end
            else:
                break

    def expect(self, token: str) -> None:
        if not self.text.startswith(token, self.pos):
            self.fail("expected %r" % token)
        self.pos += len(token)

    def end_of_line(self) -> None:
        self.skip()
        if self.peek() not in ("", "\r", "\n"):
            self.fail("unexpected text after the value")

    def string(self) -> str:
        quote = self.peek()
        if self.text.startswith(quote * 3, self.pos):
            self.fail("a multi-line string is not read on a Python older than 3.11")
        self.pos += 1
        out = []
        while True:
            char = self.peek()
            if char in ("", "\n"):
                self.fail("string without a closing quote")
            self.pos += 1
            if char == quote:
                return "".join(out)
            if char == "\\" and quote == '"':
                escape = self.peek()
                self.pos += 1
                if escape in self.ESCAPES:
                    out.append(self.ESCAPES[escape])
                elif escape in ("u", "U"):
                    digits = self.text[self.pos:self.pos + (4 if escape == "u" else 8)]
                    if not re.fullmatch(r"[0-9A-Fa-f]{4}|[0-9A-Fa-f]{8}", digits):
                        self.fail("bad \\%s escape" % escape)
                    out.append(chr(int(digits, 16)))
                    self.pos += len(digits)
                else:
                    self.fail("unknown escape \\%s" % escape)
            else:
                out.append(char)

    def key(self) -> list:
        """One key as its parts: a.b."c d" gives ['a', 'b', 'c d']."""
        parts = []
        while True:
            self.skip()
            if self.peek() in ('"', "'"):
                parts.append(self.string())
            else:
                match = self.BARE_KEY.match(self.text, self.pos)
                if not match:
                    self.fail("expected a key")
                parts.append(match.group())
                self.pos = match.end()
            self.skip()
            if self.peek() != ".":
                return parts
            self.pos += 1

    def value(self):
        char = self.peek()
        if char in ('"', "'"):
            return self.string()
        if char == "[":
            return self.array()
        if char == "{":
            return self.inline_table()
        match = self.WORD.match(self.text, self.pos)
        word = match.group() if match else ""
        if word in ("true", "false"):
            self.pos = match.end()
            return word == "true"
        if self.INTEGER.fullmatch(word):
            self.pos = match.end()
            return int(word.replace("_", ""))
        if self.FLOAT.fullmatch(word):
            self.pos = match.end()
            return float(word.replace("_", ""))
        self.fail("value %r is not read on a Python older than 3.11 "
                  "(one-line strings, decimal numbers, booleans, arrays and tables are)" % (word or char))

    def array(self) -> list:
        self.pos += 1
        items = []
        while True:
            self.skip(newlines=True)
            if self.peek() == "]":
                self.pos += 1
                return items
            items.append(self.value())
            self.skip(newlines=True)
            if self.peek() == ",":
                self.pos += 1
            elif self.peek() != "]":
                self.fail("expected ',' or ']' in an array")

    def inline_table(self) -> dict:
        self.pos += 1
        table: dict = {}
        self.skip()
        if self.peek() == "}":
            self.pos += 1
            return table
        while True:
            self.pair(table)
            self.skip()
            if self.peek() == "}":
                self.pos += 1
                return table
            self.expect(",")

    def pair(self, table: dict) -> None:
        """Read `key = value` into table; a dotted key makes the tables on its way."""
        parts = self.key()
        self.expect("=")
        self.skip()
        for part in parts[:-1]:
            table = table.setdefault(part, {})
            if not isinstance(table, dict):
                self.fail("%s is not a table" % part)
        if parts[-1] in table:
            self.fail("%s is set twice" % parts[-1])
        table[parts[-1]] = self.value()

    def header(self) -> None:
        """[a.b] opens a table; [[a.b]] adds one to an array of tables."""
        array = self.text.startswith("[[", self.pos)
        self.pos += 2 if array else 1
        parts = self.key()
        self.expect("]]" if array else "]")
        node = self.root
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if isinstance(node, list) and node:
                node = node[-1]
            if not isinstance(node, dict):
                self.fail("%s is not a table" % part)
        if array:
            tables = node.setdefault(parts[-1], [])
            if not isinstance(tables, list):
                self.fail("%s is not an array of tables" % parts[-1])
            tables.append({})
            self.table = tables[-1]
            return
        self.table = node.setdefault(parts[-1], {})
        if not isinstance(self.table, dict) or any(self.table is seen for seen in self.headers):
            self.fail("%s is defined twice" % ".".join(parts))
        self.headers.append(self.table)

    def read(self) -> dict:
        while True:
            self.skip(newlines=True)
            if not self.peek():
                return self.root
            if self.peek() == "[":
                self.header()
            else:
                self.pair(self.table)
            self.end_of_line()


def load_toml(path: Path) -> dict:
    """The file's contents, or {} when there is no such file."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    if tomllib is None:
        return SubsetReader(text, str(path)).read()
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit("%s: %s" % (path, exc))


# --------------------------------------------------------------------------- configuration


def deep_merge(base: dict, override: dict) -> dict:
    """Tables merge recursively; scalars and lists in ``override`` replace."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def find_root(explicit) -> Path:
    """The checkout holding the working directory (a linked worktree is its own root)."""
    if explicit:
        return Path(explicit).resolve()
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".git").exists():
            return candidate
    return here


def local_config_path(root: Path) -> Path:
    """The developer's file: this checkout's, or the main checkout's for a linked worktree
    that has none (there ``.git`` is a file)."""
    local = root / LOCAL_CONFIG
    if local.is_file() or not (root / ".git").is_file():
        return local
    try:
        proc = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-common-dir"],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return local
    if proc.returncode == 0 and proc.stdout.strip():
        return (root / proc.stdout.strip()).resolve().parent / LOCAL_CONFIG
    return local


def load_config(root: Path) -> dict:
    return deep_merge(load_toml(root / TEAM_CONFIG), load_toml(local_config_path(root)))


def table(config: dict, *names: str) -> dict:
    """config[a][b]..., which must be a table; {} when it is absent."""
    for index, name in enumerate(names):
        config = config.get(name, {})
        if not isinstance(config, dict):
            raise SystemExit("coder pool configuration: %s must be a table" % ".".join(names[:index + 1]))
    return config


# --------------------------------------------------------------------------- the pool


def detect(which=shutil.which) -> dict:
    """Map each known tool to its PATH location (None when absent)."""
    return {name: which(name) for name in KNOWN_TOOLS}


def coder_accounts(config: dict, tool: str) -> list:
    """One pool entry per account of a coder. A coder with no model or effort of its own
    takes them from a [tools.<name>] table when the files have one."""
    cfg = table(config, "coders", tool)
    defaults = table(config, "tools", tool)
    accounts = cfg.get("accounts", [{"name": "default"}])
    if not isinstance(accounts, list) or not all(
            isinstance(account, dict) and isinstance(account.get("name"), str)
            and isinstance(account.get("env", {}), dict) for account in accounts):
        raise SystemExit("coder pool configuration: coders.%s.accounts must be a list of tables, each with "
                         "a name and an optional env table" % tool)
    return [
        {
            "tool": tool,
            "account": account["name"],
            "env": dict(account.get("env", {})),
            "model": cfg.get("model", defaults.get("model", "")),
            "effort": cfg.get("effort", defaults.get("effort", "")),
            "risk": cfg.get("risk", "any"),
        }
        for account in accounts
    ]


def resolve(config: dict, installed: dict) -> dict:
    """The coder pool and its parallel limits, with what was dropped or replaced as warnings."""
    warnings = []
    roles = table(config, "roles")
    implementer = roles.get("implementer")
    candidates = roles.get("coders", [implementer] if implementer else DEFAULT_CODERS)
    if not isinstance(candidates, list) or not all(isinstance(name, str) for name in candidates):
        raise SystemExit("coder pool configuration: roles.coders must be a list of tool names")
    available = []
    for name in candidates:
        if installed.get(name):
            available.append(name)
        elif name in KNOWN_TOOLS:
            warnings.append("coders: %s not on PATH, dropped" % name)
        else:
            warnings.append("coders: %s is not one of %s, dropped" % (name, ", ".join(KNOWN_TOOLS)))
    fallback = not available and bool(installed.get(FALLBACK_TOOL))
    if fallback:
        available = [FALLBACK_TOOL]
        warnings.append("coders: no configured coder on PATH; falling back to the Claude Code coder (claude -p)")
    elif not available:
        warnings.append("coders: no coder on PATH; ask the user before Implement")
    pool = [entry for tool in available for entry in coder_accounts(config, tool)]
    limits = {}
    for key in LIMITS:
        value = table(config, "parallel").get(key, DEFAULT_LIMIT)
        if type(value) is not int or value < 1:
            warnings.append("parallel: %s must be an integer >= 1, using %d" % (key, DEFAULT_LIMIT))
            value = DEFAULT_LIMIT
        limits[key] = value
    capacity = len(pool) * limits["max_sessions_per_account"]
    coders = {"pool": pool, "fallback": fallback, **limits, "capacity": capacity,
              "effective_tracks": min(limits["max_tracks"], capacity)}
    return {"installed": {name: path for name, path in installed.items() if path},
            "coders": coders, "warnings": warnings}


def render(resolved: dict) -> str:
    coders = resolved["coders"]
    lines = ["coders:"]
    for entry in coders["pool"]:
        env = " ".join("%s=%s" % pair for pair in entry["env"].items())
        lines.append("  %s/%s: model=%s effort=%s risk=%s" % (
            entry["tool"], entry["account"], entry["model"], entry["effort"], entry["risk"])
            + (" " + env if env else ""))
    if coders["fallback"]:
        lines.append("  (fallback: Claude Code coder)")
    lines.append("parallel:")
    lines += ["  %s: %s" % (key, coders[key]) for key in (*LIMITS, "capacity", "effective_tracks")]
    lines += ["warning: " + warning for warning in resolved["warnings"]]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    show = sub.add_parser("show", help="the pool and its limits after merge and detection")
    # Both options go before or after the command: after it, one left out keeps the value given before.
    for target, default in ((parser, None), (show, argparse.SUPPRESS)):
        target.add_argument("--json", action="store_true", default=default or False,
                            help="print JSON instead of text")
        target.add_argument("--root", default=default, help="project root (default: the checkout holding the "
                            "working directory)")
    args = parser.parse_args(argv)
    resolved = resolve(load_config(find_root(args.root)), detect())
    print(json.dumps(resolved, indent=2, sort_keys=True) if args.json else render(resolved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
