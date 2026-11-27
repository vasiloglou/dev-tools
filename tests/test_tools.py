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


def new_project(tmp_path, *init):
    """A project that took the skills, in a new repository made with `git init` and the arguments `init`."""
    root = tmp_path / "widget"
    (root / "src/widget").mkdir(parents=True)
    (root / "src/widget/__init__.py").write_text('"""widget."""\n')
    config = (ROOT / "examples/phase-project.devtools.toml").read_text().replace("myapp", "widget")
    (root / ".devtools.toml").write_text(config)
    subprocess.run(["git", "init", "-q", "-b", "main", *init, str(root)], check=True)
    assert sync.main(["apply", "--project", str(root)]) == 0
    return root


@pytest.fixture
def project(tmp_path):
    return new_project(tmp_path)


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
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--color=no", *args],
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
    assert code == 2 and "shared_files must be a list of paths" in out


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


def extra_tools(project, count=None):
    """An extra source folder, tools/, with one module, and the package itself covered."""
    (project / "tools").mkdir()
    (project / "tools/report.py").write_text('"""Print a size report."""\n\n\ndef report(rows):\n    """Print rows."""\n')
    settings = project / "scripts/components_index.settings.json"
    values = dict(json.loads(settings.read_text()), extra_source_dirs=["tools"])
    if count is not None:
        values["count_extra_dirs"] = count
    settings.write_text(json.dumps(values))
    catalog(project, entry("core.package", "Hold the package", "src/widget/__init__.py"))


def test_extra_folders_are_not_counted_unless_the_setting_says_so(project):
    extra_tools(project)
    assert tool(project, "--check", "--strict", script=INDEX)[0] == 0
    code, out = tool(project, "stats", script=INDEX)
    assert code == 0 and "coverage: 1/1 src/widget modules assigned" in out and "tools/report.py" not in out


@pytest.fixture
def counted(project):
    extra_tools(project, count=True)
    return project


def test_strict_check_names_a_module_of_a_counted_extra_folder(counted):
    code, out = tool(counted, "--check", "--strict", script=INDEX)
    assert code == 1 and "no component: tools/report.py" in out
    catalog(counted, entry("tools.report", "Print a size report", "tools/report.py"))
    assert tool(counted, "--check", "--strict", script=INDEX)[0] == 0


def test_draft_stubs_a_module_of_a_counted_extra_folder(counted):
    code, out = tool(counted, "draft", script=INDEX)
    assert code == 0, out
    assert "### tools.report" in out and "- does: TODO Print a size report." in out and "- modules: tools/report.py" in out


