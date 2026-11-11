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


def install(root, planning_dir=".planning", **settings):
    config = (ROOT / "examples/phase-project.devtools.toml").read_text().replace('"myapp"', '""')
    config = config.replace("after_apply =", "# after_apply =")
    config = config.replace('planning_dir = ".planning"', 'planning_dir = "%s"' % planning_dir)
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
    assert data["current_phase"] == "02.1" and data["phase_status"] == "not_started", \
        "phase 3 was under way but depends on 2.1, which GSD never finished: 2.1 goes first"
    assert data["completed_phases"] == ["01", "02"] and data["blockers"] == []
    assert "base_branch: main" in (project / ".planning/STATE.md").read_text(), "not the branch the move runs on"
    changed = subprocess.run(["git", "status", "--short", ".planning/phases/01-scan-the-tree",
                              ".planning/phases/02-find-duplicates"], cwd=project, capture_output=True, text=True)
    assert changed.stdout == "", "the folders of finished phases are not touched"


def test_a_phase_gsd_did_not_finish_is_carried_no_further_than_its_discussion(project):
    road = project / ".planning/ROADMAP.md"
    road.write_text(road.read_text().replace("**Depends on:** Phase 2, Phase 2.1", "**Depends on:** Phase 2"))
    install(project)
    code, out = run("survey", "--project", str(project))
    assert "Current phase after the move: 3 (Report), context_approved" in out
    assert "GSD's 3 plan, summary and verification file(s) for it move to phases/03-report/gsd/" in out
    assert run("convert", "--project", str(project))[0] == 0
    folder = project / ".planning/phases/03-report"
    assert sorted(p.name for p in folder.iterdir()) == ["03-CONTEXT.md", "gsd"], "the context stays, the rest is input"
    assert sorted(p.name for p in (folder / "gsd").iterdir()) == ["03-01-PLAN.md", "03-01-SUMMARY.md", "03-02-PLAN.md"]
    block = road.read_text().split("## Phase 3: Report")[1].split("## Phase")[0]
    assert "- **Status:** context_approved" in block and "`tests/acceptance/p03_report/`" in block
    assert "- **Under GSD:** a CONTEXT file, 2 plan(s), 1 summary(ies). Its plans, summaries and verification are in " \
           "`phases/03-report/gsd/`" in block
    git(project, "add", "-A")
    assert phase(project, "check", "--all")[0] == 0
    code, env = phase(project, "status")
    assert env["data"]["phase_status"] == "context_approved" and env["data"]["next_step"] == "specify"
    code, env = phase(project, "advance", "--to", "tests_approved")
    assert code == 1 and "missing artifact: 03-TESTLOCK.json" in env["data"]["problems"], \
        "the tests are written and locked here, as for any phase"
    (folder / "03-TESTLOCK.json").write_text('{"phase": "03", "files": {}}')
    (folder / "03-EVIDENCE").mkdir()
    (folder / "03-EVIDENCE/red.txt").write_text("1 failed\n")
    assert phase(project, "advance", "--to", "tests_approved")[0] == 0
    code, env = phase(project, "advance", "--to", "plan_approved")
    assert code == 1 and env["data"]["problems"] == ["missing artifact: 03-MM-PLAN.md"], \
        "GSD's plans do not pass for the plan this step writes"


def test_gsds_own_files_are_kept_in_the_archive(project):
    before = {name: (project / ".planning" / name).read_text() for name in gsd.MOVED}
    assert run("convert", "--project", str(project))[0] == 0
    archive = project / ".planning/archive/gsd"
    assert {name: (archive / name).read_text() for name in gsd.MOVED} == before
    assert not (project / ".planning/PROJECT.md").exists() and not (project / ".planning/config.json").exists()
    assert (project / ".planning/MILESTONES.md").is_file(), "history that other files link to stays in place"
    record = (archive / "CONVERSION.md").read_text()
    assert "| SCAN-01 | REQ-SCAN-01 |" in record
    assert "| 3 Report | not_started | under GSD: a CONTEXT file, 2 plan(s), 1 summary(ies) | `phases/03-report/` |" in record
    assert "| `phases/03-report/gsd/03-01-PLAN.md` | GSD's file of a phase it did not finish, moved from " \
           "`phases/03-report/` |" in record
    assert "phase 3 was under way under GSD and depends on phase 2.1, which is not finished" in record


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
    assert code == 0 and "Phases: 5 (2 complete, 3 not_started)" in out, out
    assert "Current phase after the move: 2.1 (Hash Cache), not_started" in out
    assert "Base branch STATE.md will record: main (from the branch of that name)" in out
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


