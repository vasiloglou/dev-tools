"""Tests for devtools/sync.py: what it copies, and what it refuses to overwrite."""
import importlib.util
import json
import re
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


def test_a_destination_reached_through_a_link_out_of_the_project_is_refused(source, project, tmp_path, capsys):
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (project / ".claude/skills").mkdir(parents=True)
    (project / ".claude/skills/demo").symlink_to(outside)
    assert apply(source, project) == 2
    assert "would be written outside the project" in capsys.readouterr().err
    assert list(outside.iterdir()) == [], "nothing was written through the link"


def test_two_destinations_that_are_one_file_are_refused(source, project, capsys):
    (project / ".claude/skills").mkdir(parents=True)
    (project / ".codex").mkdir()
    (project / ".codex/skills").symlink_to("../.claude/skills")
    (project / ".devtools.toml").write_text(CONFIG + '[[sync]]\nsource = "skills/demo"\ndest = ".codex/skills/demo"\n')
    assert apply(source, project) == 2
    assert "are one file" in capsys.readouterr().err
    (project / ".devtools.toml").write_text(CONFIG.replace(".claude/skills/demo", ".codex/skills/demo"))
    assert apply(source, project) == 0, "a link that stays inside the project is fine when it is used once"
    assert (project / ".claude/skills/demo/SKILL.md").is_file() and run("check", "--project", project) == 0


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


def test_in_a_git_project_the_survey_does_not_walk_what_git_ignores(shipped, grown, capsys, monkeypatch):
    import subprocess
    (grown / ".gitignore").write_text("runs/\n.codex/\n")
    (grown / "runs/2026/skills/process").mkdir(parents=True)
    (grown / "runs/2026/skills/process/SKILL.md").write_text("Orient before anything else.\n")
    (grown / "runs/2026/tool.py").write_text("print('a copy in ignored output')\n")
    subprocess.run(["git", "init", "-q", str(grown)], check=True)
    walked = []
    real_walk = sync.walk
    monkeypatch.setattr(sync, "walk", lambda top: walked.append(top) or real_walk(top))
    assert run("survey", "--project", grown, "--source", shipped) == 0
    out = capsys.readouterr().out
    assert "runs/" not in out, "ignored output is not read"
    assert "  .codex/skills/process" in out, "a skills folder is read even when git ignores it"
    assert "  .claude/skills/acme-index" in out and "skills/flow/process/scripts/tool.py\n  tools/tool.py" in out
    assert grown not in walked and all(top.name in ("skills", "agents") for top in walked)


def test_the_survey_says_when_the_planning_folder_is_gsds(shipped, grown, capsys):
    (grown / ".planning").mkdir()
    (grown / ".planning/STATE.md").write_text("---\ngsd_state_version: 1.0\n---\n")
    run("survey", "--project", grown, "--source", shipped)
    assert "## A planning folder written by GSD" in capsys.readouterr().out


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


def test_the_survey_names_a_plan_kept_by_another_tool(shipped, grown, capsys):
    (grown / ".kiro/specs/login").mkdir(parents=True)
    (grown / ".planning").mkdir()
    (grown / ".planning/ROADMAP.md").write_text("# Plan\n\n1. Build it\n")
    run("survey", "--project", grown, "--source", shipped)
    out = capsys.readouterr().out
    assert "## A plan kept by another planning tool" in out and ".kiro/specs/: Kiro" in out
    assert ".planning/: a plan in a format the phase tool does not read" in out
    assert "Coming from another planning tool" in out


def test_a_plan_the_phase_tool_wrote_is_not_another_tools(shipped, grown, capsys):
    (grown / ".planning").mkdir()
    (grown / ".planning/STATE.md").write_text('---\ncurrent_phase: "01"\nphase_status: not_started\n---\n')
    (grown / ".planning/ROADMAP.md").write_text("# Roadmap\n\n## Phase 1: Scan\n")
    run("survey", "--project", grown, "--source", shipped)
    assert "another planning tool" not in capsys.readouterr().out


def test_apply_says_when_git_ignores_what_it_delivers(source, project, capsys):
    import subprocess
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    (project / ".gitignore").write_text(".claude/skills/*\n")
    assert apply(source, project, "--dry-run") == 0
    err = capsys.readouterr().err
    assert "warning: git ignores 3 of the files delivered to .claude/skills/demo" in err
    assert "tools/one.py" not in err, "only the entry whose files git ignores is named"
    assert apply(source, project) == 0
    assert "warning: git ignores 3 of the files delivered to .claude/skills/demo" in capsys.readouterr().err
    (project / ".gitignore").write_text(".claude/skills/*\n!.claude/skills/demo/\n")
    assert apply(source, project) == 0
    assert "warning" not in capsys.readouterr().err, "an exception in .gitignore lets them in"


def test_apply_outside_git_says_nothing_about_ignored_files(source, project, capsys):
    assert apply(source, project) == 0
    assert "warning" not in capsys.readouterr().err


def test_compare_before_the_config_exists_says_how_to_write_it(source, project, capsys):
    (project / ".devtools.toml").unlink()
    assert run("compare", "--project", project, "--source", source) == 2
    err = capsys.readouterr().err
    assert "compare reads the entries it lists" in err and "survey --project" in err and "--toml" in err
    assert all(example in err for example in sync.EXAMPLES)


def test_every_example_the_tools_name_exists():
    assert all((sync.SOURCE_ROOT / example).is_file() for example in sync.EXAMPLES)


def test_the_starter_for_a_project_with_no_copies_points_to_the_examples(shipped, tmp_path, capsys):
    bare = tmp_path / "bare"
    (bare / ".claude/skills/deploy").mkdir(parents=True)
    (bare / ".claude/skills/deploy/SKILL.md").write_text("How Acme deploys.\n")
    out = starter(shipped, bare, capsys)
    assert "[[sync]]" not in out and "nothing here to migrate" in out
    assert all(f"#   {example}" in out for example in sync.EXAMPLES)
    assert "skills/move-from-gsd/SKILL.md" in out


def test_the_survey_tells_a_gsd_plan_kept_as_history_from_one_not_moved(shipped, grown, capsys):
    (grown / ".planning").mkdir()
    (grown / ".planning/PROJECT.md").write_text("# Acme\n")
    run("survey", "--project", grown, "--source", shipped)
    out = capsys.readouterr().out
    assert "from_gsd.py converts the plan" in out and "stays as history" in out
    (grown / ".devtools.toml").write_text('[[sync]]\nsource = "skills/milestone/process-phase"\n'
                                          'dest = ".claude/skills/process-phase"\n')
    run("survey", "--project", grown, "--source", shipped)
    out = capsys.readouterr().out
    assert "takes the milestone workflow, not applied yet" in out and "from_gsd.py is not run on it" in out
    assert "under .planning/milestones/" in out


