#!/usr/bin/env python3
"""Build the Claude Code plugins in plugins/ from the skills in this repository.

    python3 devtools/build_plugins.py          # write plugins/ and .claude-plugin/marketplace.json
    python3 devtools/build_plugins.py --check  # exit 1 if they differ from what a build writes

Each workflow is its own plugin, because both have a skill called process-phase:
``dvt-phase`` (the phase workflow, its agents and the component index) and
``dvt-milestone`` (the milestone workflow and the component index). The marketplace at the
root of this repository lists both; a project installs one.

A plugin is one copy shared by every project, so the build rewrites what in a synced copy
points into the project. Script paths become ``${CLAUDE_PLUGIN_ROOT}/skills/...``, which
Claude Code fills in. The project's rules, which a synced copy keeps in
``references/project.md`` beside the skill, are ``.devtools/project.md`` in the project. The
scripts read their settings from ``.devtools/<script>.settings.json`` in the project when they
run from a plugin (they look for ``.claude-plugin/plugin.json`` above themselves).
``{{devtools:<key>}}`` takes the default in VALUES. Every rewrite must change some file, so
one that stops matching fails the build instead of leaving a stale path.

Scripts are copied byte for byte. plugins/ is generated: change the skills, then rebuild.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "plugins"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
MARKETPLACE_NAME = "dvt"
OWNER = {"name": "vasiloglou", "url": "https://github.com/vasiloglou"}
REPOSITORY = "https://github.com/vasiloglou/dev-tools"
LICENSE = "Apache-2.0"
# Claude Code installs a plugin version once, so every change ships under a new version:
# devtools/release_plugins.py bump raises it (and rebuilds), release_plugins.py tag releases it.
VERSION_FILE = ROOT / "devtools" / "PLUGIN_VERSION"
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def version() -> str:
    text = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not SEMVER.match(text):
        raise SystemExit(f"{VERSION_FILE}: {text!r} is not a version like 1.2.3")
    return text
# The defaults a plugin's skill text is written with.
VALUES = {"planning_dir": ".planning"}
# Inside a skill folder: eval sets and Codex's own metadata, which a Claude Code plugin does not read.
EXCLUDE = {"evals", "agents"}
SKIP = {"__pycache__", ".DS_Store"}
PROJECT_RULES = ".devtools/project.md"
PLUGINS = {
    "dvt-phase": {
        "description": "The dev-tools phase workflow: roadmap phases run test first through the .planning/ "
                       "contract (process-phase, phase-tests), its helper agents, the component index, GitHub issue handling (handle-issue), "
                       "and hand-offs between assistants and machines (dev-handoff, dev-takeover).",
        "keywords": ["workflow", "planning", "tdd", "phases", "components"],
        "skills": {"process-phase": "skills/phase/process-phase",
                   "phase-tests": "skills/phase/phase-tests",
                   "components": "skills/components",
                   "handle-issue": "skills/handle-issue",
                   "dev-handoff": "skills/dev-handoff",
                   "dev-takeover": "skills/dev-takeover"},
        "files": {"skills/process-phase/pytest/phase_selection.py": "skills/phase/pytest/phase_selection.py"},
        "agents": "agents",
        # A plugin's agents are named after the plugin.
        "rewrites": [(r"`\.claude/agents/(phase-[\w-]+)\.md`", r"the `dvt-phase:\1` agent"),
                     (r"`(phase-(?:implementer|researcher|test-writer|verifier|code-reviewer))`", r"`dvt-phase:\1`")],
    },
    "dvt-milestone": {
        "description": "The dev-tools milestone workflow: plan, run and close milestones phase by phase "
                       "(start-milestone, process-milestone, process-phase), independent PR reviews "
                       "(review-pr), the component index, GitHub issue handling (handle-issue), "
                       "and hand-offs between assistants and machines (dev-handoff, dev-takeover).",
        "keywords": ["workflow", "planning", "milestones", "review", "components"],
        "skills": {"start-milestone": "skills/milestone/start-milestone",
                   "process-milestone": "skills/milestone/process-milestone",
                   "process-phase": "skills/milestone/process-phase",
                   "review-pr": "skills/milestone/review-pr",
                   "components": "skills/components",
                   "handle-issue": "skills/handle-issue",
                   "dev-handoff": "skills/dev-handoff",
                   "dev-takeover": "skills/dev-takeover"},
        "files": {},
        "agents": None,
        "rewrites": [],
    },
}
# (pattern, replacement), applied in order to every Markdown file. The phrases come first,
# then the paths they contain.
REWRITES = [
    (r"`\./references/project\.md` exists beside this file", f"`{PROJECT_RULES}` exists in the project"),
    (r"own `project\.md` beside its synced skills",
     f"own rules (`{PROJECT_RULES}` with a plugin, or the project.md beside its synced skills)"),
    (r"`references/project\.md` in this skill directory", f"`{PROJECT_RULES}` in the project"),
    (r"`project\.md` in this skill's `references/`\s+directory", f"`{PROJECT_RULES}` in the project"),
    (r"`references/project\.md` exists in this skill's directory", f"`{PROJECT_RULES}` exists in the project"),
    (r"`references/project\.md` exists in the process-phase skill(\s+)directory",
     f"`{PROJECT_RULES}` exists in the project\\1"),
    (r"`references/project\.md` beside the(\s+)process-phase skill", f"`{PROJECT_RULES}`"),
    (r"`references/project\.md`\s+beside the process-phase skill", f"`{PROJECT_RULES}`"),
    (r"(?:\.claude/skills/process-phase/|\.\./process-phase/)?references/project\.md", PROJECT_RULES),
    (r"`project\.md`", f"`{PROJECT_RULES}`"),
    (r"`(\w+)\.settings\.json`(\s+)beside the script", r"`.devtools/\1.settings.json`\2in the project"),
    (r"(?:\.claude/skills/[\w-]+/)?(?<![\w.}-])scripts/(\w+)\.settings\.json", r".devtools/\1.settings.json"),
    (r"skills/phase/pytest/phase_selection\.py", "${CLAUDE_PLUGIN_ROOT}/skills/process-phase/pytest/phase_selection.py"),
    (r"\.claude/skills/(process-phase|phase-tests|components|start-milestone|process-milestone|review-pr|handle-issue|dev-handoff|dev-takeover)\b",
     r"${CLAUDE_PLUGIN_ROOT}/skills/\1"),
    (r"(?<![\w/.}-])scripts/components_index\.py",
     "${CLAUDE_PLUGIN_ROOT}/skills/components/scripts/components_index.py"),
    (r"\.\./process-phase/scripts/review_tool\.py", "${CLAUDE_PLUGIN_ROOT}/skills/process-phase/scripts/review_tool.py"),
    (r"\.\./process-phase/references/", "${CLAUDE_PLUGIN_ROOT}/skills/process-phase/references/"),
    (r"\.\./dev-handoff/references/", "${CLAUDE_PLUGIN_ROOT}/skills/dev-handoff/references/"),
]
MODES: dict[Path, int] = {}  # each built file's mode, from its source
TOKEN = re.compile(r"\{\{devtools:([a-z_]+)\}\}")
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def note(plugin: str) -> str:
    """What a skill installed from the plugin reads first: where the project's own files are."""
    return (f"\n> **Installed from the `{plugin}` plugin.** This copy is shared by every project, so the "
            f"project's own files live in the project: its rules for these skills in `{PROJECT_RULES}`, "
            "and each script's settings in `.devtools/<script>.settings.json` (the same keys a synced "
            "copy keeps beside the script; a missing file means the defaults). The scripts are under "
            "`${CLAUDE_PLUGIN_ROOT}/skills/` and are run from the project root. `${CLAUDE_PLUGIN_ROOT}` is "
            "the plugin's folder, two levels above this file (`<plugin>/skills/<skill>/SKILL.md`): Claude "
            "Code fills it in, Codex leaves it empty, so under Codex write that folder's path in its place. "
            f"The planning folder is `{VALUES['planning_dir']}`.\n")


