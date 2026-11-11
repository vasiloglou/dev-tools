#!/usr/bin/env python3
"""Move a project's planning folder from GSD to the dev-tools phase workflow.

Both keep their plan in ``.planning/`` and both name a phase folder ``phases/NN-<slug>/``,
so the phase folders stay as they are. What differs is the format of three files
(``STATE.md``, ``ROADMAP.md``, ``REQUIREMENTS.md``) and the files GSD does not have
(``MANIFESTO.md``, ``DECISIONS.md`` and the smaller ones).

    python3 <dev-tools>/devtools/from_gsd.py survey  --project .
    python3 <dev-tools>/devtools/from_gsd.py convert --project . [--dry-run]

``survey`` writes nothing. ``convert`` copies GSD's own files to
``.planning/archive/gsd/``, writes the three files in the dev-tools format, creates the
missing ones (never overwriting a file that exists) and writes a record of every choice
it made. It never calls git and never touches a phase folder.
``skills/move-from-gsd/SKILL.md`` is the guide that uses it. Python 3.11 or newer.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SOURCE_ROOT / "skills/phase/process-phase/templates/planning"
ARCHIVE = "archive/gsd"
MOVED = ["STATE.md", "ROADMAP.md", "REQUIREMENTS.md", "PROJECT.md", "config.json"]
# GSD's own files and folders that stay where they are: other documents link to them.
HISTORY = ["MILESTONES.md", "RETROSPECTIVE.md", "milestones", "research", "codebase", "quick",
           "debug", "todos", "workstreams", "forensics", "notes"]
RUNTIMES = [".claude", ".codex", ".opencode", ".gemini", ".agents"]
INSTALLED = ["get-shit-done", "gsd-core", "commands/gsd", "commands/gsd-*", "agents/gsd-*", "hooks/gsd-*",
             "skills/gsd-*", "GSD-SETUP.md", "gsd-file-manifest.json"]
INSTRUCTION_FILES = ["CLAUDE.md", "AGENTS.md", "GEMINI.md"]

HEAD = re.compile(r"^(#{2,4})\s+(?:\S+\s+)?Phase\s+(\d+(?:\.\d+)?)\s*[:—–-]\s*(.+?)\s*$")
ITEM = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(\*\*)?Phase\s+(\d+(?:\.\d+)?)\s*[:—–-]\s*(.+)$")
FIELD = re.compile(r"^\*\*([A-Za-z ]+?)(?:\*\*\s*:|:\*\*)\s*(.*)$")
VERSION = re.compile(r"\bv\d+(?:\.\d+)+\b")
REQ_BULLET = re.compile(r"^\s*[-*]\s+(?:\[([ xX])\]\s+)?\*\*([A-Za-z][A-Za-z0-9-]*-\d+[a-z]?)\*\*\s*:?\s*(.*)$")
TRACE_ROW = re.compile(r"^\|\s*([A-Za-z][A-Za-z0-9-]*-\d+[a-z]?)\s*\|\s*([^|]*)\|")
SIMPLE_ID = re.compile(r"^(?:REQ-)?([A-Za-z][A-Za-z0-9-]*?)-(\d+)$")
FOLDER = re.compile(r"^(\d+(?:\.\d+)?)-(.+)$")


class Stop(Exception):
    """The project cannot be converted as it stands; the message says what to do."""


def norm(value: str) -> str:
    major, dot, minor = str(value).partition(".")
    return "%02d.%d" % (int(major), int(minor)) if dot else "%02d" % int(major)


def key(nn: str) -> tuple:
    major, dot, minor = nn.partition(".")
    return int(major), int(minor) if dot else -1


def shown(nn: str) -> str:
    """The id as a roadmap heading writes it: 7, 7.1."""
    major, dot, minor = nn.partition(".")
    return "%d.%s" % (int(major), minor) if dot else str(int(major))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    out = {}
    for line in text[3:end if end > 0 else len(text)].splitlines():
        if line[:1] not in (" ", "\t", "") and ":" in line:
            name, _, value = line.partition(":")
            out[name.strip()] = value.strip().strip('"').strip("'")
    return out


def plain(text: str) -> str:
    text = re.sub(r"\s*\((?:INSERTED|inserted)\)", "", text)
    return re.sub(r"\s+", " ", text.replace("**", "").replace("`", "")).strip(" -—–:*✅✓")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60].strip("-") or "phase"


def cell(text: str) -> str:
    """Text that is safe inside one table cell: the phase tool splits a row on every '|'."""
    return re.sub(r"\s+", " ", text.replace("|", "/")).strip()


def sections(text: str, level: int = 2) -> dict:
    """{heading: body} for the headings of one level, in order."""
    out, name, mark = {}, None, "#" * level + " "
    for line in text.splitlines():
        if line.startswith(mark):
            name = line[len(mark):].strip()
            out[name] = []
        elif name is not None:
            out[name].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


# --------------------------------------------------------------------------- reading GSD


def runs(found: list) -> list:
    """Split phases in file order into numbering runs: a run ends where a number comes back
    with another title, which is how a milestone that restarted its numbering shows."""
    out, current = [], {}
    for entry in found:
        old = current.get(entry["id"])
        if old is not None and old["title"].lower() != entry["title"].lower():
            out.append(current)
            current = {}
        current[entry["id"]] = entry
    return out + [current] if current else out


def read_roadmap(text: str) -> tuple:
    """(runs of checklist entries, runs of detail sections)."""
    lines = text.splitlines()
    items, heads, milestone = [], [], ""
    for i, line in enumerate(lines):
        if (line.startswith("#") or line.startswith("**") or "<summary>" in line) and not HEAD.match(line):
            found = VERSION.search(line)
            milestone = found.group(0) if found else milestone
        m = ITEM.match(line)
        if m:
            rest = m.group(4)
            if m.group(2):
                title, _, tail = rest.partition("**")
            else:
                cut = re.search(r"\s[-—–]\s|\s\(", rest)
                title, tail = (rest[:cut.start()], rest[cut.start():]) if cut else (rest, "")
            date = re.search(r"\d{4}-\d{2}-\d{2}", tail)
            items.append({"id": norm(m.group(3)), "title": plain(title), "done": m.group(1) != " ",
                          "note": plain(tail), "date": date.group(0) if date else "",
                          "milestone": milestone, "line": i + 1})
            continue
        m = HEAD.match(line)
        if not m:
            continue
        level, fields, criteria, plans, in_criteria = len(m.group(1)), {}, [], 0, False
        for body in lines[i + 1:]:
            if re.match(r"^#{1,%d}\s" % level, body) or HEAD.match(body):
                break
            fm = FIELD.match(body)
            if body.lower().startswith("**success criteria"):
                in_criteria = True
            elif fm:
                in_criteria = fm.group(1).strip().lower().startswith("success criteria")
                fields.setdefault(fm.group(1).strip().lower(), fm.group(2).strip())
            elif in_criteria and re.match(r"^\s*(?:\d+\.|[-*])\s+\S", body):
                criteria.append(plain(re.sub(r"^\s*(?:\d+\.|[-*])\s+", "", body)))
            elif re.match(r"^\s*[-*]\s+\[[ xX]\]\s+\S*PLAN\.md", body):
                plans += 1
        heads.append({"id": norm(m.group(2)), "title": plain(m.group(3)), "fields": fields,
                      "criteria": criteria, "plans": plans, "line": i + 1})
    return runs(items), runs(heads)


def read_folders(planning: Path) -> tuple:
    folders, odd = {}, []
    base = planning / "phases"
    for path in sorted(base.iterdir()) if base.is_dir() else []:
        m = FOLDER.match(path.name)
        if not path.is_dir():
            continue
        if not m:
            odd.append("%s: not named NN-<slug>, so no phase reads it" % path.name)
            continue
        nn = norm(m.group(1))
        if nn != m.group(1):
            odd.append("%s: the phase tool looks for %s-%s; rename the folder" % (path.name, nn, m.group(2)))
        if nn in folders:
            odd.append("%s: a second folder for phase %s; only %s is read" % (path.name, shown(nn), folders[nn]["name"]))
            continue
        plans = sorted(p.name for p in path.glob("*-PLAN.md"))
        summaries = sorted(p.name for p in path.glob("*-SUMMARY.md"))
        verification = sorted(path.glob("*-VERIFICATION.md"))
        folders[nn] = {
            "name": path.name, "slug": m.group(2), "context": any(path.glob("*-CONTEXT.md")),
            "plans": plans, "summaries": summaries,
            "unnumbered": [p for p in plans if not re.match(r"^\d+(?:\.\d+)?-\d\d-PLAN\.md$", p)],
            "verification": verification[0].name if verification else "",
            "verified": frontmatter(read(verification[0])).get("status", "") if verification else "",
        }
    return folders, odd


def status_from_files(folder) -> tuple:
    """The furthest status the files of an unfinished phase support, and why."""
    if not folder:
        return "not_started", "no folder"
    if folder["plans"] and len(folder["summaries"]) >= len(folder["plans"]):
        return "implemented", "every plan has a summary; Verify has not run under dev-tools"
    if folder["plans"]:
        return "plan_approved", "%d plan(s), %d summary(ies)" % (len(folder["plans"]), len(folder["summaries"]))
    if folder["context"]:
        return "context_approved", "a CONTEXT file and no plan"
    return "not_started", "a folder with no CONTEXT and no plan"


def read_requirements(planning: Path) -> dict:
    """Requirements GSD tracks now, those it put off, and every definition in the archives."""
    current, later, where, group = [], [], {}, ""
    text = read(planning / "REQUIREMENTS.md")
    for line in text.splitlines():
        if line.startswith("#"):
            group = plain(line.lstrip("#"))
            continue
        m = REQ_BULLET.match(line)
        if m and m.group(1) is not None:
            current.append({"gsd": m.group(2), "text": plain(m.group(3)), "done": m.group(1) != " ", "group": group})
        elif m:
            later.append({"gsd": m.group(2), "text": plain(m.group(3)), "group": group})
        elif current and line.startswith("  ") and line.strip() and not later:
            current[-1]["text"] += " " + plain(line)
        t = TRACE_ROW.match(line)
        if t and "---" not in line:
            where.setdefault(t.group(1), []).extend(norm(n) for n in re.findall(r"Phase\s+(\d+(?:\.\d+)?)", t.group(2)))
    archived = {}
    for path in sorted((planning / "milestones").glob("*REQUIREMENTS.md")) if (planning / "milestones").is_dir() else []:
        for line in read(path).splitlines():
            m = REQ_BULLET.match(line)
            if m:
                archived.setdefault(m.group(2), {"text": plain(m.group(3)), "file": path.name})
    return {"current": current, "later": later, "where": where, "archived": archived, "exists": bool(text)}


def read_project(planning: Path) -> dict:
    text = read(planning / "PROJECT.md")
    parts = sections(text)
    title = re.search(r"^#\s+(.+)$", text, re.M)

    def part(name):
        return next((body for head, body in parts.items() if head.lower().startswith(name)), "")

    decisions = []
    for line in part("key decisions").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and "---" not in line and cells[0].lower() != "decision":
            decisions.append(cells + [""] * (3 - len(cells)))
    constraints = [plain(re.sub(r"^\s*[-*]\s+", "", ln)) for ln in part("constraints").splitlines()
                   if re.match(r"^[-*]\s+\S", ln)]
    return {"name": plain(title.group(1)) if title else "", "what": part("what this is"),
            "value": part("core value"), "constraints": constraints, "decisions": decisions}


def git(project: Path, *args: str) -> str:
    try:
        done = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def installed(project: Path) -> list:
    """GSD's own files inside the project, one entry per runtime folder that has any.
    GSD's manifest names them exactly; without one they are found by name."""
    out = []
    for runtime in RUNTIMES:
        base = project / runtime
        manifest = base / "gsd-file-manifest.json"
        paths, version = set(), ""
        if manifest.is_file():
            try:
                data = json.loads(read(manifest))
            except ValueError:
                data = {}
            version = str(data.get("version", ""))
            paths = {name for name in data.get("files", {}) if (base / name).is_file()}
        for pattern in INSTALLED:
            for found in base.glob(pattern) if base.is_dir() else []:
                paths |= {str(f.relative_to(base)) for f in found.rglob("*") if f.is_file()} if found.is_dir() \
                    else {str(found.relative_to(base))}
        if paths:
            out.append({"runtime": runtime, "version": version, "by_manifest": manifest.is_file(),
                        "files": sorted(runtime + "/" + name for name in paths)})
    return out