@pytest.mark.parametrize("count", [True, False])
def test_changed_names_a_new_module_of_an_extra_folder_only_when_counted(project, count):
    extra_tools(project, count=count)
    if count:
        catalog(project, entry("tools.report", "Print a size report", "tools/report.py"))
    commit(project)
    (project / "tools/new.py").write_text('"""New."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    code, out = tool(project, "changed", "--base", "main", script=INDEX)
    if count:
        assert code == 1 and "fail: no component: tools/new.py (new file;" in out
    else:
        assert code == 0 and "no component" not in out, out


def test_review_and_stats_name_a_module_of_a_counted_extra_folder(counted):
    code, out = tool(counted, "review", script=INDEX)
    assert code == 0 and "## Modules with no component (1)\ntools/report.py" in out
    code, out = tool(counted, "stats", script=INDEX)
    assert code == 0 and "coverage: 1/2 src/widget, tools modules assigned" in out and "tools/report.py" in out


def test_count_extra_dirs_must_be_a_boolean(project):
    extra_tools(project)
    settings = project / "scripts/components_index.settings.json"
    settings.write_text(json.dumps(dict(json.loads(settings.read_text()), count_extra_dirs="yes")))
    code, out = tool(project, "stats", script=INDEX)
    assert code != 0 and "count_extra_dirs must be true or false" in out


def test_the_baseline_can_hold_a_module_of_a_counted_extra_folder(counted):
    assert tool(counted, "stats", "--write-baseline", script=INDEX)[0] == 0
    assert "tools/report.py" in (counted / "docs/components/unassigned-baseline.txt").read_text().split()
    assert tool(counted, "--check", "--strict", script=INDEX)[0] == 0


def test_show_prints_a_module_of_a_counted_extra_folder(counted):
    catalog(counted, entry("tools.report", "Print a size report", "tools/report.py"))
    code, out = tool(counted, "show", "tools.report", script=INDEX)
    assert code == 0 and "## tools/report.py (" in out and "report(rows)" in out


@pytest.mark.parametrize("key, value, stub", [
    ("extra_source_dirs", ["./tools"], "### tools.report"),
    ("extra_source_dirs", ["<absolute>"], "### tools.report"),
    ("package_dir", "./src/widget", "### widget.sizes"),
])
def test_draft_takes_a_folder_written_with_a_leading_dot(project, key, value, stub):
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    extra_tools(project, count=True)
    settings = project / "scripts/components_index.settings.json"
    if value == ["<absolute>"]:
        value = [str(project / "tools")]
    values = dict(json.loads(settings.read_text()), **{key: value})
    if key == "package_dir":
        values["count_extra_dirs"] = False
    settings.write_text(json.dumps(values))
    code, out = tool(project, "draft", script=INDEX)
    assert code == 0 and stub in out, out


def test_draft_keeps_the_package_name_as_it_is_for_the_area(project):
    (project / "src/widget_").mkdir()
    (project / "src/widget_/report.py").write_text('"""Report."""\n')
    settings = project / "scripts/components_index.settings.json"
    settings.write_text(json.dumps(dict(json.loads(settings.read_text()), package_dir="src/widget_", import_prefix="")))
    code, out = tool(project, "draft", script=INDEX)
    assert code == 0 and "### widget_.report" in out, out


def test_unassigned_modules_keep_the_order_of_their_paths(project):
    for name in ("src/widget/a.py", "src/widget/a/z.py"):
        (project / name).parent.mkdir(parents=True, exist_ok=True)
        (project / name).write_text('"""M."""\n')
    out = tool(project, "stats", script=INDEX)[1]
    assert out.index("src/widget/a/z.py") < out.index("src/widget/a.py\n")


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


def fake_gnd(project, report=None, exit_code=0, stderr="", newer=False, comparison=None, discovery=None, cases=None,
             synth_exit=0, synth_stderr=""):
    """A stand-in for gnd: it keeps the model and the facts it is given and prints the report prepared for it.
    `check --help` names the flags of a GND newer than 0.3.0 when `newer`; with `--baseline-model` it keeps the
    base edition and prints `comparison`. With `discovery`, `gnd discover` has the guarded-join family and
    writes that report; with `cases`, `gnd synth --guarded-cases` writes that manifest, unless `synth_exit` is not 0:
    then it writes `synth_stderr` to standard error and exits with that code, leaving no manifest."""
    folder = project.parent / "fake-gnd"
    folder.mkdir(exist_ok=True)
    script = folder / "gnd"
    script.write_text(
        "#!%s\nimport shutil, sys\nfrom pathlib import Path\n"
        "here = Path(__file__).parent\n"
        "if '--help' in sys.argv:\n"
        "    print((here / 'help.txt').read_text()); sys.exit(0)\n"
        "if sys.argv[1] in ('discover', 'synth'):\n"
        "    (here / (sys.argv[1] + '-argv.txt')).write_text(' '.join(sys.argv[1:]))\n"
        "    shutil.copy(sys.argv[2], here / (sys.argv[1] + '-model.json'))\n"
        "    if sys.argv[1] == 'discover':\n"
        "        Path(sys.argv[sys.argv.index('--report') + 1]).write_text((here / 'discovery.json').read_text())\n"
        "    else:\n"
        "        refusal = int((here / 'synth-exit.txt').read_text())\n"
        "        if refusal:\n"
        "            sys.stderr.write((here / 'synth-stderr.txt').read_text()); sys.exit(refusal)\n"
        "        out = Path(sys.argv[sys.argv.index('--out') + 1]); out.mkdir()\n"
        "        (out / 'guarded-cases.json').write_text((here / 'cases.json').read_text())\n"
        "    sys.exit(0)\n"
        "if '--baseline-model' in sys.argv:\n"
        "    shutil.copy(sys.argv[sys.argv.index('--baseline-model') + 1], here / 'base-model.json')\n"
        "    print((here / 'comparison.json').read_text()); sys.exit(0)\n"
        "shutil.copy(sys.argv[2], here / 'model.json'); shutil.copy(sys.argv[3], here / 'head.facts.json')\n"
        "(here / 'argv.txt').write_text(' '.join(sys.argv[1:]))\n"
        "sys.stderr.write((here / 'stderr.txt').read_text())\n"
        "print((here / 'report.json').read_text())\n"
        "sys.exit(int((here / 'exit.txt').read_text()))\n" % sys.executable)
    script.chmod(0o755)
    (folder / "help.txt").write_text("usage: gnd check [--rule-ids] [--baseline BASE] [--allow-vacuous]"
                                     + (" [--baseline-model BASE] [--guarded-diagnostics]" if newer else "")
                                     + (" [--joined-relation FACT:SOURCE:TARGET]" if discovery is not None else "")
                                     + (" [--guarded-cases]" if cases is not None else ""))
    (folder / "comparison.json").write_text(json.dumps(comparison or {}))
    (folder / "discovery.json").write_text(json.dumps(discovery or {}))
    (folder / "cases.json").write_text(json.dumps(cases or {}))
    (folder / "synth-exit.txt").write_text(str(synth_exit))
    (folder / "synth-stderr.txt").write_text(synth_stderr)
    (folder / "base-model.json").unlink(missing_ok=True)
    (folder / "report.json").write_text(report if isinstance(report, str) else json.dumps(report or gnd_report()))
    (folder / "exit.txt").write_text(str(exit_code))
    (folder / "stderr.txt").write_text(stderr)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": str(script)}))
    return folder


STARTER_IDS = ["no_forbidden_area_use", "no_use_of_a_higher_rank", "no_import_inside_a_loop",
               "canonical_component_has_a_test", "private_module_stays_in_its_component"]
PLAN_RULE = "plan_names_the_components_it_touches"  # the one starter rule about plans: only `check --phase` judges it


def rule_ids(model):
    """The ids of the rules in a model the script built, without the value lists it adds."""
    return [c["id"] for c in model["constraints"] if not c["id"].startswith("devtools_")]


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
    rules = [c for c in model["constraints"] if not c["id"].startswith("devtools_")]
    assert [c["id"] for c in rules] == STARTER_IDS
    assert all("level" not in c and "examples" not in c and c["remedy"] for c in rules)
    assert [c["modality"] for c in rules] == ["alethic", "alethic", "deontic", "deontic", "deontic"]
    assert {c["id"]: c.get("allowed") for c in model["constraints"] if c["id"].startswith("devtools_")} == {
        "devtools_component_has_status_status_values": ["canonical", "deprecated", "duplicate-of", "experimental", "external"],
        "devtools_area_values": ["cli", "core"]}, "the values a role can hold, for a literal outside them"
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
NEWER_GND = bool(REAL_GND) and "--baseline-model" in subprocess.run(
    [*REAL_GND.split(), "check", "--help"], capture_output=True, text=True).stdout


def test_rules_say_when_a_rule_judged_nothing_or_names_a_value_nothing_holds(project):
    layered(project)
    silent = verdict("no_forbidden_area_use", "pass")
    silent["guarded_antecedent"] = {"binding_count": 0, "first_empty_atom_index": 2}
    counted = verdict("canonical_component_has_a_test", "pass")
    counted["guarded_antecedent"] = {"binding_count": 2, "first_empty_atom_index": None}
    warning = {"path": "$.constraints[3].antecedent[0].bind[status]", "rule_id": "semantic:guarded-literal-outside-domain",
               "message": "Literal lies outside the value domain declared by constraints[5]."}
    report = gnd_report(silent, counted, version=16, warnings=[warning])

    seen = fake_gnd(project, report)
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "report version 16" in out, "a GND that has no such flag was not asked for that report"
    assert "--guarded-diagnostics" not in (seen / "argv.txt").read_text()

    seen = fake_gnd(project, report, newer=True)
    code, out = tool(project, "check", script=RULES)
    assert code == 0, out
    assert "--guarded-diagnostics" in (seen / "argv.txt").read_text()
    assert ("reread: no_forbidden_area_use matched nothing: no binding gets past atom 2 (component_in_area) of its "
            "antecedent, though every fact it names has rows\n") in out
    assert ("reread: canonical_component_has_a_test: 'canonical' is not a value component_has_status.status can hold "
            "(canonical, deprecated, duplicate-of, experimental, external)\n") in out, "the rule and the role GND named"
    code, out = tool(project, "check", "--format", "json", script=RULES)
    assert json.loads(out)["bindings"] == {"no_forbidden_area_use": 0, "canonical_component_has_a_test": 2}

    rules = project / "docs/components/rules.json"
    rules.write_text(rules.read_text().replace('"no_import_inside_a_loop"', '"devtools_loop"'))
    code, out = tool(project, "check", script=RULES)
    assert code == 2 and "devtools_loop: an id starting with devtools_ is kept" in out


def test_rules_say_what_an_edit_of_the_rules_hides(project):
    layered(project)
    commit(project)
    rules = project / "docs/components/rules.json"
    rules.write_text(rules.read_text().replace('"no_import_inside_a_loop", "level": "should"', '"no_import_inside_a_loop", "level": "must"', 1)
                     .replace('"id": "no_forbidden_area_use"', '"id": "no_forbidden_area_use_2"'))
    gone = {"$a": "cli.run", "$b": "core.sizes", "$from": "cli", "$to": "core"}
    side = lambda modality: {"constraint_ref": "constraints[0]", "constraint_type": "guarded", "modality": modality, "verdict": "fail"}
    comparison = {"schema_version": "gnd-rule-edition-comparison/1", "exit_code": 0, "reason": None, "rules": [
        {"address": "constraint:no_forbidden_area_use", "pairing": "removed", "base": side("alethic"), "head": None,
         "delta": {"base_only": [gone], "head_only": [], "standing": []}, "reason": None},
        {"address": "constraint:canonical_component_has_a_test", "pairing": "paired", "base": side("alethic"),
         "head": side("deontic"), "delta": {"base_only": [{"$a": "x"}] * 5, "head_only": [], "standing": []}, "reason": None},
        {"address": "constraint:no_import_inside_a_loop", "pairing": "paired", "base": side("deontic"), "head": side("alethic"),
         "delta": None, "reason": "alignment-ambiguous"},
        {"address": "constraint:devtools_area_values", "pairing": "paired", "base": side("deontic"), "head": side("deontic"),
         "delta": {"base_only": [{"x": 1}], "head_only": [], "standing": []}, "reason": None}]}

    seen = fake_gnd(project, gnd_report(rules=["no_forbidden_area_use_2", *STARTER_IDS[1:]]), comparison=comparison)
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0 and "reread: rules changed in this change: docs/components/rules.json" in out, out
    assert not (seen / "base-model.json").exists(), "a GND without --baseline-model is not asked"

    seen = fake_gnd(project, gnd_report(rules=["no_forbidden_area_use_2", *STARTER_IDS[1:]], version=16), newer=True, comparison=comparison)
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0, out
    assert ("reread: no_forbidden_area_use was removed in this change; on this code it reported 1 finding(s); "
            "a=cli.run b=core.sizes from=cli to=core\n") in out
    assert ("reread: canonical_component_has_a_test was edited in this change and no longer reports 5 finding(s) it "
            "reported before; a=x; a=x; a=x; …\n") in out
    assert "reread: canonical_component_has_a_test went from must to should in this change\n" in out
    assert "reread: no_import_inside_a_loop: the two editions could not be compared (alignment-ambiguous)\n" in out
    assert "devtools_area_values" not in out, "the value lists the script adds are not rules"
    base = json.loads((seen / "base-model.json").read_text())
    assert rule_ids(base) == STARTER_IDS, "the base edition is the rules file at the base"
    assert rule_ids(json.loads((seen / "model.json").read_text()))[0] == "no_forbidden_area_use_2"

    commit(project)
    seen = fake_gnd(project, gnd_report(rules=["no_forbidden_area_use_2", *STARTER_IDS[1:]], version=16), newer=True, comparison=comparison)
    tool(project, "check", "--base", "HEAD", script=RULES)
    assert not (seen / "base-model.json").exists(), "rules that did not change are not compared"


def test_starter_rules_carry_examples_and_the_vocabulary_lists_match_the_phase_tool(project):
    rules = json.loads(tool(project, "init", "--print", script=RULES)[1].split("\n", 1)[1].rsplit("# docs/components/layers.toml", 1)[0])
    assert all(set(rule["examples"]) == {"fails", "passes"} for rule in rules["rules"]), "every starter rule shows both"
    spec = importlib.util.spec_from_file_location("rules_check", ROOT / "skills/components/scripts/rules_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    spec = importlib.util.spec_from_file_location("phase_tool", ROOT / "skills/phase/process-phase/scripts/phase_tool.py")
    phase_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase_module)
    assert module.PLAN_KEYS == sorted(phase_module.PLAN_KEYS)


@pytest.mark.skipif(not REAL_GND, reason="GND is not installed (put gnd on PATH or set GND_COMMAND)")
def test_rules_are_tested_on_their_own_examples_with_real_gnd(project):
    layered(project)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": REAL_GND}))
    code, out = tool(project, "test", script=RULES)
    assert code == 0 and out.endswith("rules test: 6 rule(s), 12 example(s); 0 wrong\n"), out
    assert "note: no_import_inside_a_loop: the passing example 1 matched nothing" in out, "no loop: nothing to judge"

    path = project / "docs/components/rules.json"
    rules = json.loads(path.read_text())
    rules["rules"][3]["antecedent"][0]["bind"]["status"] = "canonicl"
    rules["rules"][0]["examples"]["passes"] = rules["rules"][0]["examples"]["fails"]
    rules["rules"].append({"id": "no_examples", "level": "should", "type": "guarded",
                           "antecedent": [{"fact_type": "component_is_listed", "bind": {"component": "$a"}}],
                           "consequent": {"atom": {"fact_type": "component_has_test", "bind": {"component": "$a", "path": "x"}}},
                           "examples": {"fails": {"component_is_lsted": [{"component": "a.b"}]}}})
    path.write_text(json.dumps(rules))
    code, out = tool(project, "test", script=RULES)
    assert code == 1, out
    assert "wrong: canonical_component_has_a_test: the failing example 1 does not break the rule" in out
    assert "wrong: no_forbidden_area_use: the passing example 1 breaks the rule: a=cli.run b=core.sizes from=cli to=core" in out
    assert "wrong: no_examples: the failing example 1 names component_is_lsted, which no fact type of this project is" in out
    assert out.endswith("7 rule(s), 13 example(s); 3 wrong\n"), out
    rules["rules"][-1]["examples"] = {"fails": "x"}
    path.write_text(json.dumps(rules))
    code, out = tool(project, "test", script=RULES)
    assert code == 2 and 'no_examples: "examples" is' in out


@pytest.mark.skipif(not NEWER_GND, reason="needs a GND newer than 0.3.0 (--guarded-diagnostics, --baseline-model)")
def test_a_misspelt_or_loosened_rule_is_named_with_newer_gnd(project):
    layered(project)
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": REAL_GND}))
    commit(project)
    path = project / "docs/components/rules.json"
    rules = json.loads(path.read_text())
    rules["rules"][3]["antecedent"][0]["bind"]["status"] = "canonicl"
    path.write_text(json.dumps(rules))
    code, out = tool(project, "check", "--base", "main", script=RULES)
    assert code == 0, out
    assert ("reread: canonical_component_has_a_test was edited in this change and no longer reports 2 finding(s) it "
            "reported before; a=cli.run; a=core.sizes\n") in out
    assert ("reread: canonical_component_has_a_test matched nothing: no binding gets past atom 0 (component_has_status) "
            "of its antecedent") in out
    assert "reread: canonical_component_has_a_test: 'canonicl' is not a value component_has_status.status can hold" in out
    code, out = tool(project, "test", script=RULES)
    assert code == 1 and "no binding gets past atom 0 (component_has_status)" in out, out


def forbidden(source, target, **more):
    """A forbidden pair as GND's guarded-join family proposes it: a use from `source` never reaches `target`."""
    return {"family": "guarded-join", "constraint": {"id": "gj_" + source + "_" + target, "type": "guarded", "antecedent": [
        {"fact_type": "component_uses", "bind": {"caller": "$a", "callee": "$b"}},
        {"fact_type": "component_in_area", "bind": {"component": "$a", "area": source}}],
        "consequent": {"absence": {"fact_type": "component_in_area", "bind": {"component": "$b", "area": target}}}}, **more}


def test_rules_suggest_reads_the_directions_the_code_keeps(project):
    layered(project)  # cli.run uses core.sizes, and layers.toml forbids cli to core
    fake_gnd(project)
    code, out = tool(project, "suggest", script=RULES)
    assert code == 0 and out.startswith("skip: suggest needs a GND whose `gnd discover` has the guarded-join family")
    assert tool(project, "suggest", "--require", script=RULES)[0] == 1

    ref = "ft%d#0" % list(facts(project)["types"]["facts"]).index("component_uses")
    discovery = {"joined_rules": {"reason": None}, "emitted": [forbidden("core", "cli"), forbidden("core", "core")],
                 "near_misses": [forbidden("cli", "core", violations=1, subjects=20, counterexamples=[ref])]}
    seen = fake_gnd(project, discovery=discovery)
    code, out = tool(project, "suggest", script=RULES)
    assert code == 0, out
    assert "--families guarded-join --joined-relation component_uses:caller:callee --joined-classifier " \
           "component_in_area:component:area" in (seen / "discover-argv.txt").read_text()
    assert "kept: core never uses cli (each uses it)\n" in out
    assert "almost:" not in out, "a pair layers.toml forbids is what `check` reports"
    assert "core never uses core" not in out, "a use inside one area is not a layer"

    layers = project / "docs/components/layers.toml"
    layers.write_text("")
    code, out = tool(project, "suggest", script=RULES)
    assert "almost: cli uses core in 1 of its 20 use(s): cli.run -> core.sizes (src/widget/cli.py -> src/widget/sizes.py)\n" in out
    assert out.endswith("2 component(s) in 2 area(s), 1 use(s); 1 near miss(es), 1 direction(s) the code keeps that "
                        "layers.toml does not say; --format toml prints them as [[forbid]] lines\n"), out
    code, out = tool(project, "suggest", "--format", "toml", script=RULES)
    assert tomllib.loads(out)["forbid"] == [{"from": "core", "to": "cli"}]
    code, out = tool(project, "suggest", "--format", "json", script=RULES)
    assert json.loads(out)["near_misses"][0]["rows"] == [
        {"caller": "cli.run", "callee": "core.sizes", "imports": [["src/widget/cli.py", "src/widget/sizes.py"]]}]

    layers.write_text("[rank]\ncore = 0\ncli = 1\n")
    code, out = tool(project, "suggest", script=RULES)
    assert "kept:" not in out, "a rank already says core does not use cli"

    fake_gnd(project, discovery={"joined_rules": {"reason": "coverage-gap"}})
    code, out = tool(project, "suggest", script=RULES)
    assert code == 2 and "could not look for rules over the areas: coverage-gap" in out


def test_rules_test_asks_gnd_for_the_cases_a_rule_cannot_have(project):
    layered(project)
    path = project / "docs/components/rules.json"
    rules = json.loads(path.read_text())
    for rule in rules["rules"]:
        rule.pop("examples")
    path.write_text(json.dumps(rules))
    manifest = {"schema_version": "gnd-guarded-cases/1", "rules": [
        {"rule_id": "no_forbidden_area_use", "reason": None, "cases": [{"kind": "failing"}, {"kind": "passing"}]},
        {"rule_id": "no_use_of_a_higher_rank", "reason": "no-failing-case", "cases": []},
        {"rule_id": "no_import_inside_a_loop", "reason": "no-passing-case", "cases": []},
        {"rule_id": "canonical_component_has_a_test", "reason": "search-limit", "cases": []},
        {"rule_id": "private_module_stays_in_its_component", "reason": "antecedent-unreachable", "cases": []}]}
    code, out = tool(project, "test", script=RULES)
    assert "can never" not in out, "a GND without --guarded-cases is not asked"

    seen = fake_gnd(project, cases=manifest)
    code, out = tool(project, "test", script=RULES)
    assert code == 1, out
    assert ("wrong: no_use_of_a_higher_rank can never fail: whatever matches its antecedent already meets its consequent "
            "(gnd synth --guarded-cases: no-failing-case)\n") in out
    assert "note: no_import_inside_a_loop can never pass once it applies: right for a ban, else reread it" in out
    assert "wrong: private_module_stays_in_its_component can never apply: no facts can match its antecedent" in out
    assert "search-limit" not in out, "a search that ran out says nothing about the rule"
    assert rule_ids(json.loads((seen / "synth-model.json").read_text())) == STARTER_IDS + [PLAN_RULE]

    fake_gnd(project, cases={"schema_version": "gnd-guarded-cases/9"})
    code, out = tool(project, "test", script=RULES)
    assert code == 0 and "note: gnd synth --guarded-cases wrote 'gnd-guarded-cases/9'" in out, out


def offered(command, flag):
    return bool(REAL_GND) and flag in subprocess.run([*REAL_GND.split(), command, "--help"],
                                                     capture_output=True, text=True).stdout


SYNTH_EXTRA = "needs the optional 'synth' extra"


def without_synth_extra(code: int, out: str) -> bool:
    """Whether `rules_check.py test` found nothing wrong (exit 0) and reported that GND built no cases for want
    of its synth extra. With anything wrong the answer is no: the refusal is then not the only thing to see."""
    return code == 0 and any(
        line.startswith("note: gnd synth --guarded-cases built no cases (exit 5): ") and SYNTH_EXTRA in line
        for line in out.splitlines())


def skip_without_synth_extra(code: int, out: str) -> None:
    """Skip the running test when GND lists --guarded-cases and cannot run it: the flag is in `gnd synth --help`
    with or without the extra, so `offered` cannot tell. Any other failure of `gnd synth`, and any rule or
    example `test` calls wrong, skips nothing."""
    if without_synth_extra(code, out):
        pytest.skip("this GND lacks its synth extra: uv tool install --force 'get-nick-done[synth]'")


EXTRA_MISSING = "ERROR: the synthetic-value generator needs the optional 'synth' extra.\n"  # what GND 0.4.0 prints


def rules_without_examples(project):
    """The starter rules with their examples taken out: the stand-in for gnd judges nothing, so `test` is left
    with what `gnd synth` says."""
    layered(project)
    path = project / "docs/components/rules.json"
    rules = json.loads(path.read_text())
    for rule in rules["rules"]:
        rule.pop("examples")
    path.write_text(json.dumps(rules))


def test_a_gnd_without_its_synth_extra_is_a_note_and_the_guard_skips(project):
    # A GND installed without [synth] lists --guarded-cases and refuses only when the command runs.
    rules_without_examples(project)
    fake_gnd(project, cases={}, synth_exit=5, synth_stderr=EXTRA_MISSING)
    code, out = tool(project, "test", script=RULES)
    assert code == 0, out
    assert ("note: gnd synth --guarded-cases built no cases (exit 5): ERROR: the synthetic-value generator needs "
            "the optional 'synth' extra.\n") in out
    assert without_synth_extra(code, out)
    with pytest.raises(pytest.skip.Exception, match="lacks its synth extra"):
        skip_without_synth_extra(code, out)


def test_the_guard_does_not_hide_a_rule_that_is_wrong(project):
    # The refusal is one line of the output; an example that is wrong is another, and still a failure.
    layered(project)  # the starter rules with their examples: the stand-in judges nothing, so each is "wrong"
    fake_gnd(project, cases={}, synth_exit=5, synth_stderr=EXTRA_MISSING)
    code, out = tool(project, "test", script=RULES)
    assert code == 1 and "wrong: no_forbidden_area_use: the failing example 1 does not break the rule" in out, out
    assert "note: gnd synth --guarded-cases built no cases (exit 5): " in out and SYNTH_EXTRA in out
    assert not without_synth_extra(code, out)
    assert skip_without_synth_extra(code, out) is None


@pytest.mark.parametrize("synth_exit, synth_stderr, cases", [
    (3, EXTRA_MISSING, {}),                                          # the extra's sentence, another exit
    (5, "ERROR: no solver\n", {}),                                   # exit 5, another reason
    (3, "ERROR: model validation failed: $.constraints[5]\n", {}),   # a model GND refuses
    (0, "", {"schema_version": "gnd-guarded-cases/1", "rules": []}),  # the cases were built
])
def test_the_guard_skips_for_the_missing_extra_only(project, synth_exit, synth_stderr, cases):
    rules_without_examples(project)
    fake_gnd(project, cases=cases, synth_exit=synth_exit, synth_stderr=synth_stderr)
    code, out = tool(project, "test", script=RULES)
    assert code == 0, out
    assert ("built no cases (exit %d)" % synth_exit in out) == bool(synth_exit), out
    assert not without_synth_extra(code, out)
    assert skip_without_synth_extra(code, out) is None


@pytest.mark.skipif(not offered("discover", "--joined-relation") or not offered("synth", "--guarded-cases"),
                    reason="needs a GND newer than 0.3.0 (gnd discover guarded-join, gnd synth --guarded-cases)")
def test_suggestions_and_generated_cases_with_newer_gnd(project):
    # core: a base and twenty components on it, one of which uses cli; cli uses core; app uses cli.
    (project / "src/widget/base.py").write_text('"""Base."""\n')
    (project / "src/widget/cli.py").write_text('"""Cli."""\nfrom widget import base\n')
    (project / "src/widget/app.py").write_text('"""App."""\nfrom widget import cli\n')
    parts = [entry("core.base", "Base", "src/widget/base.py"), entry("cli.run", "Run", "src/widget/cli.py"),
             entry("app.main", "Main", "src/widget/app.py")]
    for number in range(20):
        (project / ("src/widget/c%d.py" % number)).write_text(
            '"""Part."""\nfrom widget import base\n' + ("from widget import cli\n" if number == 0 else ""))
        parts.append(entry("core.c%d" % number, "Part %d" % number, "src/widget/c%d.py" % number))
    catalog(project, *parts)
    assert tool(project, "init", script=RULES)[0] == 0
    (project / RULES_SETTINGS).write_text(json.dumps({"gnd_command": REAL_GND}))
    code, out = tool(project, "suggest", script=RULES)
    assert code == 0, out
    assert ("almost: core uses cli in 1 of its 21 use(s); cli uses core 1 time(s), so this closes a loop: "
            "core.c0 -> cli.run (src/widget/c0.py -> src/widget/cli.py)\n") in out
    assert "kept: cli never uses app (each uses it)\n" in out

    path = project / "docs/components/rules.json"
    rules = json.loads(path.read_text())
    rules["rules"].append({"id": "cannot_fail", "level": "should", "type": "guarded",
                           "antecedent": [{"fact_type": "component_uses", "bind": {"caller": "$a", "callee": "$b"}}],
                           "consequent": {"atom": {"fact_type": "component_uses", "bind": {"caller": "$a", "callee": "$b"}}}})
    path.write_text(json.dumps(rules))
    code, out = tool(project, "test", script=RULES)
    skip_without_synth_extra(code, out)
    assert code == 1 and "wrong: cannot_fail can never fail" in out, out
    assert out.endswith("7 rule(s), 12 example(s); 1 wrong; 1 rule(s) without examples\n"), out


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
    assert rule_ids(json.loads((seen / "model.json").read_text())) == STARTER_IDS

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
    assert rule_ids(model) == [PLAN_RULE] and "about" not in model["constraints"][0]
    assert "devtools_task_has_type_type_values" in {c["id"] for c in model["constraints"]}
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
    assert code == 0 and json.loads(out) == {"rows": [], "notes": [], "bindings": {},
                                        "summary": "plan rules for phase 01: 1 rule(s); 0 to fix, 0 warning(s)"}
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
    assert "warn:" not in out, out
    # The regrouping is no new caller, but it is a change to the component that gave the module up: the
    # owner's ruling of 2026-11-26 on review pr-51-r1 (test_changed_asks_both_components_when_a_module_moves...).
    assert code == 1 and "reread: core.report (only modules edited): src/widget/rows.py\n" in out, out
    assert tool(project, "changed", "--base", "main", script=INDEX)[0] == 0


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
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--color=no", *args],
                              cwd=project, capture_output=True, text=True)
        return proc.stdout.strip().splitlines()[-1]

    assert run().startswith("2 passed, 1 deselected")
    assert run("--phase", "2").startswith("1 passed, 2 deselected")
    assert run("tests/acceptance/p02_later/test_p02_later.py").startswith("1 passed")


