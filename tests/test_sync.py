"""Tests for devtools/sync.py: what it copies, and what it refuses to overwrite."""
import importlib.util
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("sync", Path(__file__).resolve().parents[1] / "devtools/sync.py")
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)

CONFIG = """
[[sync]]
source = "skills/demo"
dest = ".claude/skills/demo"
[sync.settings."scripts/tool.settings.json"]
planning_dir = ".planning"

[[sync]]
source = "scripts/one.py"
dest = "tools/one.py"
"""


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "devtools-source"
    (root / "skills/demo/scripts").mkdir(parents=True)
    (root / "skills/demo/SKILL.md").write_text("demo skill\n")
    (root / "skills/demo/scripts/tool.py").write_text("print('tool')\n")
    (root / "skills/demo/scripts/tool.py").chmod(0o755)
    (root / "skills/demo/__pycache__").mkdir()
    (root / "skills/demo/__pycache__/x.pyc").write_bytes(b"cache")
    (root / "scripts").mkdir()
    (root / "scripts/one.py").write_text("ONE = 1\n")
    return root


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / ".devtools.toml").write_text(CONFIG)
    return root


def run(*args):
    return sync.main([str(a) for a in args])


def apply(source, project, *flags):
    return run("apply", "--project", project, "--source", source, *flags)


def test_apply_copies_files_settings_and_modes(source, project):
    assert apply(source, project) == 0
    assert (project / ".claude/skills/demo/SKILL.md").read_text() == "demo skill\n"
    assert (project / ".claude/skills/demo/scripts/tool.py").stat().st_mode & 0o777 == 0o755
    assert json.loads((project / ".claude/skills/demo/scripts/tool.settings.json").read_text()) == {
        "planning_dir": ".planning"}
    assert (project / "tools/one.py").read_text() == "ONE = 1\n"
    assert not (project / ".claude/skills/demo/__pycache__").exists()
    receipt = json.loads((project / ".devtools-receipt.json").read_text())
    assert sorted(receipt["files"]) == [
        ".claude/skills/demo/SKILL.md", ".claude/skills/demo/scripts/tool.py",
        ".claude/skills/demo/scripts/tool.settings.json", "tools/one.py"]
    assert not (project / ".devtools-sync.journal").exists()
    assert run("check", "--project", project) == 0


def test_apply_twice_changes_nothing(source, project, capsys):
    apply(source, project)
    capsys.readouterr()
    assert apply(source, project) == 0
    assert '"keep": 4' in capsys.readouterr().out


def test_upstream_change_updates_an_untouched_copy(source, project):
    apply(source, project)
    (source / "scripts/one.py").write_text("ONE = 2\n")
    assert apply(source, project) == 0
    assert (project / "tools/one.py").read_text() == "ONE = 2\n"


def test_hand_edit_is_reported_and_never_overwritten_without_force(source, project):
    apply(source, project)
    (project / "tools/one.py").write_text("ONE = 'mine'\n")
    assert run("check", "--project", project) == 1
    (source / "scripts/one.py").write_text("ONE = 2\n")
    (source / "skills/demo/SKILL.md").write_text("changed upstream\n")
    assert apply(source, project) == 3
    assert (project / "tools/one.py").read_text() == "ONE = 'mine'\n"
    assert (project / ".claude/skills/demo/SKILL.md").read_text() == "demo skill\n", "a refusal writes nothing"
    assert apply(source, project, "--force") == 0
    assert (project / "tools/one.py").read_text() == "ONE = 2\n"


def test_existing_unmanaged_file_needs_adopt(source, project):
    (project / "tools").mkdir()
    (project / "tools/one.py").write_text("the project's own version\n")
    assert apply(source, project) == 3
    assert (project / "tools/one.py").read_text() == "the project's own version\n"
    assert not (project / ".devtools-receipt.json").exists()
    assert apply(source, project, "--adopt") == 0
    assert (project / "tools/one.py").read_text() == "ONE = 1\n"


def test_identical_existing_file_is_taken_over_without_adopt(source, project):
    (project / "tools").mkdir()
    (project / "tools/one.py").write_text("ONE = 1\n")
    assert apply(source, project) == 0