def test_the_gsd_history_line_says_whether_the_milestone_skills_are_synced_and_where_records_go(tmp_path, capsys):
    project = tmp_path / "gsd-project"
    (project / ".planning").mkdir(parents=True)
    (project / ".planning/PROJECT.md").write_text("# Acme\n")
    (project / ".devtools.toml").write_text(
        (sync.SOURCE_ROOT / "examples/milestone-project.devtools.toml").read_text().replace('".planning"', '"docs/plan"'))
    run("survey", "--project", project)
    assert "not applied yet" in capsys.readouterr().out
    assert run("apply", "--project", project) == 0
    capsys.readouterr()
    run("survey", "--project", project)
    out = capsys.readouterr().out
    assert "takes the milestone workflow, synced here. Its records go under docs/plan/milestones/" in out
    assert "the notes on GSD's files, project.md" in out, "being synced is not the whole move"


def test_an_exception_under_a_folder_excluded_whole_is_still_warned_about(source, project, capsys):
    import subprocess
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    (project / ".gitignore").write_text(".claude/skills/\n!.claude/skills/demo/\n")
    assert apply(source, project) == 0
    err = capsys.readouterr().err
    assert "warning: git ignores 3 of the files delivered to .claude/skills/demo" in err
    assert "works only when no parent folder is excluded as a whole" in err


def test_settings_written_beside_a_file_are_warned_about_with_their_entry(source, project, capsys):
    import subprocess
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    (project / ".devtools.toml").write_text('[[sync]]\nsource = "scripts/one.py"\ndest = "tools/one.py"\n'
                                             '[sync.settings."one.settings.json"]\nlimit = 3\n')
    (project / ".gitignore").write_text("*.settings.json\n")
    assert apply(source, project) == 0
    assert "warning: git ignores 1 of the files delivered to tools/one.py (tools/one.settings.json)" \
        in capsys.readouterr().err


def test_a_git_error_is_reported_not_taken_for_nothing_ignored(source, project, capsys):
    import subprocess
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    (project / ".git/index").write_bytes(b"not an index")
    assert apply(source, project) == 0
    assert "warning: could not ask git which delivered files it ignores" in capsys.readouterr().err


def test_the_milestone_example_applies_as_it_is(tmp_path):
    project = tmp_path / "fresh"
    project.mkdir()
    (project / ".devtools.toml").write_text((sync.SOURCE_ROOT / "examples/milestone-project.devtools.toml").read_text())
    assert run("apply", "--project", project) == 0
    synced = sorted(json.loads((project / ".devtools-receipt.json").read_text())["files"])
    assert ".claude/skills/process-phase/references/milestone-record-format.md" in synced
    assert not any("{{devtools:" in (project / path).read_text() for path in synced)
    assert run("check", "--project", project) == 0


def test_review_pr_finds_process_phase_beside_it_in_the_milestone_example(tmp_path):
    # review-pr cites process-phase's references and runs its helper by relative path, so the
    # example must deliver both skills into one folder. project.md is the project's own file.
    project = tmp_path / "fresh"
    project.mkdir()
    (project / ".devtools.toml").write_text((sync.SOURCE_ROOT / "examples/milestone-project.devtools.toml").read_text())
    assert run("apply", "--project", project) == 0
    skill = project / ".claude/skills/review-pr"
    cited = set(re.findall(r"\.\./process-phase/[\w./-]+[\w]", (skill / "SKILL.md").read_text()))
    cited.discard("../process-phase/references/project.md")
    assert "../process-phase/scripts/review_tool.py" in cited
    assert [path for path in sorted(cited) if not (skill / path).is_file()] == []


@pytest.mark.parametrize("example", ["phase-project.devtools.toml", "milestone-project.devtools.toml"])
def test_both_examples_deliver_handle_issue_and_it_passes_the_skill_check(tmp_path, example):
    # handle-issue works in either workflow, so each example ships it, and the copy must meet
    # the phase tool's skill rules (name, description, no backticked file it lacks).
    project = tmp_path / "fresh"
    project.mkdir()
    (project / ".devtools.toml").write_text((sync.SOURCE_ROOT / "examples" / example).read_text())
    assert run("apply", "--project", project) == 0
    skill = project / ".claude/skills/handle-issue"
    assert (skill / "SKILL.md").is_file()
    spec = importlib.util.spec_from_file_location("phase_tool", sync.SOURCE_ROOT / "skills/phase/process-phase/scripts/phase_tool.py")
    phase_tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase_tool)
    assert phase_tool.check_skill(project, skill) == []


@pytest.mark.parametrize("example", ["phase-project.devtools.toml", "milestone-project.devtools.toml"])
def test_both_examples_deliver_the_handoff_skills_with_the_script_they_share(tmp_path, example):
    # dev-handoff and dev-takeover work in either workflow. dev-takeover runs dev-handoff's script
    # and cites its reference, so the example delivers both into one folder; both meet the phase
    # tool's skill rules, and the settings the example writes are ones the script knows.
    project = tmp_path / "fresh"
    project.mkdir()
    (project / ".devtools.toml").write_text((sync.SOURCE_ROOT / "examples" / example).read_text())
    assert run("apply", "--project", project) == 0
    skills = project / ".claude/skills"
    spec = importlib.util.spec_from_file_location("phase_tool", sync.SOURCE_ROOT / "skills/phase/process-phase/scripts/phase_tool.py")
    phase_tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase_tool)
    for name in ("dev-handoff", "dev-takeover"):
        assert phase_tool.check_skill(project, skills / name) == []
        text = (skills / name / "SKILL.md").read_text()
        assert ".claude/skills/dev-handoff/scripts/handoff.py" in text
    cited = set(re.findall(r"\.\./dev-handoff/[\w./-]+[\w]", (skills / "dev-takeover/SKILL.md").read_text()))
    assert cited == {"../dev-handoff/references/handoff.md"}
    assert (skills / "dev-takeover" / "../dev-handoff/references/handoff.md").is_file()
    script = skills / "dev-handoff/scripts/handoff.py"
    assert json.loads(script.with_suffix(".settings.json").read_text())["planning_dir"] == ".planning"
    import subprocess
    import sys
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    done = subprocess.run([sys.executable, str(script), "doctor"], cwd=project, capture_output=True, text=True)
    assert done.returncode == 0 and "handoff doctor:" in done.stdout, done.stderr


# --------------------------------------------------------------------------- what the sync says about units
# Milestone sync-reports, phase 1: units the config does not take, `declined`, the receipt's
# `shipped`, and `check` against a dev-tools source.

import os
import subprocess

NAMED = "not taken, and named by a file this project has:"
NEW = "new in dev-tools since this project's last sync:"
UNLISTED = ("not taken (this receipt was written before the sync recorded what dev-tools ships; "
            "listed this once):")
CLOSING = ("to take a unit, add a [[sync]] entry to .devtools.toml; to stop hearing of one, "
           "add its path to `declined` there")
HEADINGS = (NAMED, NEW, UNLISTED, CLOSING)


@pytest.fixture(autouse=True)
def no_implicit_source(monkeypatch):
    """Plain `check` in a test never reads the repository's own checkout as its source."""
    monkeypatch.setattr(sync, "default_source", lambda *args, **kwargs: None, raising=False)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.com",
                           *args], check=True, capture_output=True, text=True).stdout.strip()