# --- The index tool: a baseline a project refuses, a base that is behind, a reread entry, the counted folders.

INDEX_SETTINGS = "scripts/components_index.settings.json"


def index_settings(project, **values):
    path = project / INDEX_SETTINGS
    path.write_text(json.dumps(dict(json.loads(path.read_text()), **values)))


def run_index(project, *args, script=INDEX, env=None):
    """Run a script of the project with its standard output and standard error kept apart."""
    env = {**os.environ, "XDG_CACHE_HOME": str(project.parent / "cache"), **(env or {})}
    return subprocess.run([sys.executable, script, *args], cwd=project, capture_output=True, text=True, env=env)


def git_in(project, *args):
    done = subprocess.run([GIT, "-c", "user.name=t", "-c", "user.email=t@example.com", *args], cwd=project,
                          capture_output=True, text=True, check=True)
    return done.stdout.strip()


def test_strict_check_refuses_a_baseline_when_the_setting_says_so(project):
    (project / "src/widget/loose.py").write_text('"""Loose."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    assert tool(project, "stats", "--write-baseline", script=INDEX)[0] == 0
    assert "src/widget/loose.py" in (project / "docs/components/unassigned-baseline.txt").read_text().split()
    assert tool(project, "--check", "--strict", script=INDEX)[0] == 0, "by default a baseline excuses its modules"

    index_settings(project, allow_baseline=False)
    code, out = tool(project, "--check", "--strict", script=INDEX)
    assert code == 1, out
    assert ("baseline refused: docs/components/unassigned-baseline.txt exists and allow_baseline is false "
            "(give its modules a component, then delete the file)\n") in out
    assert "no component: src/widget/loose.py" in out, "the file excuses nothing"
    code, out = tool(project, "--check", script=INDEX)
    assert code == 0 and "baseline refused" not in out and "no component" not in out, out

    catalog(project, entry("core.all", "Hold every module", "src/widget/"))
    (project / "docs/components/unassigned-baseline.txt").unlink()
    code, out = tool(project, "--check", "--strict", script=INDEX)
    assert code == 0, out


def test_no_baseline_is_written_when_the_setting_refuses_one(project):
    (project / "src/widget/loose.py").write_text('"""Loose."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    index_settings(project, allow_baseline=False)
    code, out = tool(project, "stats", "--write-baseline", script=INDEX)
    assert code == 1 and "allow_baseline is false: this project keeps no baseline; give each module a component" in out
    assert not (project / "docs/components/unassigned-baseline.txt").exists()
    code, out = tool(project, "stats", script=INDEX)
    assert code == 0 and "src/widget/loose.py" in out


def test_allow_baseline_must_be_a_boolean(project):
    index_settings(project, allow_baseline="no")
    code, out = tool(project, "stats", script=INDEX)
    assert code != 0 and "allow_baseline must be true or false" in out


def behind(project):
    """A remote under tmp_path; `main` tracks origin/main and is one commit behind it; the work is on a
    branch cut from origin/main. Returns the commits of main and of origin/main."""
    catalog(project, entry("core.all", "Hold every module", "src/widget/"))
    commit(project)
    first = git_in(project, "rev-parse", "HEAD")
    origin = project.parent / "origin.git"
    git_in(project.parent, "clone", "-q", "--bare", str(project), str(origin))
    git_in(project, "remote", "add", "origin", str(origin))
    (project / "src/widget/later.py").write_text('"""Added upstream."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    git_in(project, "push", "-q", "origin", "main")
    git_in(project, "fetch", "-q", "origin")
    git_in(project, "branch", "-q", "-u", "origin/main", "main")
    git_in(project, "checkout", "-q", "-b", "work")
    git_in(project, "branch", "-q", "-f", "main", first)
    return first, git_in(project, "rev-parse", "origin/main")


def summary(out):
    return next(line for line in out.splitlines() if line.startswith("changed against "))


def test_changed_compares_with_the_upstream_of_a_base_that_is_behind(project):
    first, upstream = behind(project)
    code, out = tool(project, "changed", "--base", "main", script=INDEX)
    assert code == 0, out
    lines = out.splitlines()
    note = ("note: main (%s) is 1 commit(s) behind origin/main (%s): comparing with origin/main"
            % (first[:7], upstream[:7]))
    assert note in lines and lines.index(note) == lines.index(summary(out)) - 1, out
    assert summary(out) == summary(tool(project, "changed", "--base", "origin/main", script=INDEX)[1])
    assert summary(out).startswith("changed against origin/main (%s): " % upstream[:7])


def test_changed_reads_a_branch_named_in_full_like_its_short_name(project):
    first, upstream = behind(project)
    code, out = tool(project, "changed", "--base", "refs/heads/main", script=INDEX)
    assert code == 0, out
    assert ("note: refs/heads/main (%s) is 1 commit(s) behind origin/main (%s): comparing with origin/main"
            % (first[:7], upstream[:7])) in out.splitlines(), out
    assert summary(out).startswith("changed against origin/main (%s): " % upstream[:7])


@pytest.mark.parametrize("state", ["level", "ahead", "diverged", "no upstream", "commit", "origin/main given",
                                   "only the remote has it", "a tag of the same name", "a tag"])
def test_changed_reads_every_other_base_as_it_is(project, state):
    first, upstream = behind(project)
    base, named = "main", "main"
    if state == "level":
        git_in(project, "branch", "-q", "-f", "main", upstream)
    elif state in ("ahead", "diverged"):
        git_in(project, "branch", "-q", "-f", "main", upstream if state == "ahead" else first)
        git_in(project, "checkout", "-q", "main")
        git_in(project, "commit", "-q", "--allow-empty", "-m", state)
        git_in(project, "checkout", "-q", "work")
    elif state == "no upstream":
        git_in(project, "branch", "-q", "--unset-upstream", "main")
    elif state == "commit":
        base = named = first
    elif state == "origin/main given":
        base = named = "origin/main"
    elif state == "a tag of the same name":
        git_in(project, "tag", "main", first)  # git reads the name as the tag; so must the index
    elif state == "a tag":
        git_in(project, "tag", "v1", first)
        base = named = "v1"
    else:
        git_in(project, "branch", "-q", "-D", "main")
        named = "origin/main"
    code, out = tool(project, "changed", "--base", base, script=INDEX)
    assert code == 0, out
    assert "note:" not in out, out
    assert summary(out).startswith("changed against %s (" % named), out


def test_no_command_of_the_index_fetches(project):
    behind(project)
    folder = project.parent / "recording-git"
    folder.mkdir()
    log = project.parent / "git-calls.txt"
    (folder / "git").write_text('#!/bin/sh\necho "$@" >> %s\nexec %s "$@"\n' % (log, GIT))
    (folder / "git").chmod(0o755)
    env = {"PATH": "%s%s%s" % (folder, os.pathsep, os.environ["PATH"])}
    for args in (("changed", "--base", "main"), ("facts", "--base", "main")):
        assert run_index(project, *args, env=env).returncode == 0
    calls = log.read_text().splitlines()
    assert calls, "the recording git was not the one run"
    assert not [call for call in calls if {"fetch", "pull", "push", "remote"} & set(call.split())], calls


def test_facts_follow_the_same_base_and_stay_one_json_document(project):
    first, upstream = behind(project)
    done = run_index(project, "facts", "--base", "main")
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout) == json.loads(run_index(project, "facts", "--base", "origin/main").stdout)
    assert done.stderr == ("note: main (%s) is 1 commit(s) behind origin/main (%s): comparing with origin/main\n"
                           % (first[:7], upstream[:7]))
    out = project.parent / "facts.json"
    assert run_index(project, "facts", "--base", "main", "--out", str(out)).returncode == 0
    assert json.loads(out.read_text()) == json.loads(done.stdout)


def test_the_rule_check_says_which_base_it_judged_against(project):
    layered(project)
    first, upstream = behind(project)
    fake_gnd(project)
    done = run_index(project, "check", "--base", "main", script=RULES)
    assert done.returncode == 0, done.stdout + done.stderr
    assert ("note: main (%s) is 1 commit(s) behind origin/main (%s): comparing with origin/main"
            % (first[:7], upstream[:7])) in done.stderr, done.stderr
    # The summary names the base as it was asked for, and the commit the facts were read at: origin/main's.
    assert done.stdout.endswith("rules against main (%s): 5 rule(s); 0 to fix, 0 warning(s), 0 standing\n"
                                % upstream[:7]), done.stdout
    other = run_index(project, "check", "--base", "origin/main", script=RULES)
    assert done.stdout == other.stdout.replace("rules against origin/main (", "rules against main ("), other.stdout


def reread_entry(project, text):
    path = project / "docs/components/COMPONENTS.md"
    path.write_text(path.read_text().replace("- modules: src/widget/sizes.py\n",
                                             "- modules: src/widget/sizes.py\n- reread: %s\n" % text))


def older_than_code(project):
    out = tool(project, "review", script=INDEX)[1]
    return [line for line in out.split("## Descriptions older than their code")[1].split("\n## ")[0].splitlines()[1:]
            if line.strip()]


def test_a_reread_line_brings_an_entrys_date_forward(project):
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    commit(project)
    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    [lead] = older_than_code(project)
    assert lead.startswith("core.sizes: 1 commit(s) to its modules since ") and lead.endswith(
        ", when its does and verbs were last edited"), lead

    reread_entry(project, "2026-11-23, read beside the rewrite, still accurate")
    assert tool(project, "write", script=INDEX)[0] == 0
    assert tool(project, "--check", script=INDEX)[0] == 0
    assert older_than_code(project) == [], "a reread line not committed yet counts as now"
    commit(project)
    assert older_than_code(project) == []
    assert "- reread: 2026-11-23, read beside the rewrite, still accurate" in (
        project / "docs/components/COMPONENTS.md").read_text(), "write keeps the line"

    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten again."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    [lead] = older_than_code(project)
    assert lead.startswith("core.sizes: 1 commit(s) to its modules since ") and lead.endswith(
        ", when it was last marked as reread"), lead


def test_a_reread_line_committed_in_the_same_second_still_counts(project, monkeypatch):
    # Commit times have a resolution of one second; a tie is settled by history, not by the clock.
    for name in ("GIT_AUTHOR_DATE", "GIT_COMMITTER_DATE"):
        monkeypatch.setenv(name, "2026-11-23T12:00:00+00:00")
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    commit(project)
    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    assert len(older_than_code(project)) == 1
    reread_entry(project, "2026-11-23, still accurate")
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    assert older_than_code(project) == [], "the reread line's commit is the newer one, though the clock ties"


def test_a_tie_in_commit_time_is_settled_by_history_without_a_reread_line(project, monkeypatch):
    # The verbs edited in the same commit as the code, and in the same second as the entry was written: the entry
    # was updated with its code, so it is not listed. Before ties were settled by history, the blame order decided.
    for name in ("GIT_AUTHOR_DATE", "GIT_COMMITTER_DATE"):
        monkeypatch.setenv(name, "2026-11-23T12:00:00+00:00")
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    commit(project)
    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten."""\n')
    path = project / "docs/components/COMPONENTS.md"
    path.write_text(path.read_text().replace("- verbs: sizes\n", "- verbs: sizes, parse sizes\n"))
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    assert older_than_code(project) == []


def test_a_reread_line_written_twice_is_refused(project):
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    reread_entry(project, "once")
    reread_entry(project, "twice")
    code, out = tool(project, "--check", script=INDEX)
    assert code == 1 and "core.sizes: reread appears twice" in out, out


def test_changed_takes_a_reread_line_as_an_edit_of_the_entry(project):
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    commit(project)
    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    code, out = tool(project, "changed", "--base", "main", script=INDEX)
    assert code == 0 and "reread: core.sizes (entry not edited): src/widget/sizes.py" in out, out
    reread_entry(project, "2026-11-23, still accurate")
    assert tool(project, "write", script=INDEX)[0] == 0
    code, out = tool(project, "changed", "--base", "main", script=INDEX)
    assert code == 0 and "reread:" not in out, out


FLOW = ("\n### subsystem.report\n- does: Print sizes\n- verbs: report\n- status: canonical\n"
        "- components: core.sizes, core.rows\n- flow: core.rows -> core.sizes\n- notes: One pass.\n")


def code_moved(project, sizes=""):
    """A committed catalog of two components and a subsystem of both, then a change to the module of
    core.sizes with the index regenerated. `sizes` is added to the core.sizes entry before the commit."""
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    (project / "src/widget/rows.py").write_text('"""Rows."""\n')
    (project / "tests").mkdir()
    (project / "tests/test_sizes.py").write_text("")
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py") + sizes,
            entry("core.rows", "Build report rows", "src/widget/rows.py"), FLOW)
    commit(project)
    # The new name is one the entry's sentence already speaks of, so the line carries no lead about names
    # (test_changed_names_the_public_names_the_entry_does_not_speak_of).
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n\n\ndef format_count(count):\n    """Format it."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0


def edit_catalog(project, old, new):
    path = project / "docs/components/COMPONENTS.md"
    text = path.read_text()
    assert old in text, old
    path.write_text(text.replace(old, new))
    code, out = tool(project, "write", script=INDEX)
    assert code == 0, out


def rereads(project, *args):
    code, out = tool(project, "changed", "--base", "main", *args, script=INDEX)
    return code, [line for line in out.splitlines() if line.startswith("reread: ")], out


SIZES_MODULES = "- modules: src/widget/sizes.py\n"


@pytest.mark.parametrize("field, line", [
    ("notes", "- notes: parse reads a size back.\n"),
    ("tests", "- tests: tests/test_sizes.py\n"),
    ("in", "- in: a byte count\n"),
    ("out", "- out: text\n"),
    ("distinct_from", "- distinct_from: core.rows\n"),
])
def test_changed_still_asks_for_a_reread_when_only_another_field_was_edited(project, field, line):
    # Issue 50: `review` dates an entry from does, verbs, flow and reread only, so an edit to any other
    # field left the entry on its list while `changed` printed nothing.
    code_moved(project)
    edit_catalog(project, SIZES_MODULES, SIZES_MODULES + line)
    code, lines, out = rereads(project)
    assert code == 0, out
    assert "reread: core.sizes (only %s edited): src/widget/sizes.py" % field in lines, out


def test_changed_names_every_other_field_that_was_edited(project):
    code_moved(project)
    edit_catalog(project, SIZES_MODULES,
                 "- modules: src/widget/sizes.py, src/widget/__init__.py\n- notes: parse reads a size back.\n")
    # The file the entry took in is named beside the one that was edited, though it does not differ itself.
    assert ("reread: core.sizes (only modules, notes edited): src/widget/__init__.py, src/widget/sizes.py"
            in rereads(project)[1])


@pytest.mark.parametrize("old, new", [
    ("- does: Format a byte count\n", "- does: Format and parse a byte count\n"),
    ("- verbs: sizes\n", "- verbs: sizes, parse sizes\n"),
    (SIZES_MODULES, SIZES_MODULES + "- reread: 2026-11-26, read beside the change, still accurate\n"),
    (SIZES_MODULES, SIZES_MODULES + "- flow: read, then format\n"),
])
def test_changed_asks_for_no_reread_of_an_entry_whose_dating_field_was_edited(project, old, new):
    code_moved(project)
    assert "reread: core.sizes (entry not edited): src/widget/sizes.py" in rereads(project)[1]
    edit_catalog(project, old, new)
    assert not [line for line in rereads(project)[1] if line.startswith("reread: core.sizes ")]


def test_changed_takes_an_updated_reread_line_as_an_answer_and_an_old_one_as_none(project):
    code_moved(project, sizes="- reread: 2026-11-01, read at the build, still accurate\n")
    assert "reread: core.sizes (entry not edited): src/widget/sizes.py" in rereads(project)[1], \
        "a reread line that was already there at the base says nothing about this change"
    edit_catalog(project, "2026-11-01, read at the build", "2026-11-26, read beside the new parse")
    assert not [line for line in rereads(project)[1] if line.startswith("reread: core.sizes ")]


def test_changed_asks_for_no_reread_of_an_entry_written_in_the_change(project):
    # The module moves, changed, from the entry that had it to an entry that did not exist at the base.
    code_moved(project)
    (project / "src/widget/units.py").write_text('"""Units."""\n')
    edit_catalog(project, SIZES_MODULES, "- modules: src/widget/units.py\n")
    catalog(project, entry("core.parse", "Read a size back from text", "src/widget/sizes.py"))
    code, lines, out = rereads(project)
    assert code == 0 and not [line for line in lines if "core.parse" in line], out
    assert "reread: core.sizes (only modules edited): src/widget/sizes.py, src/widget/units.py" in lines, out


OLD_REREAD = "- reread: 2026-11-01, read at the build, still accurate\n"


@pytest.mark.parametrize("new, said", [
    ("", "reread removed"),
    ("- reread:\n", "reread removed"),
    ("- reread: \t\n", "reread removed"),
    ("- reread: 2026-11-01, read at the build, still accurate \n", "entry not edited"),
    ("- notes: parse reads a size back.\n", "only notes edited, reread removed"),
])
def test_changed_takes_a_reread_line_deleted_or_emptied_as_no_answer(project, new, said):
    # Review pr-51-r1, F1: any difference in a dating field counted as an answer, so deleting the old line passed
    # the strict form, and `review` then dated the entry from its older does and verbs.
    code_moved(project, sizes=OLD_REREAD)
    assert rereads(project, "--strict")[0] == 1, "the old line, left as it was, answers nothing"
    edit_catalog(project, OLD_REREAD, new)
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert "reread: core.sizes (%s): src/widget/sizes.py" % said in lines, out


def test_review_does_not_date_an_entry_from_an_empty_reread_line(project):
    # The other half of F1: `changed` takes an empty line as no answer, so `review` must not date the entry from it.
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    commit(project)
    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    [lead] = older_than_code(project)
    edit_catalog(project, SIZES_MODULES, SIZES_MODULES + "- reread:\n")
    assert older_than_code(project) == [lead], "an empty line not committed yet is not a reading"
    commit(project)
    assert older_than_code(project) == [lead]
    assert lead.endswith(", when its does and verbs were last edited"), lead


BOTH_MODULES = "- modules: src/widget/sizes.py, src/widget/parse.py\n"
ROWS_MODULES = "- modules: src/widget/rows.py\n"
SYSTEM_LINE = "reread: subsystem.report (entry not edited): its members changed: core.sizes"
STILL_PARSE = "; removed public names still in does or verbs: parse"  # core.sizes says it parses, in two_modules


def two_modules(project, flow=FLOW):
    """A committed catalog where core.sizes holds sizes.py and parse.py, core.rows holds rows.py, and a
    subsystem has both components."""
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    (project / "src/widget/parse.py").write_text('"""Parse sizes."""\n\n\ndef parse(text):\n    """Read a size."""\n')
    (project / "src/widget/rows.py").write_text('"""Rows."""\n')
    catalog(project, entry("core.sizes", "Format and parse a byte count", "src/widget/sizes.py, src/widget/parse.py"),
            entry("core.rows", "Build report rows", "src/widget/rows.py"), flow)
    commit(project)


def test_changed_asks_the_component_that_gave_up_a_deleted_module(project):
    # Review pr-51-r1, F2: the paths were matched against the catalog as it is now, so a module deleted and
    # dropped from `modules:` was nobody's, and the component that lost what it did was not asked.
    two_modules(project)
    (project / "src/widget/parse.py").unlink()
    edit_catalog(project, BOTH_MODULES, SIZES_MODULES)
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ["reread: core.sizes (only modules edited): src/widget/parse.py" + STILL_PARSE, SYSTEM_LINE], out
    edit_catalog(project, "- does: Format and parse a byte count\n", "- does: Format a byte count\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 0 and lines == [SYSTEM_LINE], out


def test_changed_asks_for_a_renamed_module_under_both_of_its_names(project):
    two_modules(project)
    (project / "src/widget/parse.py").rename(project / "src/widget/read.py")
    edit_catalog(project, BOTH_MODULES, "- modules: src/widget/sizes.py, src/widget/read.py\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ["reread: core.sizes (only modules edited): src/widget/parse.py, src/widget/read.py",
                     SYSTEM_LINE], out


@pytest.mark.parametrize("rewritten", [True, False])
def test_changed_asks_both_components_when_a_module_moves_from_one_to_the_other(project, rewritten):
    # The component that gave the module up no longer does what the module did, and the one that took it does
    # more than its sentence says, whether or not the file itself was edited: the owner's ruling of 2026-11-26
    # on Q6 of review pr-51-r1's record. Each line says which names to look for.
    two_modules(project)
    if rewritten:
        (project / "src/widget/parse.py").write_text('"""Parse sizes."""\n\n\ndef parse(text, base=1024):\n    """Read."""\n')
    edit_catalog(project, BOTH_MODULES, SIZES_MODULES)
    edit_catalog(project, ROWS_MODULES, "- modules: src/widget/rows.py, src/widget/parse.py\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ["reread: core.sizes (only modules edited): src/widget/parse.py" + STILL_PARSE,
                     "reread: core.rows (only modules edited): src/widget/parse.py"
                     "; new public names not in does or verbs: parse",
                     "reread: subsystem.report (entry not edited): its members changed: core.sizes, core.rows"], out
    assert rereads(project)[0] == 0, "without --strict a reread line fails nothing"
    edit_catalog(project, "- does: Format and parse a byte count\n", "- does: Format a byte count\n")
    edit_catalog(project, "- does: Build report rows\n", "- does: Build report rows and parse a size\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 0 and [line.split(":")[1] for line in lines] == [" subsystem.report (entry not edited)"], out


def test_changed_asks_nothing_when_modules_names_the_same_files_another_way(project):
    two_modules(project)
    edit_catalog(project, BOTH_MODULES, "- modules: src/widget/parse.py, src/widget/sizes.py\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 0 and lines == [], out
    edit_catalog(project, "- modules: src/widget/parse.py, src/widget/sizes.py\n", "- modules: src/widget/\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 1, "a folder that takes in __init__.py and rows.py is not the same files"
    assert lines[0] == "reread: core.sizes (only modules edited): src/widget/__init__.py, src/widget/rows.py", out


def test_changed_asks_a_component_that_takes_in_a_module_no_entry_held(project):
    two_modules(project)
    edit_catalog(project, ROWS_MODULES, "- modules: src/widget/rows.py, src/widget/__init__.py\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ["reread: core.rows (only modules edited): src/widget/__init__.py",
                     "reread: subsystem.report (entry not edited): its members changed: core.rows"], out


@pytest.mark.parametrize("line, new, said", [
    ("- owner_team: café\n", "- owner_team: Δ\n", "only owner_team edited"),
    ("- audit-owner: café\n", "- audit-owner: Δ\n", "only other lines edited"),
    ("- owner2: café\n", "- owner2: Δ\n", "only other lines edited"),
    ("Kept for the report.\n", "Kept for the report and the export.\n", "only other lines edited"),
    ("- notes: One.\n- owner2: café\n", "- notes: Two.\n- owner2: Δ\n", "only notes, other lines edited"),
    ("- notes: One.\n", "- notes: One.\n\n\n", "entry not edited"),
    # Review pr-51-r2, F7: a comment, or a line that starts with # and is no heading, does not end the entry.
    ("<!-- Maintainer note -->\n- owner2: café\n", "<!-- Maintainer note -->\n- owner2: Δ\n", "only other lines edited"),
    ("#ticket\nKept for the report.\n", "#ticket\nKept for the export.\n", "only other lines edited"),
    # F8: the parser's own keys are no field's name, so a field named like one of them is a field.
    ("- _rest: red\n", "- _rest: blue\n", "only _rest edited"),
    ("- _repeated: red\n", "- _repeated: blue\n", "only _repeated edited"),
    ("\n## The rows\n\nWhat builds a row.\n", "\n## The rows\n\nWhat builds a row, by area.\n", "entry not edited"),
])
def test_changed_says_an_entry_was_edited_when_the_edited_line_is_no_field(project, line, new, said):
    # Review pr-51-r1, F3: a line whose key the field reader does not take (a digit, a hyphen), or that has no
    # key, was read as nothing, so the label said `entry not edited` of an entry that was. What follows the
    # next heading is the catalog's, not the entry's, and blank space is no edit.
    code_moved(project, sizes=line)
    edit_catalog(project, line, new)
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert "reread: core.sizes (%s): src/widget/sizes.py" % said in lines, out


def test_show_prints_a_field_named_like_the_parsers_own_key(project):
    code_moved(project, sizes="- _rest: red\n")
    assert "- _rest: red\n" in tool(project, "show", "core.sizes", script=INDEX)[1]


def test_changed_asks_both_components_when_a_folder_outside_the_package_moves(project):
    # Review pr-51-r2, F1: the regrouped files were looked for among the counted modules and the files a
    # modules line names one by one, so a file reached only through a folder outside the package was not seen.
    # Any file git tracks counts, whatever its kind.
    for name in ("a", "b"):
        (project / "src/widget" / (name + ".py")).write_text('"""%s."""\n' % name)
    (project / "tools/export").mkdir(parents=True)
    (project / "tools/export/format.py").write_text('"""Format."""\n\n\ndef export():\n    pass\n')
    (project / "tools/export/columns.json").write_text("[]\n")
    catalog(project, entry("core.alpha", "Do alpha", "src/widget/a.py, tools/export/"),
            entry("core.beta", "Do beta", "src/widget/b.py"))
    commit(project)
    edit_catalog(project, "- modules: src/widget/a.py, tools/export/\n", "- modules: src/widget/a.py\n")
    edit_catalog(project, "- modules: src/widget/b.py\n", "- modules: src/widget/b.py, tools/export/\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ["reread: core.alpha (only modules edited): tools/export/columns.json, tools/export/format.py",
                     "reread: core.beta (only modules edited): tools/export/columns.json, tools/export/format.py"
                     "; new public names not in does or verbs: export"], out


@pytest.mark.parametrize("spelling", ["./src/widget/a.py", "src/./widget//a.py"])
def test_changed_reads_two_spellings_of_a_path_as_one_file(project, spelling):
    # Review pr-51-r2, F2: the catalog check takes both spellings, and the paths were compared as written: a
    # spelling changed alone asked for a reread of both, and with ./ at the base an edit to the file asked nothing.
    (project / "src/widget/a.py").write_text('"""a."""\n')
    catalog(project, entry("core.alpha", "Do alpha", "src/widget/a.py"))
    commit(project)
    edit_catalog(project, "- modules: src/widget/a.py\n", "- modules: %s\n" % spelling)
    code, lines, out = rereads(project, "--strict")
    assert code == 0 and lines == [], out
    commit(project)
    (project / "src/widget/a.py").write_text('"""a."""\n# edited\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    code, lines, out = rereads(project, "--strict")
    assert code == 1 and lines == ["reread: core.alpha (entry not edited): src/widget/a.py"], out


def test_a_field_line_under_a_later_heading_is_not_the_entrys(project):
    # Review pr-51-r2, F3: an entry was read up to the next ###, so a reread: line under a heading that is no
    # entry answered the component before it in `changed` and dated it in `review`.
    code_moved(project)
    path = project / "docs/components/COMPONENTS.md"
    path.write_text(path.read_text() + "\n### core.last\n- does: Hold the package\n- verbs: package\n"
                                       "- status: canonical\n- modules: src/widget/__init__.py\n")
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    (project / "src/widget/__init__.py").write_text('"""widget, edited."""\n')
    path.write_text(path.read_text() + "\n## Release checklist\n\n- reread: confirm release notes\n- modules: nowhere.py\n")
    code, out = tool(project, "write", script=INDEX)
    assert code == 0, out
    assert "- modules: nowhere.py\n- uses:" not in path.read_text(), "write adds its lines to entries only"
    code, lines, out = rereads(project, "--strict")
    assert code == 1 and "reread: core.last (entry not edited): src/widget/__init__.py" in lines, out
    commit(project)
    assert any(line.startswith("core.last: 1 commit(s) to its modules since ") for line in older_than_code(project))


def test_changed_reads_the_names_of_a_source_file_in_its_own_encoding(project):
    # Review pr-51-r2, F4: the base text was decoded as UTF-8, encoded again and then read by its coding line,
    # so the plain `changed`, which fails nothing, exited 1 on a valid file that is not UTF-8.
    source = '# coding: shift_jis\n"""日本語"""\n\n\ndef run(): pass\n'.encode("shift_jis")
    (project / "src/widget/jp.py").write_bytes(source)
    catalog(project, entry("core.jp", "Run it", "src/widget/jp.py"))
    commit(project)
    (project / "src/widget/jp.py").write_bytes(source + b"\n\ndef walk(): pass\n")
    code, out = tool(project, "write", script=INDEX)
    assert code == 0, out
    code, lines, out = rereads(project)
    assert code == 0, out
    assert lines == ["reread: core.jp (entry not edited): src/widget/jp.py; new public names not in does or verbs: walk"], out


def test_changed_asks_for_a_file_whose_name_git_would_quote(project):
    # Review pr-51-r2, F5: git writes a name that holds a quote inside quotes, with a backslash before it, and
    # that spelling is no file of any component.
    name = 'src/widget/say"hello.py'
    (project / name).write_text('"""Say."""\n')
    (project / "src/widget/été.py").write_text('"""Summer."""\n')
    catalog(project, entry("core.say", "Say hello", name), entry("core.summer", "Say summer", "src/widget/été.py"))
    commit(project)
    (project / name).write_text('"""Say."""\n# a comment\n')
    (project / "src/widget/été.py").write_text('"""Summer."""\n# a comment\n')
    (project / 'src/widget/new"one.py').write_text('"""New."""\n')
    code, out = tool(project, "write", script=INDEX)
    assert code == 0, out
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ['reread: core.say (entry not edited): src/widget/say"hello.py',
                     "reread: core.summer (entry not edited): src/widget/été.py"], out
    assert 'fail: no component: src/widget/new"one.py ' in out, out


@pytest.mark.parametrize("ignored, alpha, beta", [
    # A file a modules line names one by one, outside the package.
    ("tools/gen.py", "src/widget/a.py, tools/gen.py", "src/widget/b.py, tools/gen.py"),
    # A package module reached through a folder: it is counted, so it needs a component.
    ("src/widget/gen/out.py", "src/widget/a.py, src/widget/gen/", "src/widget/b.py, src/widget/gen/"),
])
def test_changed_asks_both_components_when_a_file_git_ignores_moves(project, ignored, alpha, beta):
    # Close review close-r1, F1: the regrouped files were looked for among the files git tracks only, so a
    # file that git ignores moved from one entry to another and `changed --strict` asked neither.
    (project / ".gitignore").write_text(ignored + "\n")
    (project / ignored).parent.mkdir(parents=True, exist_ok=True)
    (project / ignored).write_text('"""Generated."""\n')
    for name in ("a", "b"):
        (project / "src/widget" / (name + ".py")).write_text('"""%s."""\n' % name)
    catalog(project, entry("core.alpha", "Do alpha", alpha), entry("core.beta", "Do beta", "src/widget/b.py"))
    commit(project)
    edit_catalog(project, "- modules: %s\n" % alpha, "- modules: src/widget/a.py\n")
    edit_catalog(project, "- modules: src/widget/b.py\n", "- modules: %s\n" % beta)
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ["reread: core.alpha (only modules edited): %s" % ignored,
                     "reread: core.beta (only modules edited): %s" % ignored], out


@pytest.mark.parametrize("move", ["named to folder", "folder to named"])
def test_changed_asks_both_components_when_an_ignored_file_moves_between_a_name_and_a_folder(project, move):
    # Review pr-53-r1, F2: the files a modules line names were taken from the entry being asked about only, so
    # the entry that takes the file through a folder never saw it.
    (project / ".gitignore").write_text("tools/gen/out.py\n")
    (project / "tools/gen").mkdir(parents=True)
    (project / "tools/gen/out.py").write_text('"""Generated."""\n')
    named, folder = "src/widget/a.py, tools/gen/out.py", "src/widget/b.py, tools/gen/"
    alpha, beta = (named, "src/widget/b.py") if move == "named to folder" else ("src/widget/a.py", folder)
    for name in ("a", "b"):
        (project / "src/widget" / (name + ".py")).write_text('"""%s."""\n' % name)
    catalog(project, entry("core.alpha", "Do alpha", alpha), entry("core.beta", "Do beta", beta))
    commit(project)
    edit_catalog(project, "- modules: %s\n" % alpha,
                 "- modules: %s\n" % ("src/widget/a.py" if move == "named to folder" else named))
    edit_catalog(project, "- modules: %s\n" % beta,
                 "- modules: %s\n" % (folder if move == "named to folder" else "src/widget/b.py"))
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ["reread: core.alpha (only modules edited): tools/gen/out.py",
                     "reread: core.beta (only modules edited): tools/gen/out.py"], out


def test_changed_asks_both_components_when_a_tracked_link_without_its_target_moves(project):
    # Review pr-53-r1, F3: a file was kept only when it opened as a regular file, so a link git tracks whose
    # target is gone was no file of either entry.
    (project / "tools/gen").mkdir(parents=True)
    os.symlink("missing.json", project / "tools/gen/latest")
    for name in ("a", "b"):
        (project / "src/widget" / (name + ".py")).write_text('"""%s."""\n' % name)
    catalog(project, entry("core.alpha", "Do alpha", "src/widget/a.py, tools/gen/"),
            entry("core.beta", "Do beta", "src/widget/b.py"))
    commit(project)
    edit_catalog(project, "- modules: src/widget/a.py, tools/gen/\n", "- modules: src/widget/a.py\n")
    edit_catalog(project, "- modules: src/widget/b.py\n", "- modules: src/widget/b.py, tools/gen/\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert lines == ["reread: core.alpha (only modules edited): tools/gen/latest",
                     "reread: core.beta (only modules edited): tools/gen/latest"], out


def test_changed_reads_a_project_whose_folder_name_holds_a_line_break(tmp_path):
    # Review pr-53-r1, F4: only the file's own name was looked at for a line break, and the folder of the project
    # under the top of the checkout was put before it afterwards, so git was asked for two names.
    outer = tmp_path / "outer"
    outer.mkdir()
    project = new_project(outer)
    shutil.move(str(project / ".git"), str(outer / ".git"))
    moved = outer / "team\nwidget"
    project.rename(moved)
    (moved / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(moved, entry("core.sizes", "Format sizes", "src/widget/sizes.py"))
    commit(outer)
    (moved / "src/widget/sizes.py").write_text('"""Sizes."""\n\n\ndef parse(): pass\n')
    assert tool(moved, "write", script=INDEX)[0] == 0
    code, lines, out = rereads(moved)
    assert code == 0, out
    assert lines == ["reread: core.sizes (entry not edited): src/widget/sizes.py; "
                     "new public names not in does or verbs: parse"], out


def test_help_prints_on_a_stream_that_takes_ascii_only(project):
    # Review pr-53-r1, F6: argparse prints the help before the streams were told to escape what they cannot write.
    shutil.copy(project / INDEX, project / "scripts/índice.py")
    shutil.copy(project / INDEX_SETTINGS, project / "scripts/índice.settings.json")
    env = {**os.environ, "PYTHONIOENCODING": "ascii", "XDG_CACHE_HOME": str(project.parent / "cache")}
    done = subprocess.run([sys.executable, "scripts/índice.py", "--help"], cwd=project, capture_output=True,
                          text=True, env=env)
    assert done.returncode == 0, done.stderr
    assert "usage: \\xedndice.py" in done.stdout, done.stdout


@pytest.mark.parametrize("control", ["\r", "\n"])
def test_changed_reads_a_file_whose_name_holds_a_line_break(project, control):
    # Close review close-r1, F2: git's -z listings were read as text, which turns a carriage return into a line
    # break, so plain `changed` could not read the file at the base and exited 1. A line break in a name broke
    # the request to git for the file's bytes.
    name = "src/widget/a%sfile.py" % control
    (project / "src/widget/a.py").write_text('"""A."""\n')
    (project / name).write_text('"""Odd."""\n\n\ndef odd(): pass\n')
    (project / ("assets/pic%sone.png" % control)).parent.mkdir()
    (project / ("assets/pic%sone.png" % control)).write_bytes(b"x")
    catalog(project, entry("core.aa", "Do a", "src/widget/"))
    commit(project)
    (project / name).write_text('"""Odd."""\n\n\ndef odd(): pass\n\n\ndef even(): pass\n')
    code, out = tool(project, "write", script=INDEX)
    assert code == 0, out
    code, lines, out = rereads(project)
    assert code == 0, out
    # The test reads the output as text, which turns the carriage return into a line break as well.
    assert "reread: core.aa (entry not edited): src/widget/a\nfile.py; new public names not in does or verbs: " \
           "even" in out, out


def test_changed_prints_a_file_whose_name_is_not_utf8(project):
    # Close review close-r1, F2: a name git does not spell as UTF-8 stopped plain `changed` with a decoding
    # error, even for a file no component holds. macOS refuses such a name, and the test with it.
    raw = os.fsencode(str(project / "src/widget")) + b"/caf\xe9.py"
    try:
        with open(raw, "wb") as handle:
            handle.write(b'"""Cafe."""\n')
    except OSError as exc:
        pytest.skip("the file system refuses a name that is not UTF-8: %s" % exc)
    (project / "assets").mkdir()
    with open(os.fsencode(str(project / "assets")) + b"/pic\xff.png", "wb") as handle:
        handle.write(b"x")
    catalog(project, entry("core.aa", "Do a", "src/widget/"))
    commit(project)
    with open(raw, "ab") as handle:
        handle.write(b"\n\ndef brew(): pass\n")
    code, out = tool(project, "write", script=INDEX)
    assert code == 0, out
    code, lines, out = rereads(project)
    assert code == 0, out
    assert lines == ["reread: core.aa (entry not edited): src/widget/caf\\udce9.py; "
                     "new public names not in does or verbs: brew"], out


def test_changed_and_review_agree_on_a_reread_line_after_a_no_break_space(project):
    # Review pr-51-r2, F6: `changed` took the line as an answer and `review` did not date the entry from it.
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    commit(project)
    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    assert rereads(project, "--strict")[0] == 1
    edit_catalog(project, SIZES_MODULES, SIZES_MODULES + "- reread:\u00a0still accurate\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 0 and lines == [], out
    commit(project)
    assert older_than_code(project) == []
    edit_catalog(project, "- reread:\u00a0still accurate\n", "- reread:\u00a0\n")
    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten again."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    assert len(older_than_code(project)) == 1, "a line of blanks only dates nothing, whatever the blank"


def test_review_dates_an_entry_in_a_sha256_repository(tmp_path):
    # Review pr-51-r1, F5: the commit id of a blame line was read as 40 digits, so in a repository made with
    # --object-format=sha256 (64 digits) no entry had a date and `review` listed no description as old.
    project = new_project(tmp_path, "--object-format=sha256")
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"))
    commit(project)
    assert len(subprocess.run(["git", "rev-parse", "HEAD"], cwd=project, capture_output=True, text=True,
                              check=True).stdout.strip()) == 64
    assert older_than_code(project) == []
    (project / "src/widget/sizes.py").write_text('"""Sizes, rewritten."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    [lead] = older_than_code(project)
    assert lead.startswith("core.sizes: 1 commit(s) to its modules since "), lead
    code, lines, out = rereads(project, "--strict")
    assert code == 0 and lines == [], out


def names_changed(project, source, does="Format a byte count"):
    """A committed catalog as in code_moved, then sizes.py rewritten as `source`; the line of core.sizes."""
    code_moved(project)
    if does != "Format a byte count":
        edit_catalog(project, "- does: Format a byte count\n", "- does: %s\n" % does)
        commit(project)
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n' + source)
    assert tool(project, "write", script=INDEX)[0] == 0
    code, lines, out = rereads(project)
    assert code == 0, out
    return next(line for line in lines if line.startswith("reread: core.sizes ")).partition("src/widget/sizes.py")[2]


def test_changed_names_the_public_names_the_entry_does_not_speak_of(project):
    # Issue 50, part 4: most descriptions found wrong after a reread lacked a public name the change had added.
    # A name is spoken of when each of its words is in does or verbs, whatever its case and underscores; a
    # private name and a method ask for no verb.
    lead = names_changed(project, "\n\ndef parse(text):\n    pass\n\n\ndef format_count(count):\n    pass\n"
                                  "\n\ndef byte_counts():\n    pass\n\n\nclass ByteFormat:\n    def render(self):\n"
                                  "        pass\n\n\nclass SizeTable:\n    pass\n\n\ndef _helper():\n    pass\n")
    assert lead == "; new public names not in does or verbs: SizeTable, parse"


def test_changed_names_the_removed_names_the_entry_still_speaks_of(project):
    # The other half: a name the change removed that does or verbs still speak of is a sentence that may say too
    # much. A removed name they never spoke of is nothing to look for, and neither is one with no word of its own.
    lead = names_changed(project, "\n\ndef unit(count):\n    pass\n")
    assert lead == "; new public names not in does or verbs: unit", "format_count went, and no line says so: " + lead
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n\n\ndef format_count(count):\n    pass\n'
                                                 '\n\ndef parse(text):\n    pass\n\n\ndef to():\n    pass\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    commit(project)
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    code, lines, out = rereads(project, "--strict")
    assert code == 1, out
    assert "reread: core.sizes (entry not edited): src/widget/sizes.py; removed public names still in does or verbs: " \
           "format_count" in lines, out


def test_changed_finds_a_class_the_entry_names_in_its_own_spelling(project):
    # Review pr-51-r2, F9: the identifier was split at its capital humps and the prose was not, and a run of
    # capitals was not split from the word after it, so a class the sentence names was listed as left out.
    does = "Format a byte count, call RenderReport and start an HTTP server"
    lead = names_changed(project, "\n\ndef format_count(count):\n    pass\n\n\nclass RenderReport:\n    pass\n"
                                  "\n\nclass HTTPServer:\n    pass\n\n\nclass URLTable:\n    pass\n", does=does)
    assert lead == "; new public names not in does or verbs: URLTable"


def test_changed_does_not_name_a_public_name_that_moved_inside_the_component(project):
    two_modules(project)
    (project / "src/widget/parse.py").write_text('"""Parse sizes."""\n')
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n\n\ndef parse(text):\n    """Read a size."""\n')
    assert tool(project, "write", script=INDEX)[0] == 0
    code, lines, out = rereads(project)
    assert lines[0] == "reread: core.sizes (entry not edited): src/widget/parse.py, src/widget/sizes.py", out


def test_changed_shows_eight_names_and_counts_the_rest(project):
    lead = names_changed(project, "".join("\n\ndef probe_%02d():\n    pass\n" % n for n in range(11)))
    assert lead == "; new public names not in does or verbs: " + ", ".join("probe_%02d" % n for n in range(8)) + ", +3 more"



def test_changed_tells_a_subsystem_of_a_member_removed_with_its_code(project):
    two_modules(project, flow=FLOW.replace("- flow: core.rows -> core.sizes\n", ""))
    for name in ("sizes.py", "parse.py"):
        (project / "src/widget" / name).unlink()
    path = project / "docs/components/COMPONENTS.md"
    text = path.read_text()
    start = text.index("\n### core.sizes\n")
    path.write_text(text[:start] + text[text.index("\n### ", start + 1):])
    edit_catalog(project, "- components: core.sizes, core.rows\n", "- components: core.rows\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 0, out
    assert lines == ["reread: subsystem.report (only components edited): its members changed: core.sizes"], out


@pytest.mark.parametrize("old, new, said", [
    ("- notes: One pass.\n", "- notes: One pass.\n", "entry not edited"),
    ("- notes: One pass.\n", "- notes: One pass over the rows.\n", "only notes edited"),
    ("- components: core.sizes, core.rows\n", "- components: core.rows, core.sizes\n", "only components edited"),
    ("- flow: core.rows -> core.sizes\n", "", "flow removed"),
    ("- flow: core.rows -> core.sizes\n", "- flow: core.rows -> core.sizes -> core.rows\n", None),
    ("- does: Print sizes\n", "- does: Print and parse sizes\n", None),
    ("- notes: One pass.\n", "- notes: One pass.\n- reread: 2026-11-26, read beside core.sizes, still accurate\n", None),
])
def test_changed_reads_a_subsystem_whose_member_moved_by_the_same_fields(project, old, new, said):
    code_moved(project)
    edit_catalog(project, "- does: Format a byte count\n", "- does: Format and parse a byte count\n")
    edit_catalog(project, old, new)
    code, lines, out = rereads(project)
    assert code == 0, out
    expected = ["reread: subsystem.report (%s): its members changed: core.sizes" % said] if said else []
    assert lines == expected, out
    assert ("1 to reread, 1 of them subsystem(s)" if said else "0 to reread\n") in out, out
    # A subsystem's line is advice: with its member answered, the strict form prints the same and accepts it.
    assert tool(project, "changed", "--base", "main", "--strict", script=INDEX) == (0, out)


def test_strict_changed_fails_while_a_components_reread_line_is_unanswered(project):
    component = "reread: core.sizes (entry not edited): src/widget/sizes.py"
    system = "reread: subsystem.report (entry not edited): its members changed: core.sizes"
    asked = "note: --strict fails while a component's reread: line is unanswered"
    code_moved(project)
    code, lines, out = rereads(project)
    assert code == 0 and lines == [component, system], out
    assert "0 to fix, 0 warning(s), 2 to reread, 1 of them subsystem(s)\n" in out, out
    assert "--strict" not in out, "the plain form says nothing about the strict one"
    code, lines, out = rereads(project, "--strict")
    assert code == 1 and lines == [component, system] and asked in out, out

    # The subsystem answered and the component not: still refused, for the component.
    edit_catalog(project, "- notes: One pass.\n", "- notes: One pass.\n- reread: 2026-11-26, flow unchanged\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 1 and lines == [component] and asked in out and "1 to reread\n" in out, out
    # The component answered, without a sentence edited: accepted.
    edit_catalog(project, SIZES_MODULES, SIZES_MODULES + "- reread: 2026-11-26, read beside parse, still accurate\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 0 and lines == [] and "0 to reread\n" in out and "note:" not in out, out


def test_strict_changed_prints_a_subsystems_reread_line_and_does_not_fail_on_it(project):
    # A component many subsystems share would ask each of them for an answer on every change: the line is advice.
    code_moved(project)
    edit_catalog(project, SIZES_MODULES, SIZES_MODULES + "- reread: 2026-11-26, read beside parse, still accurate\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 0, out
    assert lines == ["reread: subsystem.report (entry not edited): its members changed: core.sizes"], out
    assert "1 to reread, 1 of them subsystem(s)\n" in out and "note:" not in out, out


def test_strict_changed_accepts_a_change_that_touches_no_component(project):
    code_moved(project)
    commit(project)
    (project / "README.md").write_text("widget\n")
    code, lines, out = rereads(project, "--strict")
    assert code == 0 and lines == [] and "0 to fix, 0 warning(s), 0 to reread" in out, out


def section(out, title):
    """The lines of one group of `review`, its heading included."""
    start = out.index("## " + title)
    return out[start:out.index("\n\n", start)].splitlines()


@pytest.mark.parametrize("count", [True, False])
def test_review_reads_the_counted_folders_for_names_and_docstrings(project, count):
    extra_tools(project, count=count)
    (project / "tools/bare.py").write_text("def unnamed():\n    return 1\n")
    (project / "src/widget/sizes.py").write_text('"""Sizes."""\n\n\ndef report(rows):\n    """Print rows."""\n')
    catalog(project, entry("core.sizes", "Format a byte count", "src/widget/sizes.py"),
            entry("tools.report", "Print a size report", "tools/"))
    commit(project)
    out = tool(project, "review", script=INDEX)[1]
    same = section(out, "The same public name in two or three components")
    bare = section(out, "Modules with no docstring")
    if count:
        assert [line for line in same[1:] if line.startswith("report")
                and "src/widget/sizes.py (core.sizes)" in line and "tools/report.py (tools.report)" in line], same
        assert "tools/bare.py" in bare, bare
        assert "from 3 component(s) and 4 module(s)" in out, out.splitlines()[-1]
    else:
        assert same == ["## The same public name in two or three components (a duplicate?) (0)"], same
        assert "tools/bare.py" not in bare, bare
        assert "from 3 component(s) and 2 module(s)" in out, out.splitlines()[-1]


@pytest.mark.parametrize("count", [True, False])
def test_review_sizes_a_component_by_its_counted_modules(project, count):
    extra_tools(project, count=count)
    for number in range(12):
        (project / ("tools/part%d.py" % number)).write_text('"""Part %d."""\n' % number)
    catalog(project, entry("tools.report", "Print a size report", "tools/"))
    commit(project)
    rows = section(tool(project, "review", script=INDEX)[1], "Components that cover more than 12 modules")
    assert bool([line for line in rows[1:] if line.startswith("tools.report: 13 modules")]) == count, rows


@pytest.mark.parametrize("count", [True, False])
def test_review_labels_an_entry_point_in_a_counted_folder(project, count):
    extra_tools(project, count=count)
    (project / "tools/cli.py").write_text('"""Command line."""\n\n\ndef main():\n    """Run."""\n')
    catalog(project, entry("tools.cli", "Run the report from the command line", "tools/cli.py"))
    commit(project)
    rows = section(tool(project, "review", script=INDEX)[1], "Components nothing in the package imports")
    assert ("tools.cli (defines main)" in rows) == count and ("tools.cli" in rows) != count, rows


# --- Starter rules where there is no phase tool, and settings files a script cannot use.

PHASE_TOOL = ".claude/skills/process-phase/scripts/phase_tool.py"


def test_a_rule_about_plans_is_skipped_where_the_phase_tool_is_not(project):
    rules_without_examples(project)
    (project / PHASE_TOOL).unlink()
    seen = fake_gnd(project, cases={"schema_version": "gnd-guarded-cases/1", "rules": []})
    code, out = tool(project, "test", script=RULES)
    assert code == 0, out
    assert ("skip: %s: a rule about plans, and .claude/skills/process-phase/scripts/phase_tool.py is not here "
            "(it is judged where the phase tool is installed)\n" % PLAN_RULE) in out
    assert out.rstrip().endswith("; 1 rule(s) about plans skipped"), out
    assert rule_ids(json.loads((seen / "synth-model.json").read_text())) == STARTER_IDS, "not given to gnd synth"
    code, out = tool(project, "test", "--format", "json", script=RULES)
    assert {"level": "skip", "text": "%s: a rule about plans, and .claude/skills/process-phase/scripts/phase_tool.py "
            "is not here (it is judged where the phase tool is installed)" % PLAN_RULE} in json.loads(out)["results"]


def test_a_rule_that_is_not_about_plans_still_names_only_known_facts(project):
    layered(project)
    (project / PHASE_TOOL).unlink()
    path = project / "docs/components/rules.json"
    rules = json.loads(path.read_text())
    rules["rules"].append({"id": "tasks_are_planned", "level": "should", "type": "guarded",
                           "antecedent": [{"fact_type": "component_is_listed", "bind": {"component": "$a"}}],
                           "consequent": {"atom": {"fact_type": "component_is_listed", "bind": {"component": "$a"}}},
                           "examples": {"fails": {"task_in_plan": [{"task": "01-01-T1", "plan": "01-01"}]}}})
    path.write_text(json.dumps(rules))
    fake_gnd(project)
    code, out = tool(project, "test", script=RULES)
    assert code == 1, out
    assert "wrong: tasks_are_planned: the failing example 1 names task_in_plan, which no fact type of this project is" in out


@pytest.mark.parametrize("script, settings", [
    (INDEX, INDEX_SETTINGS), (RULES, RULES_SETTINGS), (PHASE_TOOL, PHASE_TOOL.replace(".py", ".settings.json"))])
@pytest.mark.parametrize("text, says", [('{"no_such_setting": 1}', "unknown setting(s): no_such_setting"),
                                         ("{", "not valid JSON"), ("[]", "the settings must be a JSON object")])
def test_a_settings_file_the_script_cannot_use_exits_2(project, script, settings, text, says):
    (project / settings).write_text(text)
    args = {INDEX: ("--check",), RULES: ("test",), PHASE_TOOL: ("status",)}[script]
    done = run_index(project, *args, script=script)
    assert done.returncode == 2, done.stdout + done.stderr
    assert says in done.stdout + done.stderr and settings.rsplit("/", 1)[1] in done.stdout + done.stderr
    assert "Traceback" not in done.stderr, done.stderr


@pytest.mark.parametrize("args", [("status",), ("check", "--roadmap"), ("roadmap", "list")])
def test_phase_tool_reports_a_bad_settings_file_in_one_envelope(project, args):
    (project / PHASE_TOOL.replace(".py", ".settings.json")).write_text('{"planing_dir": "x"}')
    done = run_index(project, "--format", "json", *args, script=PHASE_TOOL)
    assert done.returncode == 2, done.stdout + done.stderr
    envelope = json.loads(done.stdout)  # one JSON object, nothing before or after it
    assert envelope["ok"] is False and envelope["error"]["code"] == "SETTINGS", envelope
    assert "phase_tool.settings.json: unknown setting(s): planing_dir" in envelope["error"]["message"]
    assert envelope["tool"] == "phase_tool." + args[0]


def test_the_phase_tool_can_be_loaded_with_a_bad_settings_file(project, monkeypatch):
    (project / PHASE_TOOL.replace(".py", ".settings.json")).write_text('{"planing_dir": "x"}')
    monkeypatch.chdir(project)
    spec = importlib.util.spec_from_file_location("phase_tool_loaded", project / PHASE_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # no SystemExit: a caller that reads its fact types is not stopped
    assert module.FACT_TYPES and "unknown setting(s): planing_dir" in module.SETTINGS_ERROR



@pytest.mark.parametrize("script, settings, text, says", [
    (INDEX, INDEX_SETTINGS, '{"verb_list": []}', "verb_list must be a string"),
    (INDEX, INDEX_SETTINGS, '{"extra_source_dirs": "tools"}', "extra_source_dirs must be a list of strings"),
    (RULES, RULES_SETTINGS, '{"index_script": 7}', "index_script must be a string"),
    (PHASE_TOOL, PHASE_TOOL.replace(".py", ".settings.json"), '{"package_prefix": 7}', "package_prefix must be a string"),
    (PHASE_TOOL, PHASE_TOOL.replace(".py", ".settings.json"), '{"process_skill": null}', "process_skill must be a string"),
    (PHASE_TOOL, PHASE_TOOL.replace(".py", ".settings.json"), '{"phase_gaps": 1}', "phase_gaps must be true or false"),
    (PHASE_TOOL, PHASE_TOOL.replace(".py", ".settings.json"), '{"skill_roots": [7]}', "skill_roots must be a list of strings"),
])
def test_a_setting_of_the_wrong_type_exits_2(project, script, settings, text, says):
    (project / settings).write_text(text)
    args = {INDEX: ("--check",), RULES: ("init", "--print"), PHASE_TOOL: ("--format", "json", "status")}[script]
    done = run_index(project, *args, script=script)
    assert done.returncode == 2, done.stdout + done.stderr
    assert says in done.stdout + done.stderr and "Traceback" not in done.stderr, done.stdout + done.stderr
    if script == PHASE_TOOL:
        assert json.loads(done.stdout)["error"]["code"] == "SETTINGS"


@pytest.mark.parametrize("args, tool_name, as_json", [
    (("--for=json", "status"), "status", True),            # an abbreviation the parser accepts
    (("--format", "json", "--root", "status", "check", "--roadmap"), "check", True),  # a command word as a value
    (("--format=json", "status", "--format", "md"), "status", False),  # the last one wins in the parser
])
def test_the_settings_envelope_follows_the_parsed_command_line(project, args, tool_name, as_json):
    (project / PHASE_TOOL.replace(".py", ".settings.json")).write_text('{"planing_dir": "x"}')
    done = run_index(project, *args, script=PHASE_TOOL)
    assert done.returncode == 2, done.stdout + done.stderr
    if as_json:
        envelope = json.loads(done.stdout)
        assert envelope["tool"] == "phase_tool." + tool_name and envelope["error"]["code"] == "SETTINGS"
    else:
        assert done.stdout.startswith("phase_tool.%s: FAILED\nerror SETTINGS: " % tool_name), done.stdout