@pytest.mark.parametrize("line, depends, also", [
    ("Nothing (first phase)", [], []),
    ("Phase 4 and Phase 04.1", ["04", "04.1"], []),
    ("Phases 132 and 134 (documents shipped behavior)", ["132", "134"], []),
    ("Phases 6, 8", ["06", "08"], []),
    ("Phase 1, 2 and 3", ["01", "02", "03"], []),
    ("Phases 1-4", ["01", "02", "03", "04"], []),
    ("Phase 10, Phase 13, Phase 14, and the Phase 7/07.1/8 source", ["07", "07.1", "08", "10", "13", "14"], []),
    ("Phase 131 (shares the access pattern; independent of Phases 132 and 133)", ["131"], ["132", "133"]),
    ("Phase 6 only. May execute in parallel with Phases 7 and 8 — it touches only `evolve/`", ["06"], ["07", "08"]),
    ("Nothing (runs in parallel with Phases 81/82)", [], ["81", "82"]),
    ("Phase 81 (fact inventory). Grounding source: `.planning/milestones/v1.12-phases/73.5-x/`", ["81"], []),
])
def test_a_dependency_line_is_read_however_the_roadmap_words_it(line, depends, also):
    assert gsd.dependencies(line) == (depends, also)


def test_dependencies_in_the_plural_are_carried_and_doubtful_ones_are_reported(project):
    road = project / ".planning/ROADMAP.md"
    road.write_text(road.read_text()
                    .replace("**Depends on:** Phase 2, Phase 2.1", "**Depends on:** Phases 1 and 2")
                    .replace("**Depends on**: Phase 3\n", "**Depends on**: Phase 1 (independent of Phase 2)\n"))
    code, out = run("convert", "--project", str(project))
    assert code == 0, out
    text = road.read_text()
    assert "- **Depends on:** 1, 2" in text.split("## Phase 3: Report")[1].split("## Phase")[0]
    assert "- **Depends on:** 1\n" in text.split("## Phase 4: Export")[1]
    record = (project / ".planning/archive/gsd/CONVERSION.md").read_text()
    assert "phase 4: its dependency line in GSD also names phase 2, which is not carried as a dependency" in record


PUT_OFF = """
<details>
<summary>v0.9 Old Engine (Phases 5-6) - PAUSED</summary>

- [x] **Phase 5: Engine Spike** - done before the pause
- [ ] **Phase 6: Engine Rewrite** - never started

</details>

- [ ] **Phase 7: Themes** (DEFERRED) - later
- [ ] **Phase 8: Plugin System** - deferred work on plugins is not a marker

## Backlog

### Phase 999.1: Dark Mode

**Goal**: someday

## Phase Details
"""


def test_phases_gsd_put_off_are_listed_and_not_queued(project):
    road = project / ".planning/ROADMAP.md"
    road.write_text(road.read_text().replace("\n## Phase Details\n", PUT_OFF, 1))
    code, out = run("survey", "--project", str(project), "--format", "json")
    found = json.loads(out)
    assert [(p["id"], p["parked"]) for p in found["parked"]] == [("06", "paused"), ("07", "deferred"), ("999.1", "backlog")]
    ids = [p["id"] for p in found["phases"]]
    assert "05" in ids and "08" in ids and "999" not in ids, "a finished phase and an ordinary one stay phases"
    install(project, phase_gaps="true")
    assert run("convert", "--project", str(project))[0] == 0
    text = road.read_text()
    assert "## Phase 6:" not in text and "## Phase 999" not in text
    tail = text.split("## Put off under GSD")[1]
    assert "- Phase 6, Engine Rewrite (paused, GSD milestone v0.9). Goal: never started" in tail
    assert "- Phase 999.1, Dark Mode (backlog). Goal: someday" in tail
    git(project, "add", "-A")
    assert phase(project, "check", "--all")[0] == 0
    code, env = phase(project, "status", "--phase", "next")
    assert env["data"]["current_phase"] == "02.1", "nothing GSD put off is next"


def test_the_owner_can_bring_a_put_off_phase_back(project):
    road = project / ".planning/ROADMAP.md"
    road.write_text(road.read_text().replace("\n## Phase Details\n", PUT_OFF, 1))
    code, out = run("survey", "--project", str(project), "--open", "6", "--format", "json")
    found = json.loads(out)
    assert [p["id"] for p in found["parked"]] == ["07", "999.1"]
    assert next(p for p in found["phases"] if p["id"] == "06")["status"] == "not_started"


