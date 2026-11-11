"""Tests for the scripts a project runs after a sync: the phase state tool, the coder
pool, the component index and the phase-selection plugin. Each test works in a new project made by the sync."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync", ROOT / "devtools/sync.py")
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)
GIT = shutil.which("git")  # found once: a test that replaces PATH still needs the real one

ROADMAP = """# Roadmap

## Phase 1: Scan
- **Slug:** scan
- **Status:** not_started
- **Depends on:** none
- **Requirements:** REQ-CORE-001
- **Reuses:** nothing
- **Acceptance tests (written first):** `tests/acceptance/p01_scan/`

## Phase 2: Dupes
- **Slug:** dupes
- **Status:** not_started
- **Depends on:** 1
- **Requirements:** REQ-CORE-001
- **Reuses:** nothing
- **Acceptance tests (written first):** `tests/acceptance/p02_dupes/`

## Phase 3: Report
- **Slug:** report
- **Status:** not_started
- **Depends on:** 1
- **Requirements:** REQ-CORE-001
- **Reuses:** nothing
- **Acceptance tests (written first):** `tests/acceptance/p03_report/`

## Phase 4: Export
- **Slug:** export
- **Status:** not_started
- **Depends on:** 2, 3
- **Requirements:** REQ-CORE-001
- **Reuses:** nothing
- **Acceptance tests (written first):** `tests/acceptance/p04_export/`
"""


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "widget"
    (root / "src/widget").mkdir(parents=True)
    (root / "src/widget/__init__.py").write_text('"""widget."""\n')
    config = (ROOT / "examples/phase-project.devtools.toml").read_text().replace("myapp", "widget")
    (root / ".devtools.toml").write_text(config)
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    assert sync.main(["apply", "--project", str(root)]) == 0
    return root


def tool(project, *args, script=".claude/skills/process-phase/scripts/phase_tool.py"):
    env = {**os.environ, "XDG_CACHE_HOME": str(project.parent / "cache")}  # the index search keeps a cache there
    proc = subprocess.run([sys.executable, script, *args], cwd=project, capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout + proc.stderr


def phase(project, *args):
    code, out = tool(project, "--format", "json", *args)
    return code, json.loads(out)


def state(project, **values):
    path = project / ".planning/STATE.md"
    text = path.read_text()
    for key, value in values.items():
        line = next(l for l in text.splitlines() if l.startswith(key + ":"))
        text = text.replace(line, "%s: %s" % (key, value))
    path.write_text(text)


def commit(project):
    subprocess.run(["git", "add", "-A"], cwd=project, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qm", "x"],
                   cwd=project, check=True)


def test_a_new_project_is_clean_after_sync_and_setup(project):
    assert (project / "docs/components/COMPONENTS.md").is_file(), "the first sync writes a starter catalog"
    code, env = phase(project, "setup", "--name", "widget")
    assert code == 0 and len(env["data"]["created"]) == 11
    commit(project)
    code, env = phase(project, "check", "--all")
    assert code == 0, env
    code, env = phase(project, "setup")
    assert env["data"]["created"] == [] and len(env["data"]["kept"]) == 11, "setup never overwrites"


def test_a_step_cannot_be_approved_without_its_file(project):
    phase(project, "setup")
    code, env = phase(project, "advance", "--to", "context_approved")
    assert code == 1 and env["error"]["code"] == "GATE_BLOCKED"
    assert env["data"]["problems"] == ["missing artifact: 01-CONTEXT.md"]
    phase(project, "init", "--phase", "1")
    code, env = phase(project, "advance", "--to", "context_approved")
    assert code == 0, env
    code, env = phase(project, "advance", "--to", "tests_approved")
    assert code == 1 and "missing artifact: 01-TESTLOCK.json" in env["data"]["problems"]


def test_gated_from_plan_approved_only_warns_for_the_first_two_steps(project):
    settings = project / ".claude/skills/process-phase/scripts/phase_tool.settings.json"
    settings.write_text(json.dumps(dict(json.loads(settings.read_text()), gated_from="plan_approved")))
    phase(project, "setup")
    code, env = phase(project, "advance", "--to", "context_approved")
    assert code == 0 and env["data"]["warnings"] == ["missing artifact: 01-CONTEXT.md"]


def test_a_phase_with_unfinished_dependencies_cannot_advance(project):
    phase(project, "setup")
    (project / ".planning/ROADMAP.md").write_text(ROADMAP)
    state(project, current_phase='"04"', completed_phases='"01"')
    code, env = phase(project, "advance", "--to", "context_approved")
    assert code == 1 and env["error"]["code"] == "DEPENDENCIES_INCOMPLETE"
    assert env["data"]["waiting_on"] == ["02", "03"]


def test_closing_out_of_order_goes_back_to_the_skipped_phase(project):
    phase(project, "setup")
    (project / ".planning/ROADMAP.md").write_text(ROADMAP)
    state(project, current_phase='"03"', completed_phases='"01"', phase_status="verified")
    code, env = phase(project, "complete", "--phase", "3")
    assert code == 0, env
    assert env["data"]["completed_phases"] == ["01", "03"] and env["data"]["current_phase"] == "02"
    assert "blockers" not in env["data"]
    code, env = phase(project, "status", "--phase", "next", "--brief")
    assert env["data"]["current_phase"] == "02"


def test_roadmap_may_start_at_phase_one_but_not_skip_a_number(project):
    phase(project, "setup")
    (project / ".planning/ROADMAP.md").write_text(ROADMAP)
    assert phase(project, "check", "--roadmap")[0] == 0
    (project / ".planning/ROADMAP.md").write_text(ROADMAP.replace("## Phase 2:", "## Phase 5:"))
    assert phase(project, "check", "--roadmap")[0] == 1


PHASE_BLOCK = """
## Phase %s: %s
- **Slug:** %s
- **Status:** %s
- **Depends on:** none
- **Requirements:** REQ-CORE-001
- **Reuses:** nothing
- **Acceptance tests (written first):** `tests/acceptance/`
"""


def setting(project, **values):
    path = project / ".claude/skills/process-phase/scripts/phase_tool.settings.json"
    path.write_text(json.dumps(dict(json.loads(path.read_text()), **values)))


def test_a_phase_added_after_the_roadmap_was_finished_becomes_the_current_one(project):
    phase(project, "setup")
    road = project / ".planning/ROADMAP.md"
    road.write_text(ROADMAP.replace("- **Status:** not_started", "- **Status:** complete", 3))
    state(project, current_phase='"04"', completed_phases='"01,02,03"', phase_status="verified")
    code, env = phase(project, "complete", "--phase", "4")
    assert code == 0 and env["data"]["current_phase"] == "04", "there is no later phase to move on to"
    assert "phase_status: complete" in (project / ".planning/STATE.md").read_text()

    road.write_text(road.read_text() + PHASE_BLOCK % (5, "Web view", "web-view", "not_started")
                    + PHASE_BLOCK % (6, "Sync", "sync", "not_started"))
    code, env = phase(project, "status")
    assert env["data"]["current_phase"] == "05" and env["data"]["phase_status"] == "not_started"
    assert env["data"]["next_step"] == "discuss"
    assert phase(project, "check", "--roadmap", "--state")[0] == 0
    phase(project, "init", "--phase", "5")
    code, env = phase(project, "advance", "--to", "context_approved")
    assert code == 0 and env["data"]["phase"] == "05", env
    text = (project / ".planning/STATE.md").read_text()
    assert 'current_phase: "05"' in text and "phase_status: context_approved" in text
    assert "- **Status:** context_approved" in road.read_text().split("## Phase 5:")[1]


def test_another_phase_can_be_activated_once_the_roadmap_was_finished(project):
    phase(project, "setup")
    road = project / ".planning/ROADMAP.md"
    road.write_text(ROADMAP.replace("- **Status:** not_started", "- **Status:** complete")
                    + PHASE_BLOCK % (5, "Web view", "web-view", "not_started")
                    + PHASE_BLOCK % (6, "Sync", "sync", "not_started"))
    state(project, current_phase='"04"', completed_phases='"01,02,03,04"', phase_status="complete")
    code, env = phase(project, "activate", "--phase", "6", "--dec", "DEC-001")
    assert code == 0 and env["data"]["phase"] == "06", env
    assert 'current_phase: "06"' in (project / ".planning/STATE.md").read_text()


def test_phase_numbers_above_99_work_like_any_other(project):
    phase(project, "setup")
    setting(project, phase_gaps=True)
    (project / ".planning/ROADMAP.md").write_text(
        "# Roadmap\n" + PHASE_BLOCK % (121, "Ledger", "ledger", "complete")
        + PHASE_BLOCK % (122, "Deck", "deck", "not_started") + PHASE_BLOCK % ("122.1", "Deck fix", "deck-fix", "not_started"))
    state(project, current_phase='"122"', completed_phases='"121"')
    assert phase(project, "check", "--roadmap")[0] == 0
    code, env = phase(project, "branch", "--set", "phase/122-deck")
    assert code == 0 and env["data"]["phase_branch"] == "phase/122-deck", env
    assert phase(project, "branch", "--set", "phase/121-ledger")[0] == 2, "a branch of another phase is still refused"
    for name in ("p122_deck", "p122_1_deck_fix"):
        (project / "tests/acceptance" / name).mkdir(parents=True)
        (project / "tests/acceptance" / name / ("test_%s.py" % name)).write_text("def test_it():\n    assert True\n")
    code, env = phase(project, "testlock", "--phase", "122")
    assert list(env["data"]["files"]) == ["tests/acceptance/p122_deck/test_p122_deck.py"], \
        "the tests of inserted phase 122.1 are not phase 122's"
    code, env = phase(project, "testlock", "--phase", "122.1")
    assert list(env["data"]["files"]) == ["tests/acceptance/p122_1_deck_fix/test_p122_1_deck_fix.py"]

    def run(*args):
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args],
                              cwd=project, capture_output=True, text=True)
        return proc.stdout.strip().splitlines()[-1]

    assert run().startswith("2 deselected"), "neither phase is complete"
    assert run("--phase", "122").startswith("1 passed, 1 deselected")
    assert run("--phase", "122.1").startswith("1 passed, 1 deselected")
    state(project, completed_phases='"121,122"')
    assert run().startswith("1 passed, 1 deselected")


def test_the_skill_check_can_be_limited_to_what_the_sync_delivered(project):
    phase(project, "setup")
    commit(project)
    (project / ".claude/agents/README.md").write_text("# Our agents\n")
    (project / ".claude/agents/reviewer.md").write_text("---\nname: code-reviewer\ndescription: reviews\n---\n")
    own = project / ".claude/skills/release-notes"
    own.mkdir()
    (own / "SKILL.md").write_text("---\nname: release_notes\ndescription: Writes notes\n---\nRun `scripts/make.py`.\n")
    code, env = phase(project, "check", "--all")
    assert code == 1 and {i["rule"] for i in env["data"]["issues"]} == {"skill", "agent"}
    assert len(env["data"]["issues"]) == 6
    setting(project, skill_check="synced")
    code, env = phase(project, "check", "--all")
    assert code == 0, env
    (project / ".claude/skills/process-phase/SKILL.md").write_text("no frontmatter\n")
    code, env = phase(project, "check", "--all")
    assert code == 1 and any(i["rule"] == "skill" and "process-phase" in i["file"] for i in env["data"]["issues"]), \
        "a synced skill is still checked"
    (project / ".devtools-receipt.json").unlink()
    code, env = phase(project, "check", "--all")
    assert any("receipt is missing" in i["message"] for i in env["data"]["issues"])


def test_a_slug_that_starts_with_a_digit_is_reported(project):
    phase(project, "setup")
    road = project / ".planning/ROADMAP.md"
    road.write_text("# Roadmap\n" + PHASE_BLOCK % (1, "Two factor", "2-factor-auth", "not_started"))
    code, env = phase(project, "check", "--roadmap")
    assert code == 1 and "p01_2_factor_auth reads as the tests of an inserted phase" in env["data"]["issues"][0]["message"]
    road.write_text("# Roadmap\n" + PHASE_BLOCK % (1, "Two factor", "two-factor-auth", "not_started"))
    assert phase(project, "check", "--roadmap")[0] == 0


def test_status_asks_nothing_of_a_phase_finished_under_another_process(project):
    phase(project, "setup")
    block = PHASE_BLOCK % (1, "Scan", "scan", "complete")
    road = project / ".planning/ROADMAP.md"
    road.write_text("# Roadmap\n" + block + PHASE_BLOCK % (2, "Report", "report", "not_started"))
    state(project, current_phase='"02"', completed_phases='"01"')
    code, env = phase(project, "status", "--phase", "1")
    assert len(env["data"]["missing"]) == 6, "a phase of this process is asked for its files"
    road.write_text(road.read_text().replace(
        "- **Acceptance tests (written first):** `tests/acceptance/`",
        "- **Acceptance tests:** none: the phase was finished under GSD", 1))
    code, env = phase(project, "status", "--phase", "1")
    assert env["data"]["phase_status"] == "complete" and env["data"]["missing"] == []


def test_every_plan_needs_its_own_summary(project):
    phase(project, "setup")
    phase(project, "init", "--phase", "1")
    folder = next((project / ".planning/phases").glob("01-*"))
    for name in ("01-01-PLAN.md", "01-02-PLAN.md", "01-01-SUMMARY.md"):
        (folder / name).write_text("# x\n")
    state(project, phase_status="implemented")
    code, env = phase(project, "status")
    assert "01-02-SUMMARY.md" in env["data"]["missing"], "one summary does not stand for two plans"
    (folder / "01-02-SUMMARY.md").write_text("# x\n")
    code, env = phase(project, "status")
    assert not [name for name in env["data"]["missing"] if "SUMMARY" in name]


def test_setup_refuses_a_plan_written_in_another_format(project):
    planning = project / ".planning"
    planning.mkdir()
    (planning / "STATE.md").write_text("---\ngsd_state_version: 1.0\nstatus: executing\n---\n")
    (planning / "ROADMAP.md").write_text("# Roadmap\n\n### Phase 1: Scan\n\n**Goal**: list files\n")
    code, env = phase(project, "setup")
    assert code == 1 and env["error"]["code"] == "FOREIGN_PLAN", env
    assert env["data"]["files"] == ["STATE.md", "ROADMAP.md"] and "from_gsd.py" in env["error"]["hint"]
    assert sorted(p.name for p in planning.iterdir()) == ["ROADMAP.md", "STATE.md"], "nothing was added"


PLAN = """---
phase: "01"
plan: "01-01"
wave: 1
depends_on: []
requirements: [REQ-CORE-001]
turns_green: [tests/acceptance/p01_scan/test_scan.py::test_lists_files]
---

