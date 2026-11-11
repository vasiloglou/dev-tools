"""Tests for moving a GSD planning folder to the dev-tools phase workflow. Each test builds a
small GSD project, syncs the phase skills into it, converts it and asks the phase tool."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "devtools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sync, gsd = load("sync"), load("from_gsd")

STATE = """---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Reports
status: executing
stopped_at: Completed 03-01-PLAN.md
progress:
  total_phases: 4
  completed_phases: 2
---

# Project State
"""
ROADMAP = """# Roadmap: Widget

## Phases

- [x] **Phase 1: Scan the Tree** - walk a folder and list files (completed 2026-05-01)
- [x] **Phase 2: Find Duplicates** - group files by content (completed 2026-05-03)
- [ ] **Phase 2.1: Hash Cache** (INSERTED) - skip files that did not change
- [ ] **Phase 3: Report** - print what was found
- [ ] **Phase 4: Export** - write the report as JSON

## Phase Details

### Phase 1: Scan the Tree

**Goal**: A user can list every file under a folder
**Depends on**: Nothing (first phase)
**Requirements**: SCAN-01, SCAN-02
**Success Criteria** (what must be TRUE):

  1. Every file is listed once
  2. A folder that cannot be read is reported
**Plans**: 1/1 plans complete

Plans:
- [x] 01-01-PLAN.md — the walker

### Phase 2: Find Duplicates

**Goal**: A user can see which files are copies
**Depends on**: Phase 1
**Requirements**: DUPE-01

### Phase 2.1: Hash Cache (INSERTED)

**Goal**: A second run is fast
**Depends on**: Phase 2
**Requirements**: DUPE-02

### Phase 3: Report

**Goal:** A user can read the result
**Depends on:** Phase 2, Phase 2.1
**Requirements:** [OUT-01]

### Phase 4: Export

**Goal**: The result can be read by another program
**Depends on**: Phase 3
**Requirements**: OUT-02a
"""
REQUIREMENTS = """# Requirements: Widget

## v1 Requirements

### Scanning

- [x] **SCAN-01**: User can list every file under a folder
- [x] **SCAN-02**: A folder that cannot be read is reported | not skipped

### Duplicates

- [x] **DUPE-01**: User can see which files are copies
- [ ] **DUPE-02**: A second run reuses the hashes of unchanged files

### Output

- [ ] **OUT-01**: User can read the result on a terminal
- [ ] **OUT-02a**: User can export the result as JSON
- [ ] **OUT-03**: User can choose the columns

## v2 Requirements

- **SYNC-01**: User can delete duplicates in place

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCAN-01 | Phase 1 | Complete |
| OUT-01 | Phase 3 | Pending |
"""
PROJECT = """# Widget

## What This Is

A command that finds duplicate files.

## Core Value

Never delete a file the user did not name.

## Constraints

