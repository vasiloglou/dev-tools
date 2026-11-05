"""Tests for the scripts a project runs after a sync: the phase state tool, the component
index and the phase-selection plugin. Each test works in a new project made by the sync."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync", ROOT / "devtools/sync.py")
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)

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
    proc = subprocess.run([sys.executable, script, *args], cwd=project, capture_output=True, text=True)
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