# Plan 01-01: Scan a folder (Phase 01: Scan)

## Objective
Deliver the scanner, so that the acceptance tests under tests/acceptance/p01_scan turn green.
This paragraph only has to make the plan longer than a stub of two hundred characters.

## Reuse
searched: "scan walk list files" (scripts/components_index.py search)
external: none checked
new_component: fs.scan because no entry lists files

<tasks>

### 01-01-T1 — Write the scanner
- **type:** auto
- **turns_green:** `tests/acceptance/p01_scan/test_scan.py::test_lists_files`
- **files:** `src/widget/scan.py`, `tests/unit/`
- **verify:** `pytest tests/unit -q`

</tasks>
"""

TESTS = """---
phase: "01"
test_dir: tests/acceptance/p01_scan/
---

# Phase 01: Scan — Acceptance tests

## Traceability

| # | Criterion | Test ids | Red reason | Kind |
|---|---|---|---|---|
| 1 | Lists every file | `test_scan.py::test_lists_files` | ImportError | contract |
| 2 | Skips hidden files | `test_scan.py::test_skips_hidden` | ImportError | contract |
| 3 | Still prints sizes | `test_scan.py::test_sizes[kb, mb]` | — (green at red) | guard |

## Red run
"""


def planned(project):
    """Phase 1 with one plan and its test list; returns the plan's path."""
    phase(project, "setup")
    (project / ".planning/ROADMAP.md").write_text(ROADMAP)
    phase(project, "init", "--phase", "1")
    folder = project / ".planning/phases/01-scan"
    (folder / "01-TESTS.md").write_text(TESTS)
    (folder / "01-01-PLAN.md").write_text(PLAN)
    return folder / "01-01-PLAN.md"


def messages(env):
    return [i["message"] for i in env["data"]["issues"]]


def test_a_plan_names_its_requirements_and_how_each_task_is_verified(project):
    plan = planned(project)
    uncovered = ["no plan task turns this test green: test_scan.py::test_skips_hidden"]
    assert phase(project, "check", "--plan", str(plan))[0] == 0
    plan.write_text(PLAN.replace("[REQ-CORE-001]", "[]            # REQ ids, non-empty")
                    .replace("`pytest tests/unit -q`", ""))
    assert phase(project, "check", "--plan", str(plan))[0] == 0, "the check every plan must pass does not judge these"
    code, env = phase(project, "check", "--plans", "1")
    assert code == 1 and messages(env) == ["plan frontmatter: requirements names no REQ id",
                                           "task 01-01-T1: verify is empty", *uncovered,
                                           "no plan of phase 01 names requirement REQ-CORE-001"]
    for written in ("requirements:\n  - REQ-CORE-001", "requirements:\n- REQ-CORE-001  # the scanner",
                    'requirements: ["REQ-CORE-001"]'):
        plan.write_text(PLAN.replace("requirements: [REQ-CORE-001]", written))
        assert messages(phase(project, "check", "--plans", "1")[1]) == uncovered, written
    plan.write_text(PLAN.replace("- **verify:** `pytest tests/unit -q`", "- **verify:**\n  `pytest tests/unit -q`"))
    assert messages(phase(project, "check", "--plans", "1")[1]) == uncovered, "a field may run on over indented lines"


def test_every_listed_test_is_turned_green_by_some_plan(project):
    plan = planned(project)
    code, env = phase(project, "check", "--plans", "1")
    assert code == 1 and messages(env) == ["no plan task turns this test green: test_scan.py::test_skips_hidden"]
    assert env["data"]["issues"][0]["file"] == ".planning/phases/01-scan/01-TESTS.md"

    plan.write_text(PLAN.replace("[tests/acceptance/p01_scan/test_scan.py::test_lists_files]",
                                 "[test_scan.py::test_lists_files, test_scan.py::test_skips_hidden]"))
    code, env = phase(project, "check", "--plans", "1")
    assert code == 1 and messages(env) == [
        "no plan task turns this test green: test_scan.py::test_skips_hidden",
        "plan frontmatter: turns_green lists tests/acceptance/p01_scan/test_scan.py::test_skips_hidden, "
        "which no task of the plan claims"], "a test listed in the frontmatter is claimed only by a task"
    both = PLAN.replace("[tests/acceptance/p01_scan/test_scan.py::test_lists_files]",
                        "[test_scan.py::test_lists_files, test_scan.py::test_skips_hidden]")
    plan.write_text(both.replace("`tests/acceptance/p01_scan/test_scan.py::test_lists_files`",
                                 "\n  `test_scan.py::test_lists_files`,\n  `tests/acceptance/p01_scan/test_scan.py::test_skips_hidden`"))
    assert phase(project, "check", "--plans", "1")[0] == 0, "a bare file name and a full path name the same test"
    plan.write_text(PLAN.replace("p01_scan/test_scan.py::test_lists_files`", "p09_other/test_scan.py::test_skips_hidden`"))
    code, env = phase(project, "check", "--plans", "1")
    assert code == 1 and sum(m.startswith("no plan task turns this test green") for m in messages(env)) == 2, \
        "the same file name in another folder is another test"
    plan.write_text(PLAN.split("<tasks>")[0])
    code, env = phase(project, "check", "--plans", "1")
    assert code == 1 and "no task found (a '### <id>' block between <tasks> and </tasks>)" in messages(env)
    plan.write_text(PLAN)

    second = PLAN.replace("01-01", "01-02").replace("test_lists_files", "test_skips_hidden").replace("wave: 1", "wave: 2")
    (plan.parent / "01-02-PLAN.md").write_text(second.replace("[REQ-CORE-001]", "[REQ-CORE-001, REQ-CORE-009]"))
    code, env = phase(project, "check", "--plans", "1")
    assert code == 1 and messages(env) == ["REQ-CORE-009 is not a requirement of phase 01"]
    (plan.parent / "01-02-PLAN.md").write_text(second)
    assert phase(project, "check", "--plans", "1")[0] == 0

    plan.write_text(PLAN.replace("[REQ-CORE-001]", "[]"))
    (plan.parent / "01-02-PLAN.md").write_text(second.replace("[REQ-CORE-001]", "[]"))
    code, env = phase(project, "check", "--plans", "1")
    assert code == 1 and messages(env) == ["plan frontmatter: requirements names no REQ id"] * 2 + [
        "no plan of phase 01 names requirement REQ-CORE-001"]
    code, env = phase(project, "check", "--plans", "2")
    assert code == 1 and messages(env) == ["phase 02 has no plan"]


def plan_text(number, wave=1, depends_on="[]", files="`src/widget/scan.py`", test="test_skips_hidden"):
    """PLAN as plan 01-<number>: its wave, what it depends on, its task's files and the test it turns green."""
    return (PLAN.replace("01-01", "01-" + number).replace("wave: 1", "wave: %s" % wave)
            .replace("depends_on: []", "depends_on: " + depends_on)
            .replace("`src/widget/scan.py`, `tests/unit/`", files).replace("test_lists_files", test))


def second_plan(folder, **how):
    """Write plan 01-02 beside 01-01 (whose task names src/widget/scan.py and tests/unit/); return the messages."""
    (folder / "01-02-PLAN.md").write_text(plan_text("02", **how))
    return messages(phase(folder.parents[2], "check", "--plans", "1")[1])


