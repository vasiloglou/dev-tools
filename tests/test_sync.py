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


def test_after_apply_command_that_does_not_exist_is_reported(source, project, capsys):
    (project / ".devtools.toml").write_text(
        CONFIG.replace("[[sync]]", 'after_apply = ["no-such-command-here"]\n\n[[sync]]', 1))
    assert apply(source, project) == 4
    assert "after_apply failed: no-such-command-here" in capsys.readouterr().err


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


# --------------------------------------------------------------------------- a project that has its own copies

@pytest.fixture
def shipped(tmp_path):
    """A dev-tools source with one skill that ships a script, one more skill, and agents."""
    root = tmp_path / "devtools-source"
    (root / "skills/flow/process/scripts").mkdir(parents=True)
    (root / "skills/flow/process/SKILL.md").write_text(
        "---\nname: process\n---\n# Process\nOrient before anything else.\nWrite the tests before the code.\n"
        "Ask for approval at every gate, and never skip one because the change is small.\n"
        "Records go in {{devtools:planning_dir}}/records.\n")
    (root / "skills/flow/process/scripts/tool.py").write_text(
        'DEFAULT_SETTINGS = {"package": "", "script_path": "x", "limit": 3}\n')
    (root / "skills/index").mkdir(parents=True)
    (root / "skills/index/SKILL.md").write_text(
        "---\nname: index\n---\nSearch the index first.\nRecord the reuse decision.\nRegenerate after a change.\n")
    (root / "skills/adopt-devtools").mkdir()
    (root / "skills/adopt-devtools/SKILL.md").write_text("read here, never copied\n")
    (root / "agents").mkdir()
    (root / "agents/reviewer.md").write_text("Review the change.\n")
    return root


@pytest.fixture
def grown(tmp_path):
    """A project that grew its own copies: one under its name in two runtime folders, one renamed, plus a skill of its own."""
    root = tmp_path / "grown"
    for runtime in (".claude", ".codex"):
        (root / runtime / "skills/process").mkdir(parents=True)
        (root / runtime / "skills/process/SKILL.md").write_text(
            "---\nname: process\n---\n# Process\nOrient before anything else.\nWrite the tests before the code.\n"
            "Ask for approval at every gate, and never skip one\nbecause the change is small.\n"
            "Records go in plans/records.\n## Acme rules\nNever call the billing service in a test.\n"
            "Write the tests before any code.\n")
    (root / ".claude/skills/process/OLD.md").write_text("a file dev-tools does not ship\n")
    (root / ".claude/skills/acme-index").mkdir()
    (root / ".claude/skills/acme-index/SKILL.md").write_text(
        "---\nname: acme-index\n---\nSearch the index first.\nRecord the reuse decision.\nAcme names follow the ledger.\n")
    (root / ".claude/skills/deploy").mkdir()
    (root / ".claude/skills/deploy/SKILL.md").write_text("How Acme deploys.\n")
    (root / "tools").mkdir()
    (root / "tools/tool.py").write_text('PACKAGE = "acme"\nprint("the project\'s own copy of the script")\n')
    (root / ".claude/agents").mkdir()
    (root / ".claude/agents/reviewer.md").write_text("Review the change.\n")
    (root / "node_modules/x/skills/process").mkdir(parents=True)
    (root / "node_modules/x/skills/process/SKILL.md").write_text("Orient before anything else.\n")
    return root


def starter(shipped, grown, capsys):
    run("survey", "--project", grown, "--source", shipped, "--toml")
    return capsys.readouterr().out


def test_survey_finds_copies_renamed_copies_and_the_projects_own_skills(shipped, grown, capsys):
    assert run("survey", "--project", grown, "--source", shipped) == 0
    out = capsys.readouterr().out
    counterparts, rest = out.split("## The project's own skills")
    rest, search = rest.split("## To find what reads these copies")
    assert "  .claude/skills/process\n      80% of the shipped SKILL.md lines; 0 of 1 other shipped files present\n" \
           "      not here: scripts/tool.py" in counterparts
    assert "  .codex/skills/process\n      80%" in counterparts
    assert "  .claude/skills/acme-index\n      dev-tools names it `index`" in counterparts
    assert ".claude/agents  (1 of 1 shipped files present)" in counterparts
    assert "skills/flow/process/scripts/tool.py\n  tools/tool.py" in counterparts
    assert "deploy" in rest and "acme-index" not in rest
    assert "git grep -l -e 'skills/process' -e 'tool' -e 'skills/acme-index' -e '.claude/agents' -- . " \
           "':!.claude/skills/process'" in search
    assert "adopt-devtools" not in out and "node_modules" not in out
    assert not (grown / ".devtools.toml").exists(), "the survey writes nothing"


def test_the_starter_config_keeps_the_projects_paths_and_cannot_run_with_a_todo(shipped, grown, capsys):
    text = starter(shipped, grown, capsys)
    assert 'dest = ".claude/skills/index"\nreplaces = ".claude/skills/acme-index"' in text
    assert text.count('exclude = ["scripts/tool.py"]') == 2 and text.count('dest = "tools/tool.py"') == 1
    # What the project's copies show is read; what they do not show must be decided.
    assert text.count('values = { planning_dir = "plans" }') == 2 and "read from SKILL.md line 9" in text
    assert 'package = "acme"  # read from PACKAGE in tools/tool.py' in text
    assert 'script_path = "tools/tool.py"  # from the survey' in text
    assert 'limit = "TODO"  # default 3\n' in text
    (grown / ".devtools.toml").write_text(text)
    assert run("compare", "--project", grown, "--source", shipped) == 2
    assert "still TODO" in capsys.readouterr().err
    assert apply(shipped, grown, "--adopt") == 2
    assert "own copy of the script" in (grown / "tools/tool.py").read_text()