def commit(root, message="change"):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def workflows(tmp_path):
    """A dev-tools source with both workflows, a skill that names another, agents and a script."""
    root = tmp_path / "workflows-source"
    files = {
        "skills/milestone/process-phase/SKILL.md": "The milestone phase protocol, step by step.\n",
        "skills/milestone/process-phase/references/review-tool.md":
            "A pull-request review is taken by the `review-pr` skill.\n",
        "skills/milestone/process-phase/scripts/review_tool.py": "print('review')\n",
        "skills/milestone/review-pr/SKILL.md":
            "Run `../process-phase/scripts/review_tool.py brief` for the pull request.\n",
        "skills/milestone/start-milestone/SKILL.md": "Plan a milestone before any phase runs.\n",
        "skills/phase/process-phase/SKILL.md": "The phase workflow, with its own state tool.\n",
        "skills/phase/phase-tests/SKILL.md": "Acceptance tests written before the code.\n",
        "skills/phase/pytest/phase_selection.py": "SELECT = True\n",
        "skills/handle-issue/SKILL.md": "Route a fix to `review-pr` or the plan to `start-milestone`.\n",
        "skills/components/SKILL.md": "The component index of the project's code.\n",
        "agents/phase-implementer.md": "Implement one plan.\n",
    }
    for name, text in files.items():
        write(root / name, text)
    git(root, "init", "-q")
    commit(root, "first")
    return root


def milestone_config(declined=None, entries=("skills/milestone/process-phase", "skills/milestone/start-milestone",
                                             "skills/handle-issue", "skills/components"),
                     folders=(".claude/skills", ".codex/skills"), extra=""):
    lines = [f"declined = {json.dumps(declined)}", ""] if declined is not None else []
    for folder in folders:
        for source in entries:
            lines += ["[[sync]]", f'source = "{source}"', f'dest = "{folder}/{source.rsplit("/", 1)[-1]}"', extra, ""]
    return "\n".join(lines)


@pytest.fixture
def mproject(tmp_path):
    root = tmp_path / "mproject"
    root.mkdir()
    (root / ".devtools.toml").write_text(milestone_config())
    return root


def out_of(capsys, *args):
    code = run(*args)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def check_source(project, source, *flags):
    return ("check", "--project", project, "--source", source, *flags)


def report_of(source, project):
    config = sync.read_config(project)
    wanted = sync.desired_files(source, config, project)
    return sync.unit_report(source, config, wanted, sync.read_json(project / ".devtools-receipt.json"))


def test_the_observed_case_a_missing_named_skill_and_a_receipt_older_than_the_source(workflows, mproject, capsys):
    # T1: the config lacks review-pr, the delivered process-phase names it, and the source moved on.
    first = git(workflows, "rev-parse", "HEAD")
    assert apply(workflows, mproject) == 0
    write(workflows / "skills/milestone/process-phase/SKILL.md", "The milestone phase protocol, revised.\n")
    second = commit(workflows)
    capsys.readouterr()
    code, out, _ = out_of(capsys, "apply", "--project", mproject, "--source", workflows, "--dry-run")
    assert code == 0
    lines = out.splitlines()
    assert lines[lines.index(NAMED) + 1:lines.index(NAMED) + 3] == [
        "  skills/milestone/review-pr",
        "      named by .claude/skills/handle-issue/SKILL.md and 3 more file(s)"]
    assert lines[-1] == CLOSING
    code, out, _ = out_of(capsys, *check_source(mproject, workflows))
    assert code == 0
    lines = out.splitlines()
    assert lines[0] == "12 managed file(s), 0 problem(s)"
    assert lines[1] == (f"not current: an apply would update 2 file(s) "
                        f"(synced from dev-tools at {first[:7]}; this source is at {second[:7]})")
    assert NAMED in lines
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 5
    code, out, _ = out_of(capsys, "check", "--project", mproject, "--receipt-only")
    assert (code, out) == (0, "12 managed file(s), 0 problem(s)\n")


def test_the_report_is_rows_before_it_is_lines(workflows, mproject):
    # T2
    assert apply(workflows, mproject) == 0
    assert report_of(workflows, mproject) == {
        "named": [{"unit": "skills/milestone/review-pr",
                   "by": [".claude/skills/handle-issue/SKILL.md",
                          ".claude/skills/process-phase/references/review-tool.md",
                          ".codex/skills/handle-issue/SKILL.md",
                          ".codex/skills/process-phase/references/review-tool.md"]}],
        "new": [], "unlisted": [], "stale_declined": []}


def test_a_declined_unit_is_never_reported(workflows, mproject, capsys):
    # T3
    (mproject / ".devtools.toml").write_text(milestone_config(declined=["skills/milestone/review-pr"]))
    code, out, _ = out_of(capsys, "apply", "--project", mproject, "--source", workflows)
    assert code == 0 and not any(h in out for h in HEADINGS)
    code, out, _ = out_of(capsys, *check_source(mproject, workflows))
    assert (code, out) == (0, "12 managed file(s), 0 problem(s)\n")
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 0


def test_a_workflow_the_config_takes_nothing_from_is_silent(workflows, tmp_path):
    # T4: handle-issue names two milestone skills, but the project runs the phase workflow.
    project = tmp_path / "phase-project"
    project.mkdir()
    (project / ".devtools.toml").write_text(milestone_config(
        entries=("skills/phase/process-phase", "skills/handle-issue"), folders=(".claude/skills",)))
    assert apply(workflows, project) == 0
    assert report_of(workflows, project)["named"] == []


def test_a_name_a_taken_unit_has_is_satisfied(workflows, tmp_path):
    # T5: `process-phase` names the phase workflow's skill, which the project takes.
    write(workflows / "skills/handle-issue/SKILL.md", "Route a fix to `review-pr`; the work runs in `process-phase`.\n")
    project = tmp_path / "p"
    project.mkdir()
    (project / ".devtools.toml").write_text(milestone_config(
        entries=("skills/phase/process-phase", "skills/milestone/start-milestone", "skills/handle-issue"),
        folders=(".claude/skills",)))
    assert apply(workflows, project) == 0
    named = [row["unit"] for row in report_of(workflows, project)["named"]]
    assert named == ["skills/milestone/review-pr"]


def test_a_unit_added_since_the_last_sync_is_new_until_the_next_apply(workflows, mproject, capsys):
    # T6
    (mproject / ".devtools.toml").write_text(milestone_config(declined=["skills/milestone/review-pr", "agents"]))
    assert apply(workflows, mproject) == 0
    write(workflows / "skills/extra/SKILL.md", "Something new to take.\n")
    for args in (("apply", "--project", mproject, "--source", workflows, "--dry-run"), check_source(mproject, workflows)):
        code, out, _ = out_of(capsys, *args)
        lines = out.splitlines()
        assert code == 0
        assert lines[lines.index(NEW) + 1] == "  skills/extra"
        assert NAMED not in lines and UNLISTED not in lines and not out.count("not current")
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 5
    code, out, _ = out_of(capsys, "apply", "--project", mproject, "--source", workflows)
    assert NEW in out
    assert "skills/extra" in json.loads((mproject / ".devtools-receipt.json").read_text())["shipped"]
    code, out, _ = out_of(capsys, "apply", "--project", mproject, "--source", workflows)
    assert not any(h in out for h in HEADINGS)
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 0