def test_two_plans_of_one_wave_do_not_name_the_same_file(project):
    folder = planned(project).parent
    together = "plans 01-01 and 01-02 are both in wave 1, neither depends on the other, and both name "
    assert second_plan(folder) == [together + "src/widget/scan.py"]
    assert second_plan(folder, files="`tests/unit/test_scan.py`") == [together + "tests/unit/ and tests/unit/test_scan.py"], \
        "a file inside a folder the other plan names"
    assert second_plan(folder, files="`src/widget/*.py`, `docs/guide.md`") == [together + "src/widget/scan.py and src/widget/*.py"], \
        "a pattern that matches the other plan's file"
    assert second_plan(folder, files="`src/*/scan.py`, `tests/unit/sizes/`") == [
        together + "src/widget/scan.py and src/*/scan.py, tests/unit/ and tests/unit/sizes/"]

    assert second_plan(folder, files="`src/widget/dupes.py`") == [], "different files"
    many = ", ".join("`src/widget/m%d.py`" % number for number in range(7))
    (folder / "01-01-PLAN.md").write_text(PLAN.replace("`src/widget/scan.py`, `tests/unit/`", many))
    assert second_plan(folder, files=many) == [together + ", ".join("src/widget/m%d.py" % n for n in range(5)) + " and 2 more"]
    (folder / "01-01-PLAN.md").write_text(PLAN)
    assert second_plan(folder, wave=2) == [], "another wave"
    for written in ('["01-01"]', "[01]", "\n  - 01-01-PLAN.md"):
        assert second_plan(folder, depends_on=written) == [], "one runs after the other: " + written
    assert second_plan(folder, depends_on="none", files="`src/widget/dupes.py`") == [], "none, written out"

    # A generated file is regenerated after the merge, so two plans may both name it.
    shared = "`src/widget/%s.py`, `docs/components/COMPONENTS.md`, `docs/components/modules/widget.md`, `.planning/todos/x.md`"
    (folder / "01-01-PLAN.md").write_text(PLAN.replace("`src/widget/scan.py`, `tests/unit/`", shared % "scan"))
    assert second_plan(folder, files=shared % "dupes") == [], "the component index and the planning folder"
    (folder / "01-01-PLAN.md").write_text(PLAN)
    assert second_plan(folder, files="`tests/unit/`, `build/report.html`") == [together + "tests/unit/"]
    setting(project, shared_files=["tests/unit/", "build/*.html"])
    assert second_plan(folder, files="`tests/unit/`, `build/report.html`") == [], "the project's own shared files"
    assert second_plan(folder) == [together + "src/widget/scan.py"], "which excuse nothing else"
    setting(project, shared_files="tests/unit/")
    code, out = tool(project, "check", "--plans", "1")
    assert code == 1 and "shared_files must be a list of paths" in out


def test_a_plan_depends_only_on_plans_that_come_before_it(project):
    folder = planned(project).parent
    other = dict(files="`src/widget/dupes.py`")
    assert second_plan(folder, depends_on='["01-07"]', **other) == ["depends_on names 01-07, which is no plan of phase 01"]
    assert second_plan(folder, depends_on="[01-02]", **other) == ["depends_on names 01-02, which is this plan"]

    (folder / "01-01-PLAN.md").write_text(PLAN.replace("depends_on: []", "depends_on: [01-02]"))
    assert second_plan(folder, depends_on="[01-01]", **other) == [
        "depends_on forms a loop: 01-01 depends on itself through 01-02",
        "depends_on forms a loop: 01-02 depends on itself through 01-01"]
    assert second_plan(folder, wave=2, **other) == [
        "depends_on names 01-02, which is in a later wave (2) than this plan (1)"]
    (folder / "01-01-PLAN.md").write_text(PLAN)

    for written in ("soon", "0", "1.5", '""'):
        assert second_plan(folder, wave=written, **other) == [
            "plan frontmatter: wave is missing or not a whole number from 1 up"], written
    (folder / "01-02-PLAN.md").unlink()
    (folder / "01-01-PLAN.md").write_text(PLAN.replace("wave: 1\n", ""))
    assert messages(phase(project, "check", "--plans", "1")[1]) == [
        "no plan task turns this test green: test_scan.py::test_skips_hidden"], "one plan needs no wave"


def test_a_plans_frontmatter_lists_the_tests_its_tasks_turn_green(project):
    plan = planned(project)
    uncovered = "no plan task turns this test green: test_scan.py::test_skips_hidden"
    listed = "[tests/acceptance/p01_scan/test_scan.py::test_lists_files]"
    plan.write_text(PLAN.replace(listed, "[]"))
    assert messages(phase(project, "check", "--plans", "1")[1]) == [uncovered, (
        "plan frontmatter: turns_green does not list tests/acceptance/p01_scan/test_scan.py::test_lists_files, "
        "which its tasks claim")]
    plan.write_text(PLAN.replace(listed, "\n  - test_scan.py::test_lists_files   # the bare file name"))
    assert messages(phase(project, "check", "--plans", "1")[1]) == [uncovered], "one test, written two ways"
    plan.write_text(PLAN.replace(listed, "[test_scan.py::test_lists_files[a, b]]"))
    assert messages(phase(project, "check", "--plans", "1")[1]) == [uncovered], "one test whatever its parameters"


def test_a_wave_wider_than_the_coder_pool_is_a_warning(project, monkeypatch):
    folder = planned(project).parent
    (folder / "01-02-PLAN.md").write_text(plan_text("02", files="`src/widget/dupes.py`"))
    coders(project, '[roles]\ncoders = ["codex"]\n\n[parallel]\nmax_tracks = 1\n')
    monkeypatch.setenv("PATH", str(stand_ins(project, ["codex"])))
    code, env = phase(project, "check", "--plans", "1")
    assert code == 0 and [w["message"] for w in env["data"]["warnings"]] == [
        "wave 1 has 2 plans that can start at once (01-01, 01-02); the coder pool here runs 1"], env
    assert "- warning: .planning/phases/01-scan/01-01-PLAN.md:0 [plans] wave 1 has 2 plans" in tool(project, "check", "--plans", "1")[1]

    (folder / "01-02-PLAN.md").write_text(plan_text("02", files="`src/widget/dupes.py`", depends_on="[01-01]"))
    assert phase(project, "check", "--plans", "1")[1]["data"]["warnings"] == [], "one of the two waits for the other"
    (folder / "01-02-PLAN.md").write_text(plan_text("02", files="`src/widget/dupes.py`"))
    stand_ins(project, [])
    assert phase(project, "check", "--plans", "1")[1]["data"]["warnings"] == [], "no coder here: nothing to compare with"


def test_a_change_outside_the_plans_is_named(project):
    plan = planned(project)
    commit(project)
    subprocess.run(["git", "checkout", "-qb", "phase/01-scan"], cwd=project, check=True)
    for folder in ("tests/unit", "tests/acceptance/p01_scan", "tests/acceptance/p02_dupes", "docs"):
        (project / folder).mkdir(parents=True, exist_ok=True)
    for name in ("src/widget/scan.py", "src/widget/extra.py", "src/widget/extra.py.bak", "tests/unit/test_scan.py",
                 "tests/acceptance/p01_scan/test_scan.py", "tests/acceptance/p02_dupes/test_dupes.py", "docs/guide.md"):
        (project / name).write_text('"""New."""\n')
    code, env = phase(project, "check", "--scope", "1", "--base", "main")
    assert code == 0, "a file outside the plans is a warning, and the index built in this phase is not news"
    assert [w["file"] for w in env["data"]["warnings"]] == [
        "docs/guide.md", "src/widget/extra.py", "src/widget/extra.py.bak", "tests/acceptance/p02_dupes/test_dupes.py"], \
        "the phase's own acceptance tests and the declared files and folders are not named"
    assert "- warning: docs/guide.md:0 [scope]" in tool(project, "check", "--scope", "1", "--base", "main")[1]

    catalog(project, entry("fs.scan", "List the files of a folder", "src/widget/scan.py"))
    commit(project)
    subprocess.run(["git", "branch", "-f", "main"], cwd=project, check=True)
    catalog(project, entry("fs.extra", "Something nobody planned", "src/widget/extra.py"))
    code, env = phase(project, "check", "--scope", "1", "--base", "main")
    assert code == 1 and messages(env) == ["new component fs.extra is on no plan's new_component: line"]
    assert env["data"]["warnings"] == [], "docs/components is the index, and the rest is committed at the base"

    (project / "src/widget/more.py").write_text('"""More."""\n')
    (plan.parent / "01-01-SUMMARY.md").write_text(
        "# Summary\n\n## Deviations from plan\nsrc/widget/more.py is mentioned outside the table.\n\n"
        "| Deviation | Reason | Approved by |\n|---|---|---|\n"
        "| Added `src/widget/more.py.bak` | a backup | human |\n\n## Next\n")
    plan.write_text(PLAN.replace("new_component: fs.scan because", "new_component: fs.scan, fs.extra because"))
    code, env = phase(project, "check", "--scope", "1", "--base", "main")
    assert code == 0 and [w["file"] for w in env["data"]["warnings"]] == ["src/widget/more.py"], \
        "only a table row excuses a file, and only the file it names"
    summary = plan.parent / "01-01-SUMMARY.md"
    summary.write_text(summary.read_text().replace("more.py.bak", "more.py"))
    code, env = phase(project, "check", "--scope", "1", "--base", "main")
    assert code == 0 and env["data"]["warnings"] == []
    code, env = phase(project, "check", "--scope", "1", "--base", "no-such-branch")
    assert code == 1 and "cannot find what changed" in messages(env)[0]


def test_component_check_is_strict_only_on_request(project):
    index = "scripts/components_index.py"
    assert tool(project, "--check", script=index)[0] == 0
    code, out = tool(project, "--check", "--strict", script=index)
    assert code == 1 and "no component: src/widget/__init__.py" in out
    catalog = project / "docs/components/COMPONENTS.md"
    catalog.write_text(catalog.read_text() + "\n### core.package\n- does: Hold the package\n- verbs: package\n"
                       "- status: canonical\n- modules: src/widget/__init__.py\n")
    assert tool(project, "write", script=index)[0] == 0
    assert tool(project, "--check", "--strict", script=index)[0] == 0
    assert "component core.package" in tool(project, "search", "package", script=index)[1]


INDEX = "scripts/components_index.py"


def entry(name, does, modules, status="canonical"):
    return "\n### %s\n- does: %s\n- verbs: %s\n- status: %s\n- modules: %s\n" % (
        name, does, name.split(".")[1], status, modules)


def catalog(project, *entries):
    path = project / "docs/components/COMPONENTS.md"
    path.write_text(path.read_text() + "".join(entries))
    code, out = tool(project, "write", script=INDEX)
    assert code == 0, out