def test_file_dropped_upstream_is_deleted_only_if_untouched(source, project):
    apply(source, project)
    (source / "skills/demo/scripts/tool.py").unlink()
    assert apply(source, project) == 0
    assert not (project / ".claude/skills/demo/scripts/tool.py").exists()

    (project / ".claude/skills/demo/SKILL.md").write_text("edited\n")
    (source / "skills/demo/SKILL.md").unlink()
    assert apply(source, project) == 3
    assert (project / ".claude/skills/demo/SKILL.md").read_text() == "edited\n"


def test_files_the_project_adds_beside_managed_ones_are_left_alone(source, project):
    apply(source, project)
    extra = project / ".claude/skills/demo/NOTES.md"
    extra.write_text("project notes\n")
    assert apply(source, project) == 0
    assert extra.read_text() == "project notes\n"
    assert run("check", "--project", project) == 0


@pytest.mark.parametrize("dest", ["../outside.py", "/tmp/outside.py"])
def test_destination_outside_the_project_is_refused(source, project, dest):
    (project / ".devtools.toml").write_text(f'[[sync]]\nsource = "scripts/one.py"\ndest = "{dest}"\n')
    assert apply(source, project) == 2


def test_interrupted_apply_is_reported_and_finished_by_running_again(source, project, capsys):
    apply(source, project)
    (project / ".devtools-sync.journal").write_text('{"files": {}}')
    assert run("check", "--project", project) == 1
    assert "interrupted" in capsys.readouterr().out
    assert apply(source, project) == 0
    assert run("check", "--project", project) == 0


def test_excluded_file_stays_the_projects_own(source, project):
    (project / ".devtools.toml").write_text(
        '[[sync]]\nsource = "skills/demo"\ndest = ".claude/skills/demo"\nexclude = ["SKILL.md"]\n')
    (project / ".claude/skills/demo").mkdir(parents=True)
    own = project / ".claude/skills/demo/SKILL.md"
    own.write_text("the project's own skill text\n")
    assert apply(source, project) == 0
    assert own.read_text() == "the project's own skill text\n"
    assert (project / ".claude/skills/demo/scripts/tool.py").is_file()
    assert "SKILL.md" not in (project / ".devtools-receipt.json").read_text()
    assert run("check", "--project", project) == 0


def test_exclude_must_name_a_shipped_file(source, project):
    (project / ".devtools.toml").write_text(
        '[[sync]]\nsource = "skills/demo"\ndest = ".claude/skills/demo"\nexclude = ["nope.md"]\n')
    assert apply(source, project) == 2


def test_after_apply_runs_only_when_something_changed(source, project):
    marker = project / "ran.txt"
    (project / ".devtools.toml").write_text(
        CONFIG.replace("[[sync]]", f'after_apply = ["touch {marker.name}"]\n\n[[sync]]', 1))
    assert apply(source, project) == 0
    assert marker.is_file()
    marker.unlink()
    assert apply(source, project) == 0
    assert not marker.exists()


def test_failing_after_apply_is_reported(source, project):
    (project / ".devtools.toml").write_text(CONFIG.replace("[[sync]]", 'after_apply = ["false"]\n\n[[sync]]', 1))
    assert apply(source, project) == 4
    assert run("check", "--project", project) == 0, "the files and receipt are still consistent"


def test_unknown_top_level_key_is_an_error(source, project):
    (project / ".devtools.toml").write_text('surprise = 1\n' + CONFIG)
    assert apply(source, project) == 2


TOKENS = """
[[sync]]
source = "skills/demo"
dest = ".claude/skills/demo"
values = { planning_dir = ".plans" }

[[sync]]
source = "skills/demo"
dest = ".codex/skills/demo"
values = { planning_dir = ".plans" }
"""


def test_values_fill_tokens_and_one_source_can_land_in_two_places(source, project):
    (source / "skills/demo/SKILL.md").write_text("records go in {{devtools:planning_dir}}/milestones\n")
    (project / ".devtools.toml").write_text(TOKENS)
    assert apply(source, project) == 0
    for runtime in (".claude", ".codex"):
        assert (project / runtime / "skills/demo/SKILL.md").read_text() == "records go in .plans/milestones\n"
    assert run("check", "--project", project) == 0
    assert apply(source, project) == 0


def test_token_without_a_value_is_an_error(source, project):
    (source / "skills/demo/SKILL.md").write_text("records go in {{devtools:planning_dir}}\n")
    assert apply(source, project) == 2
    assert not (project / ".claude").exists()


def test_value_that_matches_no_token_is_an_error(source, project):
    (project / ".devtools.toml").write_text(TOKENS)
    assert apply(source, project) == 2