@pytest.mark.parametrize("where, declined", [("skills/phase/extra", ["skills/milestone/review-pr", "agents"]),
                                              ("skills/extra", ["skills/milestone/review-pr", "agents", "skills/extra"])])
def test_a_new_unit_under_an_untaken_workflow_or_declined_is_silent(workflows, mproject, capsys, where, declined):
    # T7
    (mproject / ".devtools.toml").write_text(milestone_config(declined=["skills/milestone/review-pr", "agents"]))
    assert apply(workflows, mproject) == 0
    (mproject / ".devtools.toml").write_text(milestone_config(declined=declined))
    write(workflows / where / "SKILL.md", "Something new.\n")
    code, out, _ = out_of(capsys, *check_source(mproject, workflows))
    assert code == 0 and not any(h in out for h in HEADINGS)
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 0


def test_a_receipt_from_before_shipped_lists_the_untaken_units_once(workflows, mproject, capsys):
    # T8
    (mproject / ".devtools.toml").write_text(milestone_config(declined=["skills/milestone/review-pr"]))
    assert apply(workflows, mproject) == 0
    receipt_path = mproject / ".devtools-receipt.json"
    receipt = json.loads(receipt_path.read_text())
    del receipt["shipped"]
    receipt_path.write_text(json.dumps(receipt))
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(mproject, workflows))
    assert code == 0
    assert out.splitlines()[1:] == [UNLISTED, "  agents", CLOSING]
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 5
    assert apply(workflows, mproject) == 0
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(mproject, workflows))
    assert not any(h in out for h in HEADINGS)
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 0


def test_the_first_apply_reports_named_units_and_nothing_new(workflows, mproject, capsys):
    # T9
    code, out, _ = out_of(capsys, "apply", "--project", mproject, "--source", workflows)
    assert code == 0 and NAMED in out and NEW not in out and UNLISTED not in out


@pytest.mark.parametrize("declined", ['"skills/milestone/review-pr"', '["/abs"]', '["../x"]', '["skills/milestone"]'])
def test_a_declined_value_that_cannot_be_right_is_refused_before_anything_is_written(workflows, mproject, capsys, declined):
    # T10, the four refusals
    (mproject / ".devtools.toml").write_text(f"declined = {declined}\n\n" + milestone_config())
    code, _, err = out_of(capsys, "apply", "--project", mproject, "--source", workflows)
    assert code == 2 and "declined" in err
    assert sorted(p.name for p in mproject.iterdir()) == [".devtools.toml"]


def test_a_declined_path_dev_tools_no_longer_ships_is_a_warning(workflows, mproject, capsys):
    # T10, the fifth case
    (mproject / ".devtools.toml").write_text(milestone_config(declined=["skills/milestone/review-pr", "skills/retired"]))
    code, _, err = out_of(capsys, "apply", "--project", mproject, "--source", workflows)
    assert code == 0
    assert "warning: declined names nothing dev-tools ships: skills/retired" in err
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 0


def test_an_excluded_file_names_nothing(workflows, tmp_path):
    # T11
    project = tmp_path / "p"
    project.mkdir()
    (project / ".devtools.toml").write_text("\n".join([
        "[[sync]]", 'source = "skills/milestone/process-phase"', 'dest = ".claude/skills/process-phase"',
        'exclude = ["references/review-tool.md"]', "",
        "[[sync]]", 'source = "skills/handle-issue"', 'dest = ".claude/skills/handle-issue"', 'exclude = ["SKILL.md"]', ""]))
    assert apply(workflows, project) == 0
    assert report_of(workflows, project)["named"] == []


def test_an_agent_and_a_script_are_named_by_their_own_names(workflows, tmp_path):
    # T12
    write(workflows / "skills/phase/process-phase/references/notes.md",
          "Brief `phase-implementer`, then run `phase_selection.py`.\n")
    project = tmp_path / "p"
    project.mkdir()
    (project / ".devtools.toml").write_text(milestone_config(entries=("skills/phase/process-phase",),
                                                             folders=(".claude/skills",)))
    assert apply(workflows, project) == 0
    by = [".claude/skills/process-phase/references/notes.md"]
    assert report_of(workflows, project)["named"] == [
        {"unit": "agents", "by": by}, {"unit": "skills/phase/pytest/phase_selection.py", "by": by}]


def test_a_name_is_found_only_alone_in_backticks_or_as_a_folder_after_dotdot(workflows, tmp_path):
    # T13
    notes = workflows / "skills/phase/process-phase/references/notes.md"
    write(notes, "The review-pr skill; see `review-pr/SKILL.md`; the index is in docs/components/.\n")
    project = tmp_path / "p"
    project.mkdir()
    (project / ".devtools.toml").write_text(milestone_config(
        entries=("skills/phase/process-phase", "skills/milestone/start-milestone"), folders=(".claude/skills",)))
    assert apply(workflows, project) == 0
    assert report_of(workflows, project)["named"] == []
    write(notes, notes.read_text() + "Search `components` first.\n")
    assert [row["unit"] for row in report_of(workflows, project)["named"]] == ["skills/components"]


@pytest.mark.parametrize("config", [None, "unknown_key = 1\n", "[[sync]\n", "unreadable"])
def test_a_check_that_cannot_read_the_config_keeps_the_receipt_verdict(workflows, mproject, capsys, config):
    # T14
    assert apply(workflows, mproject) == 0
    path = mproject / ".devtools.toml"
    if config is None:
        path.unlink()
    elif config == "unreadable":
        if os.geteuid() == 0:
            pytest.skip("root reads a file of mode 000")
        path.chmod(0)
    else:
        path.write_text(config)
    capsys.readouterr()
    try:
        code, out, err = out_of(capsys, *check_source(mproject, workflows))
        assert (code, out) == (0, "12 managed file(s), 0 problem(s)\n")
        assert err.startswith("warning: not compared with dev-tools: ")
        assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 5
    finally:
        path.chmod(0o644) if path.exists() else None


def test_apply_with_a_config_that_is_not_toml_is_a_configuration_error(workflows, mproject, capsys):
    # T14b
    (mproject / ".devtools.toml").write_text("[[sync]\n")
    code, _, err = out_of(capsys, "apply", "--project", mproject, "--source", workflows)
    assert code == 2 and err.startswith("error: ")


def test_drift_wins_over_every_note_under_strict(workflows, mproject, capsys):
    # T15
    assert apply(workflows, mproject) == 0
    (mproject / ".claude/skills/start-milestone/SKILL.md").write_text("edited\n")
    assert out_of(capsys, *check_source(mproject, workflows, "--strict"))[0] == 1