def test_draft_gives_a_stub_that_cannot_be_kept_as_it_is(project):
    (project / "src/widget/sizes.py").write_text(
        '"""Turn byte counts into text."""\nimport widget\n\n\ndef humanize(n):\n    """Format n."""\n')
    (project / "tests").mkdir()
    (project / "tests/test_sizes.py").write_text("")
    code, out = tool(project, "draft", script=INDEX)
    assert code == 0
    stub = out[out.index("### widget.sizes"):]
    assert "- does: TODO Turn byte counts into text." in stub and "- tests: tests/test_sizes.py" in stub
    assert "symbols: humanize(n)" in stub and "imports: src/widget/__init__.py" in stub
    path = project / "docs/components/COMPONENTS.md"
    before = path.read_text()
    path.write_text(before + "\n" + stub)
    code, out = tool(project, "write", script=INDEX)
    assert code == 1 and "widget.sizes: does is still a draft (TODO)" in out
    path.write_text(before)
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/"))
    assert "0 module(s)" in tool(project, "draft", script=INDEX)[1]


def test_changed_names_what_a_change_left_out_of_the_index(project):
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n\n\ndef humanize(n):\n    """Format n."""\n')
    catalog(project, entry("core.package", "Hold the package", "src/widget/__init__.py"),
            entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    commit(project)
    code, out = tool(project, "changed", "--base", "main", script=INDEX)
    assert code == 0 and "0 to fix, 0 warning(s), 0 to reread" in out

    (project / "src/widget/export.py").write_text('"""Export."""\n')
    with (project / "src/widget/sizes.py").open("a") as stream:
        stream.write('\n\ndef parse(text):\n    """Read a size."""\n')
    code, out = tool(project, "changed", "--base", "main", script=INDEX)
    assert code == 1
    assert "fail: stale or missing: docs/components/modules/_root.md" in out
    assert "fail: no component: src/widget/export.py" in out
    assert "reread: core.sizes (entry not edited): src/widget/sizes.py" in out
    assert "reread: core.package" not in out

    path = project / "docs/components/COMPONENTS.md"
    path.write_text(path.read_text().replace("Format a byte count", "Format and parse a byte count"))
    catalog(project, entry("core.export", "Export a report", "src/widget/export.py"))
    code, out = tool(project, "changed", "--base", "main", script=INDEX)
    assert code == 0 and "reread:" not in out and "0 to fix" in out


def test_changed_warns_about_a_new_caller_of_a_retired_component(project):
    for name, body in (("old", '"""Old."""\n'), ("cli", '"""Cli."""\nfrom widget import old\n'),
                       ("report", '"""Report."""\n')):
        (project / "src/widget" / (name + ".py")).write_text(body)
    catalog(project, entry("core.package", "Hold the package", "src/widget/__init__.py"),
            entry("core.old", "The old way", "src/widget/old.py", status="deprecated"),
            entry("core.cli", "Run commands", "src/widget/cli.py"),
            entry("core.report", "Build a report", "src/widget/report.py"))
    commit(project)
    (project / "src/widget/report.py").write_text('"""Report."""\nfrom widget.old import x\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    code, out = tool(project, "changed", "--base", "main", script=INDEX)
    assert code == 0, out
    assert "warn: new caller of core.old (deprecated): core.report: src/widget/report.py -> src/widget/old.py" in out
    assert "core.cli:" not in out, "a caller that was already there is not new"
    assert tool(project, "changed", "--base", "main", "--strict", script=INDEX)[0] == 1


def facts(project, *args):
    code, out = tool(project, "facts", *args, script=INDEX)
    assert code == 0, out
    return json.loads(out)


def test_facts_lists_components_edges_and_layers(project):
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    (project / "src/widget/cli.py").write_text('"""Cli."""\nfrom widget import sizes\n')
    (project / "tests").mkdir()
    (project / "tests/test_sizes.py").write_text("")
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py") + "- tests: tests/test_sizes.py\n",
            entry("cli.run", "Run commands", "src/widget/cli.py", status="experimental"),
            "\n### subsystem.report\n- does: Print sizes\n- verbs: report\n- status: canonical\n"
            "- components: cli.run, core.sizes\n")
    layers = project / "docs/components/layers.toml"
    layers.write_text('[rank]\ncore = 0\ncli = 1\n\n[[forbid]]\nfrom = "core"\nto = "cli"\n')
    found = facts(project)
    rows = found["facts"]
    assert found["format"] == "devtools-facts/1"
    assert rows["component_is_listed"] == [{"component": "cli.run"}, {"component": "core.sizes"}]
    assert {"component": "cli.run", "status": "experimental"} in rows["component_has_status"]
    assert {"component": "core.sizes", "area": "core"} in rows["component_in_area"]
    assert rows["component_uses"] == [{"caller": "cli.run", "callee": "core.sizes"}]
    assert rows["component_uses_in_cycle"] == []
    assert rows["component_has_test"] == [{"component": "core.sizes", "path": "tests/test_sizes.py"}]
    assert {"subsystem": "subsystem.report", "component": "cli.run"} in rows["subsystem_has_member"]
    assert rows["area_has_rank"] == [{"area": "cli", "rank": 1}, {"area": "core", "rank": 0}]
    assert rows["area_must_not_use"] == [{"source": "core", "target": "cli"}]
    assert set(found["types"]["facts"]) == set(rows), "every fact type is described"
    assert found["types"]["facts"]["component_uses"]["roles"] == [["caller", "component"], ["callee", "component"]]
    assert found["evidence"]["component_uses"] == [
        {"caller": "cli.run", "callee": "core.sizes", "imports": [["src/widget/cli.py", "src/widget/sizes.py"]]}]
    assert "src/widget" not in json.dumps(rows), "module paths stay out of the facts"

    out_file = project.parent / "facts.json"
    code, out = tool(project, "facts", "--out", str(out_file), script=INDEX)
    assert code == 0 and out == "" and json.loads(out_file.read_text()) == found

    layers.write_text('[rank]\ncore = 0\nweb = "high"\n\n[[forbid]]\nfrom = "core"\n')
    code, out = tool(project, "facts", script=INDEX)
    assert code == 1 and "layers.toml" in out and "whole number" in out and "from =" in out
    layers.write_text('[rank]\nweb = 2\n')
    code, out = tool(project, "facts", script=INDEX)
    assert code == 1 and "no component is in area web" in out


def test_facts_at_base_leaves_out_what_the_change_added(project):
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    (project / "src/widget/cli.py").write_text('"""Cli."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"),
            entry("cli.run", "Run commands", "src/widget/cli.py"))
    commit(project)
    (project / "src/widget/cli.py").write_text('"""Cli."""\nfrom widget import sizes\n')
    (project / "src/widget/export.py").write_text('"""Export."""\nfrom widget import sizes\n')
    catalog(project, entry("core.export", "Export a report", "src/widget/export.py"))
    (project / "docs/components/layers.toml").write_text('[[forbid]]\nfrom = "cli"\nto = "core"\n')

    head, base = facts(project), facts(project, "--base", "main")
    assert {"component": "core.export"} in head["facts"]["component_is_listed"]
    assert head["facts"]["component_uses"] == [{"caller": "cli.run", "callee": "core.sizes"},
                                               {"caller": "core.export", "callee": "core.sizes"}]
    assert base["facts"]["component_is_listed"] == [{"component": "cli.run"}, {"component": "core.sizes"}]
    assert base["facts"]["component_uses"] == []
    assert base["facts"]["area_must_not_use"] == head["facts"]["area_must_not_use"] != [], \
        "the layers are today's at both revisions"
    assert base["revision"] == head["revision"] != "", "nothing is committed since the base"


def test_facts_marks_every_edge_inside_a_cycle(project):
    for name, target in (("a", "b"), ("b", "c"), ("c", "a"), ("d", "a")):
        (project / "src/widget" / (name + ".py")).write_text('"""%s."""\nfrom widget import %s\n' % (name, target))
    (project / "src/widget/sub").mkdir()
    (project / "src/widget/sub/__init__.py").write_text('"""Re-exports."""\nfrom widget import c, b\n')
    catalog(project, *(entry("loop." + name, "Part " + name, "src/widget/%s.py" % name) for name in "bcd"),
            entry("loop.a", "Part a", "src/widget/a.py, src/widget/sub/"))
    found = facts(project)
    assert found["facts"]["component_uses_in_cycle"] == [
        {"caller": "loop.a", "callee": "loop.b"}, {"caller": "loop.b", "callee": "loop.c"},
        {"caller": "loop.c", "callee": "loop.a"}]
    uses = found["facts"]["component_uses"]
    assert len(uses) == 5 and {"caller": "loop.a", "callee": "loop.c"} in uses, \
        "an import only a package __init__ makes is a use, and is not part of the loop"
    assert next(row["imports"] for row in found["evidence"]["component_uses"]
                if (row["caller"], row["callee"]) == ("loop.a", "loop.b")) == [
        ["src/widget/a.py", "src/widget/b.py"], ["src/widget/sub/__init__.py", "src/widget/b.py"]], \
        "the import a package __init__ makes comes last"
    assert found["evidence"]["cycle_groups"] == [["loop.a", "loop.b", "loop.c"]]
    out = tool(project, "review", script=INDEX)[1]
    assert "## Loops of imports through three or more components (1)" in out
    assert "3 components: loop.a, loop.b, loop.c" in out


RULES = ".claude/skills/components/scripts/rules_check.py"
RULES_SETTINGS = ".claude/skills/components/scripts/rules_check.settings.json"


def layered(project, cli_imports_sizes=True):
    """Two components in two areas, the starter rules, and core forbidden to cli."""
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    (project / "src/widget/cli.py").write_text('"""Cli."""\n' + ("from widget import sizes\n" * cli_imports_sizes))
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"),
            entry("cli.run", "Run commands", "src/widget/cli.py"))
    code, out = tool(project, "init", script=RULES)
    assert code == 0 and "wrote docs/components/rules.json" in out and "wrote docs/components/layers.toml" in out
    (project / "docs/components/layers.toml").write_text('[[forbid]]\nfrom = "cli"\nto = "core"\n')


def fake_gnd(project, report=None, exit_code=0, stderr=""):
    """A stand-in for gnd: it keeps the model and the facts it is given and prints the report prepared for it."""
    folder = project.parent / "fake-gnd"
    folder.mkdir(exist_ok=True)
    script = folder / "gnd"
    script.write_text(
        "#!%s\nimport shutil, sys\nfrom pathlib import Path\n"
        "here = Path(__file__).parent\n"
        "shutil.copy(sys.argv[2], here / 'model.json'); shutil.copy(sys.argv[3], here / 'head.facts.json')\n"
        "(here / 'argv.txt').write_text(' '.join(sys.argv[1:]))\n"
        "sys.stderr.write((here / 'stderr.txt').read_text())\n"
        "print((here / 'report.json').read_text())\n"
        "sys.exit(int((here / 'exit.txt').read_text()))\n" % sys.executable)
    script.chmod(0o755)
    (folder / "report.json").write_text(report if isinstance(report, str) else json.dumps(report or gnd_report()))
    (folder / "exit.txt").write_text(str(exit_code))
    (folder / "stderr.txt").write_text(stderr)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": str(script)}))
    return folder


STARTER_IDS = ["no_forbidden_area_use", "no_use_of_a_higher_rank", "no_import_inside_a_loop",
               "canonical_component_has_a_test", "private_module_stays_in_its_component"]