WORKSTREAM = {
    "active-workstream": "harbor\n",
    "workstreams/harbor/STATE.md": "---\ngsd_state_version: 1.0\nstatus: executing\nlast_activity: 2026-07-01 -- ran it\n---\n",
    "workstreams/harbor/ROADMAP.md": "# Roadmap\n\n- [x] **Phase 38: Matrix** - done\n- [ ] **Phase 39: Report** - next\n",
    "workstreams/harbor/phases/38-matrix/38-01-PLAN.md": "# Plan\n",
    "workstreams/harbor/phases/38-matrix/38-01-SUMMARY.md": "# Summary\n",
    "workstreams/old/ROADMAP.md": "# Roadmap\n\n- [x] **Phase 1: Before** - done\n",
}


def test_a_project_with_workstreams_is_not_moved_until_the_owner_names_the_plan(project):
    for name, text in WORKSTREAM.items():
        write(project / ".planning", name, text)
    git(project, "add", "-A")
    git(project, "commit", "-qm", "workstreams")
    code, out = run("survey", "--project", str(project))
    assert "Plans GSD keeps here (a move reads one of them):" in out
    assert "  root plan          3 phase folder(s)" in out and "<- this survey" in out
    assert "  workstream harbor  1 phase folder(s), last activity 2026-07-01, status executing   <- GSD's active workstream" in out
    code, out = run("convert", "--project", str(project))
    assert code == 2 and "GSD keeps 2 workstream(s) under .planning/workstreams/ and names 'harbor' as the one in use" in out
    assert (project / ".planning/PROJECT.md").is_file(), "nothing was written"
    code, out = run("convert", "--project", str(project), "--root-plan")
    assert code == 0, out
    record = (project / ".planning/archive/gsd/CONVERSION.md").read_text()
    assert "| workstream `harbor` | 1 | 2026-07-01 | GSD's active workstream |" in record
    assert (project / ".planning/workstreams/harbor/STATE.md").read_text() == WORKSTREAM["workstreams/harbor/STATE.md"]


def test_a_workstream_can_be_the_plan_that_is_moved(project):
    for name, text in WORKSTREAM.items():
        write(project / ".planning", name, text)
    git(project, "add", "-A")
    git(project, "commit", "-qm", "workstreams")
    where = ".planning/workstreams/harbor"
    install(project, planning_dir=where, phase_gaps="true")
    root_before = {name: (project / ".planning" / name).read_text() for name in gsd.MOVED}
    code, out = run("survey", "--project", str(project), "--planning-dir", where)
    assert 'planning_dir = "%s"' % where in out and "this is workstream 'harbor'" in out
    code, out = run("convert", "--project", str(project), "--planning-dir", where)
    assert code == 0, out
    assert {name: (project / ".planning" / name).read_text() for name in gsd.MOVED} == root_before, \
        "the root plan stays as GSD wrote it"
    assert "Hash with SHA-256" in (project / where / "DECISIONS.md").read_text(), "the project's decisions come from the root"
    assert (project / where / "archive/gsd/ROADMAP.md").read_text() == WORKSTREAM["workstreams/harbor/ROADMAP.md"]
    git(project, "add", "-A")
    code, env = phase(project, "check", "--all")
    assert code == 0, env
    code, env = phase(project, "status")
    assert env["data"]["current_phase"] == "39" and env["data"]["completed_phases"] == ["38"]


def test_a_planning_folder_that_git_ignores_is_not_moved_without_a_word(tmp_path):
    root = tmp_path / "widget"
    for name, text in [("STATE.md", STATE), ("ROADMAP.md", ROADMAP), ("PROJECT.md", PROJECT), ("config.json", "{}")]:
        write(root / ".planning", name, text)
    write(root, ".gitignore", ".planning/\n")
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "start")
    code, out = run("survey", "--project", str(root))
    assert code == 0 and "git ignores .planning/, so nothing the move writes could be committed" in out
    code, out = run("convert", "--project", str(root))
    assert code == 2 and "--ignored-plan" in out and (root / ".planning/PROJECT.md").is_file()
    assert run("convert", "--project", str(root), "--ignored-plan")[0] == 0