def test_receipt_only_reads_no_source_and_the_default_source_is_a_dev_tools_checkout(source, project, capsys,
                                                                                     monkeypatch, tmp_path):
    # T16
    assert apply(source, project) == 0
    capsys.readouterr()
    real = sync.__dict__["default_source"]
    monkeypatch.undo()
    assert sync.default_source() == sync.SOURCE_ROOT
    assert sync.default_source(tmp_path) is None
    monkeypatch.setattr(sync, "default_source", real)

    def refuse(*args, **kwargs):
        raise AssertionError("check --receipt-only started a process")
    monkeypatch.setattr(sync.subprocess, "run", refuse)
    code, out, _ = out_of(capsys, "check", "--project", project, "--receipt-only")
    assert (code, out) == (0, "4 managed file(s), 0 problem(s)\n")
    monkeypatch.undo()
    monkeypatch.setattr(sync, "default_source", lambda *args, **kwargs: None)
    assert out_of(capsys, "check", "--project", project, "--receipt-only", "--source", source)[0] == 2
    assert out_of(capsys, "check", "--project", project, "--receipt-only", "--strict")[0] == 2
    assert out_of(capsys, "check", "--project", project, "--strict")[0] == 5


@pytest.mark.parametrize("declined, mark", [
    (["skills/milestone/review-pr"], "skills/milestone/review-pr  [declined in .devtools.toml]"),
    (None, "skills/milestone/review-pr  [named by .claude/skills/handle-issue/SKILL.md]")])
def test_the_survey_marks_a_declined_unit_and_a_named_one(workflows, mproject, capsys, declined, mark):
    # T17
    (mproject / ".devtools.toml").write_text(milestone_config(declined=declined))
    assert apply(workflows, mproject) == 0
    capsys.readouterr()
    assert run("survey", "--project", mproject, "--source", workflows) == 0
    out = capsys.readouterr().out.splitlines()
    assert mark in out[out.index("## Shipped, with no counterpart here"):]


@pytest.mark.parametrize("example", ["phase-project.devtools.toml", "milestone-project.devtools.toml"])
def test_each_example_applies_with_no_unit_report(tmp_path, capsys, example):
    # T18
    project = tmp_path / "fresh"
    project.mkdir()
    (project / ".devtools.toml").write_text((sync.SOURCE_ROOT / "examples" / example).read_text())
    code, out, _ = out_of(capsys, "apply", "--project", project)
    assert code == 0 and not any(h in out for h in HEADINGS), out


def test_a_current_project_prints_exactly_what_main_printed(source, project, capsys):
    # T19
    assert apply(source, project) == 0
    capsys.readouterr()
    assert out_of(capsys, "apply", "--project", project, "--source", source)[1] == 'applied: {"keep": 4}\n'
    assert out_of(capsys, *check_source(project, source))[1] == "4 managed file(s), 0 problem(s)\n"


def test_not_current_counts_what_an_apply_would_create_update_and_delete(source, project, capsys):
    # T20
    assert apply(source, project) == 0
    (source / "skills/demo/SKILL.md").write_text("demo skill, revised\n")
    (source / "skills/demo/new.md").write_text("new\n")
    (source / "skills/demo/scripts/tool.py").unlink()
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(project, source))
    assert out.splitlines()[1] == ("not current: an apply would create 1, update 1 and delete 1 file(s) "
                                   "(synced from dev-tools at an unknown commit; this source is at an unknown commit)")


def test_a_path_covers_whole_segments_only():
    # T21
    assert [sync.takes("skills/phase", unit) for unit in ("skills/phase-extra", "skills/phase/x", "skills/phase/")] == [
        False, True, True]
    assert [sync.covers("skills/phase", unit) for unit in ("skills/phase-extra", "skills/phase/x", "skills/phase/")] == [
        False, True, True]
    assert sync.takes("skills/phase/x/y", "skills/phase/x") and not sync.covers("skills/phase/x/y", "skills/phase/x")


def test_a_relative_path_names_the_folder_it_climbs_into(workflows, tmp_path):
    # T22
    project = tmp_path / "p"
    project.mkdir()
    (project / ".devtools.toml").write_text(milestone_config(entries=("skills/milestone/review-pr",),
                                                             folders=(".claude/skills",)))
    assert apply(workflows, project) == 0
    assert report_of(workflows, project)["named"] == [
        {"unit": "skills/milestone/process-phase", "by": [".claude/skills/review-pr/SKILL.md"]}]


def test_each_cause_alone_makes_strict_fail(workflows, mproject, capsys):
    # T23 (a) pending only, (b) named only; (c) new only is T6
    (mproject / ".devtools.toml").write_text(milestone_config(declined=["skills/milestone/review-pr"]))
    assert apply(workflows, mproject) == 0
    write(workflows / "skills/components/SKILL.md", "The component index, revised.\n")
    commit(workflows)
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(mproject, workflows, "--strict"))
    assert code == 5 and "not current" in out and not any(h in out for h in HEADINGS)
    (mproject / ".devtools.toml").write_text(milestone_config())
    assert apply(workflows, mproject) == 0
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(mproject, workflows, "--strict"))
    assert code == 5 and NAMED in out and "not current" not in out and NEW not in out


def test_a_unit_both_new_and_named_is_reported_as_named(workflows, mproject):
    # T24
    (mproject / ".devtools.toml").write_text(milestone_config(declined=["skills/milestone/review-pr", "agents"]))
    assert apply(workflows, mproject) == 0
    write(workflows / "skills/milestone/extra/SKILL.md", "Something new.\n")
    write(workflows / "skills/handle-issue/SKILL.md", "Route a fix with `extra`.\n")
    report = report_of(workflows, mproject)
    assert [row["unit"] for row in report["named"]] == ["skills/milestone/extra"]
    assert report["new"] == []


def test_a_hand_edited_file_is_drift_and_not_a_sign_the_project_is_behind(workflows, mproject, capsys):
    # T25 (implementation finding 1): "not current" counts the receipt against the source.
    (mproject / ".devtools.toml").write_text(milestone_config(declined=["skills/milestone/review-pr"]))
    assert apply(workflows, mproject) == 0
    (mproject / ".claude/skills/start-milestone/SKILL.md").write_text("edited\n")
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(mproject, workflows))
    assert (code, out) == (1, ".claude/skills/start-milestone/SKILL.md: differs from the receipt\n"
                              "12 managed file(s), 1 problem(s)\n")


# Regression tests for phase 1 review round 1 (notes/reviews/phase-1-r1).

@pytest.mark.parametrize("config", ["sync = 42\n", '[[sync]]\nsource = 42\ndest = "x"\n', 'after_apply = "make"\n',
                                    "sync = [1]\n"])