PLAN_RULE = "plan_names_the_components_it_touches"  # the one starter rule about plans: only `check --phase` judges it


def gnd_report(*verdicts, exit_code=0, version=15, rules=STARTER_IDS, baseline=None, **more):
    """A version-15 report with a verdict for each rule: the ones given, and a pass for the rest."""
    given = {v["address"] for v in verdicts}
    rest = [verdict(name, "pass") for name in rules if "constraint:" + name not in given]
    return {"schema_version": version, "exit_code": exit_code, "outcome": "accepted", "issues": [],
            "verdicts": list(verdicts) + rest, "baseline": baseline, **more}


def verdict(name, state, *offending, standing=(), reason=None):
    """A verdict on the rule `name`; `standing` lists the offending rows that were broken at the base too."""
    marks = ["standing" if row in standing else "new" for row in offending] if standing else None
    return {"address": "constraint:" + name, "addressing": "declared-id", "constraint_type": "guarded",
            "modality": "alethic", "verdict": state, "message": "as gnd words it", "remedy": None,
            "offending_facts": list(offending), "reason_code": reason,
            "novelty": ("standing" if marks and all(m == "standing" for m in marks) else "new") if marks else None,
            "row_novelty": marks}


USE = {"$a": "cli.run", "$b": "core.sizes", "$from": "cli", "$to": "core"}
OTHER = {"$a": "cli.old", "$b": "core.sizes", "$from": "cli", "$to": "core"}


def test_rules_init_never_overwrites(project):
    layered(project)
    path = project / "docs/components/rules.json"
    starter = path.read_text()
    assert [rule["id"] for rule in json.loads(starter)["rules"]] == STARTER_IDS + [PLAN_RULE]
    path.write_text('{"rules": []}\n')
    code, out = tool(project, "init", script=RULES)
    assert code == 0 and "docs/components/rules.json exists; left as it is" in out
    assert path.read_text() == '{"rules": []}\n' and "from = \"cli\"" in (project / "docs/components/layers.toml").read_text()
    code, out = tool(project, "init", "--print", script=RULES)
    assert code == 0 and starter in out and path.read_text() == '{"rules": []}\n'

    settings = project / "scripts/components_index.settings.json"
    settings.write_text(json.dumps(dict(json.loads(settings.read_text()), docs_dir="docs/index")))
    code, out = tool(project, "init", script=RULES)
    assert code == 0 and "wrote docs/index/rules.json" in out and "wrote docs/index/layers.toml" in out, \
        "the rules and the layers go where the index script reads the layers"


def test_rules_skips_without_gnd(project):
    layered(project)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": "no-such-gnd-here"}))
    code, out = tool(project, "check", script=RULES)
    assert code == 0 and out.startswith("skip: gnd not found")
    assert tool(project, "check", "--require", script=RULES)[0] == 1


def test_rules_names_rule_id_and_import_evidence(project):
    layered(project)
    seen = fake_gnd(project, gnd_report(verdict("no_forbidden_area_use", "fail", USE),
                                        verdict("no_use_of_a_higher_rank", "vacuous"),
                                        verdict("canonical_component_has_a_test", "warning", {"$a": "cli.run"}),
                                        exit_code=1))
    code, out = tool(project, "check", script=RULES)
    assert code == 1, out
    assert ("fail: no_forbidden_area_use: a=cli.run b=core.sizes from=cli to=core (src/widget/cli.py -> src/widget/sizes.py)\n"
            "  remedy: This area must not use that one (a [[forbid]] pair in layers.toml): move the import, "
            "or the module to the component it belongs to\n") in out
    assert "warn: canonical_component_has_a_test: a=cli.run\n  remedy: A canonical component lists no test" in out
    assert "rules: 5 rule(s); 1 to fix, 1 warning(s)" in out

    model = json.loads((seen / "model.json").read_text())
    facts_seen = json.loads((seen / "head.facts.json").read_text())
    argv = (seen / "argv.txt").read_text()
    assert argv.startswith("check ") and "--rule-ids --allow-vacuous --format json" in argv and "--baseline" not in argv
    assert [c["id"] for c in model["constraints"]] == STARTER_IDS
    assert all("level" not in c and c["remedy"] for c in model["constraints"])
    assert [c["modality"] for c in model["constraints"]] == ["alethic", "alethic", "deontic", "deontic", "deontic"]
    assert {f["id"] for f in model["fact_types"]} == set(facts_seen["facts"]) == set(facts_seen["population"]["covers"])
    assert facts_seen["population"]["source"] == "tool-output"
    assert facts_seen["population"]["producer"].startswith("components_index.py facts @ ")
    assert facts_seen["facts"]["area_must_not_use"] == [{"source": "cli", "target": "core"}]

    code, out = tool(project, "check", "--format", "json", script=RULES)
    rows = json.loads(out)["rows"]
    assert code == 1 and rows[0]["rule"] == "no_forbidden_area_use" and rows[0]["binding"] == USE and rows[0]["new"]


def test_rules_reports_only_violations_new_since_base(project):
    layered(project, cli_imports_sizes=False)
    commit(project)
    (project / "src/widget/cli.py").write_text('"""Cli."""\nfrom widget import sizes\n')
    base = {"population": "base.pop.json", "new": 1, "standing": 1, "resolved": 0, "positional_keyed": 0, "undecided": 0}
    seen = fake_gnd(project, gnd_report(verdict("no_forbidden_area_use", "fail", OTHER, USE, standing=[OTHER]),
                                        exit_code=1, baseline=base))
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 1, out
    assert "--baseline" in (seen / "argv.txt").read_text()
    assert "a=cli.run b=core.sizes" in out and out.count("fail:") == 1, "what was broken at the base is not news"
    assert "(src/widget/cli.py -> src/widget/sizes.py) [new import]" in out
    assert "rules against main (" in out and "1 to fix, 0 warning(s), 1 standing" in out
    assert json.loads(tool(project, "check", "--base", "main", "--format", "json", script=RULES)[1])["baseline"] == base
    fake_gnd(project, gnd_report(verdict("no_forbidden_area_use", "fail", OTHER, USE), exit_code=1))
    code, out = tool(project, "check", script=RULES)
    assert code == 1 and out.count("fail:") == 2 and "[new import]" not in out and "standing" not in out

    fake_gnd(project, gnd_report(verdict("no_import_inside_a_loop", "warning",
                                         *({"$a": "c.x%d" % n} for n in range(13)), standing=[{"$a": "none"}]),
                                 baseline=base))
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0 and out.count("warn:") == 10 and "… +3 more for no_import_inside_a_loop" in out
    assert tool(project, "check", "--base", "main", "--strict", script=RULES)[0] == 1


def test_rules_vacuous_is_not_a_failure(project):
    layered(project)
    fake_gnd(project, gnd_report(*(verdict(name, "vacuous") for name in STARTER_IDS), allow_vacuous=True))
    code, out = tool(project, "check", script=RULES)
    assert code == 0 and "0 to fix, 0 warning(s)" in out

    fake_gnd(project, gnd_report(verdict("no_use_of_a_higher_rank", "unchecked", reason="values-not-comparable"), exit_code=4))
    code, out = tool(project, "check", script=RULES)
    assert code == 1 and "fail: no_use_of_a_higher_rank\n  remedy: gnd could not decide this rule (values-not-comparable)" in out

    fake_gnd(project, {"schema_version": 15, "exit_code": 3, "outcome": "ill_formed",
                       "issues": [{"path": "$.constraints[0]", "message": "unknown fact type"}]}, exit_code=3)
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "gnd did not judge the rules (ill_formed, exit 3): $.constraints[0]: unknown fact type" in out
    fake_gnd(project, {"schema_version": 15, "exit_code": 70, "outcome": "internal_error", "issues": [],
                       "verdicts": [], "error": "boom"}, exit_code=70)
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "gnd did not judge the rules (internal_error, exit 70): boom" in out, \
        "a report with no verdicts is not a pass"
    fake_gnd(project, gnd_report(rules=STARTER_IDS[:3]))
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "gnd gave no verdict for: canonical_component_has_a_test" in out
    fake_gnd(project, gnd_report(verdict("no_such_rule", "fail", USE)))
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "gnd wrote a report this script cannot read" in out
    fake_gnd(project, gnd_report(version=7))
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "report version 7" in out
    fake_gnd(project, "Traceback: gnd broke", exit_code=70)
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "gnd check failed" in out
    fake_gnd(project, "", exit_code=64, stderr="usage: gnd check ...\ngnd check: error: unrecognized arguments: --rule-ids\n")
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "this GND has no --rule-ids: install get-nick-done 0.2.0 or newer" in out

    (project / "docs/components/rules.json").write_text('{"rules": [{"id": "Bad Id"}, {"id": "ok", "level": "maybe"}]}')
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "rule 1: needs an \"id\"" in out and "ok: \"level\" is must or should" in out


def test_rules_says_when_the_rules_file_changed(project):
    layered(project)
    commit(project)
    fake_gnd(project, gnd_report(baseline={"new": 0, "standing": 0}))
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0 and "reread:" not in out
    path = project / "docs/components/rules.json"
    path.write_text(path.read_text().replace('"must"', '"should"'))
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0 and "reread: rules changed in this change: docs/components/rules.json" in out


REAL_GND = os.environ.get("GND_COMMAND") or shutil.which("gnd")


@pytest.mark.skipif(not REAL_GND, reason="GND is not installed (put gnd on PATH or set GND_COMMAND)")
def test_rules_with_real_gnd(project):
    layered(project, cli_imports_sizes=False)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": REAL_GND}))
    commit(project)
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0 and "0 to fix, 0 warning(s), 2 standing" in out, out  # neither component lists a test
    (project / "src/widget/cli.py").write_text('"""Cli."""\nfrom widget import sizes\n')
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 1, out
    assert "fail: no_forbidden_area_use: a=cli.run b=core.sizes from=cli to=core" in out and "\n  remedy: This area" in out
    assert "(src/widget/cli.py -> src/widget/sizes.py) [new import]" in out and "1 to fix, 0 warning(s), 2 standing" in out
    (project / "docs/components/layers.toml").write_text("[rank]\ncli = 0\ncore = 1\n")
    code, out = tool(project, "check", script=RULES)
    assert code == 1 and "fail: no_use_of_a_higher_rank:" in out and "rank=0 used=1" in out, out