def rewrite(text: str, plugin: str, origin: str, hits: dict) -> str:
    """Fill the tokens and apply REWRITES, then the plugin's own; count each pattern's matches in hits."""
    def fill(match: re.Match) -> str:
        if match.group(1) not in VALUES:
            raise SystemExit(f"{origin}: no plugin value for {{{{devtools:{match.group(1)}}}}}")
        return VALUES[match.group(1)]

    text = TOKEN.sub(fill, text)
    for pattern, replacement in REWRITES + PLUGINS[plugin]["rewrites"]:
        text, count = re.subn(pattern, replacement, text)
        hits[pattern] = hits.get(pattern, 0) + count
    return text


def shipped(folder: Path):
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        if path.is_file() and not SKIP & set(relative.parts) and relative.parts[0] not in EXCLUDE:
            yield path, relative


def build_plugin(name: str, spec: dict, hits: dict) -> dict[str, bytes]:
    files: dict[str, bytes] = {}

    def add(dest: str, source: Path, skill: bool = False) -> None:
        data = source.read_bytes()
        if source.suffix == ".md":
            text = rewrite(data.decode("utf-8"), name, str(source.relative_to(ROOT)), hits)
            if skill and source.name == "SKILL.md":
                head = FRONTMATTER.match(text)
                if not head:
                    raise SystemExit(f"{source}: no frontmatter")
                text = text[:head.end()] + note(name) + text[head.end():]
            data = text.encode("utf-8")
        files[dest] = data
        MODES[OUT / name / dest] = source.stat().st_mode & 0o777

    for skill, source in spec["skills"].items():
        for path, relative in shipped(ROOT / source):
            add(f"skills/{skill}/{relative.as_posix()}", path, skill=relative.as_posix() == "SKILL.md")
    for dest, source in spec["files"].items():
        add(dest, ROOT / source)
    if spec["agents"]:
        for path in sorted((ROOT / spec["agents"]).glob("*.md")):
            add(f"agents/{path.name}", path)
    manifest = {"name": name, "version": version(), "description": spec["description"], "author": OWNER,
                "repository": REPOSITORY, "license": LICENSE, "keywords": spec["keywords"]}
    files[".claude-plugin/plugin.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    return files


def build() -> dict[Path, bytes]:
    hits: dict[str, int] = {}
    out: dict[Path, bytes] = {}
    for name, spec in PLUGINS.items():
        for dest, data in build_plugin(name, spec, hits).items():
            out[OUT / name / dest] = data
    every = REWRITES + [rule for spec in PLUGINS.values() for rule in spec["rewrites"]]
    unused = [pattern for pattern, _ in every if not hits.get(pattern)]
    if unused:
        raise SystemExit("rewrites that matched nothing (update REWRITES):\n  " + "\n  ".join(unused))
    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": OWNER,
        "description": "The dev-tools development-process skills as Claude Code plugins. Install one workflow.",
        "plugins": [{"name": name, "source": f"./plugins/{name}", "description": spec["description"],
                     "category": "development", "keywords": spec["keywords"]} for name, spec in PLUGINS.items()],
    }
    out[MARKETPLACE] = (json.dumps(marketplace, indent=2) + "\n").encode("utf-8")
    return out


