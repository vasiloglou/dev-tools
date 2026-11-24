"""Tests for the Claude Code plugins in plugins/, which devtools/build_plugins.py writes from
the skills. Scripts that run from a plugin install read the project's settings in .devtools/;
each test copies a plugin out of the repository, as Claude Code's install cache does, and runs
its scripts in a new git project."""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_plugins", ROOT / "devtools/build_plugins.py")
build_plugins = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_plugins)
PLUGINS = sorted(build_plugins.PLUGINS)


def markdown(plugin: str):
    return sorted((ROOT / "plugins" / plugin).rglob("*.md"))


@pytest.fixture
def installed(tmp_path):
    """Copy a plugin out of the repository (a cache install) and make an empty git project."""
    def install(plugin: str) -> tuple[Path, Path]:
        copy = tmp_path / "cache" / plugin
        shutil.copytree(ROOT / "plugins" / plugin, copy)
        project = tmp_path / "project"
        project.mkdir(exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=project, check=True)
        (project / ".devtools").mkdir(exist_ok=True)
        return copy, project
    return install


def run(project: Path, script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], cwd=project, capture_output=True, text=True)


def test_the_plugins_are_what_a_build_writes():
    assert build_plugins.main(["--check"]) == 0, "plugins/ is stale: run python3 devtools/build_plugins.py"


def test_the_marketplace_lists_each_plugin_folder():
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert [p["source"] for p in market["plugins"]] == [f"./plugins/{name}" for name in build_plugins.PLUGINS]
    assert sorted(p.name for p in (ROOT / "plugins").iterdir() if p.is_dir()) == PLUGINS
    for entry in market["plugins"]:
        manifest = json.loads((ROOT / entry["source"] / ".claude-plugin/plugin.json").read_text())
        assert manifest["name"] == entry["name"]