def test_plan_facts_say_what_the_plans_say(project):
    folder = planned(project).parent
    (folder / "01-01-PLAN.md").write_text(PLAN.replace("turns_green: [", "golden_impact: none   # nothing regenerated\nturns_green: [")
                                          .replace("new_component:", "reuse: core.sizes, cli.run (adapt: one more command)\nnew_component:")
                                          .replace("- **files:**", "- **read_first:** `src/widget/cli.py`\n- **files:**"))
    (folder / "01-02-PLAN.md").write_text(plan_text("02", wave=2, depends_on="[01]", files="`src/widget/*.py`"))
    (folder / "01-03-PLAN.md").write_text(plan_text("03", wave=3, depends_on="[01-02]", files="`docs/guide.md`"))
    code, env = phase(project, "facts", "--phase", "1")
    assert code == 0 and env["data"]["format"] == "devtools-facts/1" and env["data"]["phase"] == "01", env
    rows = env["data"]["facts"]
    assert rows["plan_in_wave"] == [{"plan": "01-01", "wave": 1}, {"plan": "01-02", "wave": 2}, {"plan": "01-03", "wave": 3}]
    assert rows["plan_depends_on"] == [{"plan": "01-02", "earlier": "01-01"}, {"plan": "01-03", "earlier": "01-02"}]
    assert {"plan": "01-03", "earlier": "01-01"} in rows["plan_runs_after"] and len(rows["plan_runs_after"]) == 3
    assert {"plan": "01-01", "requirement": "REQ-CORE-001"} in rows["plan_names_requirement"]
    assert [r["component"] for r in rows["plan_reuses_component"]] == ["cli.run", "core.sizes"]
    assert {"plan": "01-01", "component": "fs.scan"} in rows["plan_adds_component"]
    assert rows["plan_declares"] == [{"plan": "01-01", "key": "golden_impact", "value": "none"}]
    assert {"task": "01-02-T1", "plan": "01-02"} in rows["task_in_plan"]
    assert {"task": "01-01-T1", "type": "auto"} in rows["task_has_type"]
    assert {"task": "01-01-T1", "test": "tests/acceptance/p01_scan/test_scan.py::test_lists_files"} in rows["task_turns_green"]
    assert [r["path"] for r in rows["task_names_file"] if r["task"] == "01-01-T1"] == ["src/widget/scan.py", "tests/unit/"]
    assert {"task": "01-02-T1", "path": "src/widget/*.py"} in rows["task_names_file"], "an entry is passed on as written"
    assert rows["task_reads_first"] == [{"task": "01-01-T1", "path": "src/widget/cli.py"}]
    assert {"test": "tests/acceptance/p01_scan/test_scan.py::test_skips_hidden", "kind": "contract"} in rows["test_is_in_contract"]
    assert {"test": "tests/acceptance/p01_scan/test_scan.py::test_sizes[kb, mb]", "kind": "guard"} in rows["test_is_in_contract"]
    assert set(env["data"]["types"]["facts"]) == set(rows), "every fact type is described"
    assert env["data"]["evidence"]["plans"]["01-02"] == ".planning/phases/01-scan/01-02-PLAN.md"

    code, env = phase(project, "facts", "--phase", "2")
    assert code == 1 and env["error"]["code"] == "NO_PLANS"


def test_facts_can_list_the_files_of_each_component(project):
    layered(project)
    (project / "src/widget/extra").mkdir()
    (project / "src/widget/extra/more.py").write_text('"""More."""\n')
    catalog(project, entry("core.extra", "Extra things", "src/widget/extra/"))
    assert "component_has_module" not in facts(project)["facts"], "only on request: a file path makes a renamed file a new fact"
    found = facts(project, "--modules")
    assert found["facts"]["component_has_module"] == [
        {"component": "cli.run", "path": "src/widget/cli.py"},
        {"component": "core.extra", "path": "src/widget/extra/more.py"},
        {"component": "core.sizes", "path": "src/widget/sizes.py"}]
    assert found["types"]["facts"]["component_has_module"]["roles"] == [["component", "component"], ["path", "path"]]
    assert found["facts"]["module_imports"] == [{"importer": "src/widget/cli.py", "imported": "src/widget/sizes.py"}]
    assert found["facts"]["module_is_private"] == []

    commit(project)
    (project / "src/widget/_impl.py").write_text('"""Private."""\n')
    (project / "src/widget/extra/_inner").mkdir()
    (project / "src/widget/extra/_inner/deep.py").write_text('"""In a private folder."""\nfrom widget import _impl\n')
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\nfrom widget import _impl\n')
    path = project / "docs/components/COMPONENTS.md"
    path.write_text(path.read_text().replace("- modules: src/widget/sizes.py", "- modules: src/widget/sizes.py, src/widget/_impl.py"))
    rows = facts(project, "--modules")["facts"]
    assert rows["module_is_private"] == [{"path": "src/widget/_impl.py"}, {"path": "src/widget/extra/_inner/deep.py"}], \
        "by the file's name or a folder's; __init__.py is not private"
    assert {"importer": "src/widget/extra/_inner/deep.py", "imported": "src/widget/_impl.py"} in rows["module_imports"]
    assert {"component": "core.sizes", "path": "src/widget/_impl.py"} in rows["component_has_module"]
    before = facts(project, "--modules", "--base", "main")["facts"]
    assert before["module_is_private"] == [] and "_impl" not in json.dumps(before), "the files as they were at the base"
    assert before["module_imports"] == [{"importer": "src/widget/cli.py", "imported": "src/widget/sizes.py"}]


def component_plan(reuse=""):
    """PLAN with a task that changes sizes.py, reads cli.py first and names a file that does not exist yet;
    `reuse` is the reuse: line of its Reuse section."""
    return (PLAN.replace("new_component:", "reuse: %s\nnew_component:" % reuse if reuse else "new_component:")
            .replace("- **files:** `src/widget/scan.py`, `tests/unit/`",
                     "- **read_first:** `src/widget/cli.py`\n- **files:** `src/widget/siz*.py`, `src/widget/new.py`"))


def planned_over_components(project):
    """Phase 1 with the plan of `component_plan`, over the two components of `layered` and a subsystem of both."""
    plan = planned(project)
    layered(project)
    catalog(project, "\n### subsystem.report\n- does: Print sizes\n- verbs: report\n- status: canonical\n"
                     "- components: cli.run, core.sizes\n")
    plan.write_text(component_plan())
    return plan


def test_rules_ask_for_the_files_only_when_a_rule_names_one(project):
    layered(project)
    commit(project)
    seen = fake_gnd(project)
    assert tool(project, "check", "--base", "main", script=RULES)[0] == 0
    model = json.loads((seen / "model.json").read_text())
    rows = json.loads((seen / "head.facts.json").read_text())["facts"]
    assert {"module_imports", "module_is_private", "component_has_module"} <= {f["id"] for f in model["fact_types"]}
    assert rows["module_imports"] == [{"importer": "src/widget/cli.py", "imported": "src/widget/sizes.py"}]

    rules = project / "docs/components/rules.json"
    kept = [rule for rule in json.loads(rules.read_text())["rules"] if rule["id"] != "private_module_stays_in_its_component"]
    rules.write_text(json.dumps({"rules": kept}))
    fake_gnd(project, gnd_report(rules=STARTER_IDS[:4]))
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0 and "rules against main" in out and "4 rule(s)" in out, out
    rows = json.loads((seen / "head.facts.json").read_text())["facts"]
    assert "module_imports" not in rows and "src/widget" not in json.dumps(rows), "no rule names a file: no file is a fact"


@pytest.mark.skipif(not REAL_GND, reason="GND is not installed (put gnd on PATH or set GND_COMMAND)")
def test_a_private_file_is_used_inside_its_component_with_real_gnd(project):
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\nfrom widget import _impl\n')
    (project / "src/widget/_impl.py").write_text('"""Private."""\n')
    (project / "src/widget/cli.py").write_text('"""Cli."""\n')
    (project / "src/widget/old.py").write_text('"""Old."""\nfrom widget import _impl\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py, src/widget/_impl.py"),
            entry("cli.run", "Run commands", "src/widget/cli.py"), entry("cli.old", "Old commands", "src/widget/old.py"))
    assert tool(project, "init", script=RULES)[0] == 0
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": REAL_GND}))
    commit(project)
    code, out = tool(project, "check", "--base", "main", "--strict", script=RULES)
    assert "private_module_stays_in_its_component" not in out, out  # sizes.py is in the component; old.py was there before
    (project / "src/widget/cli.py").write_text('"""Cli."""\nfrom widget import _impl\n')
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0 and ("warn: private_module_stays_in_its_component: a=src/widget/cli.py b=src/widget/_impl.py "
                          "c=core.sizes\n  remedy: A file imports a private file") in out, out
    assert out.count("warn: private_module_stays_in_its_component") == 1, "the import that was already there is standing"
    code, out = tool(project, "check", script=RULES)
    assert out.count("warn: private_module_stays_in_its_component") == 2, "with no base, both are listed"


def test_rules_about_plans_are_judged_for_a_phase_only(project):
    plan = planned_over_components(project)
    broken = {"$task": "01-01-T1", "$component": "core.sizes", "$plan": "01-01"}
    seen = fake_gnd(project)
    code, out = tool(project, "check", script=RULES)
    assert code == 0 and "rules: 5 rule(s); 0 to fix" in out, out
    assert [c["id"] for c in json.loads((seen / "model.json").read_text())["constraints"]] == STARTER_IDS

    seen = fake_gnd(project, gnd_report(verdict(PLAN_RULE, "warning", broken), rules=[PLAN_RULE]))
    code, out = tool(project, "check", "--phase", "1", script=RULES)
    assert code == 0 and out == (
        "warn: plan_names_the_components_it_touches: task=01-01-T1 component=core.sizes plan=01-01 "
        "(.planning/phases/01-scan/01-01-PLAN.md)\n"
        "  remedy: A task changes a file of a component the plan does not name: add the component to the "
        "plan's reuse: line, or to new_component: if the plan creates it\n"
        "plan rules for phase 01: 1 rule(s); 0 to fix, 1 warning(s)\n"), out
    assert tool(project, "check", "--phase", "1", "--strict", script=RULES)[0] == 1
    model = json.loads((seen / "model.json").read_text())
    rows = json.loads((seen / "head.facts.json").read_text())["facts"]
    assert [c["id"] for c in model["constraints"]] == [PLAN_RULE] and "about" not in model["constraints"][0]
    assert "--baseline" not in (seen / "argv.txt").read_text()
    assert {f["id"] for f in model["fact_types"]} == set(rows), "the component facts, the plan facts and the joined ones"
    assert rows["task_touches_component"] == [{"task": "01-01-T1", "component": "core.sizes"}], "a pattern names a file"
    assert rows["task_reads_component"] == [{"task": "01-01-T1", "component": "cli.run"}]
    assert rows["task_adds_file"] == [{"task": "01-01-T1", "path": "src/widget/new.py"}]
    assert rows["plan_names_component"] == [{"plan": "01-01", "component": "fs.scan"}]
    assert {"component": "core.sizes", "path": "src/widget/sizes.py"} in rows["component_has_module"]

    plan.write_text(component_plan(reuse="subsystem.report"))
    fake_gnd(project, gnd_report(rules=[PLAN_RULE]))
    code, out = tool(project, "check", "--phase", "1", "--format", "json", script=RULES)
    assert code == 0 and json.loads(out) == {"rows": [], "summary": "plan rules for phase 01: 1 rule(s); 0 to fix, 0 warning(s)"}
    rows = json.loads((project.parent / "fake-gnd/head.facts.json").read_text())["facts"]
    assert {"plan": "01-01", "component": "core.sizes"} in rows["plan_names_component"], "a subsystem names its members"

    code, out = tool(project, "check", "--phase", "1", "--base", "main", script=RULES)
    assert code == 2 and "leave out --base" in out
    code, out = tool(project, "check", "--phase", "2", script=RULES)
    assert code == 2 and "rules_check: " in out and "phase 02 has no plan" in out
    rules = project / "docs/components/rules.json"
    rules.write_text(rules.read_text().replace('"about": "plans"', '"about": "plan"'))
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and 'plan_names_the_components_it_touches: "about" is components or plans' in out


