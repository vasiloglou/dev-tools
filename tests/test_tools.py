"""Tests for the scripts a project runs after a sync: the phase state tool, the component
index and the phase-selection plugin. Each test works in a new project made by the sync."""
import importlib.util
import json
import os
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