@pytest.mark.parametrize("plugin", PLUGINS)
def test_each_skill_is_named_after_its_folder(plugin):
    skills = sorted((ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md"))
    assert skills
    for path in skills:
        name = re.search(r"^name: (\S+)$", path.read_text(), re.M).group(1)
        assert name == path.parent.name
        assert f"Installed from the `{plugin}` plugin" in path.read_text()
        # Codex installs the same plugin but leaves ${CLAUDE_PLUGIN_ROOT} empty: the note says what it is.
        assert "two levels above this file" in path.read_text() and "Codex leaves it empty" in path.read_text()


@pytest.mark.parametrize("plugin", PLUGINS)
def test_no_text_points_into_a_synced_copy(plugin):
    for path in markdown(plugin):
        text = path.read_text()
        assert "{{devtools:" not in text, path
        assert not re.search(r"\.claude/(skills|agents)/[\w-]+", text), path
        assert "references/project.md" not in text, path
        # A plugin reads each script's settings from the project's .devtools/, never beside the script.
        assert not re.search(r"settings\.json`\s+beside", text), path


def test_a_rewrite_that_matches_nothing_fails_the_build(monkeypatch):
    monkeypatch.setattr(build_plugins, "REWRITES", build_plugins.REWRITES + [("no such text anywhere", "x")])
    with pytest.raises(SystemExit, match="matched nothing"):
        build_plugins.build()


def test_scripts_are_copied_byte_for_byte_with_their_mode():
    for name, spec in build_plugins.PLUGINS.items():
        for skill, source in spec["skills"].items():
            for script in (ROOT / source).rglob("*.py"):
                copy = ROOT / "plugins" / name / "skills" / skill / script.relative_to(ROOT / source)
                assert copy.read_bytes() == script.read_bytes()
                assert copy.stat().st_mode & 0o777 == script.stat().st_mode & 0o777


def test_phase_tool_in_a_plugin_reads_the_projects_settings(installed):
    plugin, project = installed("dvt-phase")
    (project / ".devtools/phase_tool.settings.json").write_text('{"planning_dir": "plan"}')
    done = run(project, plugin / "skills/process-phase/scripts/phase_tool.py", "setup", "--name", "demo")
    assert done.returncode == 0, done.stdout + done.stderr
    assert (project / "plan/STATE.md").is_file() and not (project / ".planning").exists()
    readme = (project / "plan/README.md").read_text()
    assert "python3 ${CLAUDE_PLUGIN_ROOT}/skills/process-phase/scripts/phase_tool.py status" in readme
    status = run(project, plugin / "skills/process-phase/scripts/phase_tool.py", "status", "--format", "json")
    assert json.loads(status.stdout)["ok"], status.stdout


def test_a_synced_copy_still_reads_the_settings_beside_it(tmp_path):
    copy = tmp_path / "project/.claude/skills/process-phase"
    shutil.copytree(ROOT / "skills/phase/process-phase", copy)
    (copy / "scripts/phase_tool.settings.json").write_text('{"planning_dir": "beside"}')
    # A project that is itself a plugin still has a synced copy, not a plugin install.
    (tmp_path / "project/.claude-plugin").mkdir()
    (tmp_path / "project/.claude-plugin/plugin.json").write_text('{"name": "theirs"}')
    (tmp_path / "project/.devtools").mkdir()
    (tmp_path / "project/.devtools/phase_tool.settings.json").write_text('{"planning_dir": "devtools"}')
    done = run(tmp_path / "project", copy / "scripts/phase_tool.py", "setup")
    assert done.returncode == 0, done.stdout + done.stderr
    assert (tmp_path / "project/beside/STATE.md").is_file() and not (tmp_path / "project/devtools").exists()


def test_the_component_index_in_a_plugin_writes_into_the_project(installed):
    plugin, project = installed("dvt-milestone")
    (project / "src/demo").mkdir(parents=True)
    (project / "src/demo/__init__.py").write_text("")
    (project / "src/demo/mod.py").write_text("def f():\n    pass\n")
    (project / ".devtools/components_index.settings.json").write_text('{"package_dir": "src/demo"}')
    done = run(project, plugin / "skills/components/scripts/components_index.py", "write")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "${CLAUDE_PLUGIN_ROOT}/skills/components/scripts/components_index.py write" in done.stdout
    graph = (project / "docs/components/graph.md").read_text()
    assert "Generated by `${CLAUDE_PLUGIN_ROOT}/skills/components/scripts/components_index.py`" in graph
    assert not (plugin / "docs").exists()


def test_review_tool_in_a_plugin_reads_the_projects_settings(installed):
    plugin, project = installed("dvt-milestone")
    settings = project / ".devtools/review_tool.settings.json"
    settings.write_text('{"reviewer": "neither"}')
    done = run(project, plugin / "skills/process-phase/scripts/review_tool.py", "status", ".")
    assert done.returncode != 0 and f"{settings.resolve()}: reviewer must be" in done.stderr


def test_rules_check_in_a_plugin_uses_the_plugins_own_scripts(installed):
    plugin, project = installed("dvt-phase")
    probe = ("import runpy, sys; sys.argv = ['rules_check']; "
             f"print(__import__('json').dumps(runpy.run_path({str(plugin / 'skills/components/scripts/rules_check.py')!r}, "
             "run_name='probe')['SETTINGS']))")
    found = json.loads(subprocess.run([sys.executable, "-c", probe], cwd=project, capture_output=True,
                                      text=True, check=True).stdout)
    assert Path(found["index_script"]) == (plugin / "skills/components/scripts/components_index.py").resolve()
    assert Path(found["phase_script"]) == (plugin / "skills/process-phase/scripts/phase_tool.py").resolve()
    (project / ".devtools/rules_check.settings.json").write_text('{"index_script": "tools/index.py"}')
    found = json.loads(subprocess.run([sys.executable, "-c", probe], cwd=project, capture_output=True,
                                      text=True, check=True).stdout)
    assert found["index_script"] == "tools/index.py"


@pytest.mark.skipif(not shutil.which("claude"), reason="needs the claude CLI")
@pytest.mark.parametrize("folder", [f"plugins/{name}" for name in PLUGINS] + ["."])
def test_claude_validates_the_plugins_and_the_marketplace(folder):
    done = subprocess.run(["claude", "plugin", "validate", folder], cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_rule_change_in_a_plugin_project_needs_a_decision(installed):
    plugin, project = installed("dvt-phase")
    tool = plugin / "skills/process-phase/scripts/phase_tool.py"
    who = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run(["git", "checkout", "-q", "-b", "main"], cwd=project, check=True)
    assert run(project, tool, "setup").returncode == 0
    subprocess.run(["git", "add", "-A"], cwd=project, check=True)
    subprocess.run(["git", *who, "commit", "-q", "-m", "setup"], cwd=project, check=True)
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=project, check=True)
    (project / ".devtools/project.md").write_text("# Project rules\n\nA new rule.\n")
    done = run(project, tool, "check", "--all")
    assert done.returncode == 1 and "rule-dec" in done.stdout and ".devtools/project.md" in done.stdout


@pytest.mark.parametrize("example, plugin", [("examples/phase-project.devtools.toml", "dvt-phase"),
                                             ("examples/milestone-project.devtools.toml", "dvt-milestone")])
def test_every_skill_a_project_syncs_is_in_its_workflows_plugin(example, plugin):
    import tomllib
    config = tomllib.loads((ROOT / example).read_text())
    synced = {entry["source"] for entry in config["sync"] if (ROOT / entry["source"] / "SKILL.md").is_file()}
    assert synced
    assert synced <= set(build_plugins.PLUGINS[plugin]["skills"].values()), synced - set(
        build_plugins.PLUGINS[plugin]["skills"].values())


@pytest.mark.skipif(not (shutil.which("gnd") or __import__("os").environ.get("GND_COMMAND")),
                    reason="GND is not installed (put gnd on PATH or set GND_COMMAND)")
@pytest.mark.parametrize("plugin", PLUGINS)
def test_starter_rules_pass_their_own_test_in_each_plugin(installed, plugin):
    copy, project = installed(plugin)
    (project / "src/app").mkdir(parents=True)
    (project / "src/app/__init__.py").write_text('"""App."""\n')
    gnd = __import__("os").environ.get("GND_COMMAND") or shutil.which("gnd")
    (project / ".devtools/rules_check.settings.json").write_text(json.dumps({"gnd_command": gnd}))
    scripts = copy / "skills/components/scripts"
    assert run(project, scripts / "components_index.py", "init").returncode == 0
    assert run(project, scripts / "rules_check.py", "init").returncode == 0
    done = run(project, scripts / "rules_check.py", "test")
    assert done.returncode == 0 and " 0 wrong" in done.stdout, done.stdout + done.stderr
    skipped = "skip: plan_names_the_components_it_touches: a rule about plans"
    assert (skipped in done.stdout) == (plugin == "dvt-milestone"), done.stdout