def test_plan_rules_need_the_phase_tool_and_skip_without_gnd(project):
    planned_over_components(project)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": "no-such-gnd"}))
    code, out = tool(project, "check", "--phase", "1", script=RULES)
    assert code == 0 and out.startswith("skip: gnd not found"), out
    assert tool(project, "check", "--phase", "1", "--require", script=RULES)[0] == 1
    seen = fake_gnd(project)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": str(seen / "gnd"), "phase_script": "tools/phase_tool.py"}))
    code, out = tool(project, "check", "--phase", "1", script=RULES)
    assert code == 2 and "tools/phase_tool.py is missing (phase_script in rules_check.settings.json)" in out


@pytest.mark.skipif(not REAL_GND, reason="GND is not installed (put gnd on PATH or set GND_COMMAND)")
def test_plan_rules_with_real_gnd(project):
    plan = planned_over_components(project)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": REAL_GND}))
    code, out = tool(project, "check", "--phase", "1", script=RULES)
    assert code == 0, out
    assert "warn: plan_names_the_components_it_touches: task=01-01-T1 component=core.sizes plan=01-01" in out, out
    assert "plan rules for phase 01: 1 rule(s); 0 to fix, 1 warning(s)" in out
    plan.write_text(component_plan(reuse="core.sizes"))
    code, out = tool(project, "check", "--phase", "1", script=RULES)
    assert code == 0 and out == "plan rules for phase 01: 1 rule(s); 0 to fix, 0 warning(s)\n", out
    code, out = tool(project, "check", script=RULES)
    assert "rules: 5 rule(s)" in out, out