def test_a_config_of_the_wrong_shape_is_a_configuration_error(source, project, capsys, config):
    # r1 F1: check keeps the receipt verdict and warns; apply exits 2.
    assert apply(source, project) == 0
    (project / ".devtools.toml").write_text(config)
    capsys.readouterr()
    code, out, err = out_of(capsys, *check_source(project, source))
    assert (code, out) == (0, "4 managed file(s), 0 problem(s)\n")
    assert err.startswith("warning: not compared with dev-tools: ")
    assert out_of(capsys, *check_source(project, source, "--strict"))[0] == 5
    assert out_of(capsys, "apply", "--project", project, "--source", source)[0] == 2


def test_a_check_with_no_git_keeps_the_receipt_verdict(source, project, capsys, monkeypatch):
    # r1 F2
    assert apply(source, project) == 0
    capsys.readouterr()
    real = subprocess.run

    def no_git(argv, *args, **kwargs):
        if argv[0] == "git":
            raise FileNotFoundError("git")
        return real(argv, *args, **kwargs)
    monkeypatch.setattr(sync.subprocess, "run", no_git)
    code, out, _ = out_of(capsys, *check_source(project, source))
    assert (code, out) == (0, "4 managed file(s), 0 problem(s)\n")
    assert out_of(capsys, *check_source(project, source, "--strict"))[0] == 0


def test_a_file_already_as_shipped_is_not_counted_as_behind(source, project, capsys):
    # r1 F3: apply would keep it, so check does not call the project behind.
    assert apply(source, project) == 0
    (source / "skills/demo/new.md").write_text("new\n")
    (project / ".claude/skills/demo/new.md").write_text("new\n")
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(project, source, "--strict"))
    assert (code, out) == (0, "4 managed file(s), 0 problem(s)\n")


def test_a_receipt_with_no_files_still_hears_of_new_units(source, tmp_path, capsys):
    # r1 F4
    project = tmp_path / "empty"
    project.mkdir()
    (project / ".devtools.toml").write_text("sync = []\n")
    assert apply(source, project) == 0
    write(source / "skills/extra/SKILL.md", "Something new.\n")
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(project, source, "--strict"))
    assert code == 5 and out.splitlines()[1:3] == [NEW, "  skills/extra"]
    receipt = json.loads((project / ".devtools-receipt.json").read_text())
    del receipt["shipped"]
    (project / ".devtools-receipt.json").write_text(json.dumps(receipt))
    code, out, _ = out_of(capsys, *check_source(project, source))
    assert UNLISTED in out


# --------------------------------------------------------------------------- the latest dev-tools
# Milestone sync-reports, phase 2: a checkout only behind its upstream delivers the upstream's files.

NOTE = "note: dev-tools here is 1 commit(s) behind origin/"
OWN = "warning: dev-tools here is 1 commit(s) behind origin/"


@pytest.fixture(autouse=True)
def own_checkout_as_is(monkeypatch):
    """The repository's own checkout is read as it is in the suite, and never fetched."""
    real_run = subprocess.run

    def guarded(argv, *args, **kwargs):
        if list(argv[:4]) == ["git", "-C", str(sync.SOURCE_ROOT), "fetch"]:
            raise AssertionError("a test started git fetch in the repository's own checkout")
        return real_run(argv, *args, **kwargs)
    monkeypatch.setattr(sync.subprocess, "run", guarded)
    real_resolve = getattr(sync, "resolve_source", None)
    if real_resolve is not None:
        def resolve(path, *, as_is):
            return real_resolve(path, as_is=as_is or Path(path).resolve() == sync.SOURCE_ROOT)
        monkeypatch.setattr(sync, "resolve_source", resolve)


@pytest.fixture
def behind(tmp_path):
    """An upstream with two commits and a clone that has seen only the first."""
    upstream = tmp_path / "upstream"
    write(upstream / "skills/demo/SKILL.md", "first version\n")
    git(upstream, "init", "-q", "-b", "main")
    first = commit(upstream, "first")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(upstream), str(clone)], check=True)
    write(upstream / "skills/demo/SKILL.md", "second version\n")
    second = commit(upstream, "second")
    project = tmp_path / "behind-project"
    project.mkdir()
    (project / ".devtools.toml").write_text('[[sync]]\nsource = "skills/demo"\ndest = ".claude/skills/demo"\n')
    return {"upstream": upstream, "clone": clone, "project": project, "first": first, "second": second}


def delivered(b):
    return (b["project"] / ".claude/skills/demo/SKILL.md").read_text()


def checkout_state(root):
    return (git(root, "rev-parse", "HEAD"), git(root, "symbolic-ref", "-q", "HEAD"), git(root, "status", "--porcelain"))


def test_a_checkout_only_behind_delivers_its_upstream_and_is_not_changed(behind, capsys):
    # P2.1, T1
    before = checkout_state(behind["clone"])
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and delivered(behind) == "second version\n"
    assert NOTE + "main: delivering origin/main at " + behind["second"][:7] in err
    receipt = json.loads((behind["project"] / ".devtools-receipt.json").read_text())
    assert receipt["source"]["commit"] == behind["second"]
    assert checkout_state(behind["clone"]) == before


@pytest.mark.parametrize("own", ["commit", "uncommitted"])
def test_a_checkout_with_work_of_its_own_is_delivered_as_it_is(behind, capsys, own):
    # P2.2, T2, T3
    write(behind["clone"] / "skills/demo/SKILL.md", "the clone's own version\n")
    if own == "commit":
        commit(behind["clone"], "own")
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and delivered(behind) == "the clone's own version\n"
    assert OWN + "main and has work of its own" in err


def test_the_own_work_warning_comes_before_a_refusal(behind, capsys):
    # P2.2, T4
    commit_text = "the clone's own version\n"
    write(behind["clone"] / "skills/demo/SKILL.md", commit_text)
    commit(behind["clone"], "own")
    write(behind["project"] / ".claude/skills/demo/SKILL.md", "the project's own file\n")
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 3 and OWN + "main and has work of its own" in err


@pytest.mark.parametrize("state", ["level", "ahead", "detached", "no-upstream", "folder"])
def test_other_states_deliver_the_checkout_and_say_nothing_new(behind, capsys, state, tmp_path):
    # P2.3, T5
    clone = behind["clone"]
    if state == "level":
        git(clone, "pull", "-q")
    elif state == "ahead":
        git(clone, "pull", "-q")
        write(clone / "skills/demo/SKILL.md", "ahead\n")
        commit(clone, "ahead")
    elif state == "detached":
        git(clone, "checkout", "-q", "--detach")
    elif state == "no-upstream":
        git(clone, "checkout", "-q", "-b", "local-only")
    elif state == "folder":
        import shutil
        copy = tmp_path / "plain"
        shutil.copytree(clone / "skills", copy / "skills")
        clone = copy
    expected = (clone / "skills/demo/SKILL.md").read_text()
    code, out, err = out_of(capsys, "apply", "--project", behind["project"], "--source", clone, "--dry-run")
    assert code == 0 and "note:" not in err and "warning: dev-tools here" not in err
    assert out == out_of(capsys, "apply", "--project", behind["project"], "--source", clone, "--dry-run", "--as-is")[1]
    assert out_of(capsys, "apply", "--project", behind["project"], "--source", clone)[0] == 0
    assert delivered(behind) == expected


