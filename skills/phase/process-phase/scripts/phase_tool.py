#!/usr/bin/env python3
"""phase_tool.py: owns phase state and the planning checks (process-phase skill).

Stdlib only; runs on the system python3 (3.9). Every command prints exactly one JSON
envelope with ``--format json`` or a short human summary with ``--format md`` (default).

    phase_tool.py setup [--name NAME] [--base-branch B] [--release-branch B]
    phase_tool.py status [--phase NN|next] [--brief]
    phase_tool.py init --phase NN
    phase_tool.py activate --phase NN --dec DEC-NNN
    phase_tool.py roadmap list | roadmap get NN
    phase_tool.py check [--all] [--context F] [--plan F] [--skill DIR] [--ignored]
                        [--testlock NN] [--prove NN] [--docs] [--roadmap] [--requirements] [--state]
                        [--plans NN] [--scope NN [--base REF]]
    phase_tool.py req-coverage
    phase_tool.py testlock --phase NN [--write [--fixture PATH ...] [--relock --dec DEC-NNN]]
    phase_tool.py advance --to STATUS [--override DEC-NNN]
    phase_tool.py complete --phase NN
    phase_tool.py branch [--set NAME]
    phase_tool.py migration-check | golden-diff [--base REF] | evidence-check [--phase NN]
    phase_tool.py facts --phase NN

Common options: --format json|md, --root DIR.
Exit codes: 0 ok, 1 domain failure, 2 usage error. ``status`` always exits 0.
"""

from __future__ import annotations

import argparse
import datetime
import fnmatch
import hashlib
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path

VERSION = "1.0.0"
SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"
GATES_FILE = SCRIPT_DIR / "gates.json"

# Project settings live beside this script so that a copied skill directory carries them
# (acceptance fixtures copy the skills tree and run this file with the system python3).
SETTINGS_FILE = Path(__file__).resolve().with_suffix(".settings.json")
DEFAULT_SETTINGS = {
    "planning_dir": ".planning",
    "acceptance_dir": "tests/acceptance",
    "golden_dir": "tests/golden",
    "package_prefix": "",
    "skill_roots": [".claude/skills"],
    "agents_dir": ".claude/agents",
    "components_catalog": "docs/components/COMPONENTS.md",
    "capabilities_script": "",
    "capabilities_target": "docs/CAPABILITIES.md",
    "process_skill": ".claude/skills/process-phase",
    "branch_prefix": "phase/",
    # First status whose missing artifacts block ``advance``. "context_approved" enforces
    # every step; "plan_approved" only warns for the first two (for phases begun under that rule).
    "gated_from": "context_approved",
    # False: whole-number phases are numbered from 0 or 1 without gaps. True: any rising numbers,
    # for a roadmap whose numbers come from an earlier process (a project moved from GSD).
    "phase_gaps": False,
    # Which skills and agents ``check`` holds to the skill rules: "all" under skill_roots and
    # agents_dir, or "synced" for only the ones the sync delivered (read from the sync receipt),
    # for a project whose folders also hold skills or agents written to other rules.
    "skill_check": "all",
    # Generated files that two plans of one wave may both name (a path, a folder ending in /, or a
    # pattern with *), beside the component index, which is always one. ``check --plans`` reads it.
    "shared_files": [],
}
RECEIPT = ".devtools-receipt.json"  # written by the sync; lists every file it delivered


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
PLANNING = SETTINGS["planning_dir"]
PACKAGE_PREFIX = SETTINGS["package_prefix"] + "." if SETTINGS["package_prefix"] else ""

STATUSES = [
    "not_started", "context_approved", "tests_approved", "plan_approved",
    "implemented", "verified", "gaps_found", "complete",
]
STEPS = ["orient", "discuss", "specify", "plan", "implement", "verify", "close", "null"]
TRANSITIONS = {
    "not_started": ["context_approved"],
    "context_approved": ["tests_approved"],
    "tests_approved": ["plan_approved"],
    "plan_approved": ["implemented"],
    "implemented": ["verified", "gaps_found"],
    "gaps_found": ["plan_approved"],
}
# Step that follows reaching a status (also the "next_step" reported by status).
NEXT_STEP = {
    "not_started": "discuss", "context_approved": "specify", "tests_approved": "plan",
    "plan_approved": "implement", "implemented": "verify", "verified": "close",
    "gaps_found": "plan", "complete": "orient",
}
# Artifacts expected once a status is reached. Entries are (status, reported name, glob).
# Plans and summaries are per plan: NN-MM-PLAN.md. ``status`` reports missing ones.
# ``advance`` treats them as blockers from GATED_FROM on (the ``gated_from`` setting) and as
# warnings before it.
ARTIFACTS = [
    ("context_approved", "{nn}-CONTEXT.md", "{nn}-CONTEXT.md"),
    ("tests_approved", "{nn}-TESTLOCK.json", "{nn}-TESTLOCK.json"),
    ("tests_approved", "{nn}-EVIDENCE/red.txt", "{nn}-EVIDENCE/red.txt"),
    ("plan_approved", "{nn}-MM-PLAN.md", "{nn}-[0-9][0-9]-PLAN.md"),
    ("implemented", "{nn}-MM-SUMMARY.md", "{nn}-[0-9][0-9]-SUMMARY.md"),
    ("verified", "{nn}-VERIFICATION.md", "{nn}-VERIFICATION.md"),
]
GATED_FROM = SETTINGS["gated_from"]
if SETTINGS["skill_check"] not in ("all", "synced"):
    raise SystemExit("%s: skill_check must be all or synced" % SETTINGS_FILE)
if not isinstance(SETTINGS["shared_files"], list) or not all(isinstance(p, str) and p for p in SETTINGS["shared_files"]):
    raise SystemExit("%s: shared_files must be a list of paths" % SETTINGS_FILE)
if GATED_FROM not in ("context_approved", "tests_approved", "plan_approved"):
    raise SystemExit("%s: gated_from must be context_approved, tests_approved or plan_approved" % SETTINGS_FILE)
IGNORED_PARTS = {"__pycache__", ".pytest_cache"}
IGNORED_SUFFIXES = (".pyc", ".pyo")
DEC_ID = re.compile(r"^DEC-\d{3}$")
TOP_LEVEL = [
    "MANIFESTO.md", "README.md", "STATE.md", "ROADMAP.md", "REQUIREMENTS.md", "DECISIONS.md",
    "RISKS.md", "OPEN-QUESTIONS.md", "GLOSSARY.md", "MIGRATION.md", "planned-paths.txt",
]
STATE_KEYS = [
    "current_phase", "phase_status", "active_step", "completed_phases",
    "base_branch", "release_branch", "manifesto_version",
]
ROADMAP_FIELDS = ["Slug", "Status", "Depends on", "Requirements", "Reuses", "Acceptance tests"]
QUOTED_KEYS = {"current_phase", "completed_phases"}
PHASE_HEADING = re.compile(r"^## Phase (\d+(?:\.\d+)?): (.+?)\s*$", re.M)
FIELD_LINE = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
SKILL_NAME = re.compile(r"^[a-z0-9-]{1,64}$")
U_ROW = re.compile(r"^\|\s*(U\d+[a-z]?)\s*\|")
REQ_ROW = re.compile(r"^\|\s*(REQ-[A-Z]+-\d+)\s*\|(.*)$")


class ToolError(Exception):
    """A domain (exit 1) or usage (exit 2) failure reported in the envelope."""

    def __init__(self, code: str, message: str, hint: str = "", exit_code: int = 1, data=None):
        super().__init__(message)
        self.code, self.message, self.hint = code, message, hint
        self.exit_code, self.data = exit_code, data or {}


class Parser(argparse.ArgumentParser):
    """ArgumentParser that raises instead of printing and exiting."""

    def error(self, message):
        raise ToolError("USAGE", message, "run phase_tool.py --help", exit_code=2)


# --------------------------------------------------------------------------- helpers


def today() -> str:
    return datetime.date.today().isoformat()


def norm_phase(value) -> str:
    """Normalise whole or inserted phase ids to NN or NN.M (e.g. 06.1)."""
    text = str(value).strip().strip('"').strip("'")
    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        raise ToolError("BAD_PHASE", "phase id %r is not a number" % value, "use e.g. 01", 2)
    major, dot, minor = text.partition(".")
    return "%02d.%d" % (int(major), int(minor)) if dot else "%02d" % int(major)


def phase_key(value) -> tuple:
    """Numeric major/minor ordering, with a whole phase before its insertions."""
    major, dot, minor = norm_phase(value).partition(".")
    return int(major), int(minor) if dot else -1


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def issue(file: str, line: int, rule: str, message: str) -> dict:
    return {"file": file, "line": line, "rule": rule, "message": message}


def git(root: Path, *args: str):
    """Run git in root; return stdout or None when git is unavailable or fails."""
    try:
        proc = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def find_root(explicit) -> Path:
    if explicit:
        return Path(explicit).resolve()
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if (candidate / PLANNING).is_dir():
            return candidate
    return here


# --------------------------------------------------------------------------- frontmatter