def test_review_lists_places_to_look(project):
    (project / "src/widget/sizes.py").write_text(
        '"""Sizes."""\nfrom widget import export\n\n\ndef humanize(n):\n    """Format n."""\n')
    (project / "src/widget/export.py").write_text(
        'from widget import sizes\n\n\ndef humanize(n):\n    """Call the other one."""\n\n\n'
        'def render(n):\n    """Render n."""\n')
    (project / "src/widget/loose.py").write_text('"""Loose."""\n\n\ndef render(n):\n    """Render n again."""\n')
    (project / "tests").mkdir()
    (project / "tests/test_sizes.py").write_text("from widget.sizes import humanize\n")
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"),
            entry("core.export", "Export a report", "src/widget/export.py"))
    commit(project)
    with (project / "src/widget/sizes.py").open("a") as stream:
        stream.write('\n\ndef parse(text):\n    """Read a size."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    code, out = tool(project, "review", script=INDEX)
    assert code == 0
    assert "core.sizes: 1 commit(s) to its modules since " in out and "when its does and verbs were last edited" in out
    assert "core.export: 1 commit" not in out
    assert ("core.export <-> core.sizes: core.export imports core.sizes in 1 place(s): "
            "src/widget/export.py -> src/widget/sizes.py; core.sizes imports core.export in 1 place(s)") in out
    assert "render (same signature): src/widget/export.py (core.export), src/widget/loose.py (no component)" in out
    assert "humanize" not in out, "a definition whose module imports the other one is a wrapper, not a copy"
    assert "core.sizes: tests/test_sizes.py" in out
    assert "## Modules with no docstring (the search cannot describe them) (1)\nsrc/widget/export.py" in out
    assert "## Modules with no component (2)" in out and "src/widget/loose.py" in out
    assert "## Retired components that are still called (0)" in out, "an empty group is printed with its count"
    assert out.rstrip().splitlines()[-1].startswith("review: ")

    catalog(project, entry("core.loose", "Loose ends", "src/widget/loose.py") + "- distinct_from: core.export\n")
    out = tool(project, "review", script=INDEX)[1]
    assert "render" not in out, "a pair recorded as separate on purpose is not a lead"
    area = tool(project, "review", "core.siz", script=INDEX)[1]
    assert "core.export <-> core.sizes" in area and "## Modules with no docstring (the search cannot describe them) (0)" in area
    assert area.rstrip().splitlines()[-1].startswith("review for core.siz: ")
    assert "component core.sizes [2/2: byte, size]:" in tool(project, "search", "--explain", "byte", "sizes", script=INDEX)[1]

    code, out = tool(project, "show", "core.sizes", script=INDEX)
    assert code == 0 and "## src/widget/sizes.py (" in out
    assert "imports: src/widget/export.py (core.export)" in out
    assert "imported from tests and scripts: 1 file(s): tests/test_sizes.py" in out

    path = project / "docs/components/COMPONENTS.md"
    path.write_text(path.read_text().replace("- does: Loose ends", "- does: Loose ends\n- does: And more"))
    code, out = tool(project, "write", script=INDEX)
    assert code == 1 and "core.loose: does appears twice" in out


def test_changed_does_not_call_a_regrouped_import_new(project):
    for name, body in (("old", '"""Old."""\n'), ("report", '"""Report."""\nfrom widget import old\n'),
                       ("rows", '"""Rows."""\nfrom widget import old\n')):
        (project / "src/widget" / (name + ".py")).write_text(body)
    catalog(project, entry("core.package", "Hold the package", "src/widget/__init__.py"),
            entry("core.old", "The old way", "src/widget/old.py", status="deprecated"),
            entry("core.report", "Build a report", "src/widget/report.py, src/widget/rows.py"))
    commit(project)
    path = project / "docs/components/COMPONENTS.md"
    path.write_text(path.read_text().replace("src/widget/report.py, src/widget/rows.py", "src/widget/report.py"))
    catalog(project, entry("core.rows", "Build rows", "src/widget/rows.py"))
    code, out = tool(project, "changed", "--base", "main", "--strict", script=INDEX)
    assert code == 0 and "warn:" not in out, out

def test_the_baseline_cannot_take_a_new_module_in_exchange_for_an_old_one(project):
    for name in ("a", "b"):
        (project / "src/widget" / (name + ".py")).write_text('"""%s."""\n' % name)
    catalog(project, entry("core.package", "Hold the package", "src/widget/__init__.py"))
    code, out = tool(project, "stats", "--write-baseline", script=INDEX)
    assert code == 0 and (project / "docs/components/unassigned-baseline.txt").read_text().split() == [
        "src/widget/a.py", "src/widget/b.py"]
    (project / "src/widget/c.py").write_text('"""c."""\n')
    catalog(project, entry("core.a", "Do a", "src/widget/a.py"))
    code, out = tool(project, "stats", "--write-baseline", script=INDEX)
    assert code == 1 and "unassigned baseline cannot grow" in out and "src/widget/c.py" in out
    assert tool(project, "--check", "--strict", script=INDEX)[0] == 1
    code, out = tool(project, "--strict", script=INDEX)
    assert code == 2 and "--strict goes with --check" in out

    out = tool(project, "draft", "--only", "src/widget/c", script=INDEX)[1]
    assert "1 module(s)" in out and "### widget.c" in out and "widget.b" not in out
    assert "imported by (0): nothing in the package" in out
    out = tool(project, "list", script=INDEX)[1]
    assert "## core (2)" in out and "core.a: Do a" in out


def test_search_reads_a_file_again_only_when_it_changed(project):
    (project / "src/widget/scan.py").write_text('"""Walk a folder."""\ndef walk_folder(path):\n    """List files."""\n')
    catalog(project, entry("core.scan", "Walk a folder and list its files.", "src/widget/scan.py"))
    first = tool(project, "search", "walk", "folder", script=INDEX)
    assert "component core.scan" in first[1] and "module src/widget/scan.py" in first[1]
    assert list((project.parent / "cache/components-index").glob("*.json")), "the first search saves what it parsed"
    assert tool(project, "search", "walk", "folder", script=INDEX) == first
    assert tool(project, "search", "walk", "folder", "--no-cache", script=INDEX) == first
    # A changed file is read again: the new name is found, and the saved copy is not trusted.
    (project / "src/widget/scan.py").write_text('"""Walk a folder."""\ndef checksum_everything(path):\n    """Hash."""\n')
    assert "module src/widget/scan.py" in tool(project, "search", "checksum", "everything", script=INDEX)[1]
    # A damaged cache file only costs time.
    for saved in (project.parent / "cache/components-index").glob("*.json"):
        saved.write_text("not json")
    assert "module src/widget/scan.py" in tool(project, "search", "checksum", "everything", script=INDEX)[1]


def test_search_names_the_symbol_and_reads_the_whole_docstring(project):
    (project / "src/widget/graph.py").write_text(
        '"""Graph helpers.\n\nStrongly connected components live here.\n"""\n\n\n'
        'def ring_pairs(edges):\n    """Every genuine cycle among the edges.\n\n'
        "    Tarjan's SCC over the edge graph, with acyclic-prefix subtraction.\n"
        '    """\n\n\ndef count(edges):\n    """How many edges."""\n\n\n'
        'def _sccs(edges):\n    """Iterative Tarjan with lowlink values."""\n\n\n'
        'class _Stack:\n    """Node stack."""\n\n    def push(self, node):\n        """Push a node; its lowlink is set."""\n')
    catalog(project, entry("core.graph", "Find cycles in a graph.", "src/widget/graph.py"))
    # The pages list the public names only; `show` keeps the private ones on its "also defines" line.
    page = (project / "docs/components/modules/_root.md").read_text()
    assert "ring_pairs" in page and "_sccs" not in page and "_Stack" not in page
    shown = tool(project, "show", "core.graph", script=INDEX)[1]
    assert "  18: _sccs" not in shown and "also defines: _sccs, _Stack" in shown, shown
    # An exact function name names the symbol and its line under its module, and not the other symbol.
    out = tool(project, "search", "ring_pairs", script=INDEX)[1]
    assert ("module src/widget/graph.py: Graph helpers.\n"
            "  symbol widget.graph.ring_pairs (line 7): Every genuine cycle among the edges.\n") in out, out
    assert "widget.graph.count" not in out
    # A word from the third docstring line finds the function; the summary shown is still the first line.
    out = tool(project, "search", "--explain", "tarjan", script=INDEX)[1]
    assert "  symbol widget.graph.ring_pairs (line 7) [1/1: tarjan]: Every genuine cycle among the edges." in out, out
    assert "acyclic" not in out
    assert "  symbol widget.graph._sccs (line 18, private) [1/1: tarjan]: Iterative Tarjan with lowlink values." in out, out
    # A later line of the module docstring is searched too; a module hit with no matching symbol lists none.
    out = tool(project, "search", "strongly", "connected", script=INDEX)[1]
    assert "module src/widget/graph.py: Graph helpers.\nno component matched" in out, out
    # A private function, and a method of a private class, are searched too and marked as private.
    out = tool(project, "search", "lowlink", script=INDEX)[1]
    assert ("  symbol widget.graph._sccs (line 18, private): Iterative Tarjan with lowlink values.\n"
            "  symbol widget.graph._Stack.push (line 25, private): Push a node; its lowlink is set.\n") in out, out
    # The same with and without the cache.
    assert tool(project, "search", "tarjan", script=INDEX) == tool(project, "search", "tarjan", "--no-cache", script=INDEX)


def test_scope_check_ignores_the_supervisors_own_files(project):
    phase(project, "setup")
    commit(project)
    (project / "src/widget/new.py").write_text("X = 1\n")
    evidence = project / ".planning/phases/01-first-phase/01-EVIDENCE/briefs"
    evidence.mkdir(parents=True)
    (evidence / "brief.md").write_text("a\nb\nc\n")
    gate = ".claude/skills/process-phase/scripts/codex_gate.py"
    code, out = tool(project, "--allow", "src/widget/*", "--max-added", "2", script=gate)
    assert code == 1 and "outside allowlist" in out and "added 4 lines" in out
    code, out = tool(project, "--allow", "src/widget/*", "--ignore", ".planning/phases/*-EVIDENCE/*",
                     "--max-added", "2", script=gate)
    assert code == 0 and out.strip() == "ok 1 files, 1 added"


POOL = ".claude/skills/process-phase/scripts/coder_pool.py"
TEAM = """[roles]
coders = ["codex", "gemini"]

[parallel]
max_tracks = 3
max_sessions_per_account = 2

[coders.codex]
model = "big"
effort = "medium"
"""


def stand_ins(project, on_path):
    """A folder to use as PATH: git, and an empty stand-in for each named assistant."""
    bin_dir = project.parent / "bin"
    shutil.rmtree(bin_dir, ignore_errors=True)
    bin_dir.mkdir()
    for name, body in [(name, "") for name in on_path] + [("git", 'exec "%s" "$@"\n' % GIT)]:
        (bin_dir / name).write_text("#!/bin/sh\n" + body)
        (bin_dir / name).chmod(0o755)
    return bin_dir


def pool(project, on_path, *args, cwd=None):
    """Run the coder-pool command with nothing on PATH but git and an empty stand-in for each named assistant."""
    proc = subprocess.run([sys.executable, POOL, "show", *args], cwd=cwd or project, capture_output=True, text=True,
                          env={**os.environ, "PATH": str(stand_ins(project, on_path))})
    return proc.returncode, proc.stdout + proc.stderr


def coders(project, text, name=".devtools/coders.toml"):
    (project / name).parent.mkdir(exist_ok=True)
    (project / name).write_text(text)


def test_coder_pool_from_the_team_file_alone(project):
    coders(project, TEAM)
    code, out = pool(project, ["codex", "gemini", "claude"])
    assert code == 0 and out == (
        "coders:\n  codex/default: model=big effort=medium risk=any\n  gemini/default: model= effort= risk=any\n"
        "parallel:\n  max_tracks: 3\n  max_sessions_per_account: 2\n  capacity: 4\n  effective_tracks: 3\n")
    code, out = pool(project, ["codex", "claude"])
    assert code == 0 and "gemini/" not in out and "capacity: 2" in out and "effective_tracks: 2" in out
    assert "warning: coders: gemini not on PATH, dropped" in out


def test_a_developers_local_file_overrides_the_team_file(project):
    coders(project, TEAM)
    coders(project, '[roles]\ncoders = ["codex"]\n\n[parallel]\nmax_tracks = 12\n\n[coders.codex]\neffort = "high"\n'
           'stuck_model = "bigger"\naccounts = [\n  { name = "A" },\n  { name = "B", env = { CODEX_HOME = "/x/b" } },\n]\n',
           ".devtools/coders.local.toml")
    code, out = pool(project, ["codex", "gemini"], "--json")
    data = json.loads(out)
    assert code == 0 and data["warnings"] == [] and sorted(data["installed"]) == ["codex", "gemini"]
    assert [(e["tool"], e["account"], e["model"], e["effort"], e["risk"], e["env"]) for e in data["coders"]["pool"]] == [
        ("codex", "A", "big", "high", "any", {}), ("codex", "B", "big", "high", "any", {"CODEX_HOME": "/x/b"})]
    assert [e["stuck_model"] for e in data["coders"]["pool"]] == ["bigger", "bigger"]
    assert {key: value for key, value in data["coders"].items() if key != "pool"} == {
        "fallback": False, "max_tracks": 12, "max_sessions_per_account": 2, "capacity": 4, "effective_tracks": 4}
    assert "  codex/B: model=big effort=high risk=any stuck_model=bigger CODEX_HOME=/x/b\n" in pool(project, ["codex", "gemini"])[1]


def test_a_worktree_without_a_local_file_reads_the_main_checkouts(project):
    coders(project, '[roles]\ncoders = ["codex"]\n')
    commit(project)
    coders(project, '[roles]\ncoders = ["gemini"]\n', ".devtools/coders.local.toml")
    tree = project.parent / "track"
    subprocess.run(["git", "worktree", "add", "-q", str(tree), "-b", "track"], cwd=project, check=True)
    assert not (tree / ".devtools/coders.local.toml").exists()
    out = pool(project, ["codex", "gemini", "claude"], cwd=tree)[1]
    assert "gemini/default" in out and "codex/" not in out
    coders(tree, '[roles]\ncoders = ["claude"]\n', ".devtools/coders.local.toml")
    out = pool(project, ["codex", "gemini", "claude"], cwd=tree)[1]
    assert "claude/default" in out and "gemini/" not in out and "fallback" not in out


def test_with_no_configured_coder_on_path_the_pool_is_claude(project):
    coders(project, '[roles]\ncoders = ["codex", "other"]\n')
    code, out = pool(project, ["claude", "gemini"])
    assert code == 0 and out.startswith(
        "coders:\n  claude/default: model= effort= risk=any\n  (fallback: Claude Code coder)\nparallel:\n")
    assert "effective_tracks: 4" in out and "warning: coders: codex not on PATH, dropped" in out
    assert "warning: coders: other is not one of claude, codex, gemini, dropped" in out
    assert "warning: coders: no configured coder on PATH; falling back to the Claude Code coder (claude -p)" in out
    assert json.loads(pool(project, ["claude"], "--json")[1])["coders"]["fallback"] is True
    code, out = pool(project, ["gemini"])
    assert code == 0 and out.startswith("coders:\nparallel:\n") and "effective_tracks: 0" in out
    assert "warning: coders: no coder on PATH; ask the user before Implement" in out
    # With neither file the pool is the team default: codex, 4 tracks, 4 sessions per account.
    (project / ".devtools/coders.toml").unlink()
    assert pool(project, ["codex", "gemini"])[1] == (
        "coders:\n  codex/default: model= effort= risk=any\n"
        "parallel:\n  max_tracks: 4\n  max_sessions_per_account: 4\n  capacity: 4\n  effective_tracks: 4\n")


def test_coder_pool_paths_are_settings_and_an_unknown_setting_is_an_error(project):
    settings = project / ".claude/skills/process-phase/scripts/coder_pool.settings.json"
    assert json.loads(settings.read_text()) == {
        "team_config": ".devtools/coders.toml", "local_config": ".devtools/coders.local.toml"}
    settings.write_text(json.dumps({"team_config": "config/team.toml", "local_config": "config/mine.toml"}))
    coders(project, '[roles]\ncoders = ["gemini"]\n', "config/team.toml")
    coders(project, "[coders.gemini]\nrisk = 'medium'\n", "config/mine.toml")
    assert "  gemini/default: model= effort= risk=medium\n" in pool(project, ["codex", "gemini"])[1]
    coders(project, '[roles]\ncoders = "gemini"\n', "config/team.toml")
    code, out = pool(project, ["gemini"])
    assert code == 1 and "roles.coders must be a list of tool names" in out
    coders(project, '[roles\n', "config/team.toml")
    code, out = pool(project, ["gemini"])
    assert code == 1 and "config/team.toml" in out and "Traceback" not in out
    settings.write_text(json.dumps({"team_config": "config/team.toml", "coders": ["codex"]}))
    code, out = pool(project, ["codex"])
    assert code == 1 and "coder_pool.settings.json: unknown setting(s): coders" in out


def test_the_reader_for_python_without_tomllib_agrees_with_tomllib(project):
    spec = importlib.util.spec_from_file_location("coder_pool", project / POOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for text in (
            TEAM, "", "# nothing\n", 'a = 1 # one\nb = -2\nc = 1_000\nd = true\ne = 1.5\n', "a.b = 1\n'c d'.e = \"f\"\n",
            'a = "x # y \\" \\\\ \\t \\u00e9"\nb = \'c:\\d\'\n', "a = [\n  1, # one\n  [2, { b = [] }],\n]\n",
            '[coders.codex]\naccounts = [{ name = "A" }, { name = "B", env = { CODEX_HOME = "~/.codex-b" } }]\n',
            '[[coders.codex.accounts]]\nname = "A"\n[[coders.codex.accounts]]\nname = "B"\n'
            '[coders.codex.accounts.env]\nCODEX_HOME = "/x"\n[coders.gemini]\nrisk = "medium"\n',
            "[a.b]\nx = 1\n[a]\ny = 2\r\n[c]"):
        assert module.SubsetReader(text, "file.toml").read() == tomllib.loads(text), text
    for text in ("a = \n", "a 1\n", "a = 1 b = 2\n", "a = 1\na = 2\n", "[a]\n[a]\n", "[a\n", 'a = "open\n', "a = [1, 2\n",
                 "a = {b = 1,}\n", "a = 01\n", "a = [1 2]\n", "[[a]]\n[a]\n", "a = 1\n[a]\n", 'a = "\\q"\n'):
        with pytest.raises(tomllib.TOMLDecodeError):
            tomllib.loads(text)
        with pytest.raises(SystemExit, match=r"file\.toml:\d+: "):
            module.SubsetReader(text, "file.toml").read()
    # What it does not read is an error, never a wrong value.
    for text in ('a = """\nb"""\n', "a = 2026-01-01\n", "a = 0x10\n", "a = inf\n"):
        assert tomllib.loads(text)
        with pytest.raises(SystemExit, match="older than 3.11"):
            module.SubsetReader(text, "file.toml").read()


def test_plain_pytest_leaves_out_phases_that_are_not_complete(project):
    phase(project, "setup")
    for name in ("p01_first_phase", "p02_later"):
        (project / "tests/acceptance" / name).mkdir(parents=True)
        (project / "tests/acceptance" / name / ("test_%s.py" % name)).write_text("def test_it():\n    assert True\n")
    (project / "tests/test_unit.py").write_text("def test_unit():\n    assert True\n")
    state(project, completed_phases='"01"')

    def run(*args):
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args],
                              cwd=project, capture_output=True, text=True)
        return proc.stdout.strip().splitlines()[-1]

    assert run().startswith("2 passed, 1 deselected")
    assert run("--phase", "2").startswith("1 passed, 2 deselected")
    assert run("tests/acceptance/p02_later/test_p02_later.py").startswith("1 passed")