def test_compare_shows_the_lines_a_replacement_would_drop(shipped, grown, capsys):
    (grown / ".devtools.toml").write_text(starter(shipped, grown, capsys).replace('"TODO"', "5"))
    assert run("compare", "--project", grown, "--source", shipped) == 0
    out = capsys.readouterr().out
    # The re-wrapped sentence and the token line are not reported; the rule and the reworded line are.
    assert "replace  .claude/skills/process/SKILL.md  3 line(s) only the project's copy has (1 close to a shipped line)" in out
    assert "replace  .codex/skills/process/SKILL.md  same as .claude/skills/process/SKILL.md: counted there" in out
    assert "old copy .claude/skills/acme-index/SKILL.md  2 line(s) only the project's copy has (1 close" in out
    assert "replace  tools/tool.py  script or data, 2 line(s) differ: read it with --diff" in out
    assert "new      .claude/skills/index/SKILL.md" in out
    assert ".claude/agents/reviewer.md" not in out, "an identical file is not listed"
    assert "only in the project, inside a synced folder" in out and ".claude/skills/process/OLD.md" in out
    assert "5 line(s) of the project's text are in no file the sync delivers (2 close to a shipped line, " \
           "0 now in a file the project owns); 2 line(s) differ in scripts and data files" in out

    assert run("compare", "--project", grown, "--source", shipped, ".claude/skills/process") == 0
    out = capsys.readouterr().out
    assert "     10: ## Acme rules\n     11: Never call the billing service in a test." in out
    assert "   11: Never call the billing service in a test." in out and "Orient before" not in out
    assert "   12: Write the tests before any code.\n       ~ shipped: Write the tests before the code." in out
    assert run("compare", "--project", grown, "--source", shipped, ".claude/skills/acme-index") == 0
    assert "Acme names follow the ledger." in capsys.readouterr().out
    assert run("compare", "--project", grown, "--source", shipped, ".claude/skills/index/SKILL.md") == 0
    assert "Read the shipped file, skills/index/SKILL.md" in capsys.readouterr().out
    assert run("compare", "--project", grown, "--source", shipped, ".claude/skills/process/SKILL.md", "--diff") == 0
    assert "+Records go in plans/records." not in capsys.readouterr().out, "the filled token matches the project's line"
    assert run("compare", "--project", grown, "--source", shipped, ".claude/skills/process/SKILL.md", "--added") == 0
    out = capsys.readouterr().out
    assert "0 line(s) only the shipped file has" in out, "what arrives: here nothing but a reworded line"
    assert run("compare", "--project", grown, "--source", shipped, ".claude/skills/acme-index", "--added") == 0
    assert "Regenerate after a change." in capsys.readouterr().out
    assert run("compare", "--project", grown, "--source", shipped, "--record") == 0
    out = capsys.readouterr().out
    assert "| `.claude/skills/process/SKILL.md` | 3 | | | | | | | |" in out and "| Total | 7 |" in out
    assert run("compare", "--project", grown, "--source", shipped, "no/such/path") == 2
    assert run("compare", "--project", grown, "--source", shipped, "--diff") == 2

    # A rule moved to a file the project owns is counted as carried.
    (grown / ".claude/skills/process/project.md").write_text("## Rules\nNever call the billing service in a test.\n")
    run("compare", "--project", grown, "--source", shipped)
    capsys.readouterr()
    run("compare", "--project", grown, "--source", shipped, ".claude/skills/process/SKILL.md")
    assert "Never call the billing service in a test.   [in .claude/skills/process/project.md]" in capsys.readouterr().out

    # After the apply the old copy under its own name is what the survey still points at.
    assert apply(shipped, grown, "--adopt") == 0
    capsys.readouterr()
    run("survey", "--project", grown, "--source", shipped)
    out = capsys.readouterr().out
    assert "  .claude/skills/index  [synced" in out
    assert "[the old copy that .devtools.toml names under replaces]" in out
    run("compare", "--project", grown, "--source", shipped)
    out = capsys.readouterr().out
    assert "replace" not in out and "old copy .claude/skills/acme-index/SKILL.md" in out


def test_an_excluded_file_is_listed_as_kept(shipped, grown, capsys):
    text = starter(shipped, grown, capsys).replace('"TODO"', "5")
    text = text.replace('exclude = ["scripts/tool.py"]', 'exclude = ["scripts/tool.py", "SKILL.md"]', 1)
    text = text.replace('values = { planning_dir = "plans" }\n', '', 1)  # no token is left in that entry
    (grown / ".devtools.toml").write_text(text)
    assert run("compare", "--project", grown, "--source", shipped) == 0
    assert "kept     .claude/skills/process/SKILL.md  excluded: stays as it is" in capsys.readouterr().out