def split_frontmatter(text: str):
    """Return (frontmatter lines, body) or (None, text) when there is no frontmatter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    block = text[4:end]
    body = text[end + 4:]
    return block.splitlines(), body


def parse_frontmatter(text: str) -> dict:
    lines, _ = split_frontmatter(text)
    result = {}
    for line in lines or []:
        if not line.strip() or line.startswith((" ", "\t", "#")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def format_value(key: str, value) -> str:
    if value is None:
        return "null"
    return '"%s"' % value if key in QUOTED_KEYS else str(value)


def update_frontmatter(path: Path, updates: dict) -> None:
    """Rewrite flat keys in place, appending missing keys at the end of the block."""
    text = path.read_text(encoding="utf-8")
    lines, body = split_frontmatter(text)
    if lines is None:
        lines, body = [], "\n" + text
    pending = dict(updates)
    out = []
    for line in lines:
        key = line.partition(":")[0].strip()
        if key in pending and not line.startswith((" ", "\t", "#")):
            out.append("%s: %s" % (key, format_value(key, pending.pop(key))))
        else:
            out.append(line)
    out.extend("%s: %s" % (k, format_value(k, v)) for k, v in pending.items())
    path.write_text("---\n" + "\n".join(out) + "\n---" + body, encoding="utf-8")


def phase_list(raw: str) -> list:
    return [norm_phase(x) for x in re.findall(r"\d+(?:\.\d+)?", raw or "")]


# --------------------------------------------------------------------------- planning model


class Planning:
    """Lazy accessors over the .planning/ directory of a repo root."""

    def __init__(self, root: Path):
        self.root = root
        self.dir = root / PLANNING

    def require(self) -> None:
        if not self.dir.is_dir():
            raise ToolError("NO_PLANNING", "no %s/ under %s" % (PLANNING, self.root),
                            "run from the repo root or pass --root; a new project starts with 'phase_tool.py setup'")

    def state(self) -> dict:
        path = self.dir / "STATE.md"
        if not path.is_file():
            raise ToolError("NO_STATE", PLANNING + "/STATE.md is missing",
                            "run 'phase_tool.py setup' to create the missing planning files")
        state = parse_frontmatter(path.read_text(encoding="utf-8"))
        # When the last phase is completed the state rests on it as ``complete``. A phase added to
        # the roadmap afterwards is then the current one, as ``complete`` would have left it had the
        # phase been there. ``advance``, ``activate`` and ``branch`` write that down.
        if state.get("phase_status") == "complete":
            todo = open_phases(self, phase_list(state.get("completed_phases", "")))
            if todo:
                state.update(current_phase=todo[0], phase_status="not_started", active_step="null")
        return state

    def roadmap_text(self) -> str:
        path = self.dir / "ROADMAP.md"
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    def phases(self) -> list:
        return sorted(parse_roadmap(self.roadmap_text()), key=lambda p: phase_key(p["id"]))

    def phase(self, nn: str):
        for phase in self.phases():
            if phase["id"] == nn:
                return phase
        return None

    def phase_dir(self, nn: str):
        found = sorted((self.dir / "phases").glob(nn + "-*")) if (self.dir / "phases").is_dir() else []
        dirs = [d for d in found if d.is_dir()]
        return dirs[0] if dirs else None

    def ensure_phase_dir(self, nn: str) -> Path:
        existing = self.phase_dir(nn)
        if existing:
            return existing
        phase = self.phase(nn)
        slug = phase["slug"] if phase and phase["slug"] else "phase"
        path = self.dir / "phases" / ("%s-%s" % (nn, slug))
        path.mkdir(parents=True, exist_ok=True)
        return path


def parse_roadmap(text: str) -> list:
    """Parse '## Phase N[.M]: Title' sections and their '- **Field:** value' bullets."""
    phases = []
    matches = list(PHASE_HEADING.finditer(text))
    for m in matches:
        start = m.start()
        nxt = re.compile(r"^## ", re.M).search(text, m.end())
        block = text[start:nxt.start() if nxt else len(text)].rstrip() + "\n"
        fields, field_lines = {}, {}
        base_line = text.count("\n", 0, start) + 1
        for offset, line in enumerate(block.splitlines()):
            fm = FIELD_LINE.match(line)
            if fm:
                name = re.sub(r"\s*\(.*\)$", "", fm.group(1)).strip()
                fields.setdefault(name, fm.group(2).strip())
                field_lines.setdefault(name, base_line + offset)
        nn = norm_phase(m.group(1))
        num = float(nn) if "." in nn else int(nn)
        phases.append({
            "id": nn, "num": num, "title": m.group(2).strip(),
            "slug": fields.get("Slug", "").strip("` "),
            "status": fields.get("Status", "").strip("` "),
            "depends_on": phase_list(fields.get("Depends on", "")),
            "requirements": re.findall(r"REQ-[A-Z]+-\d+", fields.get("Requirements", "")),
            "_fields": fields, "_lines": field_lines, "_line": base_line, "_block": block,
        })
    return phases


def public_phase(phase: dict) -> dict:
    return {k: v for k, v in phase.items() if not k.startswith("_")}


def parse_requirements(text: str):
    """Return (u_ids {id: line}, reqs [{id, u, phases, status, line, raw}])."""
    u_ids, reqs, seen = {}, [], set()
    for lineno, line in enumerate(text.splitlines(), 1):
        um = U_ROW.match(line)
        if um:
            u_ids.setdefault(um.group(1), lineno)
            continue
        rm = REQ_ROW.match(line)
        if not rm or rm.group(1) in seen:
            continue
        cells = [c.strip() for c in rm.group(2).strip().strip("|").split("|")]
        while len(cells) < 4:
            cells.append("")
        seen.add(rm.group(1))
        reqs.append({
            "id": rm.group(1), "u": re.findall(r"U\d+[a-z]?", cells[1]),
            "phases": phase_list(cells[2]), "status": cells[3], "line": lineno,
        })
    return u_ids, reqs


def load_gates() -> dict:
    try:
        return json.loads(GATES_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def gates_for(nn: str) -> list:
    gates = load_gates()
    num = phase_key(nn)[0]
    applicable = [g for g, spec in gates.items() if int(spec.get("from_phase", 0)) <= num]
    return sorted(applicable, key=lambda g: int(re.sub(r"\D", "", g) or 0))


# --------------------------------------------------------------------------- status / init / roadmap


def missing_artifacts(pl: Planning, nn: str, status: str) -> list:
    reached = STATUSES.index(status) if status in STATUSES else -1
    if status == "gaps_found":
        reached = STATUSES.index("implemented")
    pdir = pl.phase_dir(nn)
    missing = []
    for needed_at, label, pattern in ARTIFACTS:
        if STATUSES.index(needed_at) <= reached:
            if pdir is None or not any(pdir.glob(pattern.format(nn=nn))):
                missing.append(label.format(nn=nn))
    if pdir is not None and STATUSES.index("implemented") <= reached:
        # Every plan was carried out: one summary must not stand for several plans.
        for plan in sorted(pdir.glob("%s-[0-9][0-9]-PLAN.md" % nn)):
            summary = plan.name[:-len("PLAN.md")] + "SUMMARY.md"
            if any(pdir.glob("%s-[0-9][0-9]-SUMMARY.md" % nn)) and not (pdir / summary).is_file():
                missing.append(summary)
    # Only phases that opt in via CONTEXT are gated, and only at tests_approved.
    context = pdir / ("%s-CONTEXT.md" % nn) if pdir is not None else None
    if (status == "tests_approved" and context is not None and context.is_file()
            and parse_frontmatter(context.read_text(encoding="utf-8")).get("evidence_gate") == "required"):
        proof = "{nn}-EVIDENCE/prove.md".format(nn=nn)
        if not (pdir / proof).is_file():
            missing.append(proof)
    return missing


def finished_elsewhere(phase: dict, status: str) -> bool:
    """A complete phase whose roadmap block says it has no acceptance tests ("none: finished
    under GSD"): it was accepted by another process and has none of this one's files."""
    tests = (phase.get("_fields") or {}).get("Acceptance tests", "")
    return status == "complete" and tests.strip().lower().startswith("none")


def open_phases(pl: Planning, completed: list) -> list:
    """Roadmap phases that are not complete, lowest first; those that can start come before blocked ones."""
    todo = [p for p in pl.phases() if p["id"] not in completed and p["status"] != "complete"]
    ready = [p["id"] for p in todo if all(d in completed for d in p["depends_on"])]
    return ready + [p["id"] for p in todo if p["id"] not in ready]


def next_phase(pl: Planning, state: dict) -> str:
    """Lowest incomplete roadmap phase whose dependencies are complete (else the lowest incomplete one)."""
    todo = open_phases(pl, phase_list(state.get("completed_phases", "")))
    return todo[0] if todo else norm_phase(state.get("current_phase", "00"))


def cmd_status(pl: Planning, args) -> dict:
    pl.require()
    state = pl.state()
    if str(args.phase or "").strip().lower() == "next":
        nn = next_phase(pl, state)
    else:
        nn = norm_phase(args.phase or state.get("current_phase", "00"))
    completed = sorted(phase_list(state.get("completed_phases", "")), key=phase_key)
    phase = pl.phase(nn) or {}
    status = state.get("phase_status", "") if nn == norm_phase(state.get("current_phase", "00")) \
        else phase.get("status", "")
    deps = phase.get("depends_on", [])
    deps_complete = all(d in completed for d in deps)
    blockers = []
    if state.get("blocked_on") not in (None, "", "null"):
        blockers.append(state["blocked_on"])
    blockers.extend("phase %s not complete" % d for d in deps if d not in completed)
    active = state.get("active_step")
    data = {
        "current_phase": nn, "phase_status": status,
        "active_step": None if active in (None, "", "null") else active,
        "next_step": NEXT_STEP.get(status, "orient"),
    }
    if args.brief:
        return data
    pdir = pl.phase_dir(nn)
    branch = git(pl.root, "rev-parse", "--abbrev-ref", "HEAD")
    porcelain = git(pl.root, "status", "--porcelain")
    data.update({
        "completed_phases": completed,
        "phase_dir": rel(pl.root, pdir) if pdir else None,
        "phase_title": phase.get("title", ""),
        "missing": [] if finished_elsewhere(phase, status) else missing_artifacts(pl, nn, status),
        "blockers": blockers, "deps_complete": deps_complete,
        "gates_applicable": gates_for(nn),
        "branch": branch.strip() if branch else None,
        "dirty": bool(porcelain.strip()) if porcelain is not None else None,
    })
    return data


CONTEXT_SKELETON = """# Phase {{PHASE}}: {{TITLE}} - Context

## Goal

## Decisions

## Scope (in / out)

## Acceptance criteria

## Open questions
"""


def cmd_setup(pl: Planning, args) -> dict:
    """Create the planning files a new project needs; never overwrites an existing file."""
    branch = (git(pl.root, "rev-parse", "--abbrev-ref", "HEAD") or "").strip()
    base = args.base_branch or (branch if branch and branch != "HEAD" else "main")
    subs = {"{{NAME}}": args.name or pl.root.name, "{{DATE}}": today(), "{{BASE}}": base,
            "{{RELEASE}}": args.release_branch or base,
            "{{TOOL}}": rel(pl.root, Path(__file__).resolve())}
    source = TEMPLATES_DIR / "planning"
    if not source.is_dir():
        raise ToolError("NO_TEMPLATES", "%s is missing" % source, "sync the whole process-phase skill directory")
    # A plan written by something else has files of the same names. Keeping them beside new ones
    # would leave a folder that neither process can read.
    def text(name):
        return (pl.dir / name).read_text(encoding="utf-8") if (pl.dir / name).is_file() else None
    readable = {"STATE.md": lambda t: "current_phase" in parse_frontmatter(t),
                "ROADMAP.md": lambda t: bool(parse_roadmap(t)),
                "REQUIREMENTS.md": lambda t: any(parse_requirements(t))}
    foreign = [name for name, ok in readable.items() if text(name) is not None and not ok(text(name))]
    if foreign:
        raise ToolError("FOREIGN_PLAN", "%s/ already holds %s in another format" % (PLANNING, ", ".join(foreign)),
                        "setup is for a project with no plan. A project planned with GSD is moved with "
                        "devtools/from_gsd.py in the dev-tools checkout (its skills/move-from-gsd/SKILL.md is the guide); "
                        "any other plan is rewritten by hand (references/artifact-formats.md) or moved aside first",
                        1, {"files": foreign})
    created, kept = [], []
    pl.dir.mkdir(parents=True, exist_ok=True)
    for template in sorted(source.iterdir()):
        dest = pl.dir / template.name
        if dest.exists():
            kept.append(rel(pl.root, dest))
            continue
        text = template.read_text(encoding="utf-8")
        for key, value in subs.items():
            text = text.replace(key, value)
        dest.write_text(text, encoding="utf-8")
        created.append(rel(pl.root, dest))
    return {"created": created, "kept": kept,
            "next": ["describe the first phase in %s/ROADMAP.md and its requirement in REQUIREMENTS.md" % PLANNING,
                     "put your name on the DEC-001 row in %s/DECISIONS.md" % PLANNING,
                     "commit, then run 'phase_tool.py check --all'"]}


def cmd_init(pl: Planning, args) -> dict:
    pl.require()
    nn = norm_phase(args.phase)
    phase = pl.phase(nn) or {}
    pdir = pl.ensure_phase_dir(nn)
    subs = {"{{PHASE}}": nn, "{{TITLE}}": phase.get("title", "Phase " + nn),
            "{{SLUG}}": phase.get("slug", "phase")}
    created = []
    for template, target in [("CONTEXT.md", "CONTEXT.md"), ("DISCUSSION-LOG.md", "DISCUSSION-LOG.md"),
                             ("TESTS.md", "TESTS.md"),
                             ("DEFERRED.md", "DEFERRED.md")]:
        src = TEMPLATES_DIR / template
        dest = pdir / ("%s-%s" % (nn, target))
        if dest.exists():
            continue
        if src.is_file():
            text = src.read_text(encoding="utf-8")
        elif template == "CONTEXT.md":
            text = CONTEXT_SKELETON
        else:
            continue
        for key, value in subs.items():
            text = text.replace(key, value)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        created.append(rel(pl.root, dest))
    keep = pdir / ("%s-EVIDENCE" % nn) / ".gitkeep"
    if not keep.exists():
        keep.parent.mkdir(parents=True, exist_ok=True)
        keep.write_text("", encoding="utf-8")
        created.append(rel(pl.root, keep))
    return {"phase": nn, "phase_dir": rel(pl.root, pdir), "created": created}


def cmd_roadmap(pl: Planning, args) -> dict:
    pl.require()
    phases = pl.phases()
    if not phases:
        raise ToolError("NO_ROADMAP", "no '## Phase N:' sections in %s/ROADMAP.md" % PLANNING)
    if args.action == "list":
        return {"phases": [public_phase(p) for p in phases]}
    if not args.phase:
        raise ToolError("USAGE", "roadmap get needs a phase id", "roadmap get 03", 2)
    phase = pl.phase(norm_phase(args.phase))
    if phase is None:
        raise ToolError("UNKNOWN_PHASE", "phase %s is not in ROADMAP.md" % args.phase)
    return dict(public_phase(phase), block=phase["_block"])


# --------------------------------------------------------------------------- checks


def check_top_level(pl: Planning) -> list:
    return [issue(PLANNING + "/" + n, 0, "files", "required file missing")
            for n in TOP_LEVEL if not (pl.dir / n).is_file()]


def check_state(pl: Planning) -> list:
    path = pl.dir / "STATE.md"
    if not path.is_file():
        return [issue(PLANNING + "/STATE.md", 0, "state", "STATE.md missing")]
    state = parse_frontmatter(path.read_text(encoding="utf-8"))
    issues = [issue(PLANNING + "/STATE.md", 1, "state", "frontmatter key %r missing" % k)
              for k in STATE_KEYS if k not in state]
    if state.get("phase_status") and state["phase_status"] not in STATUSES:
        issues.append(issue(PLANNING + "/STATE.md", 1, "state", "invalid phase_status %r" % state["phase_status"]))
    if state.get("active_step", "null") not in STEPS:
        issues.append(issue(PLANNING + "/STATE.md", 1, "state", "invalid active_step %r" % state["active_step"]))
    return issues


def check_roadmap(pl: Planning) -> list:
    f = PLANNING + "/ROADMAP.md"
    if not (pl.dir / "ROADMAP.md").is_file():
        return [issue(f, 0, "roadmap", "ROADMAP.md missing")]
    phases = parse_roadmap(pl.roadmap_text())
    if not phases:
        return [issue(f, 0, "roadmap", "no '## Phase N: Title' sections")]
    issues = []
    nums = [p["num"] for p in phases if "." not in p["id"]]
    first = 1 if nums and nums[0] == 1 else 0
    gaps = SETTINGS["phase_gaps"]
    if not gaps and nums != list(range(first, first + len(nums))):
        issues.append(issue(f, phases[0]["_line"], "roadmap", "phases not contiguous from 0: %s" % nums))
    ids = {p["id"] for p in phases}
    keys = [phase_key(p["id"]) for p in phases]
    if (gaps or any("." in p["id"] for p in phases)) and (keys != sorted(keys) or len(ids) != len(phases)):
        issues.append(issue(f, phases[0]["_line"], "roadmap", "phases not in unique numeric order"))
    for p in phases:
        if "." in p["id"] and p["id"].split(".")[0] not in ids:
            issues.append(issue(f, p["_line"], "roadmap", "phase %s lacks its whole-number phase" % p["id"]))
        for name in ROADMAP_FIELDS:
            if name not in p["_fields"]:
                issues.append(issue(f, p["_line"], "roadmap", "phase %s lacks '**%s:**'" % (p["id"], name)))
        if p["slug"][:1].isdigit():
            issues.append(issue(f, p["_lines"].get("Slug", p["_line"]), "roadmap",
                                "phase %s has slug %r: a slug starts with a letter, or its acceptance folder "
                                "p%s_%s reads as the tests of an inserted phase"
                                % (p["id"], p["slug"], p["id"].replace(".", "_"), p["slug"].replace("-", "_"))))
        if p["status"] not in STATUSES:
            issues.append(issue(f, p["_lines"].get("Status", p["_line"]), "roadmap",
                                "phase %s has invalid status %r" % (p["id"], p["status"])))
        for dep in p["depends_on"]:
            if dep not in ids or phase_key(dep) >= phase_key(p["id"]):
                issues.append(issue(f, p["_lines"].get("Depends on", p["_line"]), "roadmap",
                                    "phase %s depends on unknown or later phase %s" % (p["id"], dep)))
    try:
        state = pl.state()
    except ToolError:
        return issues
    current = pl.phase(norm_phase(state.get("current_phase", "00")))
    if current and current["status"] != state.get("phase_status"):
        issues.append(issue(f, current["_lines"].get("Status", current["_line"]), "roadmap",
                            "phase %s status %r != STATE phase_status %r"
                            % (current["id"], current["status"], state.get("phase_status"))))
    for done in phase_list(state.get("completed_phases", "")):
        p = pl.phase(done)
        if p and p["status"] != "complete":
            issues.append(issue(f, p["_line"], "roadmap", "phase %s is in completed_phases but not complete" % done))
    return issues


def coverage(pl: Planning) -> dict:
    path = pl.dir / "REQUIREMENTS.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    u_ids, reqs = parse_requirements(text)
    known = {p["id"] for p in pl.phases()} or {"%02d" % i for i in range(7)}
    covered = {u for r in reqs for u in r["u"]}
    uncovered = [u for u in u_ids if u not in covered]
    unphased = [r["id"] for r in reqs if not r["phases"] or any(p not in known for p in r["phases"])]
    total = len(u_ids)
    pct = 100 if total and not uncovered else (len(u_ids) - len(uncovered)) * 100 // total if total else 0
    return {"u_total": total, "req_total": len(reqs), "uncovered_u": uncovered,
            "unphased_req": unphased, "pct": pct, "_u": u_ids, "_reqs": reqs}


def check_requirements(pl: Planning) -> list:
    f = PLANNING + "/REQUIREMENTS.md"
    if not (pl.dir / "REQUIREMENTS.md").is_file():
        return [issue(f, 0, "requirements", "REQUIREMENTS.md missing")]
    cov = coverage(pl)
    issues = [issue(f, cov["_u"][u], "requirements", "%s is not covered by any REQ" % u)
              for u in cov["uncovered_u"]]
    if not cov["_u"]:
        issues.append(issue(f, 0, "requirements", "no '| U01 |' user-requirement rows"))
    for r in cov["_reqs"]:
        if r["id"] in cov["unphased_req"]:
            issues.append(issue(f, r["line"], "requirements", "%s has no phase or an unknown phase" % r["id"]))
        for u in r["u"]:
            if u not in cov["_u"]:
                issues.append(issue(f, r["line"], "requirements", "%s references unknown %s" % (r["id"], u)))
        if r["status"] not in ("Planned", "Validated"):
            issues.append(issue(f, r["line"], "requirements", "%s status %r not Planned|Validated"
                                % (r["id"], r["status"])))
    return issues


def check_docs(pl: Planning) -> list:
    issues, owners = [], {}
    for path in sorted((pl.dir / "docs").glob("*.md")) if (pl.dir / "docs").is_dir() else []:
        f = rel(pl.root, path)
        front = parse_frontmatter(path.read_text(encoding="utf-8"))
        if "normative_for" not in front:
            issues.append(issue(f, 1, "docs", "frontmatter lacks normative_for"))
            continue
        for topic in [t.strip() for t in front["normative_for"].strip("[]").split(",") if t.strip()]:
            if topic in owners:
                issues.append(issue(f, 1, "docs", "topic %r already owned by %s" % (topic, owners[topic])))
            owners.setdefault(topic, path.name)
    return issues


def check_ignored(pl: Planning) -> list:
    path = pl.dir / "planned-paths.txt"
    if not path.is_file():
        return []
    paths = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.strip().startswith("#")]
    if not paths or git(pl.root, "rev-parse", "--is-inside-work-tree") is None:
        return []
    try:
        proc = subprocess.run(["git", "check-ignore", "--no-index", *paths], cwd=str(pl.root),
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    return [issue(PLANNING + "/planned-paths.txt", 0, "ignored", "planned path is git-ignored: " + p)
            for p in proc.stdout.split()]


def check_skill(root: Path, skill_dir: Path) -> list:
    skill_md = skill_dir / "SKILL.md"
    f = rel(root, skill_md)
    if not skill_md.is_file():
        return [issue(f, 0, "skill", "SKILL.md missing")]
    text = skill_md.read_text(encoding="utf-8")
    front = parse_frontmatter(text)
    issues = []
    if not text.startswith("---\n"):
        issues.append(issue(f, 1, "skill", "no frontmatter"))
    name, desc = front.get("name", ""), front.get("description", "")
    if name != skill_dir.name:
        issues.append(issue(f, 1, "skill", "name %r != directory %r" % (name, skill_dir.name)))
    if not SKILL_NAME.match(name):
        issues.append(issue(f, 1, "skill", "name %r must match ^[a-z0-9-]{1,64}$" % name))
    if not 1 <= len(desc) <= 1024:
        issues.append(issue(f, 1, "skill", "description must be 1..1024 chars"))
    if "<" in desc or ">" in desc:
        issues.append(issue(f, 1, "skill", "description must not contain < or >"))
    if len(text.splitlines()) > 500:
        issues.append(issue(f, 0, "skill", "SKILL.md longer than 500 lines"))
    for lineno, line in enumerate(text.splitlines(), 1):
        for ref in re.findall(r"`((?:references|templates|scripts)/[\w./-]+)`", line):
            if "*" not in ref and not (skill_dir / ref).exists():
                issues.append(issue(f, lineno, "skill", "referenced file missing: " + ref))
    return issues


def check_skills(pl: Planning) -> list:
    issues, synced = [], None
    if SETTINGS["skill_check"] == "synced":
        try:
            synced = set(json.loads((pl.root / RECEIPT).read_text(encoding="utf-8")).get("files", {}))
        except (OSError, ValueError, AttributeError):
            return [issue(RECEIPT, 0, "skill", "skill_check is \"synced\" and the sync receipt is missing or unreadable")]
    for base in [pl.root / r for r in SETTINGS["skill_roots"]]:
        for skill_md in sorted(base.glob("*/SKILL.md")) if base.is_dir() else []:
            if synced is None or rel(pl.root, skill_md) in synced:
                issues.extend(check_skill(pl.root, skill_md.parent))
    agents = pl.root / SETTINGS["agents_dir"]
    for path in sorted(agents.glob("*.md")) if agents.is_dir() else []:
        if synced is not None and rel(pl.root, path) not in synced:
            continue
        front = parse_frontmatter(path.read_text(encoding="utf-8"))
        if front.get("name") != path.stem:
            issues.append(issue(rel(pl.root, path), 1, "agent", "name must equal file stem %r" % path.stem))
        if not front.get("description"):
            issues.append(issue(rel(pl.root, path), 1, "agent", "description missing"))
    return issues


def hashable(path: Path) -> bool:
    return path.is_file() and not IGNORED_PARTS.intersection(path.parts) \
        and not path.name.endswith(IGNORED_SUFFIXES)


def acceptance_files(root: Path, nn: str) -> dict:
    """Hash acceptance files under pNN_* or pNN_M_*, excluding caches and other phases."""
    base = root / SETTINGS["acceptance_dir"]
    files = []
    for pdir in sorted(base.glob("p%s_*" % nn.replace(".", "_"))) if base.is_dir() else []:
        if "." not in nn and re.match(r"^p\d{2,}_\d+_", pdir.name):
            continue
        if pdir.is_dir():
            files.extend(p for p in pdir.rglob("*") if hashable(p))
    return {rel(root, p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def fixture_files(root: Path, declared) -> dict:
    """sha256 of declared fixture files; a directory entry expands to every file under it."""
    files = []
    for entry in declared:
        path = (root / entry) if not Path(entry).is_absolute() else Path(entry)
        if path.is_dir():
            files.extend(p for p in path.rglob("*") if hashable(p))
        elif path.is_file():
            files.append(path)
        else:
            raise ToolError("NO_FIXTURE", "declared fixture %s does not exist" % entry,
                            "pass existing files or directories to --fixture", 2)
    return {rel(root, p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}


def current_fixture_hashes(root: Path, locked: dict) -> dict:
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in locked if (root / p).is_file()}


def check_testlock(pl: Planning, nn: str) -> list:
    pdir = pl.phase_dir(nn)
    lock = pdir / ("%s-TESTLOCK.json" % nn) if pdir else None
    if lock is None or not lock.is_file():
        return [issue(PLANNING + "/phases/%s-*/%s-TESTLOCK.json" % (nn, nn), 0, "testlock",
                      "no lock for phase %s (run testlock --phase %s --write)" % (nn, nn))]
    f = rel(pl.root, lock)
    try:
        payload = json.loads(lock.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [issue(f, 0, "testlock", "unreadable lock: %s" % exc)]
    locked = payload.get("files", {})
    current = acceptance_files(pl.root, nn)
    issues = []
    for path in sorted(set(locked) | set(current)):
        if path not in current:
            issues.append(issue(path, 0, "testlock", "locked test removed"))
        elif path not in locked:
            issues.append(issue(path, 0, "testlock", "test added after lock"))
        elif locked[path] != current[path]:
            issues.append(issue(path, 0, "testlock", "locked test modified"))
    locked_fx = payload.get("fixtures", {})
    current_fx = current_fixture_hashes(pl.root, locked_fx)
    for path in sorted(locked_fx):
        if path not in current_fx:
            issues.append(issue(path, 0, "testlock", "locked fixture removed"))
        elif locked_fx[path] != current_fx[path]:
            issues.append(issue(path, 0, "testlock", "locked fixture modified"))
    return issues


def check_all_testlocks(pl: Planning) -> list:
    issues = []
    phases_dir = pl.dir / "phases"
    for lock in sorted(phases_dir.glob("*/*-TESTLOCK.json")) if phases_dir.is_dir() else []:
        issues.extend(check_testlock(pl, lock.name.split("-")[0]))
    return issues


def check_doc_file(root: Path, path: Path, rule: str, needs_tests: bool) -> list:
    f = rel(root, path)
    if not path.is_file():
        return [issue(f, 0, rule, "file missing")]
    text = path.read_text(encoding="utf-8")
    issues = [issue(f, n, rule, "unfilled template placeholder")
              for n, line in enumerate(text.splitlines(), 1) if re.search(r"\{\{[A-Z_]+\}\}", line)]
    if len(text.strip()) < 200:
        issues.append(issue(f, 0, rule, "file is a stub (<200 chars)"))
    if needs_tests and not re.search(r"tests/|test_\w+", text):
        issues.append(issue(f, 0, rule, "plan tasks must name the acceptance tests they turn green"))
    if rule == "plan":
        issues.extend(check_plan_reuse(root, text, f))
    return issues


def check_plan_reuse(root: Path, text: str, filename: str) -> list:
    """Require component search evidence only for an explicitly checked plan."""
    reuse = re.search(r"^## Reuse[ \t]*\n(.*?)(?=^#{1,2} |\Z)", text, re.M | re.S)
    body = reuse[1] if reuse else ""
    fields = {}
    for key, value in re.findall(r"^[ \t]*(?:- )?(searched|external|reuse|new_component):[ \t]*([^\n]+)$",
                                 body, re.M | re.I):
        if value.strip():
            fields.setdefault(key.lower(), []).append(value.strip())
    catalog = root / SETTINGS["components_catalog"]
    ids = set(re.findall(r"^### ([a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)[ \t]*$",
                         catalog.read_text(encoding="utf-8") if catalog.is_file() else "", re.M))
    named = {name for value in fields.get("reuse", []) if not value.startswith("<")
             for name in re.findall(r"[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*", value)}
    messages = [f"missing {key}: line" for key in ("searched", "external") if not fields.get(key)]
    if not named and not fields.get("new_component"):
        messages.append("missing reuse: or new_component: line")
    messages.extend(f"unknown component id in reuse: {name}" for name in sorted(named - ids))
    return [issue(filename, 0, "plan", "plan ## Reuse: " + message) for message in messages]


TEST_ID = re.compile(r"`([^`]+\.py::[^`]+)`")


def scalar(text: str) -> str:
    """One YAML-ish value: the text inside its quotes, or the text before a trailing comment."""
    text = text.strip()
    if text[:1] in ("'", '"'):
        end = text.find(text[0], 1)
        return text[1:end] if end > 0 else text[1:]
    return re.sub(r"\s+#.*$", "", text).strip()


def frontmatter_list(text: str, key: str) -> list:
    """A frontmatter list: inline (``key: [a, "b, c"]``) or one ``- item`` a line, indented or not."""
    lines, _ = split_frontmatter(text)
    items, inside = [], False
    for line in lines or []:
        if line.startswith(key + ":"):
            inside = True
            value = line.split(":", 1)[1].strip()
            if value.startswith("["):
                value = value[1:value.rfind("]")] if "]" in value else value[1:]
            elif value.startswith("#"):
                value = ""
            items.extend(scalar(item) for item in re.findall(r'"[^"]*"|\'[^\']*\'|[^,]+', value))
        elif inside and re.match(r"\s*- ", line):
            items.append(scalar(line.split("- ", 1)[1]))
        elif line.strip():
            inside = False
    return [item for item in items if item]


def listed(value: str, pattern=r"`([^`]+)`") -> list:
    """The items of a task field: what is in backticks, or without any, what commas and lines separate."""
    found = re.findall(pattern, value)
    if not found and "`" not in value:
        found = [item.strip(" \t-") for item in re.split(r"[,\n]", value)]
    return [item[2:] if item.startswith("./") else item for item in found if item]


# The one-value frontmatter keys of a plan that `facts` passes on as they are written.
PLAN_KEYS = ("golden_impact", "llm_dependency", "gap_closure", "autonomous", "prove_method")


def parse_plan(text: str) -> dict:
    """What a plan declares: its wave, the plans it depends on, its requirements and the tests
    its frontmatter lists, and for each task the files it changes, the locked tests it turns
    green and its verify command. A task is a ``### <id>`` block between <tasks> and </tasks>;
    a field is ``- **name:** value`` and may run on over indented lines."""
    _, body = split_frontmatter(text)
    front = parse_frontmatter(text)
    wave = scalar(front.get("wave", ""))
    section = re.search(r"<tasks>(.*?)</tasks>", body, re.S)
    tasks = []
    for block in re.split(r"^### ", section.group(1) if section else "", flags=re.M)[1:]:
        fields = dict(re.findall(r"^- \*\*([a-z_]+):\*\*[ \t]*(.*(?:\n[ \t]+\S.*)*)", block, re.M))
        tasks.append({"id": block.split(None, 1)[0] if block.strip() else "",
                      "files": listed(fields.get("files", "")) + listed(fields.get("unit_tests", "")),
                      "turns_green": [name for name in listed(fields.get("turns_green", ""), TEST_ID.pattern)
                                      if "::" in name],
                      "read_first": listed(fields.get("read_first", "")),
                      "type": fields.get("type", "").strip(),
                      "verify": fields.get("verify", "").strip()})
    reuse = re.search(r"^## Reuse[ \t]*\n(.*?)(?=^#{1,2} |\Z)", text, re.M | re.S)
    new = re.findall(r"^[ \t]*(?:- )?new_component:[ \t]*([^\n]+)$", reuse.group(1) if reuse else "", re.M | re.I)
    old = re.findall(r"^[ \t]*(?:- )?reuse:[ \t]*([^\n<]+)$", reuse.group(1) if reuse else "", re.M | re.I)
    return {"wave": int(wave) if wave.isdigit() and int(wave) else None,
            "declares": {key: scalar(front[key]) for key in PLAN_KEYS if scalar(front.get(key, ""))},
            "reuse": re.findall(r"[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*", " ".join(old)),
            "depends_on": frontmatter_list(text, "depends_on"),
            "claims": [name for name in frontmatter_list(text, "turns_green") if "::" in name],
            "requirements": re.findall(r"REQ-[A-Z]+-\d+", " ".join(frontmatter_list(text, "requirements"))),
            "new_components": re.findall(r"[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*", " ".join(new)),
            "tasks": tasks}


def phase_plans(pl: Planning, nn: str) -> dict:
    """{repo-relative path: parsed plan} for every NN-MM-PLAN.md of a phase. A plan's id is the
    NN-MM its file name starts with, whatever its frontmatter says."""
    pdir = pl.phase_dir(nn)
    plans = {}
    for path in (sorted(pdir.glob(nn + "-*-PLAN.md")) if pdir else []):
        plans[rel(pl.root, path)] = dict(parse_plan(path.read_text(encoding="utf-8")), id=path.name[:-len("-PLAN.md")])
    return plans


def overlap(a: str, b: str) -> bool:
    """Whether two entries of tasks' `files` can name the same file. An entry is a path, a
    folder ending in /, or a pattern with *. Two patterns, or a pattern and a folder, are taken
    to overlap when the text before the first * of one starts the other's: this errs towards
    saying yes."""
    if a == b:
        return True
    for one, other in ((a, b), (b, a)):
        if "*" in one:
            if "*" in other or other.endswith("/"):
                fixed, rest = one.split("*", 1)[0], other.split("*", 1)[0]
                if fixed.startswith(rest) or rest.startswith(fixed):
                    return True
            elif fnmatch.fnmatch(other, one):
                return True
        elif one.endswith("/") and other.startswith(one):
            return True
    return False


def index_paths() -> tuple:
    """The component index as (files, folders): the catalog and what is generated beside it."""
    catalog = SETTINGS["components_catalog"]
    index = catalog.rsplit("/", 1)[0] + "/" if "/" in catalog else ""
    return {catalog} | {index + name for name in INDEX_FILES}, (index + "modules/", index + "external/")


def inside(entry: str, entries) -> bool:
    """Whether everything an entry names is named by one of `entries` too."""
    return any(entry == other or (other.endswith("/") and entry.startswith(other))
               or ("*" in other and "*" not in entry and fnmatch.fnmatch(entry, other)) for other in entries)


def track_cap(root: Path):
    """How many tracks the coder pool runs at once here (coder_pool.py beside this script), or
    None when the script is missing, fails, or finds no coder at all."""
    script = SCRIPT_DIR / "coder_pool.py"
    if not script.is_file():
        return None
    try:
        proc = subprocess.run([sys.executable, str(script), "show", "--json", "--root", str(root)],
                              capture_output=True, text=True, timeout=30)
        cap = json.loads(proc.stdout)["coders"]["effective_tracks"]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError):
        return None
    return cap if proc.returncode == 0 and type(cap) is int and cap > 0 else None


def plan_order(nn: str, plans: dict) -> tuple:
    """The order `depends_on` gives the plans of a phase, by plan id: the plans each one names,
    every plan that runs before it, and the entries that name no other plan of the phase, as
    (plan file, entry, the id read from it). An id may be written NN-MM, MM or as the file name."""
    ids = {plan["id"] for plan in plans.values()}
    after, unknown = {}, []
    for name, plan in plans.items():
        wanted = []
        for raw in plan["depends_on"]:
            if raw.lower() in ("none", "null", "~"):
                continue  # written out instead of an empty list
            dep = raw[:-len("-PLAN.md")] if raw.endswith("-PLAN.md") else raw
            dep = nn + "-" + dep if re.fullmatch(r"\d\d", dep) else dep
            if dep in ids and dep != plan["id"]:
                wanted.append(dep)
            else:
                unknown.append((name, raw, dep))
        after[plan["id"]] = wanted

    def reach(start):
        seen, todo = set(), list(after[start])
        while todo:
            dep = todo.pop()
            if dep not in seen:
                seen.add(dep)
                todo.extend(after[dep])
        return seen

    return after, {plan_id: reach(plan_id) for plan_id in after}, unknown


SHOWN_FILES = 5  # the files named in one line about two plans; the line counts the rest


def check_plan_order(pl: Planning, nn: str, plans: dict) -> tuple:
    """How the plans of a phase are ordered and what they share; returns (issues, warnings).

    An issue: a `depends_on` that names no plan of the phase, forms a loop, or points to a
    later wave; a `wave` that is not a whole number when the phase has several plans; and two
    plans of one wave, neither after the other through `depends_on`, that both name a file.
    A generated file is excepted: the component index, the capabilities file, the planning
    folder and the `shared_files` setting. A warning: a wave with more plans that can start at
    once than the coder pool runs here."""
    by_id = {plan["id"]: (name, plan) for name, plan in plans.items()}
    issues, warnings = [], []
    after, earlier, unknown = plan_order(nn, plans)
    for name, plan in plans.items():
        issues.extend(issue(name, 0, "plans", "depends_on names %s, which is %s"
                            % (raw, "this plan" if dep == plan["id"] else "no plan of phase " + nn))
                      for where, raw, dep in unknown if where == name)
        if plan["wave"] is None and len(plans) > 1:
            issues.append(issue(name, 0, "plans", "plan frontmatter: wave is missing or not a whole number from 1 up"))
    for plan_id in sorted(after):
        name, plan = by_id[plan_id]
        if plan_id in earlier[plan_id]:
            issues.append(issue(name, 0, "plans", "depends_on forms a loop: %s depends on itself through %s"
                                % (plan_id, ", ".join(sorted(earlier[plan_id] - {plan_id})) or "its own line")))
        for dep in after[plan_id]:
            if plan["wave"] and by_id[dep][1]["wave"] and by_id[dep][1]["wave"] > plan["wave"]:
                issues.append(issue(name, 0, "plans", "depends_on names %s, which is in a later wave (%d) than this plan (%d)"
                                    % (dep, by_id[dep][1]["wave"], plan["wave"])))
    files, folders = index_paths()
    shared = sorted(files) + list(folders) + [PLANNING + "/", SETTINGS["capabilities_target"]] + list(SETTINGS["shared_files"])
    waves = {}
    for plan_id in sorted(after):
        waves.setdefault(by_id[plan_id][1]["wave"], []).append(plan_id)
    for wave, members in sorted((w, m) for w, m in waves.items() if w):
        for i, first in enumerate(members):
            for second in members[i + 1:]:
                if first in earlier[second] or second in earlier[first]:
                    continue
                named = sorted({a if a == b else "%s and %s" % (a, b)
                                for task in by_id[first][1]["tasks"] for a in task["files"]
                                for other in by_id[second][1]["tasks"] for b in other["files"]
                                if overlap(a, b) and not inside(a, shared) and not inside(b, shared)})
                if named:
                    more = " and %d more" % (len(named) - SHOWN_FILES) if len(named) > SHOWN_FILES else ""
                    issues.append(issue(by_id[first][0], 0, "plans",
                                        "plans %s and %s are both in wave %d, neither depends on the other, and both name %s"
                                        % (first, second, wave, ", ".join(named[:SHOWN_FILES]) + more)))
        cap = track_cap(pl.root) if len(members) > 1 else None
        free = [m for m in members if not earlier[m] & set(members)]
        if cap and len(free) > cap:
            warnings.append(issue(by_id[free[0]][0], 0, "plans", "wave %d has %d plans that can start at once (%s); "
                                  "the coder pool here runs %d" % (wave, len(free), ", ".join(free), cap)))
    return issues, warnings


def traceability(text: str) -> tuple:
    """What NN-TESTS.md lists: its test_dir, and each row of the Traceability table that names
    a test, as (line number, test ids, whether the row is a guard). The rows are None when the
    file has no such table."""
    folder = parse_frontmatter(text).get("test_dir", "").rstrip("/")
    table = re.search(r"^## Traceability[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not table:
        return folder, None
    rows = [(number, TEST_ID.findall(line), line.strip().strip("|").split("|")[-1].strip() == "guard")
            for number, line in enumerate(table.group(1).splitlines(), text[:table.start(1)].count("\n") + 1)]
    return folder, [row for row in rows if row[1]]


def test_path(folder: str, name: str) -> str:
    """A test id with its folder: one written as a bare file name is in the phase's test_dir."""
    name = name[2:] if name.startswith("./") else name
    return folder + "/" + name if folder and "/" not in name.split("::")[0] else name


def check_plans(pl: Planning, nn: str) -> tuple:
    """The plans of a phase together; returns (issues, warnings). Every contract test id in the
    Traceability table of NN-TESTS.md is turned green by a task, the requirements the plans
    name are the phase's, every plan names a requirement and gives each task a verify command,
    a plan's frontmatter lists the tests its tasks claim, and the plans are ordered and share
    files as `check_plan_order` says.
    The ids are the ones the table lists, not every test in the locked files.
    Advisory: no step of the workflow requires it yet."""
    plans = phase_plans(pl, nn)
    pdir = pl.phase_dir(nn)
    where = PLANNING + "/phases/%s-*/" % nn
    if not plans:
        return [issue(where + nn + "-*-PLAN.md", 0, "plans", "phase %s has no plan" % nn)], []
    issues = [issue(name, 0, "plans", "no task found (a '### <id>' block between <tasks> and </tasks>)")
              for name, plan in plans.items() if not plan["tasks"]]
    issues.extend(issue(name, 0, "plans", "plan frontmatter: requirements names no REQ id")
                  for name, plan in plans.items() if not plan["requirements"])
    issues.extend(issue(name, 0, "plans", "task %s: verify is empty" % task["id"])
                  for name, plan in plans.items() for task in plan["tasks"] if not task["verify"])
    tests = pdir / (nn + "-TESTS.md")
    folder, rows = traceability(tests.read_text(encoding="utf-8") if tests.is_file() else "")
    if rows is None:
        issues.append(issue(where + nn + "-TESTS.md", 0, "plans", "no Traceability table to read the test ids from"))

    def full(name):
        return test_path(folder, name)

    claimed = {full(name) for plan in plans.values() for task in plan["tasks"] for name in task["turns_green"]}
    for number, names, guard in rows or []:
        if guard:
            continue  # green from the start by design: no task turns it green
        for name in names:
            if not any(c == full(name) or (not folder and (c.endswith("/" + name) or name.endswith("/" + c)))
                       for c in claimed):
                issues.append(issue(rel(pl.root, tests), number, "plans", "no plan task turns this test green: " + name))
    for name, plan in plans.items():
        # One test whatever its parameters: an id is compared up to its first [.
        listed = {full(test).split("[")[0] for test in plan["claims"]}
        by_tasks = {full(test).split("[")[0] for task in plan["tasks"] for test in task["turns_green"]}
        for message, tests_named in (("plan frontmatter: turns_green does not list %s, which its tasks claim", by_tasks - listed),
                                     ("plan frontmatter: turns_green lists %s, which no task of the plan claims", listed - by_tasks)):
            if tests_named:
                issues.append(issue(name, 0, "plans", message % ", ".join(sorted(tests_named))))
    phase = pl.phase(nn) or {}
    path = pl.dir / "REQUIREMENTS.md"
    _, reqs = parse_requirements(path.read_text(encoding="utf-8")) if path.is_file() else ({}, [])
    owned = set(phase.get("requirements", [])) | {r["id"] for r in reqs if nn in r["phases"]}
    for name, plan in plans.items():
        issues.extend(issue(name, 0, "plans", "%s is not a requirement of phase %s" % (req, nn))
                      for req in sorted(set(plan["requirements"]) - owned))
    served = {req for plan in plans.values() for req in plan["requirements"]}
    issues.extend(issue(PLANNING + "/ROADMAP.md", 0, "plans", "no plan of phase %s names requirement %s" % (nn, req))
                  for req in sorted(owned - served))
    ordered, warnings = check_plan_order(pl, nn, plans)
    return issues + ordered, warnings


INDEX_FILES = ("graph.md", "external.toml", "unassigned-baseline.txt", "layers.toml", "rules.json", "REVIEW.md")


def check_scope(pl: Planning, nn: str, base) -> tuple:
    """What the phase branch changed against what its plans declared; returns (issues, warnings).
    Advisory: no step of the workflow requires it yet.

    A warning: a changed file that is in no task's `files` or `unit_tests` (a path, a folder
    ending in /, or a pattern with *) and is not named in a row of a summary's Deviations table.
    An issue: a component new in the catalog that is on no plan's `new_component:` line (not
    judged when the base has no component, as when the index was first built in this phase).
    Not judged: planning files, the phase's own acceptance tests and locked fixtures (written
    and locked before the plans), and the files of the component index."""
    plans = phase_plans(pl, nn)
    if not plans:
        return [issue(PLANNING + "/phases/%s-*/%s-*-PLAN.md" % (nn, nn), 0, "scope", "phase %s has no plan" % nn)], []
    sha = (git(pl.root, "merge-base", base, "HEAD") or "").strip() if base else merge_base(pl)[1]
    status = git(pl.root, "diff", "--name-status", "-M", "-z", sha) if sha else None
    untracked = git(pl.root, "ls-files", "--others", "--exclude-standard", "-z")
    if status is None or untracked is None:
        return [issue(PLANNING + "/STATE.md", 0, "scope", "cannot find what changed: no merge-base with %s"
                      % (base or "the STATE.md base_branch"))], []
    catalog = SETTINGS["components_catalog"]
    index_files, index_folders = index_paths()
    pdir = pl.phase_dir(nn)
    lock = pdir / (nn + "-TESTLOCK.json")
    try:
        fixtures = set(json.loads(lock.read_text(encoding="utf-8")).get("fixtures", {})) if lock.is_file() else set()
    except (ValueError, AttributeError):
        fixtures = set()
    settled = set(acceptance_files(pl.root, nn)) | fixtures | index_files
    declared = {path for plan in plans.values() for task in plan["tasks"] for path in task["files"]}
    folders = tuple(path for path in declared if path.endswith("/")) + (PLANNING + "/",) + index_folders
    patterns = [path for path in declared if "*" in path]
    excused = set()
    for path in sorted(pdir.glob(nn + "-*-SUMMARY.md")):
        section = re.search(r"^## Deviations from plan[ \t]*\n(.*?)(?=^## |\Z)", path.read_text(encoding="utf-8"),
                            re.M | re.S)
        for row in (section.group(1).splitlines() if section else []):
            if row.strip().startswith("|"):
                excused.update(word[2:] if word.startswith("./") else word for word in re.findall(r"[^\s`|,;()]+", row))
    changed = sorted(p for p in set(changed_paths(status)) | set(untracked.split("\0")) if p)
    warnings = [issue(path, 0, "scope", "changed, but in no plan task's files and in no row of a summary's Deviations table")
                for path in changed
                if path not in settled and path not in declared and path not in excused
                and not path.startswith(folders) and not any(fnmatch.fnmatch(path, pattern) for pattern in patterns)]
    heading = r"^### ([a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)[ \t]*$"
    now = (pl.root / catalog).read_text(encoding="utf-8") if (pl.root / catalog).is_file() else ""
    before = set(re.findall(heading, git(pl.root, "show", sha + ":" + catalog) or "", re.M))
    planned = {name for plan in plans.values() for name in plan["new_components"]}
    issues = [issue(catalog, 0, "scope", "new component %s is on no plan's new_component: line" % name)
              for name in sorted(set(re.findall(heading, now, re.M)) - before - planned)
              if before and not name.startswith("subsystem.")]
    return issues, warnings


def check_capabilities(pl: Planning) -> list:
    """Compare generated capability bytes without loading the product or writing files."""
    script = SETTINGS["capabilities_script"]
    if not script:
        return []
    target = pl.root / SETTINGS["capabilities_target"]
    try:
        generator = runpy.run_path(str(SCRIPT_DIR.parents[3] / script))
        expected = generator["build_index"](pl.root).encode("utf-8")
        if target.is_file() and target.read_bytes() == expected:
            return []
        message = "capability index missing or stale; run " + script
    except (OSError, ValueError, SyntaxError) as exc:
        message = str(exc)
    return [issue("docs/CAPABILITIES.md", 0, "capabilities", message)]


PROCESS_SKILL = Path(SETTINGS["process_skill"])
# `prove.md` §4, `templates/PLAN.md` §2, prove.md "Goals and targets".
TEMPLATE_CITE = re.compile(r"`?(?:templates/([\w.-]+\.md)|(prove\.md))`?\s*(?:§\s*(\d+)|\"([^\"]+)\")")
TEMPLATE_HEADING = re.compile(r"^#{2,}\s+(?:(\d+)\.\s+)?(.+?)\s*$", re.M)
RULE_FILE = re.compile("^" + re.escape(SETTINGS["process_skill"]) + r"/(SKILL\.md|references/[^/]+\.md|templates/[^/]+\.md)$")
DEC_ROW = re.compile(r"^\|\s*(DEC-\d{3})\s*\|", re.M)
# Words after a `§N` citation that say nothing about the section's heading.
CITE_STOPWORDS = frozenset("a an and are as at by each for from gets has have in into is it its of on or per "
                           "that the this to which with".split())


def heading_words(title: str) -> set:
    return {w.lower().rstrip("s") for w in re.findall(r"[A-Za-z]+", title)}


def template_sections(path: Path):
    """Section number -> heading words, and heading titles, of a template (``## 3. Timeboxed prototype``)."""
    text = path.read_text(encoding="utf-8")
    numbers, titles = {}, set()
    for number, title in TEMPLATE_HEADING.findall(text):
        if number:
            numbers[number] = (title.strip(), heading_words(title))
        titles.add(title.strip().lower())
    return numbers, titles


def citation_words(rest: str):
    """The two words after a citation when the first is a content word; () when it is a stopword or punctuation."""
    rest = rest.lstrip()
    if not rest or not rest[0].isalpha():
        return ()
    words = [w.lower() for w in re.findall(r"[A-Za-z]+", rest)[:2]]
    return () if words[0] in CITE_STOPWORDS else tuple(words)


def check_template_citations(pl: Planning) -> list:
    """Each ``prove.md §N`` / ``templates/X.md §N`` (or quoted heading) in the skill exists, and the words
    after a ``§N`` match that section's heading (same number, changed title)."""
    skill = pl.root / PROCESS_SKILL
    files = [skill / "SKILL.md", *sorted((skill / "references").glob("*.md"))]
    issues, cache = [], {}

    def report(path, lineno, message):
        issues.append(issue(rel(pl.root, path), lineno, "citation", message))

    for path in (p for p in files if p.is_file()):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for m in TEMPLATE_CITE.finditer(line):
                name, prove, number, heading = m.groups()
                template = skill / "templates" / ("PROVE.md" if prove else name)
                cited = ("prove.md" if prove else "templates/" + name) + (" §" + number if number else ' "%s"' % heading)
                if not template.is_file():
                    report(path, lineno, "cites a missing template: " + cited)
                    continue
                numbers, titles = cache.setdefault(template, template_sections(template))
                if (number and number not in numbers) or (heading and heading.strip().lower() not in titles):
                    report(path, lineno, "%s has no such section in %s" % (cited, rel(pl.root, template)))
                    continue
                words = citation_words(line[m.end():]) if number else ()
                if words and not {w.rstrip("s") for w in words if w not in CITE_STOPWORDS} & numbers[number][1]:
                    report(path, lineno, "%s is followed by \"%s\" but its heading is \"%s\" in %s"
                           % (cited, " ".join(words), numbers[number][0], rel(pl.root, template)))
    return issues


def merge_base(pl: Planning):
    """(base branch name, merge-base sha with HEAD) using the STATE base branch or origin/<base>; sha None when unknown."""
    try:
        base = pl.state().get("base_branch") or ""
    except ToolError:
        base = ""
    for ref in (base, "origin/" + base) if base else ():
        out = git(pl.root, "merge-base", ref, "HEAD")
        if out and out.strip():
            return base, out.strip()
    return base, None


def changed_paths(name_status: str):
    """Paths in ``git diff --name-status -z`` output; a rename or copy yields both its old and new path."""
    fields = [f for f in name_status.split("\0")]
    i = 0
    while i + 1 < len(fields):
        status = fields[i]
        if status[:1] in "RC" and i + 2 < len(fields):
            yield fields[i + 1]
            yield fields[i + 2]
            i += 3
        else:
            yield fields[i + 1]
            i += 2


def check_rule_decs(pl: Planning) -> list:
    """In a git work tree, a working-tree diff against the base branch that changes process-phase rule text
    (renames and untracked files included) adds a DECISIONS.md row the base lacks, or a commit in the range
    cites an existing DEC. Outside a work tree the check is skipped."""
    if (git(pl.root, "rev-parse", "--is-inside-work-tree") or "").strip() != "true":
        return []
    base, sha = merge_base(pl)

    def cannot(why):
        return [issue(PLANNING + "/STATE.md", 0, "rule-dec", "cannot check process-phase rule changes: " + why)]

    if not sha:
        return cannot("no merge-base of HEAD with base branch %r or origin/%s (STATE.md base_branch)" % (base, base))
    status = git(pl.root, "diff", "--name-status", "-M", "-z", sha)
    untracked = git(pl.root, "ls-files", "--others", "--exclude-standard", "-z")
    if status is None or untracked is None:
        return cannot("git diff against %s (merge-base %s) failed" % (base, sha[:12]))
    changed = set(changed_paths(status)) | {p for p in untracked.split("\0") if p}
    touched = sorted(p for p in changed if RULE_FILE.match(p))
    if not touched:
        return []
    decisions = pl.dir / "DECISIONS.md"
    known = set(DEC_ROW.findall(decisions.read_text(encoding="utf-8"))) if decisions.is_file() else set()
    if known - set(DEC_ROW.findall(git(pl.root, "show", sha + ":" + PLANNING + "/DECISIONS.md") or "")):
        return []
    if known.intersection(re.findall(r"DEC-\d{3}", git(pl.root, "log", "--format=%B", sha + "..HEAD") or "")):
        return []
    return [issue(PLANNING + "/DECISIONS.md", 0, "rule-dec",
                  "process-phase rule text changed without a DEC (add a DECISIONS.md row or cite an existing "
                  "DEC-NNN in a commit message): " + ", ".join(touched))]


def markdown_tables(text: str) -> list:
    """Return pipe tables as lists of (line number, cells), excluding separators."""
    tables, current = [], []
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            current.append((lineno, cells))
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return [table[:1] + table[2:] for table in tables
            if len(table) >= 2 and len(table[0][1]) == len(table[1][1])
            and all(re.fullmatch(r":?-+:?", c) for c in table[1][1])]


def check_prove(pl: Planning, nn: str) -> list:
    pdir = pl.phase_dir(nn)
    path = (pdir or pl.dir / "phases" / nn) / (nn + "-EVIDENCE/prove.md")
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    heading = re.search(r"^### Method record(?:[ \t].*)?$", text, re.M)
    section = re.split(r"^#{1,3} ", text[heading.end():], maxsplit=1, flags=re.M)[0] if heading else ""
    tables = markdown_tables(section)
    template = (TEMPLATES_DIR / "PROVE.md").read_text(encoding="utf-8")
    header = next(line for line in template.splitlines() if line.startswith("| Goal |"))
    expected = [c.strip() for c in header.strip("|").split("|")]
    issues, goals = [], set()
    if not heading or not tables or not tables[0] or tables[0][0][1] != expected:
        issues.append(issue(rel(pl.root, path), 0, "prove", "Method record requires the template's 11-column table"))
    else:
        offset = text[:heading.end()].count("\n")
        for lineno, cells in tables[0][1:]:
            goals.add(cells[0])
            if len(cells) != len(expected) or any(not c or "to fill" in c.lower() for c in cells):
                issues.append(issue(rel(pl.root, path), offset + lineno, "prove",
                                    "method record row has empty, To fill or missing cells"))
    context = pdir / (nn + "-CONTEXT.md") if pdir else None
    context_text = context.read_text(encoding="utf-8") if context and context.is_file() else ""
    goal_heading = re.search(r"^#{1,6} (?:[0-9]+\. )?Goals and targets[^\n]*$", context_text, re.M)
    goal_section = re.split(r"^#{1,6} ", context_text[goal_heading.end():], maxsplit=1, flags=re.M)[0] if goal_heading else ""
    for table in markdown_tables(goal_section):
        if not table or "Verdict" not in table[0][1]:
            continue
        verdict = table[0][1].index("Verdict")
        for _, cells in table[1:]:
            if len(cells) > verdict and cells[verdict].startswith(("Go", "Pivot")) and cells[0] not in goals:
                issues.append(issue(rel(pl.root, path), 0, "prove", "missing method record for " + cells[0]))
    return issues


def cmd_check(pl: Planning, args) -> dict:
    pl.require()
    run_all = args.all or not any([args.context, args.plan, args.skill, args.ignored, args.testlock,
                                   args.docs, args.roadmap, args.requirements, args.state, args.prove,
                                   args.plans, args.scope])
    issues, ran = [], []

    def run(name, fn):
        ran.append(name)
        issues.extend(fn())

    if run_all:
        run("files", lambda: check_top_level(pl))
    if run_all or args.state:
        run("state", lambda: check_state(pl))
    if run_all or args.roadmap:
        run("roadmap", lambda: check_roadmap(pl))
    if run_all or args.requirements:
        run("requirements", lambda: check_requirements(pl))
    if run_all or args.docs:
        run("docs", lambda: check_docs(pl))
    if run_all or args.ignored:
        run("ignored", lambda: check_ignored(pl))
    if run_all:
        run("skills", lambda: check_skills(pl))
        run("testlocks", lambda: check_all_testlocks(pl))
        run("capabilities", lambda: check_capabilities(pl))
        run("citations", lambda: check_template_citations(pl))
        run("rule-decs", lambda: check_rule_decs(pl))
        if (pl.dir / ".eval-answers.yaml").exists():
            issues.append(issue(PLANNING + "/.eval-answers.yaml", 0, "eval", "eval answers must not be committed"))
    if args.skill:
        run("skill", lambda: check_skill(pl.root, Path(args.skill).resolve()))
    if args.testlock:
        run("testlock", lambda: check_testlock(pl, norm_phase(args.testlock)))
    if args.context:
        run("context", lambda: check_doc_file(pl.root, Path(args.context).resolve(), "context", False))
    if args.prove:
        run("prove", lambda: check_prove(pl, norm_phase(args.prove)))
    if args.plan:
        run("plan", lambda: check_doc_file(pl.root, Path(args.plan).resolve(), "plan", True))
    data = {"checks": ran, "issues": issues}
    for name, wanted, fn in (("plans", args.plans, lambda: check_plans(pl, norm_phase(args.plans))),
                             ("scope", args.scope, lambda: check_scope(pl, norm_phase(args.scope), args.base))):
        if wanted:
            ran.append(name)
            found, noted = fn()
            issues.extend(found)
            data.setdefault("warnings", []).extend(noted)
    if issues:
        raise ToolError("CHECK_FAILED", "%d issue(s) found" % len(issues), "fix the listed issues", 1, data)
    return data


def cmd_req_coverage(pl: Planning, args) -> dict:
    pl.require()
    cov = {k: v for k, v in coverage(pl).items() if not k.startswith("_")}
    if cov["pct"] != 100 or cov["unphased_req"]:
        raise ToolError("COVERAGE", "requirement coverage %d%%, %d unphased REQ"
                        % (cov["pct"], len(cov["unphased_req"])), "map every U to a REQ with a phase", 1, cov)
    return cov


# --------------------------------------------------------------------------- testlock / advance / complete


def require_dec(pl: Planning, dec) -> str:
    """A DEC id that exists as a row in DECISIONS.md (used by re-locks and gate overrides)."""
    dec = (dec or "").strip()
    if not DEC_ID.match(dec):
        raise ToolError("NEEDS_DEC", "a DEC-NNN id is required", "add the DEC row to DECISIONS.md first", 2)
    path = pl.dir / "DECISIONS.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not re.search(r"^\|\s*%s\s*\|" % re.escape(dec), text, re.M):
        raise ToolError("UNKNOWN_DEC", "%s is not a row in %s/DECISIONS.md" % (dec, PLANNING),
                        "write the DEC row (reason, human approval) before using it")
    return dec


def cmd_testlock(pl: Planning, args) -> dict:
    pl.require()
    nn = norm_phase(args.phase)
    files = acceptance_files(pl.root, nn)
    if not files:
        raise ToolError("NO_TESTS", "no tests under %s/p%s_*/" % (SETTINGS["acceptance_dir"], nn.replace(".", "_")),
                        "write the phase acceptance tests first (phase-tests skill)")
    data = {"phase": nn, "files": files}
    if not args.write:
        if args.relock or args.fixture:
            raise ToolError("USAGE", "--relock and --fixture need --write", "testlock --phase NN --write ...", 2)
        return data
    pdir = pl.phase_dir(nn)
    lock = (pdir or pl.ensure_phase_dir(nn)) / ("%s-TESTLOCK.json" % nn)
    previous = {}
    if lock.is_file():
        if not args.relock:
            raise ToolError("LOCK_EXISTS", "%s already exists; a locked test changes only by DEC" % rel(pl.root, lock),
                            "write a DEC row, get human approval, then testlock --write --relock --dec DEC-NNN",
                            1, {"lock": rel(pl.root, lock)})
        try:
            previous = json.loads(lock.read_text(encoding="utf-8"))
        except ValueError:
            previous = {}
    elif args.relock:
        raise ToolError("NO_LOCK", "nothing to re-lock for phase %s" % nn, "drop --relock for the first lock", 2)
    dec = require_dec(pl, args.dec) if args.relock else None
    declared = list(args.fixture or []) or sorted(previous.get("fixtures", {}))
    fixtures = fixture_files(pl.root, declared)
    payload = {"phase": nn, "created": previous.get("created", today()), "files": files}
    if fixtures:
        payload["fixtures"] = fixtures
    if args.relock:
        payload["relocks"] = previous.get("relocks", []) + [{"date": today(), "dec": dec}]
    lock.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    data.update({"lock": rel(pl.root, lock), "fixtures": fixtures, "relock": dec})
    return data


def set_roadmap_status(pl: Planning, nn: str, status: str) -> bool:
    path = pl.dir / "ROADMAP.md"
    phase = pl.phase(nn)
    if phase is None or "Status" not in phase["_lines"]:
        return False
    lines = path.read_text(encoding="utf-8").split("\n")
    idx = phase["_lines"]["Status"] - 1
    lines[idx] = re.sub(r"(\*\*Status:\*\*\s*).*$", lambda m: m.group(1) + status, lines[idx])
    path.write_text("\n".join(lines), encoding="utf-8")
    return True


def evidence_problems(pl: Planning, nn: str) -> list:
    try:
        cmd_evidence_check(pl, argparse.Namespace(phase=nn))
    except ToolError as exc:
        return ["evidence-check: %s" % exc.message]
    return []


def gate_problems(pl: Planning, nn: str, target: str) -> list:
    """Blocking prerequisites of a transition (empty list = the gate is satisfied)."""
    problems = []
    pdir = pl.phase_dir(nn)
    context = pdir / (nn + "-CONTEXT.md") if pdir else None
    if (STATUSES.index(target) >= STATUSES.index("tests_approved")
            and context and context.is_file()
            and parse_frontmatter(context.read_text(encoding="utf-8")).get("evidence_gate") == "required"
            and (pdir / (nn + "-EVIDENCE/prove.md")).is_file()):
        problems.extend("prove: " + i["message"] for i in check_prove(pl, nn))
    if target == "implemented" and pdir:
        for plan in sorted(pdir.glob(nn + "-*-PLAN.md")):
            goal = parse_frontmatter(plan.read_text(encoding="utf-8")).get("prove_method")
            if goal and not (pdir / (nn + "-EVIDENCE/parity/" + goal + ".md")).is_file():
                problems.append("parity: missing " + nn + "-EVIDENCE/parity/" + goal + ".md")
    if target == "gaps_found":
        return problems + ["missing artifact: " + m for m in missing_artifacts(pl, nn, "verified")
                if m.endswith("VERIFICATION.md")]
    if STATUSES.index(target) < STATUSES.index(GATED_FROM):
        if target == "tests_approved":
            problems.extend("missing artifact: " + m for m in missing_artifacts(pl, nn, target)
                            if m.endswith("/prove.md"))
        lock = pl.phase_dir(nn) and (pl.phase_dir(nn) / ("%s-TESTLOCK.json" % nn))
        if lock and lock.is_file():  # a lock that exists must be clean even before the gate
            problems.extend("testlock: %s %s" % (i["file"], i["message"]) for i in check_testlock(pl, nn))
        return problems
    problems.extend("missing artifact: " + m for m in missing_artifacts(pl, nn, target))
    problems.extend("testlock: %s %s" % (i["file"], i["message"]) for i in check_testlock(pl, nn)
                    if "no lock" not in i["message"])
    if target == "verified":
        problems.extend(evidence_problems(pl, nn))
    return problems


def cmd_advance(pl: Planning, args) -> dict:
    pl.require()
    state = pl.state()
    nn = norm_phase(state.get("current_phase", "00"))
    current, target = state.get("phase_status", "not_started"), args.to
    if target not in TRANSITIONS.get(current, []):
        hint = "allowed: %s" % (", ".join(TRANSITIONS.get(current, [])) or "none")
        if target == "complete":
            hint = "use 'phase_tool.py complete --phase %s' after verification" % nn
        raise ToolError("INVALID_TRANSITION", "%s -> %s is not allowed" % (current, target), hint,
                        1, {"phase": nn, "from": current, "to": target})
    completed = phase_list(state.get("completed_phases", ""))
    waiting = [d for d in (pl.phase(nn) or {}).get("depends_on", []) if d not in completed]
    if waiting:
        raise ToolError("DEPENDENCIES_INCOMPLETE", "phase %s depends on %s, not complete" % (nn, ", ".join(waiting)),
                        "finish those phases first, or 'activate --phase NN --dec DEC-NNN' a phase that can start",
                        1, {"phase": nn, "from": current, "to": target, "waiting_on": waiting})
    problems = gate_problems(pl, nn, target)
    # Only missing artifacts can be waived by a DEC; a dirty test lock or unsupported evidence never can.
    hard = [p for p in problems if not p.startswith("missing artifact: ")]
    override = None
    if problems and args.override and not hard:
        override = require_dec(pl, args.override)
    elif problems:
        raise ToolError("GATE_BLOCKED", "%s -> %s blocked by %d unmet prerequisite(s)" % (current, target, len(problems)),
                        "produce the artifacts in the right step; missing artifacts (only) may be waived with "
                        "--override DEC-NNN after a human-approved DEC",
                        1, {"phase": nn, "from": current, "to": target, "problems": problems, "hard": hard})
    update_frontmatter(pl.dir / "STATE.md", {
        "current_phase": nn, "phase_status": target, "active_step": NEXT_STEP[target], "last_activity": today()})
    warnings = ["missing artifact: " + m for m in missing_artifacts(pl, nn, target)]
    if override:
        warnings.append("gate overridden by %s: %s" % (override, "; ".join(problems)))
    if not set_roadmap_status(pl, nn, target):
        warnings.append("ROADMAP.md has no Status line for phase %s" % nn)
    return {"phase": nn, "from": current, "to": target, "active_step": NEXT_STEP[target],
            "warnings": warnings, "override": override}


BRANCH_NAME = re.compile("^" + re.escape(SETTINGS["branch_prefix"]) + r"(\d{2,}(?:\.\d+)?)-[a-z0-9-]+$")


def cmd_branch(pl: Planning, args) -> dict:
    """Show or set STATE.phase_branch (the only writer of that key; git itself is not touched)."""
    pl.require()
    state = pl.state()
    if args.set is None:
        return {"phase_branch": state.get("phase_branch"), "base_branch": state.get("base_branch"),
                "branch": (git(pl.root, "rev-parse", "--abbrev-ref", "HEAD") or "").strip() or None}
    name = args.set.strip()
    nn = norm_phase(state.get("current_phase", "00"))
    if name != state.get("base_branch") and not BRANCH_NAME.match(name):
        raise ToolError("BAD_BRANCH", "phase branch %r must be %sNN-<slug> or the base branch" % (name, SETTINGS["branch_prefix"]),
                        "e.g. %s01-safety-net" % SETTINGS["branch_prefix"], 2)
    if BRANCH_NAME.match(name) and BRANCH_NAME.match(name).group(1) != nn:
        raise ToolError("BAD_BRANCH", "branch %s does not match current phase %s" % (name, nn), "", 2)
    update_frontmatter(pl.dir / "STATE.md", {"current_phase": nn, "phase_status": state.get("phase_status", "not_started"),
                                           "phase_branch": name, "last_activity": today()})
    return {"phase_branch": name, "previous": state.get("phase_branch")}


def validate_requirements(pl: Planning, completed: list) -> int:
    path = pl.dir / "REQUIREMENTS.md"
    if not path.is_file():
        return 0
    lines = path.read_text(encoding="utf-8").split("\n")
    _, reqs = parse_requirements("\n".join(lines))
    count = 0
    for r in reqs:
        if r["phases"] and all(p in completed for p in r["phases"]) and r["status"] == "Planned":
            idx = r["line"] - 1
            lines[idx] = re.sub(r"\|\s*Planned\s*\|\s*$", "| Validated |", lines[idx])
            count += 1
    path.write_text("\n".join(lines), encoding="utf-8")
    return count


def cmd_activate(pl: Planning, args) -> dict:
    pl.require()
    state = pl.state()
    nn = norm_phase(args.phase)
    phase = pl.phase(nn)
    completed = phase_list(state.get("completed_phases", ""))
    if state.get("phase_status") not in (None, "", "not_started"):
        raise ToolError("NOT_ACTIVATABLE", "current phase must be not_started or empty")
    if not phase or phase["status"] == "complete" or nn in completed:
        raise ToolError("NOT_ACTIVATABLE", "phase %s must be an incomplete roadmap phase" % nn)
    if any(d not in completed for d in phase["depends_on"]):
        raise ToolError("NOT_ACTIVATABLE", "phase %s has incomplete dependencies" % nn)
    dec = require_dec(pl, args.dec)
    update_frontmatter(pl.dir / "STATE.md", {"current_phase": nn, "phase_status": "not_started",
                                           "active_step": None, "last_activity": today()})
    return {"phase": nn, "dec": dec, "phase_status": "not_started"}


def cmd_complete(pl: Planning, args) -> dict:
    pl.require()
    state = pl.state()
    nn = norm_phase(args.phase)
    if nn != norm_phase(state.get("current_phase", "00")) or state.get("phase_status") != "verified":
        raise ToolError("NOT_VERIFIED", "phase %s must be the current phase with status verified" % nn,
                        "run the Verify step and advance --to verified first")
    pdir = pl.phase_dir(nn)
    if pdir:
        sources = [pdir / (nn + "-" + suffix + ".md") for suffix in ("DISCUSSION-LOG", "VERIFICATION")]
        if any(p.is_file() and any(
                not line.startswith("#") and re.search(r"\bdeferred\b", line, re.I)
                for line in p.read_text(encoding="utf-8").splitlines()) for p in sources):
            ledger = pdir / (nn + "-DEFERRED.md")
            tables = markdown_tables(ledger.read_text(encoding="utf-8")) if ledger.is_file() else []
            if not any(len(table) > 1 and any(any(c for c in row[1]) for row in table[1:]) for table in tables):
                raise ToolError("DEFERRALS_UNLEDGERED", "phase %s mentions deferred work without a ledger row" % nn)
    completed = phase_list(state.get("completed_phases", ""))
    if nn not in completed:
        completed.append(nn)
    updated = []
    if set_roadmap_status(pl, nn, "complete"):
        updated.append(PLANNING + "/ROADMAP.md")
    completed = sorted(completed, key=phase_key)
    later = open_phases(pl, completed)
    updates = {"completed_phases": ",".join(completed), "active_step": None, "last_activity": today()}
    updates.update({"current_phase": later[0], "phase_status": "not_started"} if later
                   else {"phase_status": "complete"})
    update_frontmatter(pl.dir / "STATE.md", updates)
    updated.append(PLANNING + "/STATE.md")
    validated = validate_requirements(pl, completed)
    if validated:
        updated.append(PLANNING + "/REQUIREMENTS.md")
    data = {"phase": nn, "completed_phases": completed,
            "current_phase": later[0] if later else nn, "validated_reqs": validated, "updated": updated}
    if later:
        waiting = [d for d in (pl.phase(later[0]) or {}).get("depends_on", []) if d not in completed]
        if waiting:
            data["blockers"] = ["phase %s not complete" % d for d in waiting]
    return data


# --------------------------------------------------------------------------- migration / goldens / evidence


def module_name(token: str):
    token = token.strip("` ")
    if token.endswith(".py") or "/" in token:
        token = re.sub(r"^src/", "", token)
        token = re.sub(r"(/__init__)?\.py$", "", token).strip("/").replace("/", ".")
    if PACKAGE_PREFIX and not token.startswith(PACKAGE_PREFIX):
        token = PACKAGE_PREFIX + token
    return token if re.match(r"^[\w.]+$", token) else None


def cmd_migration_check(pl: Planning, args) -> dict:
    pl.require()
    path = pl.dir / "MIGRATION.md"
    if not path.is_file():
        raise ToolError("NO_MIGRATION", PLANNING + "/MIGRATION.md is missing")
    deleted = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) > 1 and any(re.search(r"\bdeleted\b", c, re.I) for c in cells[1:]):
            name = module_name((re.findall(r"`([^`]+)`", cells[0]) or [cells[0]])[0])
            if name and name != PACKAGE_PREFIX:
                deleted.append(name)
    violations = []
    src = pl.root / "src"
    for py in sorted(src.rglob("*.py")) if src.is_dir() else []:
        for lineno, line in enumerate(py.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for mod in deleted:
                parent, _, leaf = mod.rpartition(".")
                pattern = r"^\s*(from\s+%s(\.|\s)|import\s+%s(\.|\s|$)|from\s+%s\s+import\s+.*\b%s\b)" % (
                    re.escape(mod), re.escape(mod), re.escape(parent), re.escape(leaf))
                if re.search(pattern, line):
                    violations.append({"module": mod, "file": rel(pl.root, py), "line": lineno})
    data = {"deleted_modules": deleted, "violations": violations}
    if violations:
        raise ToolError("MIGRATION", "%d import(s) of deleted modules" % len(violations),
                        "import the new package instead (see MIGRATION.md)", 1, data)
    return data


def golden_base(pl: Planning, state: dict, explicit):
    """Ref the phase's goldens are compared against: --base, else merge-base(base_branch, HEAD)."""
    if explicit:
        return explicit, "explicit --base"
    base = state.get("base_branch") or "HEAD"
    out = git(pl.root, "merge-base", base, "HEAD")
    if out and out.strip():
        return out.strip(), "merge-base of %s and HEAD" % base
    return "HEAD", "base branch %s not found; compared with HEAD only" % base


def cmd_golden_diff(pl: Planning, args) -> dict:
    """Golden files changed on this phase (committed since the base or uncommitted) must be declared."""
    pl.require()
    state = pl.state()
    base, how = golden_base(pl, state, getattr(args, "base", None))
    out = git(pl.root, "diff", "--name-only", base, "--", SETTINGS["golden_dir"])
    if out is None:
        return {"changed": [], "undeclared": [], "base": base, "note": "git diff unavailable (no git or no HEAD)"}
    untracked = git(pl.root, "ls-files", "--others", "--exclude-standard", "--", SETTINGS["golden_dir"]) or ""
    changed = sorted({ln.strip() for ln in (out + "\n" + untracked).splitlines() if ln.strip()})
    pdir = pl.phase_dir(norm_phase(state.get("current_phase", "00")))
    declared_text = "".join(p.read_text(encoding="utf-8") for p in sorted(pdir.glob("*.md"))) if pdir else ""
    undeclared = [c for c in changed if c not in declared_text]
    data = {"changed": changed, "undeclared": undeclared, "base": base, "base_note": how}
    if undeclared:
        raise ToolError("GOLDENS_CHANGED", "%d golden file(s) changed without declaration" % len(undeclared),
                        "declare each changed golden in the phase SUMMARY/PLAN with a DEC id", 1, data)
    return data


def cmd_evidence_check(pl: Planning, args) -> dict:
    pl.require()
    nn = norm_phase(args.phase or pl.state().get("current_phase", "00"))
    pdir = pl.phase_dir(nn)
    ver = pdir / ("%s-VERIFICATION.md" % nn) if pdir else None
    if ver is None or not ver.is_file():
        raise ToolError("NO_VERIFICATION", "no %s-VERIFICATION.md for phase %s" % (nn, nn),
                        "the Verify step writes it with evidence paths")
    cited = sorted(set(p for p in re.findall(r"`([^`\s]+)`", ver.read_text(encoding="utf-8"))
                       if "-EVIDENCE/" in p))
    unsupported = [p for p in cited if not ((pl.root / p).exists() or (pdir / p).exists())]
    data = {"phase": nn, "cited": cited, "unsupported": unsupported}
    if not cited:
        raise ToolError("NO_EVIDENCE", "%s-VERIFICATION.md cites no %s-EVIDENCE/ path" % (nn, nn),
                        "cite each run log or artifact in backticks, e.g. `%s-EVIDENCE/runs/pytest.txt`" % nn, 1, data)
    if unsupported:
        raise ToolError("UNSUPPORTED_CLAIM", "%d evidence path(s) missing" % len(unsupported),
                        "save the run output under %s-EVIDENCE/" % nn, 1, data)
    return data


# --------------------------------------------------------------------------- facts


# What `facts` writes: each value type, and each fact type as (reading, ((role, value type), ...)).
# The shape is the one `components_index.py facts` writes, so one rule checker reads both.
FACT_VALUES = {"plan": "String", "task": "String", "test": "String", "path": "String", "requirement": "String",
               "component": "String", "kind": "String", "key": "String", "value": "String", "wave": "Integer"}
FACT_TYPES = {
    "plan_in_wave": ("{Plan} is in {Wave}", (("plan", "plan"), ("wave", "wave"))),
    "plan_depends_on": ("{Plan} names {Plan} in depends_on", (("plan", "plan"), ("earlier", "plan"))),
    "plan_runs_after": ("{Plan} runs after {Plan}", (("plan", "plan"), ("earlier", "plan"))),
    "plan_names_requirement": ("{Plan} names {Requirement}", (("plan", "plan"), ("requirement", "requirement"))),
    "plan_reuses_component": ("{Plan} reuses {Component}", (("plan", "plan"), ("component", "component"))),
    "plan_adds_component": ("{Plan} adds {Component}", (("plan", "plan"), ("component", "component"))),
    "plan_declares": ("{Plan} declares {Key} as {Value}", (("plan", "plan"), ("key", "key"), ("value", "value"))),
    "task_in_plan": ("{Task} is in {Plan}", (("task", "task"), ("plan", "plan"))),
    "task_has_type": ("{Task} is of {Kind}", (("task", "task"), ("type", "kind"))),
    "task_turns_green": ("{Task} turns green {Test}", (("task", "task"), ("test", "test"))),
    "task_names_file": ("{Task} names {Path} in its files", (("task", "task"), ("path", "path"))),
    "task_reads_first": ("{Task} reads {Path} first", (("task", "task"), ("path", "path"))),
    "test_is_in_contract": ("{Test} is in the contract as {Kind}", (("test", "test"), ("kind", "kind"))),
}


def cmd_facts(pl: Planning, args) -> dict:
    """The plans of a phase as rows of facts, for a rule checker (`rules_check.py check --phase`).

    A fact is what a plan says, not a judgment: `check --plans` is where the plans are checked.
    `plan_runs_after` is every plan before a plan through `depends_on`, the named ones and the
    ones they name. A test id is written with its folder, as `check --plans` compares it.
    `task_names_file` holds `files` and `unit_tests` as written: a path, a folder ending in /,
    or a pattern with *. The plan file behind each plan is under `evidence`, for printing."""
    pl.require()
    nn = norm_phase(args.phase)
    plans = phase_plans(pl, nn)
    if not plans:
        raise ToolError("NO_PLANS", "phase %s has no plan" % nn, "write the plans first (the Plan step)")
    pdir = pl.phase_dir(nn)
    tests = pdir / (nn + "-TESTS.md")
    folder, table = traceability(tests.read_text(encoding="utf-8") if tests.is_file() else "")
    after, earlier, _ = plan_order(nn, plans)
    found = {name: [] for name in FACT_TYPES}
    for plan in plans.values():
        me = plan["id"]
        if plan["wave"]:
            found["plan_in_wave"].append((me, plan["wave"]))
        found["plan_depends_on"].extend((me, dep) for dep in after[me])
        found["plan_runs_after"].extend((me, dep) for dep in earlier[me] if dep != me)
        found["plan_names_requirement"].extend((me, req) for req in plan["requirements"])
        found["plan_reuses_component"].extend((me, name) for name in plan["reuse"])
        found["plan_adds_component"].extend((me, name) for name in plan["new_components"])
        found["plan_declares"].extend((me, key, value) for key, value in plan["declares"].items())
        for task in plan["tasks"]:
            found["task_in_plan"].append((task["id"], me))
            if task["type"]:
                found["task_has_type"].append((task["id"], task["type"]))
            found["task_turns_green"].extend((task["id"], test_path(folder, test)) for test in task["turns_green"])
            found["task_names_file"].extend((task["id"], path) for path in task["files"])
            found["task_reads_first"].extend((task["id"], path) for path in task["read_first"])
    found["test_is_in_contract"] = [(test_path(folder, test), "guard" if guard else "contract")
                                    for _, names, guard in table or [] for test in names]
    return {
        "format": "devtools-facts/1",
        "revision": (git(pl.root, "rev-parse", "HEAD") or "").strip(),
        "phase": nn,
        "types": {"values": FACT_VALUES,
                  "facts": {name: {"reading": reading, "roles": [list(role) for role in roles]}
                            for name, (reading, roles) in FACT_TYPES.items()}},
        "facts": {name: [dict(zip((role for role, _ in FACT_TYPES[name][1]), row)) for row in sorted(set(rows))]
                  for name, rows in found.items()},
        "evidence": {"plans": {plan["id"]: name for name, plan in plans.items()}},
    }


# --------------------------------------------------------------------------- CLI


COMMANDS = {
    "setup": cmd_setup, "status": cmd_status, "init": cmd_init, "activate": cmd_activate, "roadmap": cmd_roadmap, "check": cmd_check,
    "req-coverage": cmd_req_coverage, "testlock": cmd_testlock, "advance": cmd_advance,
    "complete": cmd_complete, "branch": cmd_branch, "migration-check": cmd_migration_check,
    "golden-diff": cmd_golden_diff, "evidence-check": cmd_evidence_check, "facts": cmd_facts,
}


def build_parser() -> Parser:
    parser = Parser(prog="phase_tool.py", description=__doc__.splitlines()[0])
    parser.add_argument("--format", choices=["json", "md"], default="md")
    parser.add_argument("--root", default=None)
    # Sub-commands accept the same options; SUPPRESS keeps values given before the command.
    common = Parser(add_help=False)
    common.add_argument("--format", choices=["json", "md"], default=argparse.SUPPRESS)
    common.add_argument("--root", default=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd", required=True, parser_class=Parser)
    p = sub.add_parser("setup", parents=[common])
    p.add_argument("--name")
    p.add_argument("--base-branch")
    p.add_argument("--release-branch")
    p = sub.add_parser("status", parents=[common])
    p.add_argument("--phase")
    p.add_argument("--brief", action="store_true")
    sub.add_parser("init", parents=[common]).add_argument("--phase", required=True)
    p = sub.add_parser("activate", parents=[common])
    p.add_argument("--phase", required=True)
    p.add_argument("--dec", required=True)
    p = sub.add_parser("roadmap", parents=[common])
    p.add_argument("action", choices=["list", "get"])
    p.add_argument("phase", nargs="?")
    p = sub.add_parser("check", parents=[common])
    for flag in ("--all", "--ignored", "--docs", "--roadmap", "--requirements", "--state"):
        p.add_argument(flag, action="store_true")
    for flag in ("--context", "--plan", "--skill", "--testlock", "--prove", "--plans", "--scope", "--base"):
        p.add_argument(flag)
    sub.add_parser("req-coverage", parents=[common])
    p = sub.add_parser("testlock", parents=[common])
    p.add_argument("--phase", required=True)
    p.add_argument("--write", action="store_true")
    p.add_argument("--fixture", action="append", default=[])
    p.add_argument("--relock", action="store_true")
    p.add_argument("--dec")
    p = sub.add_parser("advance", parents=[common])
    p.add_argument("--to", required=True, choices=STATUSES)
    p.add_argument("--override")
    sub.add_parser("complete", parents=[common]).add_argument("--phase", required=True)
    sub.add_parser("branch", parents=[common]).add_argument("--set")
    sub.add_parser("migration-check", parents=[common])
    sub.add_parser("golden-diff", parents=[common]).add_argument("--base")
    sub.add_parser("evidence-check", parents=[common]).add_argument("--phase")
    sub.add_parser("facts", parents=[common]).add_argument("--phase", required=True)
    return parser


def render_md(env: dict) -> str:
    lines = ["%s: %s" % (env["tool"], "ok" if env["ok"] else "FAILED")]
    if "error" in env:
        err = env["error"]
        lines.append("error %s: %s" % (err["code"], err["message"]))
        if err.get("hint"):
            lines.append("hint: " + err["hint"])
    for key, value in env.get("data", {}).items():
        if key == "issues" or (key == "warnings" and value and isinstance(value[0], dict)):
            mark = "- " if key == "issues" else "- warning: "
            lines.extend(mark + "%s:%s [%s] %s" % (i["file"], i["line"], i["rule"], i["message"]) for i in value)
        elif key == "block":
            lines.append(value)
        elif isinstance(value, (list, dict)):
            lines.append("%s: %s" % (key, json.dumps(value, sort_keys=True)))
        else:
            lines.append("%s: %s" % (key, value))
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    fmt = "json" if any(a == "json" and i and argv[i - 1] == "--format" for i, a in enumerate(argv)) \
        or "--format=json" in argv else "md"
    cmd = next((a for a in argv if a in COMMANDS), "usage")
    env = {"ok": True, "tool": "phase_tool." + cmd, "version": VERSION, "data": {}}
    code = 0
    try:
        args = build_parser().parse_args(argv)
        fmt, cmd = args.format, args.cmd
        env["tool"] = "phase_tool." + cmd
        env["data"] = COMMANDS[cmd](Planning(find_root(args.root)), args)
    except ToolError as exc:
        env.update(ok=False, data=exc.data, error={"code": exc.code, "message": exc.message, "hint": exc.hint})
        code = exc.exit_code
    except Exception as exc:  # noqa: BLE001 - one envelope even on bugs
        env.update(ok=False, error={"code": "INTERNAL", "message": "%s: %s" % (type(exc).__name__, exc),
                                    "hint": "report this as a phase_tool bug"})
        code = 1
    if cmd == "status":
        code = 0
    print(json.dumps(env, indent=2, sort_keys=False) if fmt == "json" else render_md(env))
    return code


if __name__ == "__main__":
    sys.exit(main())