def stale(wanted: dict[Path, bytes]) -> list[str]:
    present = {p for p in OUT.rglob("*") if p.is_file() and not SKIP & set(p.parts)} if OUT.is_dir() else set()
    names = [p for p in wanted if not p.is_file() or p.read_bytes() != wanted[p]
             or (p in MODES and p.stat().st_mode & 0o777 != MODES[p])]
    return sorted(str(p.relative_to(ROOT)) for p in names + sorted(present - set(wanted)))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="report files a build would change; write nothing")
    args = parser.parse_args(argv)
    wanted = build()
    changed = stale(wanted)
    if args.check:
        for path in changed:
            print(f"stale: {path}")
        if changed:
            print("run: python3 devtools/build_plugins.py", file=sys.stderr)
        return 1 if changed else 0
    for path in sorted(p for p in (OUT.rglob("*") if OUT.is_dir() else []) if p.is_file()):
        if path not in wanted:
            path.unlink()
    for path, data in wanted.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_bytes() != data:
            path.write_bytes(data)
        if path in MODES and path.stat().st_mode & 0o777 != MODES[path]:
            path.chmod(MODES[path])
    for path in sorted((p for p in OUT.rglob("*") if p.is_dir()), reverse=True):
        if not any(path.iterdir()):
            path.rmdir()
    print(f"{len(changed)} file(s) written or removed" if changed else "plugins are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