def default_branch(project: Path) -> str:
    head = git(project, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if head:
        return head.split("/", 1)[-1]
    for name in ("main", "master", "develop"):
        if git(project, "rev-parse", "--verify", "--quiet", "refs/heads/" + name):
            return name
    return git(project, "rev-parse", "--abbrev-ref", "HEAD") or "main"


# --------------------------------------------------------------------------- the model


def map_ids(names: list) -> dict:
    """GSD requirement id -> an id the phase tool reads (REQ-<LETTERS>-<digits>)."""
    out, used, counters = {}, set(), {}
    hard = []
    for name in names:
        m = SIMPLE_ID.match(name)
        family = re.sub(r"[^A-Z]", "", (m.group(1) if m else name.rsplit("-", 1)[0]).upper()) or "GEN"
        new = "REQ-%s-%s" % (family, m.group(2)) if m else ""
        if not new or new in used:
            hard.append((name, family))
            continue
        out[name] = new
        used.add(new)
        counters[family] = max(counters.get(family, 0), int(m.group(2)))
    for name, family in hard:  # a letter suffix, or two ids that would become the same one
        counters[family] = counters.get(family, 0) + 1
        while "REQ-%s-%02d" % (family, counters[family]) in used:
            counters[family] += 1
        out[name] = "REQ-%s-%02d" % (family, counters[family])
        used.add(out[name])
    return out


def build(project: Path, planning_dir: str = ".planning", numbering: str = "", complete: str = "") -> dict:
    planning = project / planning_dir
    finished = {norm(n) for n in re.findall(r"\d+(?:\.\d+)?", complete)}
    state = frontmatter(read(planning / "STATE.md"))
    signs = [name for name in ("PROJECT.md", "config.json") if (planning / name).is_file()]
    if "gsd_state_version" in state:
        signs.append("STATE.md (gsd_state_version)")
    if not planning.is_dir():
        raise Stop("no %s/ under %s: nothing to move" % (planning_dir, project))
    if "current_phase" in state and "phase_status" in state and "gsd_state_version" not in state:
        raise Stop("%s/STATE.md is already in the dev-tools format: this project has been moved "
                   "(GSD's files, if it had any, are in %s/%s/)" % (planning_dir, planning_dir, ARCHIVE))
    if not signs:
        raise Stop("%s/ has no PROJECT.md, no config.json and no GSD state: this is not a GSD project. "
                   "A project with no plan starts with 'phase_tool.py setup'" % planning_dir)

    item_runs, head_runs = read_roadmap(read(planning / "ROADMAP.md"))
    restarts = max(len(item_runs), len(head_runs)) > 1
    if restarts and numbering not in ("first", "last"):
        again = sorted({shown(nn) for group in (item_runs, head_runs) for run in group[1:] for nn in run}, key=float)
        raise Stop("the GSD roadmap uses phase numbers twice (%s): a milestone restarted its numbering. "
                   "The phase tool needs each number once. Pass --numbering first or --numbering last to say "
                   "which run of numbers is the roadmap; the other run stays in the archived roadmap. Choose the "
                   "run whose folders are in %s/phases/" % (", ".join(again[:8]), planning_dir))
    pick = 0 if numbering == "first" else -1
    items = item_runs[pick] if item_runs else {}
    heads = head_runs[pick] if head_runs else {}
    folders, odd = read_folders(planning)
    if restarts:  # details and folders of the other run of numbers must not be read as this run's
        heads = {nn: h for nn, h in heads.items() if nn not in items or h["title"].lower() == items[nn]["title"].lower()}
        if items:
            heads = {nn: h for nn, h in heads.items() if nn in items}
        for nn in sorted(folders):
            title = (items.get(nn) or heads.get(nn) or {}).get("title", "")
            if not title or slugify(title).split("-")[0] != folders[nn]["slug"].split("-")[0]:
                odd.append("phases/%s: left out, it belongs to the other run of phase numbers" % folders.pop(nn)["name"])
    reqs = read_requirements(planning)

    named = [r["gsd"] for r in reqs["current"]]
    for head in heads.values():
        for name in re.findall(r"[A-Za-z][A-Za-z0-9-]*-\d+[a-z]?", head["fields"].get("requirements", "")):
            if name not in named:
                named.append(name)
    ids = map_ids(named)

    phases, notes = [], list(odd)
    for nn in sorted(set(items) | set(heads) | set(folders), key=key):
        item, head, folder = items.get(nn), heads.get(nn), folders.get(nn)
        fields = head["fields"] if head else {}
        if item:
            done, why = item["done"], "ticked in the GSD roadmap" if item["done"] else ""
        elif head and "complete" in fields.get("status", "").lower():
            done, why = True, "marked complete in the GSD roadmap"
        elif folder and folder["plans"] and len(folder["summaries"]) >= len(folder["plans"]) \
                and folder["verified"].startswith(("passed", "complete", "verified")):
            done, why = True, "every plan has a summary and GSD's verification passed"
        else:
            done, why = False, ""
        if nn in finished and not done:
            done, why = True, "complete on the owner's word (--complete)"
        status, reason = ("complete", why) if done else status_from_files(folder)
        title = (head or item or {}).get("title") or folder["slug"].replace("-", " ").capitalize()
        depends = sorted({norm(n) for n in re.findall(r"Phase\s+(\d+(?:\.\d+)?)", fields.get("depends on", ""))},
                         key=key)
        phases.append({
            "id": nn, "title": title, "slug": folder["slug"] if folder else slugify(title),
            "status": status, "reason": reason, "folder": folder,
            "source": "roadmap" if head or item else "folder only",
            "milestone": item["milestone"] if item else "", "date": item["date"] if item else "",
            "goal": plain(fields.get("goal", "")) or (item["note"] if item else ""),
            "depends": depends, "criteria": head["criteria"] if head else [],
            "requirements": [ids[n] for n in re.findall(r"[A-Za-z][A-Za-z0-9-]*-\d+[a-z]?",
                                                        fields.get("requirements", "")) if n in ids],
            "placeholder": False,
        })
    known = {p["id"] for p in phases}
    whole = sorted(int(nn) for nn in known if "." not in nn)
    for number in sorted({int(nn.split(".")[0]) for nn in known if "." in nn} - set(whole)):
        nn = "%02d" % number
        phases.append({"id": nn, "title": "Not used", "slug": "not-used-%s" % nn, "status": "complete",
                       "reason": "no phase has this number", "folder": None, "source": "added", "milestone": "",
                       "date": "", "goal": "", "depends": [], "criteria": [], "requirements": [], "placeholder": True})
        notes.append("phase %d: GSD has phase %d.x and no phase %d; a 'Not used' block stands in for it"
                     % (number, number, number))
        whole.append(number)
    whole.sort()
    gaps = bool(whole) and (whole[0] > 1 or whole != list(range(whole[0], whole[0] + len(whole))))
    if gaps:
        notes.append("the phase numbers %s: set phase_gaps = true in the phase tool's settings (.devtools.toml), "
                     "or 'check' reports the roadmap" % ("start at %d" % whole[0] if whole[0] > 1 else "have gaps"))
    phases.sort(key=lambda p: key(p["id"]))
    known = {p["id"] for p in phases}
    for p in phases:
        p["depends"] = [d for d in p["depends"] if d in known and key(d) < key(p["id"])]
        if p["folder"] and p["status"] != "complete" and p["folder"]["unnumbered"]:
            notes.append("phase %s: %s is not named NN-MM-PLAN.md, so the phase tool does not count it; rename "
                         "it before the phase goes on" % (shown(p["id"]), ", ".join(p["folder"]["unnumbered"])))

    open_ = [p for p in phases if p["status"] != "complete"]
    started = [p for p in open_ if p["status"] != "not_started"]
    current = (started or open_ or phases[-1:] or [None])[0]
    if len(started) > 1:
        notes.append("phases %s were all started under GSD and not ticked as finished; the phase tool works on "
                     "one at a time, and %s becomes the current one. Name the ones that are in fact finished with "
                     "--complete" % (", ".join(shown(p["id"]) for p in started), shown(current["id"])))
    if not phases:
        notes.append("the GSD roadmap names no phase and %s/phases/ is empty: the new roadmap gets one empty "
                     "phase to fill in" % planning_dir)

    by_phase = {}
    for p in phases:
        for rid in p["requirements"]:
            by_phase.setdefault(rid, []).append(p["id"])
    rows, loose, groups = [], [], []
    for r in reqs["current"]:
        rid = ids[r["gsd"]]
        where = sorted({nn for nn in by_phase.get(rid, []) + reqs["where"].get(r["gsd"], []) if nn in known}, key=key)
        entry = dict(r, id=rid, phases=where)
        if r["group"] not in groups:
            groups.append(r["group"])
        (rows if where else loose).append(entry)
    seen = {r["id"] for r in rows} | {r["id"] for r in loose}
    for name in named:
        if ids[name] in seen:
            continue
        old = reqs["archived"].get(name)
        text = old["text"] if old else "Named by the GSD roadmap; its text is not in the GSD requirement files"
        group = "Carried from earlier GSD milestones"
        if group not in groups:
            groups.append(group)
        done = all(p["status"] == "complete" for p in phases if p["id"] in by_phase.get(ids[name], []))
        rows.append({"gsd": name, "id": ids[name], "text": text, "done": done, "group": group,
                     "phases": sorted(set(by_phase.get(ids[name], [])), key=key)})
    used_groups = [g for g in groups if any(r["group"] == g for r in rows)]

    mentions = {name: len(re.findall(r"(?i)\bgsd\b|get-shit-done|\.planning/PROJECT\.md", read(project / name)))
                for name in INSTRUCTION_FILES if (project / name).is_file()}
    return {
        "gaps": gaps, "project": project, "planning": planning, "planning_dir": planning_dir, "signs": signs,
        "state": state, "phases": phases, "current": current, "notes": notes, "restarts": restarts,
        "numbering": numbering, "ids": ids, "rows": rows, "loose": loose, "later": reqs["later"],
        "groups": used_groups, "has_requirements": reqs["exists"], "info": read_project(planning),
        "install": installed(project), "mentions": {k: v for k, v in mentions.items() if v},
        "history": [name for name in HISTORY if (planning / name).exists()],
        "config": json.loads(read(planning / "config.json") or "{}") if (planning / "config.json").is_file() else {},
    }


# --------------------------------------------------------------------------- writing dev-tools files


def roadmap_text(model: dict) -> str:
    out = ["# Roadmap", "",
           "One block per phase. Phases keep the numbers GSD gave them. A phase finished under GSD is",
           "`complete` and has no acceptance tests; its record is its folder under `phases/`. Only",
           "**Depends on** decides what may start.", ""]
    phases = model["phases"] or [{
        "id": "01", "title": "First phase", "slug": "first-phase", "status": "not_started", "depends": [],
        "requirements": [], "goal": "Replace this with what the phase delivers, in one sentence.",
        "criteria": [], "folder": None, "milestone": "", "date": "", "placeholder": False, "empty": True}]
    for p in phases:
        nn, done = p["id"], p["status"] == "complete"
        package = "p%s_%s" % (nn.replace(".", "_"), p["slug"].replace("-", "_"))
        out += ["## Phase %s: %s" % (shown(nn), p["title"]), "",
                "- **Slug:** " + p["slug"], "- **Status:** " + p["status"],
                "- **Depends on:** " + (", ".join(shown(d) for d in p["depends"]) or "none"),
                "- **Requirements:** " + (", ".join(p["requirements"]) or ("REQ-GSD-001" if p.get("empty") else "none recorded"))]
        if p["placeholder"]:
            out += ["- **Goal:** No phase has this number in the GSD roadmap. The block is here so that the phases "
                    "after it keep their numbers.", "- **Reuses:** nothing", "- **Acceptance tests:** none", ""]
            continue
        if p["milestone"]:
            out.append("- **GSD milestone:** " + p["milestone"])
        if p["goal"]:
            out.append("- **Goal:** " + p["goal"])
        out.append("- **Reuses:** " + ("not recorded (the phase was planned under GSD)" if p["status"] != "not_started"
                                       else "to be named when the phase is discussed"))
        if done or p["status"] in ("plan_approved", "implemented"):
            verification = p["folder"] and p["folder"]["verification"]
            record = "its record is `phases/%s/%s`" % (p["folder"]["name"], verification) if verification else \
                "it has no verification file"
            out.append("- **Acceptance tests:** none: the phase was %s under GSD; %s"
                       % ("finished" + (" on " + p["date"] if p["date"] else "") if done else "planned", record))
        else:
            out.append("- **Acceptance tests (written first):** `tests/acceptance/%s/`" % package)
        if p["criteria"]:
            out.append("- **Exit criteria:**")
            out += ["  - " + c for c in p["criteria"]]
        out.append("")
    return "\n".join(out)


def requirements_text(model: dict) -> str:
    name = model["info"]["name"] or model["project"].name
    out = ["# Requirements", "", "## What users need", "",
           "Each need is a group of requirements as GSD's `REQUIREMENTS.md` grouped them. Reword a row so",
           "that it says what a user needs.", "", "| Id | Need |", "|---|---|"]
    u_of = {}
    for i, group in enumerate(model["groups"], 1):
        u_of[group] = "U%02d" % i
        out.append("| U%02d | %s |" % (i, cell(group) or "Requirements"))
    out += ["", "## What the project must do", "",
            "The **Phase** column names the roadmap phase that delivers the requirement. The last",
            "column is `Planned` until that phase is complete, then `Validated`. Ids are GSD's with",
            "`REQ-` in front, so a search for the old id still finds the row.", "",
            "| Id | Requirement | Need | Phase | Status |", "|---|---|---|---|---|"]
    if not model["rows"]:
        first = model["phases"][0]["id"] if model["phases"] else "01"
        value = cell(model["info"]["value"]) or "Replace with the first thing a user needs from " + name
        out[9:9] = ["| U01 | %s |" % value]
        out.append("| REQ-GSD-001 | Replace with the first requirement. GSD kept no requirement file here; "
                   "what was built is in the archived roadmaps | U01 | %s | %s |"
                   % (shown(first), "Validated" if model["phases"] and model["phases"][0]["status"] == "complete" else "Planned"))
    for r in model["rows"]:
        out.append("| %s | %s | %s | %s | %s |" % (r["id"], cell(r["text"]), u_of[r["group"]],
                                                   ", ".join(shown(nn) for nn in r["phases"]),
                                                   "Validated" if r["done"] else "Planned"))
    if model["loose"]:
        out += ["", "## Without a phase in this roadmap", "",
                "GSD tracked these and no phase of this roadmap names them. Give each a phase and move it",
                "into the table, or delete it.", ""]
        out += ["- **%s** (%s) %s" % (r["id"], "done" if r["done"] else "open", r["text"]) for r in model["loose"]]
    if model["later"]:
        out += ["", "## Put off under GSD", "", "Kept as GSD wrote them. They are not requirements until a phase takes them.", ""]
        out += ["- **%s** %s" % (r["gsd"], r["text"]) for r in model["later"]]
    return "\n".join(out) + "\n"


def state_text(model: dict, base: str, release: str, today: str) -> str:
    state, current = model["state"], model["current"]
    done = [p["id"] for p in model["phases"] if p["status"] == "complete"]
    status = current["status"] if current else "not_started"
    step = {"context_approved": "specify", "plan_approved": "implement", "implemented": "verify"}.get(status, "null")
    where = ["The project moved from GSD to the dev-tools phase workflow on %s." % today]
    if state.get("milestone"):
        where.append("Under GSD it was in milestone %s%s, with status `%s`."
                     % (state["milestone"], " (%s)" % state["milestone_name"] if state.get("milestone_name") else "",
                        state.get("status", "unknown")))
    if state.get("stopped_at"):
        where.append("GSD's last note: %s" % state["stopped_at"])
    if not current or status == "complete":
        nxt = "Every phase of the roadmap is complete. Add the next phase to `ROADMAP.md` and run `/process-phase next`."
    elif status == "not_started":
        nxt = "Run `/process-phase %s`: phase %s (%s) has not started." % (shown(current["id"]), shown(current["id"]), current["title"])
    else:
        nxt = ("Phase %s (%s) was under way in GSD and is carried as `%s` (%s). It has no locked acceptance tests: "
               "`phase_tool.py status` lists what the next step will ask for."
               % (shown(current["id"]), current["title"], status, current["reason"]))
    lines = ["---", 'current_phase: "%s"' % (current["id"] if current else "01"), "phase_status: " + status,
             "active_step: " + step, 'completed_phases: "%s"' % ",".join(done), "base_branch: " + base,
             "phase_branch: " + base, "release_branch: " + release, "last_activity: " + today,
             "blocked_on: null", "manifesto_version: 1.0.0", "---", "", "# State", "", "## Where we are", "",
             *where, "", "## Next step", "", nxt, "", "## Lessons", "",
             "None yet under this workflow. Each lesson gets an id `LS-NN`."]
    if "RETROSPECTIVE.md" in model["history"]:
        lines.append("What GSD's milestones taught is in `RETROSPECTIVE.md`.")
    lines += ["", "## From GSD", "",
              "GSD's own files are in `%s/`; `CONVERSION.md` there records what the move did." % ARCHIVE]
    return "\n".join(lines) + "\n"


def decisions_text(model: dict, owner: str, today: str) -> str:
    name = model["info"]["name"] or model["project"].name
    approver = owner or "Replace with your name"
    out = ["# Decisions", "",
           "One row per decision that changes the plan or waives a rule. A row needs a reason and the",
           "name of the person who approved it.", "",
           "| Id | Date | Decision | Reason | Approved by |", "|---|---|---|---|---|",
           "| DEC-001 | %s | Move %s from GSD to the dev-tools phase workflow (the process-phase skill). | One "
           "process, with tests agreed before code and state kept in the repository. | %s |" % (today, cell(name), approver),
           "| DEC-002 | %s | Phases finished under GSD stand as complete with no locked acceptance tests and no "
           "evidence folder. | They were accepted under GSD's rules; rebuilding their evidence would prove nothing "
           "new. | %s |" % (today, approver)]
    for i, row in enumerate(model["info"]["decisions"], 3):
        outcome = plain(row[2])
        reason = cell(row[1]) + (" Outcome under GSD: " + cell(outcome) if outcome.lower() not in ("", "pending") else "")
        out.append("| DEC-%03d | %s | %s | %s | Carried from GSD's PROJECT.md |" % (i, today, cell(row[0]), reason or "Not recorded"))
    return "\n".join(out) + "\n"


def manifesto_text(model: dict, template: str) -> str:
    info = model["info"]
    out = [template.rstrip()]
    for i, text in enumerate(info["constraints"], 3):
        head, colon, rest = text.partition(": ")
        out.append("- **T%d — %s.** %s" % (i, head, rest) if colon and len(head) < 60 else "- **T%d.** %s" % (i, text))
    if info["what"] or info["value"]:
        out += ["", "## What this project is", "", "Carried from GSD's `PROJECT.md`.", ""]
        out += [part for part in (info["what"], "**Core value.** " + info["value"] if info["value"] else "") if part]
    return "\n".join(out) + "\n"


def readme_text(model: dict, template: str) -> str:
    kept = {"MILESTONES.md": "The milestones GSD shipped", "RETROSPECTIVE.md": "What each milestone taught",
            "milestones": "GSD's archived roadmaps, requirements and phase folders, one set per milestone",
            "research": "Research reports", "codebase": "GSD's map of the code. The component index replaces it",
            "quick": "Small tasks GSD ran outside the roadmap", "debug": "GSD's debugging sessions",
            "todos": "Ideas put off", "workstreams": "GSD's parallel workstreams",
            "forensics": "GSD's investigations", "notes": "Notes"}
    out = [template.rstrip(), "", "## History from GSD", "",
           "This project was planned with GSD before it moved to this workflow. Nothing below is read",
           "by `phase_tool.py`; it is the record of how the project got here.", "",
           "| Path | What it holds |", "|---|---|",
           "| `%s/` | GSD's `PROJECT.md`, `config.json`, and its `STATE.md`, `ROADMAP.md` and `REQUIREMENTS.md` "
           "as they were, with `CONVERSION.md` |" % ARCHIVE]
    out += ["| `%s%s` | %s |" % (name, "" if "." in name else "/", kept[name]) for name in model["history"]]
    return "\n".join(out) + "\n"


def record_text(model: dict, written: list, kept: list, today: str) -> str:
    out = ["# Moving from GSD to dev-tools", "",
           "Written by `from_gsd.py convert` on %s. dev-tools %s." % (today, git(SOURCE_ROOT, "rev-parse", "--short", "HEAD") or "(no commit)"),
           "", "## For the owner to read", ""]
    todo = list(model["notes"])
    if model["restarts"]:
        todo.append("the GSD roadmap restarted its numbering; the %s run of numbers became the roadmap" % model["numbering"])
    if model["current"] and model["current"]["status"] not in ("complete", "not_started"):
        status = model["current"]["status"]
        todo.append("phase %s was under way and is carried as `%s`. %s" % (
            shown(model["current"]["id"]), status,
            "Its next step, Specify, writes and locks its acceptance tests as for any phase" if status == "context_approved"
            else "It has no locked acceptance tests, and the phase tool asks for them at the next step: write them "
                 "now, or waive them with a decision row the owner approves ('advance --override DEC-NNN')"))
    if model["loose"]:
        todo.append("%d requirement(s) have no phase in this roadmap (REQUIREMENTS.md, last sections)" % len(model["loose"]))
    todo.append("MANIFESTO.md, the U rows of REQUIREMENTS.md and the approver of DEC-001 and DEC-002 are drafts")
    out += ["- " + line for line in todo]
    out += ["", "## Files", "", "| File | What happened |", "|---|---|"]
    out += ["| `%s` | %s |" % row for row in written]
    out += ["| `%s` | Already there; left as it was |" % name for name in kept]
    out += ["", "## Phases", "", "| Phase | Status | Why | Folder |", "|---|---|---|---|"]
    out += ["| %s %s | %s | %s | %s |" % (shown(p["id"]), cell(p["title"]), p["status"], p["reason"],
                                           "`phases/%s/`" % p["folder"]["name"] if p["folder"] else "none")
            for p in model["phases"]]
    if model["ids"]:
        out += ["", "## Requirement ids", "", "| GSD | Now |", "|---|---|"]
        out += ["| %s | %s |" % pair for pair in model["ids"].items()]
    return "\n".join(out) + "\n"


def convert(model: dict, owner: str = "", base: str = "", release: str = "", tool: str = "",
            dry_run: bool = False) -> dict:
    if not TEMPLATES.is_dir():
        raise Stop("%s is missing: run this script from a whole dev-tools checkout" % TEMPLATES)
    planning, project = model["planning"], model["project"]
    today = datetime.date.today().isoformat()
    base = base or default_branch(project)
    name = model["info"]["name"] or project.name
    subs = {"{{NAME}}": name, "{{DATE}}": today, "{{BASE}}": base, "{{RELEASE}}": release or base,
            "{{TOOL}}": tool or ".claude/skills/process-phase/scripts/phase_tool.py"}

    def template(filename):
        text = read(TEMPLATES / filename)
        for token, value in subs.items():
            text = text.replace(token, value)
        return text

    archive = planning / ARCHIVE
    moves = [n for n in MOVED if (planning / n).is_file()]
    clash = [n for n in moves if (archive / n).exists()]
    if clash:
        raise Stop("%s/%s/ already holds %s: an earlier run stopped half way. Restore the planning folder "
                   "from git and run again" % (model["planning_dir"], ARCHIVE, ", ".join(clash)))
    files = {"STATE.md": state_text(model, base, release or base, today),
             "ROADMAP.md": roadmap_text(model), "REQUIREMENTS.md": requirements_text(model)}
    drafts = {"DECISIONS.md": decisions_text(model, owner, today),
              "MANIFESTO.md": manifesto_text(model, template("MANIFESTO.md")),
              "README.md": readme_text(model, template("README.md"))}
    for path in sorted(TEMPLATES.iterdir()):
        drafts.setdefault(path.name, template(path.name))
    for filename in files:
        drafts.pop(filename, None)
    kept = sorted(n for n in drafts if (planning / n).exists())
    written = [("%s/%s" % (ARCHIVE, n), "GSD's file, moved here unchanged") for n in moves]
    written += [(n, "Written in the dev-tools format from GSD's file" if n in moves else "Written; GSD had none")
                for n in files]
    written += [(n, "New") for n in sorted(drafts) if n not in kept]
    result = {"written": [w[0] for w in written], "kept": kept, "dry_run": dry_run}
    if dry_run:
        return result
    archive.mkdir(parents=True, exist_ok=True)
    for filename in moves:
        shutil.move(str(planning / filename), str(archive / filename))
    for filename, text in files.items():
        (planning / filename).write_text(text, encoding="utf-8")
    for filename, text in drafts.items():
        if filename not in kept:
            (planning / filename).write_text(text, encoding="utf-8")
    (archive / "CONVERSION.md").write_text(record_text(model, written, kept, today), encoding="utf-8")
    result["written"].append("%s/CONVERSION.md" % ARCHIVE)
    return result


# --------------------------------------------------------------------------- commands


def survey_lines(model: dict) -> list:
    state, phases = model["state"], model["phases"]
    count = {}
    for p in phases:
        count[p["status"]] = count.get(p["status"], 0) + 1
    out = ["GSD project: %s (%s)" % (model["info"]["name"] or model["project"].name, ", ".join(model["signs"]))]
    if state.get("milestone"):
        out.append("GSD milestone: %s %s, status %s" % (state["milestone"], state.get("milestone_name", ""), state.get("status", "?")))
    out += ["", "Phases: %d (%s)" % (len(phases), ", ".join("%d %s" % (n, s) for s, n in sorted(count.items())) or "none")]
    for p in phases:
        if p["status"] != "complete" or p["placeholder"] or p["source"] != "roadmap":
            out.append("  %-6s %-17s %s  [%s]" % (shown(p["id"]), p["status"], p["title"][:60], p["reason"] or p["source"]))
    current = model["current"]
    if current:
        out.append("Current phase after the move: %s (%s), %s" % (shown(current["id"]), current["title"], current["status"]))
        if current["status"] == "context_approved":
            out.append("  It was discussed under GSD and not planned: its next step here is Specify, as for any phase.")
        elif current["status"] != "complete" and current["status"] != "not_started":
            out.append("  It is under way. Moving between phases is simpler: finish it under GSD first, or carry it "
                       "and write its acceptance tests late or waive them with a decision row.")
    out += ["", "Requirements: %d in the table, %d without a phase, %d put off%s"
            % (len(model["rows"]), len(model["loose"]), len(model["later"]),
               "" if model["has_requirements"] else " (GSD has no REQUIREMENTS.md here)"),
            "Needs (U rows), one per GSD group: %d" % (len(model["groups"]) or 1),
            "Decisions carried from PROJECT.md: %d" % len(model["info"]["decisions"]),
            "Constraints carried into MANIFESTO.md: %d" % len(model["info"]["constraints"])]
    changed = sorted(pair for pair in model["ids"].items())[:3]
    if changed:
        out.append("Requirement ids: " + ", ".join("%s -> %s" % pair for pair in changed) + (", ..." if len(model["ids"]) > 3 else ""))
    out += ["", "Moved to %s/%s/: %s" % (model["planning_dir"], ARCHIVE,
                                         ", ".join(n for n in MOVED if (model["planning"] / n).is_file())),
            "Left where they are: " + (", ".join(model["history"]) or "nothing else of GSD's")]
    config = model["config"]
    strategy = (config.get("git") or {}).get("branching_strategy")
    if strategy:
        out.append("GSD branching strategy: %s (dev-tools works on a branch per phase, prefix 'phase/')" % strategy)
    out += ["", "GSD installed inside the project:" + ("" if model["install"] else " no (an install in your home "
                                                            "folder is not the project's)")]
    for found in model["install"]:
        tops = sorted({name.split("/")[1] for name in found["files"]})
        out.append("  %s/: %d file(s)%s, %s (%s)" % (
            found["runtime"], len(found["files"]), " of GSD " + found["version"] if found["version"] else "",
            "named by GSD's manifest" if found["by_manifest"] else "found by name", ", ".join(tops[:8])))
    if model["install"]:
        out.append("  'survey --installed' prints every path")
    for name, n in model["mentions"].items():
        out.append("  %s mentions GSD or .planning/PROJECT.md %d time(s): read and update it" % (name, n))
    out += ["", "Setting for the phase tool in .devtools.toml: phase_gaps = %s" % ("true" if model["gaps"] else "false")]
    if model["notes"]:
        out += ["", "To settle:"] + ["  - " + note for note in model["notes"]]
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("survey", "convert"):
        p = sub.add_parser(name)
        p.add_argument("--project", default=".")
        p.add_argument("--planning-dir", default=".planning")
        p.add_argument("--numbering", choices=["first", "last"], default="",
                       help="which run of phase numbers is the roadmap, when GSD restarted the numbering")
        p.add_argument("--complete", default="", metavar="N,N",
                       help="phases GSD left unticked that the owner says are finished")
        p.add_argument("--format", choices=["text", "json"], default="text")
    sub.choices["survey"].add_argument("--installed", action="store_true",
                                       help="print only the paths of GSD's own files inside the project")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--owner", default="", help="the name on the decision rows the move adds")
    p.add_argument("--base-branch", default="")
    p.add_argument("--release-branch", default="")
    p.add_argument("--tool", default="", help="path of phase_tool.py in the project, for README.md")
    args = parser.parse_args(argv)
    try:
        model = build(Path(args.project).resolve(), args.planning_dir, args.numbering, args.complete)
        if args.command == "survey" and args.installed:
            print("\n".join(name for found in model["install"] for name in found["files"]))
            return 0
        if args.command == "survey":
            if args.format == "json":
                keep = ("signs", "state", "phases", "gaps", "notes", "ids", "rows", "loose", "later", "groups", "install",
                        "mentions", "history")
                print(json.dumps({k: model[k] for k in keep}, indent=2, default=str))
            else:
                print("\n".join(survey_lines(model)))
            return 0
        result = convert(model, args.owner, args.base_branch, args.release_branch, args.tool, args.dry_run)
    except Stop as stop:
        print("from_gsd: %s" % stop, file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    print("%s in %s/:" % ("would write" if args.dry_run else "wrote", args.planning_dir))
    print("\n".join("  " + name for name in result["written"]))
    if result["kept"]:
        print("left as they were: " + ", ".join(result["kept"]))
    if not args.dry_run:
        print("next: read %s/%s/CONVERSION.md, then run 'phase_tool.py check --all'" % (args.planning_dir, ARCHIVE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