- **Runtime**: Python standard library only — it must run on a bare machine
- No network access

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Hash with SHA-256 | Collisions must not happen | ✓ Good |
| Read files in chunks | Large files | — Pending |
"""


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def git(root, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args], cwd=root, check=True,
                   capture_output=True)


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "widget"
    root.mkdir()
    planning = root / ".planning"
    for name, text in [("STATE.md", STATE), ("ROADMAP.md", ROADMAP), ("REQUIREMENTS.md", REQUIREMENTS),
                       ("PROJECT.md", PROJECT), ("config.json", '{"git": {"branching_strategy": "none"}}'),
                       ("MILESTONES.md", "# Milestones\n"),
                       ("phases/01-scan-the-tree/01-CONTEXT.md", "# Context\n"),
                       ("phases/01-scan-the-tree/01-01-PLAN.md", "# Plan\n"),
                       ("phases/01-scan-the-tree/01-01-SUMMARY.md", "# Summary\n"),
                       ("phases/01-scan-the-tree/01-VERIFICATION.md", "---\nstatus: passed\n---\n"),
                       ("phases/02-find-duplicates/02-01-PLAN.md", "# Plan\n"),
                       ("phases/02-find-duplicates/02-01-SUMMARY.md", "# Summary\n"),
                       ("phases/03-report/03-CONTEXT.md", "# Context\n"),
                       ("phases/03-report/03-01-PLAN.md", "# Plan\n"),
                       ("phases/03-report/03-02-PLAN.md", "# Plan\n"),
                       ("phases/03-report/03-01-SUMMARY.md", "# Summary\n")]:
        write(planning, name, text)
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "the GSD project")
    git(root, "switch", "-qc", "move-to-devtools")
    return root


def run(*args):
    proc = subprocess.run([sys.executable, str(ROOT / "devtools/from_gsd.py"), *args], capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def install(root, **settings):
    config = (ROOT / "examples/phase-project.devtools.toml").read_text().replace('"myapp"', '""')
    config = config.replace("after_apply =", "# after_apply =")
    for name, value in settings.items():
        config = config.replace("%s = false" % name, "%s = %s" % (name, value))
    (root / ".devtools.toml").write_text(config)
    assert sync.main(["apply", "--project", str(root)]) == 0


def phase(root, *args):
    proc = subprocess.run([sys.executable, ".claude/skills/process-phase/scripts/phase_tool.py", "--format", "json",
                           *args], cwd=root, capture_output=True, text=True)
    return proc.returncode, json.loads(proc.stdout)


def test_a_converted_project_passes_the_phase_tools_check(project):
    install(project)
    code, out = run("convert", "--project", str(project), "--owner", "Ada")
    assert code == 0, out
    git(project, "add", "-A")
    code, env = phase(project, "check", "--all")
    assert code == 0, env
    code, env = phase(project, "status")
    data = env["data"]
    assert data["current_phase"] == "03" and data["phase_status"] == "plan_approved"
    assert data["completed_phases"] == ["01", "02"]
    assert data["phase_dir"] == ".planning/phases/03-report", "the phase folders are not touched"
    assert "03-TESTLOCK.json" in data["missing"], "a phase carried mid-way shows what it lacks"


def test_gsds_own_files_are_kept_in_the_archive(project):
    before = {name: (project / ".planning" / name).read_text() for name in gsd.MOVED}
    assert run("convert", "--project", str(project))[0] == 0
    archive = project / ".planning/archive/gsd"
    assert {name: (archive / name).read_text() for name in gsd.MOVED} == before
    assert not (project / ".planning/PROJECT.md").exists() and not (project / ".planning/config.json").exists()
    assert (project / ".planning/MILESTONES.md").is_file(), "history that other files link to stays in place"
    record = (archive / "CONVERSION.md").read_text()
    assert "| SCAN-01 | REQ-SCAN-01 |" in record and "| 3 Report | plan_approved |" in record


def test_the_roadmap_keeps_numbers_goals_and_dependencies(project):
    run("convert", "--project", str(project))
    text = (project / ".planning/ROADMAP.md").read_text()
    assert [l for l in text.splitlines() if l.startswith("## Phase")] == [
        "## Phase 1: Scan the Tree", "## Phase 2: Find Duplicates", "## Phase 2.1: Hash Cache",
        "## Phase 3: Report", "## Phase 4: Export"]
    block = text.split("## Phase 3: Report")[1].split("## Phase")[0]
    assert "- **Slug:** report" in block and "- **Depends on:** 2, 2.1" in block
    assert "- **Requirements:** REQ-OUT-01" in block and "- **Goal:** A user can read the result" in block
    first = text.split("## Phase 1: Scan the Tree")[1].split("## Phase")[0]
    assert "- **Status:** complete" in first and "  - Every file is listed once" in first
    assert "`phases/01-scan-the-tree/01-VERIFICATION.md`" in first
    assert "`tests/acceptance/p04_export/`" in text, "a phase that has not started gets its acceptance folder"


def test_requirements_become_rows_with_the_old_id_inside_the_new_one(project):
    run("convert", "--project", str(project))
    text = (project / ".planning/REQUIREMENTS.md").read_text()
    assert "| U01 | Scanning |" in text and "| U03 | Output |" in text
    assert "| REQ-SCAN-01 | User can list every file under a folder | U01 | 1 | Validated |" in text
    assert "| REQ-SCAN-02 | A folder that cannot be read is reported / not skipped | U01 | 1 | Validated |" in text, \
        "a '|' in the text would shift the row's cells"
    assert "| REQ-DUPE-02 | A second run reuses the hashes of unchanged files | U02 | 2.1 | Planned |" in text
    assert "| REQ-OUT-04 | User can export the result as JSON | U03 | 4 | Planned |" in text, \
        "an id the phase tool cannot read (OUT-02a) gets the next free number of its family"
    assert "- **REQ-OUT-03** (open) User can choose the columns" in text, "no phase names it: not a table row"
    assert "- **SYNC-01** User can delete duplicates in place" in text


def test_decisions_and_constraints_are_carried_and_existing_files_are_kept(project):
    write(project, ".planning/GLOSSARY.md", "# Our words\n")
    code, out = run("convert", "--project", str(project), "--owner", "Ada")
    assert "left as they were: GLOSSARY.md" in out
    assert (project / ".planning/GLOSSARY.md").read_text() == "# Our words\n"
    decisions = (project / ".planning/DECISIONS.md").read_text()
    assert "| DEC-001 |" in decisions and "| Ada |" in decisions
    assert "| Hash with SHA-256 | Collisions must not happen Outcome under GSD: Good | Carried from GSD's PROJECT.md |" in decisions
    assert "| Read files in chunks | Large files | Carried" in decisions, "a pending outcome is not an outcome"
    manifesto = (project / ".planning/MANIFESTO.md").read_text()
    assert "- **T3 — Runtime.** Python standard library only" in manifesto and "- **T4.** No network access" in manifesto
    assert "Never delete a file the user did not name." in manifesto


def test_a_dry_run_and_a_survey_write_nothing(project):
    code, out = run("survey", "--project", str(project))
    assert code == 0 and "Phases: 5 (2 complete, 2 not_started, 1 plan_approved)" in out, out
    assert "Current phase after the move: 3 (Report), plan_approved" in out
    code, out = run("convert", "--project", str(project), "--dry-run")
    assert code == 0 and "would write" in out and "archive/gsd/PROJECT.md" in out
    assert subprocess.run(["git", "status", "--porcelain"], cwd=project, capture_output=True, text=True).stdout == ""


def test_it_refuses_what_is_not_gsd_and_what_was_already_moved(project, tmp_path):
    assert run("convert", "--project", str(project))[0] == 0
    code, out = run("convert", "--project", str(project))
    assert code == 2 and "already in the dev-tools format" in out
    write(tmp_path / "plain", ".planning/notes.md", "x\n")
    code, out = run("survey", "--project", str(tmp_path / "plain"))
    assert code == 2 and "not a GSD project" in out


def test_a_roadmap_that_restarted_its_numbers_needs_the_owners_choice(project):
    path = project / ".planning/ROADMAP.md"
    path.write_text(path.read_text().replace(
        "## Phase Details", "**Milestone v2.0:**\n\n- [ ] **Phase 1: Web View** - a page\n\n## Phase Details"))
    code, out = run("convert", "--project", str(project))
    assert code == 2 and "--numbering first or --numbering last" in out
    assert (project / ".planning/PROJECT.md").is_file(), "nothing was written"
    code, out = run("survey", "--project", str(project), "--numbering", "last", "--format", "json")
    found = json.loads(out)
    assert [(p["title"], p["status"]) for p in found["phases"]] == [("Web View", "not_started")]
    assert any("phases/01-scan-the-tree: left out" in note for note in found["notes"])
    assert run("convert", "--project", str(project), "--numbering", "first")[0] == 0
    assert "## Phase 1: Scan the Tree" in path.read_text()


def test_the_owner_can_name_phases_gsd_left_unticked(project):
    code, out = run("survey", "--project", str(project), "--complete", "2.1, 3", "--format", "json")
    by_id = {p["id"]: p for p in json.loads(out)["phases"]}
    assert by_id["02.1"]["status"] == by_id["03"]["status"] == "complete"
    assert by_id["04"]["status"] == "not_started"


def test_numbers_that_do_not_start_at_one_need_the_phase_gaps_setting(project):
    shutil.rmtree(project / ".planning/phases")
    roadmap = "# Roadmap\n\n- [x] **Phase 81: Ledger** - one\n- [ ] **Phase 84: Deck** - two\n"
    (project / ".planning/ROADMAP.md").write_text(roadmap)
    (project / ".planning/REQUIREMENTS.md").unlink()
    code, out = run("survey", "--project", str(project))
    assert "phase_gaps = true" in out and "start at 81" in out
    install(project)
    assert run("convert", "--project", str(project))[0] == 0
    git(project, "add", "-A")
    code, env = phase(project, "check", "--roadmap")
    assert code == 1 and "not contiguous" in env["data"]["issues"][0]["message"]
    install(project, phase_gaps="true")
    code, env = phase(project, "check", "--all")
    assert code == 0, env
    text = (project / ".planning/REQUIREMENTS.md").read_text()
    assert "| U01 | Never delete a file the user did not name. |" in text and "| REQ-GSD-001 |" in text, \
        "a project with no requirement file still gets one need and one requirement"


def test_a_project_between_milestones_gets_one_phase_to_fill_in(project):
    shutil.rmtree(project / ".planning/phases")
    (project / ".planning/ROADMAP.md").write_text("# Roadmap\n\nAll milestones shipped.\n")
    (project / ".planning/REQUIREMENTS.md").unlink()
    install(project)
    assert run("convert", "--project", str(project))[0] == 0
    git(project, "add", "-A")
    code, env = phase(project, "check", "--all")
    assert code == 0, env
    code, env = phase(project, "status")
    assert env["data"]["current_phase"] == "01" and env["data"]["phase_status"] == "not_started"


def test_the_survey_lists_gsds_own_files_inside_the_project(project):
    write(project, ".claude/gsd-file-manifest.json", json.dumps(
        {"version": "1.14.0", "files": {"gsd-core/VERSION": "x", "agents/gsd-planner.md": "y", "gone.md": "z"}}))
    write(project, ".claude/gsd-core/VERSION", "1.14.0\n")
    write(project, ".claude/agents/gsd-planner.md", "x\n")
    write(project, ".claude/agents/our-own.md", "x\n")
    write(project, ".codex/get-shit-done/bin/tool.cjs", "x\n")
    write(project, "CLAUDE.md", "Read .planning/PROJECT.md first. Use /gsd-next.\n")
    code, out = run("survey", "--project", str(project))
    assert ".claude/: 3 file(s) of GSD 1.14.0, named by GSD's manifest" in out
    assert ".codex/: 1 file(s), found by name" in out and "CLAUDE.md mentions GSD" in out
    code, out = run("survey", "--project", str(project), "--installed")
    assert out.split() == [".claude/agents/gsd-planner.md", ".claude/gsd-core/VERSION",
                           ".claude/gsd-file-manifest.json", ".codex/get-shit-done/bin/tool.cjs"]