def test_an_upstream_that_is_gone_is_a_warning(behind, capsys):
    # P2.3b, T6 (plan r1 F5)
    git(behind["clone"], "config", "branch.main.merge", "refs/heads/gone")
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and delivered(behind) == "first version\n"
    assert "warning: this dev-tools branch's upstream, origin/gone, was not found" in err


def test_a_fetch_that_fails_decides_from_the_refs_already_fetched(behind, capsys, tmp_path):
    # P2.4, T7
    git(behind["clone"], "fetch", "-q")
    git(behind["clone"], "remote", "set-url", "origin", str(tmp_path / "no-such-repository"))
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and delivered(behind) == "second version\n"
    assert "warning: could not fetch origin (" in err


def test_a_fetch_that_times_out_is_a_warning(behind, capsys, monkeypatch):
    # P2.4, T8
    real = sync.subprocess.run

    def slow(argv, *args, **kwargs):
        if "fetch" in argv:
            raise subprocess.TimeoutExpired(argv, 60)
        return real(argv, *args, **kwargs)
    monkeypatch.setattr(sync.subprocess, "run", slow)
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and "warning: could not fetch origin (" in err and delivered(behind) == "first version\n"


def test_as_is_starts_no_fetch(behind, capsys, monkeypatch):
    # P2.5, T9
    calls = []
    real = sync.subprocess.run

    def record(argv, *args, **kwargs):
        calls.append(list(argv))
        return real(argv, *args, **kwargs)
    monkeypatch.setattr(sync.subprocess, "run", record)
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"], "--as-is")
    assert code == 0 and delivered(behind) == "first version\n" and "note:" not in err
    assert not any("fetch" in call for call in calls)
    git(behind["clone"], "fetch", "-q")
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"], "--as-is",
                          "--dry-run")
    assert (f"warning: dev-tools here is 1 commit(s) behind origin/main; delivering the checkout as it is (--as-is)"
            in err)


def test_compare_reads_what_apply_would(behind, capsys):
    # P2.6, T10
    assert apply(behind["clone"], behind["project"], "--as-is") == 0
    capsys.readouterr()
    _, dry, _ = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"], "--dry-run")
    _, compared, _ = out_of(capsys, "compare", "--project", behind["project"], "--source", behind["clone"],
                            ".claude/skills/demo/SKILL.md", "--added")
    assert "update: .claude/skills/demo/SKILL.md" in dry
    assert "second version" in compared


def test_a_source_inside_another_repository_is_not_fetched(behind, capsys, monkeypatch, tmp_path):
    # P2.7, T11
    outer = tmp_path / "outer"
    write(outer / "holder/skills/demo/SKILL.md", "inside another repository\n")
    git(outer, "init", "-q")
    commit(outer, "first")
    calls = []
    real = sync.subprocess.run
    monkeypatch.setattr(sync.subprocess, "run", lambda argv, *a, **k: calls.append(list(argv)) or real(argv, *a, **k))
    assert apply(outer / "holder", behind["project"]) == 0
    assert delivered(behind) == "inside another repository\n"
    assert not any("fetch" in call for call in calls)
    assert sync.resolve_source(outer / "holder", as_is=False)["state"] == "folder"


def test_a_tool_older_than_the_files_it_reads_says_so(behind, capsys):
    # T12
    write(behind["upstream"] / "devtools/sync.py", "# another sync.py\n")
    commit(behind["upstream"], "tool")
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and "note: the sync.py that runs differs from the one at origin/main" in err


def test_the_examples_never_fetch_the_repository(tmp_path, capsys):
    # T13: the autouse fixture raises if one does.
    project = tmp_path / "fresh"
    project.mkdir()
    (project / ".devtools.toml").write_text((sync.SOURCE_ROOT / "examples/milestone-project.devtools.toml").read_text())
    assert run("apply", "--project", project) == 0


def test_check_compares_with_the_upstream(behind, capsys):
    # T14
    assert apply(behind["clone"], behind["project"], "--as-is") == 0
    capsys.readouterr()
    code, out, _ = out_of(capsys, *check_source(behind["project"], behind["clone"]))
    assert code == 0 and out.splitlines()[1] == (
        f"not current: an apply would update 1 file(s) (synced from dev-tools at {behind['first'][:7]}; "
        f"this source is at {behind['second'][:7]})")


def test_resolve_source_names_each_state(behind, tmp_path):
    # T15
    resolved = sync.resolve_source(behind["clone"], as_is=False)
    root = resolved["root"]
    assert resolved["state"] == "upstream" and resolved["commit"] == behind["second"]
    assert (root / "skills/demo/SKILL.md").read_text() == "second version\n"
    resolved["cleanup"]()
    assert not root.exists()
    git(behind["clone"], "config", "branch.main.merge", "refs/heads/gone")
    assert sync.resolve_source(behind["clone"], as_is=False)["state"] == "upstream-missing"
    git(behind["clone"], "config", "branch.main.merge", "refs/heads/main")
    write(behind["clone"] / "skills/demo/SKILL.md", "own\n")
    commit(behind["clone"], "own")
    assert sync.resolve_source(behind["clone"], as_is=False)["state"] == "own-work"
    git(behind["clone"], "checkout", "-q", "--detach")
    assert sync.resolve_source(behind["clone"], as_is=False)["state"] == "detached"
    git(behind["clone"], "checkout", "-q", "-b", "local-only")
    assert sync.resolve_source(behind["clone"], as_is=False)["state"] == "no-upstream"
    assert sync.resolve_source(tmp_path / "upstream" / "skills", as_is=False)["state"] == "folder"


def test_as_is_on_a_checkout_known_to_be_behind_is_its_own_state(behind):
    # T15, the as-is row
    git(behind["clone"], "fetch", "-q")
    resolved = sync.resolve_source(behind["clone"], as_is=True)
    assert resolved["state"] == "as-is" and resolved["root"] == behind["clone"].resolve()


def test_an_upstream_that_cannot_be_read_leaves_the_checkout_as_it_is(behind, capsys, monkeypatch):
    # T16: reading the upstream's tree fails (phase 2 r1 F1 replaced git archive with ls-tree)
    real = sync.subprocess.run

    def no_archive(argv, *args, **kwargs):
        if "ls-tree" in argv:
            raise subprocess.CalledProcessError(128, argv)
        return real(argv, *args, **kwargs)
    monkeypatch.setattr(sync.subprocess, "run", no_archive)
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and delivered(behind) == "first version\n"
    assert "warning: could not read origin/main at " in err


def test_the_upstream_follows_the_remote_s_fetch_refspec(behind, capsys):
    # T17 (self-review): a remote whose refspec maps branches elsewhere than refs/remotes/<remote>/.
    git(behind["clone"], "config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/mirror/*")
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and delivered(behind) == "second version\n"
    assert f"delivering mirror/main at {behind['second'][:7]}" in err


# Regression tests for phase 2 review round 1 (notes/reviews/phase-2-r1).