def test_the_decisions_table_is_read_by_its_headings(project):
    path = project / ".planning/PROJECT.md"
    table = path.read_text().split("## Key Decisions")[1]
    path.write_text(path.read_text().replace(table, """

| Decision | Outcome | Rationale / Evidence |
|----------|---------|----------------------|
| Hash with SHA-256 | ✓ Good | Collisions must not happen |
| Split on `a|b` | — Pending | The files use it |
"""))
    assert run("convert", "--project", str(project))[0] == 0
    decisions = (project / ".planning/DECISIONS.md").read_text()
    assert "| Hash with SHA-256 | Collisions must not happen Outcome under GSD: Good | Carried" in decisions
    assert "| Split on `a/b` | The files use it | Carried" in decisions, "a | inside backticks is part of the cell"


def test_a_decisions_table_with_a_number_and_a_date_column(project):
    path = project / ".planning/PROJECT.md"
    table = path.read_text().split("## Key Decisions")[1]
    path.write_text(path.read_text().replace(table, """

| # | Decision | Why | Date |
|---|----------|-----|------|
| 1 | Hash with SHA-256 | Collisions must not happen | 2026-05-01 |
| 2 | Keep the cache | | |
"""))
    assert run("convert", "--project", str(project))[0] == 0
    rows = [l for l in (project / ".planning/DECISIONS.md").read_text().splitlines() if "Carried from GSD" in l]
    assert rows[0].startswith("| DEC-003 | 2026-05-01 | Hash with SHA-256 | Collisions must not happen |")
    assert "| Keep the cache | Not recorded |" in rows[1] and len(rows) == 2, "the heading row is not a decision"


def test_what_an_existing_file_would_have_held_is_set_aside_for_the_owner(project):
    write(project, ".planning/DECISIONS.md", "# Decisions\n\n- 2026-01-02: we hash files\n")
    code, out = run("convert", "--project", str(project), "--owner", "Ada")
    assert code == 0 and "left as they were: DECISIONS.md" in out
    assert (project / ".planning/DECISIONS.md").read_text() == "# Decisions\n\n- 2026-01-02: we hash files\n"
    draft = (project / ".planning/archive/gsd/DECISIONS-to-merge.md").read_text()
    assert "| DEC-001 |" in draft and "| Ada |" in draft and "Hash with SHA-256" in draft
    record = (project / ".planning/archive/gsd/CONVERSION.md").read_text()
    assert "`DECISIONS.md` was already there and was left as it was. What the move would have written is in " \
           "`archive/gsd/DECISIONS-to-merge.md`" in record


def test_the_base_branch_is_never_the_branch_the_move_runs_on(project):
    git(project, "branch", "-m", "main", "trunk")
    code, out = run("survey", "--project", str(project))
    assert "Base branch STATE.md will record: cannot be told; pass --base-branch" in out
    code, out = run("convert", "--project", str(project))
    assert code == 2 and "base branch cannot be told" in out and (project / ".planning/PROJECT.md").is_file()
    assert run("convert", "--project", str(project), "--base-branch", "trunk")[0] == 0
    state = (project / ".planning/STATE.md").read_text()
    assert "base_branch: trunk" in state and "move-to-devtools" not in state


def test_the_survey_says_what_the_project_is_written_in(project):
    write(project, "src/app.ts", "export const a = 1\n")
    write(project, "src/view.ts", "export const b = 2\n")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "code")
    code, out = run("survey", "--project", str(project))
    assert "Files git tracks: 2 .ts. Python set up: no" in out
    assert "the phase skills are written for Python and pytest, and this project has no Python" in out
    write(project, "pyproject.toml", "[project]\nname = 'widget'\n")
    write(project, "widget/core.py", "A = 1\n")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "python")
    code, out = run("survey", "--project", str(project))
    assert "Python set up: pyproject.toml" in out and "written for Python and pytest, and this project" not in out


def test_the_survey_names_the_skill_check_setting_when_other_skills_are_there(project):
    write(project, ".claude/skills/release-notes/SKILL.md", "---\nname: release-notes\n---\n")
    write(project, ".claude/agents/gsd-planner.md", "x\n")
    code, out = run("survey", "--project", str(project))
    assert 'skill_check = "synced"   (1 skill or agent file(s) here are not the sync\'s, e.g. ' \
           '.claude/skills/release-notes/SKILL.md)' in out
    install(project)
    code, out = run("survey", "--project", str(project))
    assert "(1 skill or agent file(s) here" in out, "what the sync delivered is not counted"