def test_an_export_ignore_attribute_does_not_drop_a_shipped_file(behind, capsys):
    # r1 F1
    write(behind["upstream"] / "skills/demo/guide.md", "a guide\n")
    write(behind["upstream"] / ".gitattributes", "skills/demo/guide.md export-ignore\n")
    commit(behind["upstream"], "guide")
    capsys.readouterr()
    assert apply(behind["clone"], behind["project"]) == 0
    assert (behind["project"] / ".claude/skills/demo/guide.md").read_text() == "a guide\n"


def test_status_settings_do_not_hide_untracked_work(behind, capsys):
    # r1 F2
    git(behind["clone"], "config", "status.showUntrackedFiles", "no")
    write(behind["clone"] / "skills/demo/LOCAL.md", "the clone's own file\n")
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and OWN + "main and has work of its own" in err
    assert (behind["project"] / ".claude/skills/demo/LOCAL.md").is_file()


def test_tar_umask_does_not_change_delivered_modes(behind, capsys):
    # r1 F3
    git(behind["clone"], "config", "tar.umask", "0077")
    assert apply(behind["clone"], behind["project"]) == 0
    assert (behind["project"] / ".claude/skills/demo/SKILL.md").stat().st_mode & 0o777 == 0o644


def test_a_checkout_whose_path_ends_in_a_space_is_still_a_checkout(tmp_path, capsys):
    # r1 F4
    upstream = tmp_path / "up"
    write(upstream / "skills/demo/SKILL.md", "first version\n")
    git(upstream, "init", "-q", "-b", "main")
    commit(upstream, "first")
    clone = tmp_path / "clone "
    subprocess.run(["git", "clone", "-q", str(upstream), str(clone)], check=True)
    write(upstream / "skills/demo/SKILL.md", "second version\n")
    commit(upstream, "second")
    resolved = sync.resolve_source(clone, as_is=False)
    resolved["cleanup"]()
    assert resolved["state"] == "upstream"


def test_an_interrupted_read_of_the_upstream_leaves_no_folder(behind, monkeypatch, tmp_path):
    # r1 F5
    made = []
    real_mkdtemp = sync.tempfile.mkdtemp
    monkeypatch.setattr(sync.tempfile, "mkdtemp", lambda *a, **k: made.append(real_mkdtemp(*a, **k)) or made[-1])
    real = sync.subprocess.run

    def interrupt(argv, *args, **kwargs):
        if "cat-file" in argv or "archive" in argv or "ls-tree" in argv:
            raise KeyboardInterrupt
        return real(argv, *args, **kwargs)
    monkeypatch.setattr(sync.subprocess, "run", interrupt)
    with pytest.raises(KeyboardInterrupt):
        sync.resolve_source(behind["clone"], as_is=False)
    assert made and not any(Path(folder).exists() for folder in made)


# Regression tests for phase 2 review round 2 (notes/reviews/phase-2-r2).

def test_an_upstream_holding_a_symbolic_link_is_not_read(behind, capsys):
    # r2 F1: a link's target may be outside the commit; the checkout is delivered as it is.
    write(behind["clone"].parent / "shared-guide.md", "shared\n")
    import os as _os
    _os.symlink("../../../shared-guide.md", behind["upstream"] / "skills/demo/guide.md")
    commit(behind["upstream"], "link")
    git(behind["clone"], "pull", "-q")
    assert apply(behind["clone"], behind["project"], "--as-is") == 0
    capsys.readouterr()
    write(behind["upstream"] / "skills/demo/SKILL.md", "third version\n")
    commit(behind["upstream"], "third")
    code, _, err = out_of(capsys, "apply", "--project", behind["project"], "--source", behind["clone"])
    assert code == 0 and "is a symbolic link" in err
    assert (behind["project"] / ".claude/skills/demo/guide.md").read_text() == "shared\n"


def test_an_error_after_the_read_still_removes_the_folder(behind, monkeypatch):
    # r2 F2
    made = []
    real_mkdtemp = sync.tempfile.mkdtemp
    monkeypatch.setattr(sync.tempfile, "mkdtemp", lambda *a, **k: made.append(real_mkdtemp(*a, **k)) or made[-1])
    write(behind["upstream"] / "devtools/sync.py", "# another\n")
    commit(behind["upstream"], "tool")
    real_read = Path.read_bytes

    def fail_on_tool(self):
        if self.name == "sync.py":
            raise KeyboardInterrupt
        return real_read(self)
    monkeypatch.setattr(Path, "read_bytes", fail_on_tool)
    with pytest.raises(KeyboardInterrupt):
        sync.resolve_source(behind["clone"], as_is=False)
    assert made and not any(Path(folder).exists() for folder in made)


@pytest.mark.parametrize("hide", ["filemode", "assume-unchanged", "skip-worktree"])
def test_git_settings_do_not_hide_tracked_work(behind, capsys, hide):
    # r2 F3
    target = behind["clone"] / "skills/demo/SKILL.md"
    if hide == "filemode":
        git(behind["clone"], "config", "core.fileMode", "false")
        target.chmod(0o755)
    else:
        git(behind["clone"], "update-index", f"--{hide}", "skills/demo/SKILL.md")
        target.write_text("the clone's own version\n")
    assert sync.resolve_source(behind["clone"], as_is=False)["state"] == "own-work"


def test_only_git_s_line_terminator_is_removed():
    # r2 F4: a path may itself end in a newline.
    assert sync.git_line("/virtual/source\n\n") == "/virtual/source\n"
    assert sync.git_line("/virtual/source \n") == "/virtual/source "
    assert sync.git_line("abc") == "abc"


def test_a_run_that_reads_the_upstream_leaves_no_folder(behind, capsys, monkeypatch):
    # S0.2, C6: main removes the folder it read from.
    made = []
    real_mkdtemp = sync.tempfile.mkdtemp
    monkeypatch.setattr(sync.tempfile, "mkdtemp", lambda *a, **k: made.append(real_mkdtemp(*a, **k)) or made[-1])
    assert apply(behind["clone"], behind["project"]) == 0
    assert run("check", "--project", behind["project"], "--source", behind["clone"]) == 0
    assert len(made) == 2 and not any(Path(folder).exists() for folder in made)


@pytest.mark.parametrize("bad", ['values = []', 'exclude = "x"', 'settings = 1', '[sync.settings]\n"a.json" = 1'])
def test_a_sync_entry_of_the_wrong_shape_is_a_configuration_error(source, project, capsys, bad):
    # close review r1 F1
    assert apply(source, project) == 0
    (project / ".devtools.toml").write_text(f'[[sync]]\nsource = "skills/demo"\ndest = "copies"\n{bad}\n')
    capsys.readouterr()
    code, out, err = out_of(capsys, *check_source(project, source))
    assert (code, out) == (0, "4 managed file(s), 0 problem(s)\n")
    assert err.startswith("warning: not compared with dev-tools: ")
    assert out_of(capsys, "apply", "--project", project, "--source", source)[0] == 2
