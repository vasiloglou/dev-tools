"""Tests for handoff.py, the script behind the dev-handoff and dev-takeover skills: the note, what
check reports at each level, the ignored files it carries between checkouts, the takeover report,
and where its settings come from. Each test works in a small git repository of its own."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/dev-handoff/scripts/handoff.py"
SPEC = importlib.util.spec_from_file_location("handoff", SCRIPT)
handoff = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(handoff)


def git(repo: Path, *args: str) -> str:
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@example.com", "HOME": str(repo), "PATH": os.environ["PATH"]}
    done = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)}: {done.stderr}"
    return done.stdout.strip()


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture(autouse=True)
def default_settings(monkeypatch):
    monkeypatch.setattr(handoff, "SETTINGS", dict(handoff.DEFAULT_SETTINGS))
    monkeypatch.delenv("CLAUDECODE", raising=False)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A small project with a base branch and a feature branch checked out."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "base")
    write(repo, "src/app/core.py", "def total(xs):\n    return sum(xs)\n")
    write(repo, "AGENTS.md", "# Rules\n")
    write(repo, "CLAUDE.md", "@AGENTS.md\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "switch", "-q", "-c", "feature")
    return repo


def fill(path: Path, sections, value: str = "done") -> None:
    text = path.read_text()
    for heading in sections:
        text = text.replace(f"## {heading}\n\n{handoff.FILL}", f"## {heading}\n\n{value}")
    path.write_text(text)


def commit(repo: Path) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "handoff")


def by_check(repo: Path, path: Path) -> dict:
    return {f["check"]: f["severity"] for f in handoff.check_note(repo, path, base="base")}


def ignored_files(repo: Path) -> None:
    write(repo, ".gitignore", ".venv/\nruns/\n.env\n*.duckdb\n__pycache__/\nscratch/\n")
    write(repo, ".venv/bin/python", "#!\n")
    write(repo, "src/app/__pycache__/x.pyc", "x")
    write(repo, "runs/a/out.json", "{}\n")
    write(repo, "runs/a/big.bin", "x" * 4096)
    write(repo, "data.duckdb", "db")
    write(repo, ".env", "KEY=do-not-copy\n")
    commit(repo)


def handed_over(repo: Path, tmp_path: Path) -> Path:
    """A filled, committed note on ``repo`` and a fresh clone of it on the same branch."""
    ignored_files(repo)
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="new")
    fill(path, handoff.HUMAN_SECTIONS, "run the total tests")
    commit(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    return dest


def run(cwd: Path, *args: str, script: Path = SCRIPT, stdin=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True, input=stdin)


# --- the note ---

def test_write_creates_a_note_with_a_snapshot_and_sections_to_fill(repo):
    write(repo, "src/app/new.py", "x = 1\n")
    path = handoff.write_note(repo, base="base", today="2026-11-20")
    assert path == repo / ".planning/handoffs/feature.md"
    text = path.read_text()
    assert "branch: feature" in text and "base: base" in text
    assert "`src/app/new.py`" in text  # an untracked file is listed
    for heading in handoff.HUMAN_SECTIONS:
        assert f"## {heading}" in text
    assert handoff.FILL in text


def test_a_changed_tracked_file_is_listed_by_its_whole_path(repo):
    # git prints " M path" for the first line; stripping the output must not cost the path a letter.
    write(repo, "AGENTS.md", "# Rules\n\nMore.\n")
    assert handoff.snapshot(repo, "base")["dirty"] == ["AGENTS.md"]


def test_a_second_write_refreshes_the_snapshot_and_keeps_what_was_filled(repo):
    path = handoff.write_note(repo, base="base", today="2026-11-20")
    path.write_text(path.read_text().replace(f"## Goal\n\n{handoff.FILL}", "## Goal\n\nShip the cache."))
    write(repo, "later.txt", "x\n")
    handoff.write_note(repo, base="base", today="2026-11-21")
    again = path.read_text()
    assert "Ship the cache." in again
    assert "later.txt" in again and "updated: 2026-11-21" in again


def test_a_second_write_keeps_the_receiver_unless_a_flag_changes_it(repo):
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="same")
    handoff.write_note(repo, base="base")
    assert "to: codex" in path.read_text() and "level: 2" in path.read_text()
    handoff.write_note(repo, base="base", machine="new")
    assert "level: 3" in path.read_text() and "to: codex" in path.read_text()


def test_the_level_follows_the_receiver_and_the_machine():
    assert handoff.level("claude", "claude", "same") == 1  # another account, same assistant
    assert handoff.level("claude", "codex", "same") == 2
    assert handoff.level("claude", "any", "same") == 2  # unknown receiver: assume another assistant
    assert handoff.level("claude", "claude", "new") == 3
    assert handoff.level("claude", "codex", "new") == 3


# --- check ---

def test_check_names_empty_sections_a_pasted_key_and_uncommitted_files(repo):
    path = handoff.write_note(repo, base="base", today="2026-11-20")
    found = by_check(repo, path)
    assert "handoff/unfilled" in found
    assert "handoff/dirty" in found  # the note itself is uncommitted
    filled = path.read_text().replace(handoff.FILL, "done")
    path.write_text(filled + "\ntoken sk-ant-api03-abcdefghijklmnopqrstuvwxyz0123\n")
    found = by_check(repo, path)
    assert found["handoff/secret"] == "critical" and "handoff/unfilled" not in found
    path.write_text(filled)
    commit(repo)
    assert set(by_check(repo, path)) <= {"handoff/no-upstream"}


def test_the_same_assistant_on_the_same_machine_needs_only_the_short_note(repo):
    path = handoff.write_note(repo, base="base", sender="claude", to="claude", machine="same")
    assert "level: 1" in path.read_text()
    fill(path, handoff.REQUIRED[1])
    commit(repo)
    found = by_check(repo, path)
    assert not {"critical", "major"} & set(found.values())
    assert found["handoff/no-upstream"] == "info"  # no push needed on the same machine


def test_a_note_for_another_assistant_must_be_complete_and_stand_alone(repo):
    write(repo, ".claude/skills/process-phase/SKILL.md", "---\nname: process-phase\n---\n")
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="same")
    text = path.read_text()
    assert "level: 2" in text and "`AGENTS.md`, `CLAUDE.md`" in text and "`SKILL.md`" in text
    fill(path, handoff.REQUIRED[1])
    commit(repo)
    assert by_check(repo, path)["handoff/unfilled"] == "major"
    fill(path, handoff.HUMAN_SECTIONS, "run /process-phase 03, then /dvt-phase:process-phase 04; see docs/process-phase/x.md")
    commit(repo)
    found = {f["check"]: f for f in handoff.check_note(repo, path, base="base")}
    assert "handoff/unfilled" not in found
    assert found["handoff/claude-only"]["severity"] == "minor"  # slash commands codex cannot run
    assert found["handoff/claude-only"]["detail"] == "/dvt-phase:process-phase, /process-phase"


def test_check_exits_1_while_a_major_finding_stands_and_write_does_not(repo):
    done = run(repo, "write", "--base", "base", "--to", "claude", "--from", "claude", "--machine", "same")
    assert done.returncode == 0 and "wrote .planning/handoffs/feature.md" in done.stderr
    assert "sections missing or still empty" in done.stdout
    assert run(repo, "check", "--base", "base").returncode == 1
    fill(repo / ".planning/handoffs/feature.md", handoff.REQUIRED[1])
    commit(repo)
    done = run(repo, "check", "--base", "base")
    assert done.returncode == 0 and "[major]" not in done.stdout


# --- the files git ignores ---

def test_the_inventory_sorts_ignored_files_into_carry_rebuild_and_key(repo, monkeypatch):
    ignored_files(repo)
    write(repo, "scratch/tmp.txt", "x")
    kinds = {e["path"]: e["kind"] for e in handoff.ignored_inventory(repo)}
    assert kinds["runs/"] == "carry" and kinds["data.duckdb"] == "carry" and kinds["scratch/"] == "carry"
    assert kinds[".venv/"] == "rebuild" and kinds[".env"] == "key"
    assert not any("__pycache__" in p and k == "carry" for p, k in kinds.items())
    small = {e["path"]: e["kind"] for e in handoff.ignored_inventory(repo, max_mb=0.001)}
    assert small["runs/"] == "large" and small["data.duckdb"] == "carry"
    # A project names more paths the receiver rebuilds.
    monkeypatch.setitem(handoff.SETTINGS, "rebuild_paths", ["scratch/"])
    assert {e["path"]: e["kind"] for e in handoff.ignored_inventory(repo)}["scratch/"] == "rebuild"


def test_carry_is_a_dry_run_until_yes_and_never_copies_keys(repo, tmp_path):
    ignored_files(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    plan = handoff.carry(repo, str(dest), base="base")
    assert plan["copied"] is False and "runs/" in plan["paths"]
    assert not (dest / "runs").exists()
    done = handoff.carry(repo, str(dest), base="base", yes=True)
    assert done["copied"] is True
    assert (dest / "runs/a/out.json").read_text() == "{}\n"
    assert (dest / "data.duckdb").exists()
    assert not (dest / ".env").exists() and not (dest / ".venv").exists()
    assert ".env" in done["skipped"]["key"]
    refused = handoff.carry(repo, str(tmp_path / "missing"), base="base", yes=True)
    assert refused["copied"] is False and "not a checkout" in refused["reason"]


def test_carry_keeps_a_newer_file_at_the_destination(repo, tmp_path):
    ignored_files(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    write(dest, "runs/a/out.json", '{"newer": true}\n')
    os.utime(repo / "runs/a/out.json", (1_700_000_000, 1_700_000_000))
    handoff.carry(repo, str(dest), base="base", all_ages=True, yes=True)
    assert (dest / "runs/a/out.json").read_text() == '{"newer": true}\n'


def test_the_note_and_check_name_the_ignored_files_and_never_their_contents(repo):
    ignored_files(repo)
    path = handoff.write_note(repo, base="base", machine="new")
    assert "`runs/`" in path.read_text() and "do-not-copy" not in path.read_text()
    assert by_check(repo, path)["handoff/ignored"] == "minor"


def test_ignored_files_older_than_the_branch_stay_behind(repo, tmp_path):
    ignored_files(repo)
    os.utime(repo / "data.duckdb", (1_000_000_000, 1_000_000_000))
    since = handoff.branch_start(repo, "base")
    kinds = {e["path"]: e["kind"] for e in handoff.ignored_inventory(repo, since=since)}
    assert kinds["data.duckdb"] == "old" and kinds["runs/"] == "carry"
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    handoff.carry(repo, str(dest), base="base", yes=True)
    assert (dest / "runs/a/out.json").exists() and not (dest / "data.duckdb").exists()
    handoff.carry(repo, str(dest), base="base", all_ages=True, yes=True)
    assert (dest / "data.duckdb").exists()


def test_a_listing_from_another_host_is_held_to_this_checkouts_rules(repo):
    ignored_files(repo)
    sent = [{"path": "runs/", "kind": "carry", "bytes": 10, "files": 2},
            {"path": "../outside", "kind": "carry", "bytes": 1, "files": 1},
            {"path": "/etc/passwd", "kind": "carry", "bytes": 1, "files": 1},
            {"path": "--delete", "kind": "carry", "bytes": 1, "files": 1},
            {"path": "conf/.env", "kind": "carry", "bytes": 1, "files": 1},
            {"path": ".venv/", "kind": "carry", "bytes": 1, "files": 1},
            {"path": "x", "kind": "anything", "bytes": 1, "files": 1}, "not an entry"]
    kept = {e["path"]: e["kind"] for e in handoff._recheck(repo, sent)}
    assert kept == {"runs/": "carry", "conf/.env": "key", ".venv/": "rebuild"}
    assert handoff._recheck(repo, {"not": "a list"}) == []


def test_the_program_lists_ignored_files_when_it_arrives_on_standard_input(repo):
    # pull runs it this way on the old machine, over ssh, so that machine needs no copy of it.
    ignored_files(repo)
    done = subprocess.run([sys.executable, "-", "--repo", str(repo), "--base", "base", "--max-mb", "200",
                           "ignored", "--json"], input=SCRIPT.read_text(), capture_output=True, text=True,
                          cwd=repo.parent)
    assert done.returncode == 0, done.stderr
    assert {e["path"]: e["kind"] for e in json.loads(done.stdout)}["runs/"] == "carry"


def test_pull_from_another_host_sends_the_program_and_copies_with_rsync(repo, tmp_path, monkeypatch):
    dest = handed_over(repo, tmp_path)
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs.get("input", "")))
        if argv[0] == "ssh":
            listing = [{"path": "runs/", "kind": "carry", "bytes": 4099, "files": 2},
                       {"path": ".env", "kind": "carry", "bytes": 16, "files": 1}]
            return subprocess.CompletedProcess(argv, 0, json.dumps(listing), "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    real = subprocess.run
    monkeypatch.setattr(handoff.subprocess, "run", lambda argv, **kw: fake_run(argv, **kw) if argv[0] in {"ssh", "rsync"} else real(argv, **kw))
    monkeypatch.setattr(handoff.shutil, "which", lambda name: "/usr/bin/" + name)
    plan = handoff.pull(dest, "oldbox:~/work/repo", base="base")
    assert plan["paths"] == ["runs/"] and plan["skipped"]["key"] == [".env"] and plan["copied"] is False
    ssh, program = calls[0]
    assert ssh[:3] == ["ssh", "-o", "BatchMode=yes"] and ssh[-2] == "oldbox"
    assert ssh[-1] == "python3 - --repo ~/work/repo --base base --max-mb 200 ignored --json"
    assert program == SCRIPT.read_text()
    done = handoff.pull(dest, "oldbox:~/work/repo", base="base", yes=True)
    rsync, files = calls[-1]
    assert rsync[0] == "rsync" and rsync[-2:] == ["oldbox:~/work/repo/", f"{dest}/"]
    assert "--from0" in rsync and files == "runs/\0"
    assert done["copied"] is True
    refused = handoff.pull(dest, "oldbox:~/work; rm -rf x", base="base")
    assert "unsupported characters" in refused["reason"]


# --- taking over ---

def test_takeover_reports_the_note_its_commit_and_the_ignored_files_missing_here(repo, tmp_path):
    dest = handed_over(repo, tmp_path)
    report = handoff.takeover(dest, home=tmp_path)
    assert report["note"] == ".planning/handoffs/feature.md"
    assert report["meta"]["to"] == "codex" and report["meta"]["level"] == "3"
    assert report["head"] == "ok"  # the snapshot's commit is in this checkout's history
    assert "runs/" in report["missing_ignored"] and ".env" in report["missing_keys"]
    assert report["next_step"] == "run the total tests"
    assert report["ready"] is False


def test_pull_fetches_the_ignored_files_from_the_old_checkout(repo, tmp_path):
    dest = handed_over(repo, tmp_path)
    plan = handoff.pull(dest, str(repo), base="base")
    assert plan["copied"] is False and "runs/" in plan["paths"]
    done = handoff.pull(dest, str(repo), base="base", yes=True)
    assert done["copied"] is True and (dest / "runs/a/out.json").exists()
    assert not (dest / ".env").exists()
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_ignored"] == [] and report["ready"] is True


def test_takeover_says_when_the_notes_commit_is_not_in_this_branch(repo, tmp_path):
    dest = handed_over(repo, tmp_path)
    git(dest, "reset", "-q", "--hard", "HEAD~1")  # the note's commit, before the note was committed
    git(dest, "checkout", "-q", "origin/feature", "--", ".planning")
    assert handoff.takeover(dest, home=tmp_path)["head"] == "ok"
    note = dest / ".planning/handoffs/feature.md"
    note.write_text(note.read_text().replace(git(dest, "rev-parse", "--short", "HEAD"), "0123abc"))
    assert handoff.takeover(dest, home=tmp_path)["head"] == "missing"


def test_takeover_without_a_note_lists_the_notes_that_exist(repo, tmp_path):
    dest = handed_over(repo, tmp_path)
    git(dest, "switch", "-q", "-c", "elsewhere")
    report = handoff.takeover(dest, home=tmp_path)
    assert report["note"] is None and report["other_notes"] == ["feature.md"]
    assert report["ready"] is False
    assert "no hand-off note for branch elsewhere" in handoff._render_takeover(report)


def test_list_shows_each_branchs_own_note_once_local_and_on_origin(repo, tmp_path):
    path = handoff.write_note(repo, base="base", sender="claude", to="codex")
    fill(path, handoff.HUMAN_SECTIONS, "ship the cache\nsecond line")
    commit(repo)
    git(repo, "switch", "-q", "-c", "child")  # inherits feature.md, has no note of its own
    git(repo, "switch", "-q", "-c", "other", "base")
    other = handoff.write_note(repo, base="base", sender="codex", to="claude")
    commit(repo)
    found = {n["branch"]: n for n in handoff.available(repo)}
    assert set(found) == {"feature", "other"}
    assert found["feature"]["to"] == "codex" and found["feature"]["goal"] == "ship the cache"
    assert found["feature"]["where"] == "local" and found["other"]["current"] is True
    assert found["other"]["goal"] == ""  # a section nobody filled reads as empty
    assert other.name == "other.md"
    dest = tmp_path / "other-machine"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    remote = {n["branch"]: n for n in handoff.available(dest)}
    assert remote["feature"]["where"] == "origin" and remote["other"]["where"] == "local+origin"
    git(dest, "switch", "-q", "-c", "scratch", "origin/base")
    report = handoff.takeover(dest, home=tmp_path)
    assert report["note"] is None
    assert {n["branch"] for n in report["available"]} == {"feature", "other"}


# --- the project's settings ---

def test_doctor_checks_what_the_project_names_and_never_reads_a_key(repo, tmp_path, monkeypatch):
    home = tmp_path / "home"
    write(home, ".config/app/key", "do-not-print")
    monkeypatch.setattr(handoff, "SETTINGS", {**handoff.DEFAULT_SETTINGS, "tools": ["git", "no-such-tool-xyz"],
                                              "env_paths": [".venv"], "setup_command": "uv sync --frozen",
                                              "key_files": [".config/app/key", ".config/app/other"]})
    rows = {row["name"]: row for row in handoff.doctor(repo, home=home)}
    assert rows["git"]["ok"] and not rows["no-such-tool-xyz"]["ok"]
    assert not rows["environment: .venv"]["ok"] and rows["environment: .venv"]["fix"] == "uv sync --frozen"
    assert not rows["git remote"]["ok"] and not rows["key files"]["ok"]
    assert "~/.config/app/key" in rows["key files"]["detail"] and "missing: ~/.config/app/other" in rows["key files"]["detail"]
    assert "do-not-print" not in repr(rows)
    write(repo, ".venv/bin/python", "#!\n")
    assert {row["name"]: row for row in handoff.doctor(repo, home=home)}["environment: .venv"]["ok"]
    # With no settings a project is asked for nothing of its own.
    monkeypatch.setattr(handoff, "SETTINGS", dict(handoff.DEFAULT_SETTINGS))
    assert [row["name"] for row in handoff.doctor(repo, home=home)] == ["git remote", "base branch", "assistants"]


def test_a_worktree_finds_the_environment_in_the_main_checkout(repo, tmp_path, monkeypatch):
    monkeypatch.setitem(handoff.SETTINGS, "env_paths", [".venv"])
    write(repo, ".gitignore", ".venv/\n")
    write(repo, ".venv/bin/python", "#!\n")
    commit(repo)
    tree = tmp_path / "tree"
    git(repo, "worktree", "add", "-q", str(tree), "-b", "second")
    rows = {row["name"]: row for row in handoff.doctor(tree, home=tmp_path)}
    assert rows["environment: .venv"]["ok"] and str(repo.resolve()) in rows["environment: .venv"]["detail"]


def test_the_base_branch_comes_from_the_setting_then_the_phase_state_then_origin(repo, tmp_path, monkeypatch):
    assert handoff.default_base(repo) == "main"  # nothing says: main
    dest = tmp_path / "clone"
    git(repo, "switch", "-q", "base")
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    git(dest, "switch", "-q", "-c", "work")
    assert handoff.default_base(dest) == "base"  # origin's default branch
    write(dest, ".planning/STATE.md", "---\nbase_branch: develop\ncurrent_phase: \"03\"\nphase_status: plan_approved\n---\n")
    assert handoff.default_base(dest) == "develop"  # the phase workflow's STATE.md
    assert handoff.snapshot(dest)["state"] == {"current_phase": "03", "phase_status": "plan_approved"}
    monkeypatch.setitem(handoff.SETTINGS, "base_branch", "trunk")
    assert handoff.default_base(dest) == "trunk"


def test_a_base_that_exists_only_on_origin_is_still_compared_with(repo, tmp_path):
    dest = tmp_path / "clone"
    git(tmp_path, "clone", "-q", str(repo), str(dest))  # checks out feature; base is origin/base only
    write(dest, "more.py", "y = 2\n")
    commit(dest)
    assert handoff.base_ref(dest, "base") == "origin/base"
    snap = handoff.snapshot(dest, "base")
    assert snap["ahead_of_base"] == 1 and len(snap["commits"]) == 1
    assert handoff.base_ref(dest, "no-such-branch") == ""


def test_the_notes_follow_the_planning_folder_the_project_names(repo, monkeypatch):
    monkeypatch.setitem(handoff.SETTINGS, "planning_dir", "docs/plan")
    write(repo, "docs/plan/phases/03-cache/.continue-here.md", "next: T2\n")
    path = handoff.write_note(repo, base="base")
    assert path == repo / "docs/plan/handoffs/feature.md"
    assert "- Paused phase: `docs/plan/phases/03-cache/.continue-here.md`" in path.read_text()


def test_a_synced_copy_reads_the_settings_beside_it_and_refuses_an_unknown_key(repo, tmp_path):
    copy = repo / ".claude/skills/dev-handoff/scripts/handoff.py"
    copy.parent.mkdir(parents=True)
    shutil.copy(SCRIPT, copy)
    copy.with_suffix(".settings.json").write_text(json.dumps({"planning_dir": "plan", "base_branch": "base"}))
    done = run(repo, "write", script=copy)
    assert done.returncode == 0 and "wrote plan/handoffs/feature.md" in done.stderr
    assert "base: base" in (repo / "plan/handoffs/feature.md").read_text()
    copy.with_suffix(".settings.json").write_text(json.dumps({"planing_dir": "plan"}))
    done = run(repo, "write", script=copy)
    assert done.returncode != 0 and "unknown setting(s): planing_dir" in done.stderr


def test_a_plugin_install_reads_the_projects_settings(repo, tmp_path):
    plugin = tmp_path / "cache" / "dvt-phase"
    shutil.copytree(ROOT / "plugins/dvt-phase", plugin)
    tool = plugin / "skills/dev-handoff/scripts/handoff.py"
    write(repo, ".devtools/handoff.settings.json", json.dumps({"planning_dir": "plan", "base_branch": "base"}))
    done = run(repo, "write", "--to", "codex", script=tool)
    assert done.returncode == 0 and "wrote plan/handoffs/feature.md" in done.stderr
    # A skill of the plugin is called as /dvt-phase:<skill>; a note for codex is told so.
    note = repo / "plan/handoffs/feature.md"
    fill(note, handoff.HUMAN_SECTIONS, "then /dvt-phase:dev-takeover")
    assert "/dvt-phase:dev-takeover" in run(repo, "check", script=tool).stdout


def test_outside_a_checkout_the_script_says_so(tmp_path):
    done = run(tmp_path, "check")
    assert done.returncode == 2 and "is not a git checkout" in done.stderr


# --- what the reviews of the pull request found ---

def test_a_key_file_inside_an_ignored_folder_is_left_out(repo, tmp_path):
    ignored_files(repo)
    write(repo, "runs/.env", "KEY=do-not-copy\n")
    write(repo, "runs/a/private.pem", "pem\n")
    write(repo, "runs/secrets/db.json", "{}\n")
    entry = {e["path"]: e for e in handoff.ignored_inventory(repo)}["runs/"]
    assert entry["kind"] == "carry" and entry["keys"] == ["runs/.env", "runs/a/private.pem", "runs/secrets/"]
    assert "3 key paths inside are left out" in handoff._render_ignored([entry])
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    done = handoff.carry(repo, str(dest), base="base", yes=True)
    assert done["copied"] is True and (dest / "runs/a/out.json").exists()
    assert not (dest / "runs/.env").exists() and not (dest / "runs/a/private.pem").exists()
    assert not (dest / "runs/secrets").exists()
    assert done["skipped"]["key"] == [".env", "runs/.env", "runs/a/private.pem", "runs/secrets/"]
    handoff.carry(repo, str(dest), base="base", with_keys=True, yes=True)
    assert (dest / "runs/.env").exists() and (dest / "runs/secrets/db.json").exists()


def test_rsync_is_told_to_leave_out_the_key_files_inside_a_folder(repo, tmp_path, monkeypatch):
    ignored_files(repo)
    write(repo, "runs/.env", "KEY=x\n")
    write(repo, "runs/odd[1]*.pem", "pem\n")
    calls = []
    real = subprocess.run

    def fake(argv, **kw):
        if argv[0] in {"ssh", "rsync"}:
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, "", "")
        return real(argv, **kw)

    monkeypatch.setattr(handoff.subprocess, "run", fake)
    monkeypatch.setattr(handoff.shutil, "which", lambda name: "/usr/bin/" + name)
    handoff.carry(repo, "otherbox:~/work/repo", base="base", yes=True)
    rsync = calls[-1]
    assert rsync[0] == "rsync" and "--exclude=/runs/.env" in rsync and r"--exclude=/runs/odd\[1\]\*.pem" in rsync
    handoff.carry(repo, "otherbox:~/work/repo", base="base", with_keys=True, yes=True)
    assert not [arg for arg in calls[-1] if arg.startswith("--exclude")]


def test_real_rsync_honours_those_exclusions(repo, tmp_path):
    # The pattern is anchored at the checkout, the way rsync reads it with --files-from.
    if not shutil.which("rsync"):
        pytest.skip("rsync is not installed")
    ignored_files(repo)
    write(repo, "runs/.env", "KEY=x\n")
    dest = tmp_path / "plain"
    dest.mkdir()
    plan = handoff._plan(handoff.ignored_inventory(repo), False)
    done = handoff._rsync(plan, f"{repo}/", f"{dest}/")
    assert done["copied"] is True and (dest / "runs/a/out.json").exists()
    assert not (dest / "runs/.env").exists()


def test_a_copy_never_leaves_the_receiving_checkout_through_a_link(repo, tmp_path):
    ignored_files(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    outside = tmp_path / "outside"
    outside.mkdir()
    (dest / "runs").symlink_to(outside)
    write(dest, "data.duckdb", "")
    os.utime(dest / "data.duckdb", (1_000_000_000, 1_000_000_000))
    (dest / "data.duckdb").unlink()
    (outside / "victim.txt").write_text("mine\n")
    (dest / "data.duckdb").symlink_to(outside / "victim.txt")
    done = handoff.carry(repo, str(dest), base="base", yes=True)
    assert list(outside.iterdir()) == [outside / "victim.txt"]
    assert (outside / "victim.txt").read_text() == "mine\n"
    assert sorted(done["refused"]) == ["data.duckdb", "runs/a/big.bin", "runs/a/out.json"]
    said = handoff._render_carry(done)
    assert "refused (a link or another kind of file is in the way in the receiving checkout): data.duckdb" in said


def test_a_listing_from_another_host_cannot_name_the_checkout_or_a_tracked_path(repo):
    ignored_files(repo)
    sent = [{"path": path, "kind": "carry", "bytes": 1, "files": 1}
            for path in (".", "./", "./runs/", "src/", "src/app/core.py", "runs/", "runs/a/../../src/")]
    kinds = {e["path"]: e["kind"] for e in handoff._recheck(repo, sent)}
    assert kinds == {"src/": "refused", "src/app/core.py": "refused", "runs/": "carry"}
    plan = handoff._plan(handoff._recheck(repo, sent), False)
    assert plan["paths"] == ["runs/"] and plan["skipped"]["refused"] == ["src/", "src/app/core.py"]
    # The key paths it names inside a folder are held to the same rules.
    sent = [{"path": "runs/", "kind": "carry", "bytes": 1, "files": 1,
             "keys": ["runs/.env", "../x", "other/.env", 7, "runs/a/-x.pem"]}]
    assert handoff._recheck(repo, sent)[0]["keys"] == ["runs/.env", "runs/a/-x.pem"]


def test_show_list_and_takeover_never_print_a_key_a_note_contains(repo, tmp_path):
    fake = "sk-ant-" + "api03-" + "a" * 30
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="same")
    fill(path, handoff.HUMAN_SECTIONS, f"export KEY={fake} and run")
    commit(repo)
    for command in ("show", "list", "takeover"):
        done = run(repo, command, "--base", "base")
        assert fake not in done.stdout, command
        assert "[removed: looks like a key]" in done.stdout, command
    assert "[critical]" in run(repo, "show", "--base", "base").stdout
    assert fake not in json.dumps(handoff.takeover(repo, home=tmp_path)) + json.dumps(handoff.available(repo))


@pytest.mark.parametrize("damage", ["frontmatter alone", "blank sections", "one section deleted"])
def test_check_wants_every_required_section_present_and_written(repo, damage):
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="new")
    fill(path, handoff.HUMAN_SECTIONS)
    text = path.read_text()
    if damage == "frontmatter alone":
        text = handoff._head(handoff._frontmatter(text))
    elif damage == "blank sections":
        text = text.replace("\n\ndone\n", "\n\n\n")
    else:
        text = text.replace("## Next step\n\ndone\n", "")
    path.write_text(text)
    commit(repo)
    found = {f["check"]: f for f in handoff.check_note(repo, path, base="base")}
    assert found["handoff/unfilled"]["severity"] == "major"
    assert "Next step" in found["handoff/unfilled"]["detail"]


def test_takeover_is_not_ready_without_a_next_step_or_a_tool_the_project_names(repo, tmp_path, monkeypatch):
    dest = handed_over(repo, tmp_path)
    handoff.pull(dest, str(repo), base="base", yes=True)
    assert handoff.takeover(dest, home=tmp_path)["ready"] is True
    monkeypatch.setitem(handoff.SETTINGS, "tools", ["no-such-tool-xyz"])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["ready"] is False and report["blocking"] == ["no-such-tool-xyz"]
    assert "[MISSING] no-such-tool-xyz" in handoff._render_takeover(report)
    monkeypatch.setitem(handoff.SETTINGS, "tools", [])
    note = dest / ".planning/handoffs/feature.md"
    note.write_text(note.read_text().replace("## Next step\n\nrun the total tests\n", "## Next step\n\n"))
    report = handoff.takeover(dest, home=tmp_path)
    assert report["ready"] is False and "the note has no next step" in handoff._render_takeover(report)


def test_the_same_machine_needs_no_remote_to_be_ready(repo, tmp_path):
    path = handoff.write_note(repo, base="base", sender="claude", to="claude", machine="same")
    fill(path, handoff.HUMAN_SECTIONS)
    commit(repo)
    report = handoff.takeover(repo, home=tmp_path)  # no origin at all
    assert report["ready"] is True and report["blocking"] == []
    assert "not needed to continue: git remote" in handoff._render_takeover(report)
    handoff.write_note(repo, base="base", machine="new")
    commit(repo)
    report = handoff.takeover(repo, home=tmp_path)
    assert report["ready"] is False and report["blocking"] == ["git remote"]


def test_carry_to_another_host_first_asks_whether_the_destination_is_a_checkout(repo, monkeypatch):
    ignored_files(repo)
    calls, answers = [], {"ssh": 3}
    real = subprocess.run

    def fake(argv, **kw):
        if argv[0] in {"ssh", "rsync"}:
            calls.append(argv)
            return subprocess.CompletedProcess(argv, answers.get(argv[0], 0), "", "")
        return real(argv, **kw)

    monkeypatch.setattr(handoff.subprocess, "run", fake)
    monkeypatch.setattr(handoff.shutil, "which", lambda name: "/usr/bin/" + name)
    plan = handoff.carry(repo, "otherbox:~/work/elsewhere", base="base", yes=True)
    assert plan["copied"] is False and "is not a checkout" in plan["reason"]
    assert [call[0] for call in calls] == ["ssh"] and calls[0][-2] == "otherbox"
    assert calls[0][-1] == "test -e ~/work/elsewhere/.git || exit 3; git -C ~/work/elsewhere ls-files -z"
    answers["ssh"] = 0
    assert handoff.carry(repo, "otherbox:~/work/repo", base="base", yes=True)["copied"] is True
    assert [call[0] for call in calls] == ["ssh", "ssh", "rsync"]
    refused = handoff.carry(repo, "otherbox:~/work; rm -rf x", base="base", yes=True)
    assert "unsupported characters" in refused["reason"] and len(calls) == 3


@pytest.mark.parametrize("lost", [("START",), ("END",), ("START", "END")])
def test_write_keeps_what_a_note_without_its_markers_says(repo, lost):
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="same")
    fill(path, handoff.HUMAN_SECTIONS, "ship the cache")
    text = path.read_text()
    for marker in lost:
        text = text.replace(getattr(handoff, "SNAPSHOT_" + marker) + "\n", "")
    path.write_text(text)
    handoff.write_note(repo, base="base")
    text = path.read_text()
    assert text.count("ship the cache") == len(handoff.HUMAN_SECTIONS) and handoff.FILL not in text
    assert text.count(handoff.SNAPSHOT_START) == 1 and text.count(handoff.SNAPSHOT_END) == 1
    assert "to: codex" in text and text.count("## Goal") == 1


def test_write_leaves_alone_a_file_that_is_no_note(repo):
    path = handoff.write_note(repo, base="base")
    path.write_text("my own notes about this branch\n")
    with pytest.raises(handoff.HandoffError, match="is not a hand-off note"):
        handoff.write_note(repo, base="base")
    assert path.read_text() == "my own notes about this branch\n"
    done = run(repo, "write", "--base", "base")
    assert done.returncode == 1 and "is not a hand-off note" in done.stderr


def test_a_changed_level_changes_which_sections_the_note_calls_optional(repo):
    path = handoff.write_note(repo, base="base", sender="claude", to="claude", machine="same")
    assert path.read_text().count("Optional at level 1.") == 4
    handoff.write_note(repo, base="base", machine="new")
    assert "Optional at level" not in path.read_text()
    handoff.write_note(repo, base="base", machine="same")
    assert path.read_text().count("Optional at level 1.") == 4


def test_a_sender_recorded_as_unknown_is_replaced_once_it_is_known(repo, monkeypatch):
    path = handoff.write_note(repo, base="base", to="claude", machine="same")
    assert "from: unknown" in path.read_text() and "level: 2" in path.read_text()
    monkeypatch.setenv("CLAUDECODE", "1")
    handoff.write_note(repo, base="base")
    assert "from: claude" in path.read_text() and "level: 1" in path.read_text()


def test_ignored_names_the_paths_it_treats_as_rebuildable(repo):
    ignored_files(repo)
    write(repo, ".gitignore", ".venv/\nruns/\n.env\n*.duckdb\n__pycache__/\ntarget/\n")
    write(repo, "target/model.bin", "weights")
    text = handoff._render_ignored(handoff.ignored_inventory(repo))
    assert "rebuilt on the other side, not carried: .venv/, src/app/__pycache__/, target/" in text
    # Named exactly, a path the script would have left to be rebuilt is carried.
    assert handoff._plan(handoff.ignored_inventory(repo, include=["target/"]), False)["paths"] == ["target/"]


def test_write_sizes_the_ignored_files_once(repo, monkeypatch):
    ignored_files(repo)
    walks = []
    real = handoff.ignored_inventory
    monkeypatch.setattr(handoff, "ignored_inventory", lambda *a, **kw: walks.append(1) or real(*a, **kw))
    monkeypatch.setattr(sys, "argv", ["handoff.py"])
    assert handoff.main(["--repo", str(repo), "--base", "base", "write"]) == 0
    assert len(walks) == 1


def test_a_note_for_a_reader_without_the_skills_says_what_to_do_on_arrival(repo):
    path = handoff.write_note(repo, base="base", sender="claude", to="gemini", machine="new")
    text = path.read_text()
    assert "Without the dev-takeover skill:" in text and "approves nothing" in text
    same = handoff.write_note(repo, base="base", sender="claude", to="claude", machine="same").read_text()
    assert "Without the dev-takeover skill:" not in same


# --- the second review round ---

def test_a_rebuildable_folder_carried_by_name_still_leaves_its_key_files_out(repo, tmp_path):
    write(repo, ".gitignore", "target/\n")
    write(repo, "target/model.bin", "weights")
    write(repo, "target/private.pem", "pem\n")
    write(repo, "target/secrets/db.json", "{}\n")
    commit(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    done = handoff.carry(repo, str(dest), base="base", include=["target/"], yes=True)
    assert done["copied"] is True and (dest / "target/model.bin").exists()
    assert not (dest / "target/private.pem").exists() and not (dest / "target/secrets").exists()
    assert done["skipped"]["key"] == ["target/private.pem", "target/secrets/"]
    # Named, it is held to the size limit and the branch's age like any other path.
    small = handoff.carry(repo, str(dest), base="base", include=["target"], max_mb=0.000001)
    assert small["paths"] == [] and small["skipped"]["large"] == ["target/"]
    # A key file named by its own path is still a key file.
    named = handoff.carry(repo, str(dest), base="base", include=["target/secrets/db.json", "target/private.pem"])
    assert named["paths"] == [] and named["skipped"]["key"] == ["target/private.pem", "target/secrets/db.json"]


def test_a_copy_leaves_alone_a_file_the_receiving_checkout_tracks(repo, tmp_path):
    write(repo, ".gitignore", "report.json\nruns/\n")
    commit(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    write(dest, "report.json", "tracked here\n")
    write(dest, "runs/kept.txt", "tracked here\n")
    write(dest, "runs/only-here.txt", "tracked here\n")
    git(dest, "add", "-f", "report.json", "runs/kept.txt", "runs/only-here.txt")
    git(dest, "commit", "-q", "-m", "track them")
    for name in ("report.json", "runs/kept.txt"):
        os.utime(dest / name, (1_000_000_000, 1_000_000_000))
    write(repo, "report.json", "from the old checkout\n")
    write(repo, "runs/kept.txt", "from the old checkout\n")
    write(repo, "runs/out.json", "{}\n")
    plan = handoff.carry(repo, str(dest), base="base")
    assert plan["paths"] == ["runs/"] and plan["skipped"]["tracked"] == ["report.json", "runs/kept.txt"]
    done = handoff.carry(repo, str(dest), base="base", yes=True)
    assert done["copied"] is True and (dest / "runs/out.json").exists()
    assert git(dest, "status", "--short") == "" and (dest / "report.json").read_text() == "tracked here\n"
    said = handoff._render_carry(done)
    assert "left alone (it would replace what git tracks in the receiving checkout): report.json" in said
    (dest / "runs/out.json").unlink()
    pulled = handoff.pull(dest, str(repo), base="base", yes=True)
    assert pulled["skipped"]["tracked"] == ["report.json", "runs/kept.txt"] and (dest / "runs/out.json").exists()
    assert git(dest, "status", "--short") == ""


def test_a_copy_to_or_from_another_host_leaves_tracked_files_alone_too(repo, tmp_path, monkeypatch):
    ignored_files(repo)
    calls = []
    real = subprocess.run

    def fake(argv, **kw):
        if argv[0] not in {"ssh", "rsync"}:
            return real(argv, **kw)
        calls.append(argv)
        if argv[0] == "ssh" and "ls-files" in argv[-1]:
            return subprocess.CompletedProcess(argv, 0, "runs/a/out.json\0src/app/core.py\0data.duckdb\0", "")
        listing = [{"path": "runs/", "kind": "carry", "bytes": 4099, "files": 2},
                   {"path": "data.duckdb", "kind": "carry", "bytes": 2, "files": 1}]
        return subprocess.CompletedProcess(argv, 0, json.dumps(listing) if argv[0] == "ssh" else "", "")

    monkeypatch.setattr(handoff.subprocess, "run", fake)
    monkeypatch.setattr(handoff.shutil, "which", lambda name: "/usr/bin/" + name)
    done = handoff.carry(repo, "otherbox:~/work/repo", base="base", yes=True)
    assert done["paths"] == ["runs/"] and done["skipped"]["tracked"] == ["data.duckdb", "runs/a/out.json"]
    assert calls[-1][0] == "rsync" and "--exclude=/runs/a/out.json" in calls[-1]
    # Arriving: the receiving checkout is this one, so git here says what it tracks.
    git(repo, "add", "-f", "runs/a/big.bin")
    git(repo, "commit", "-q", "-m", "track one")
    pulled = handoff.pull(repo, "oldbox:~/work/repo", base="base", yes=True)
    assert pulled["skipped"]["tracked"] == ["runs/a/big.bin"] and "--exclude=/runs/a/big.bin" in calls[-1]


def test_include_reaches_inside_an_ignored_folder_and_matches_whole_names(repo, tmp_path):
    write(repo, ".gitignore", "runs/\nruns-private/\n.venv/\n")
    for rel in ("runs/experiment-1/out.json", "runs/experiment-2/out.json", "runs/top.json", "runs/log.txt",
                "runs-private/notes.txt", ".venv/lib/site.json"):
        write(repo, rel, "{}\n")
    write(repo, "runs/experiment-1/.env", "KEY=x\n")
    commit(repo)

    def paths(*globs):
        return sorted(e["path"] for e in handoff.ignored_inventory(repo, include=list(globs)))

    assert paths("runs") == ["runs/"] == paths("runs/")
    assert paths("runs*") == ["runs-private/", "runs/"]
    assert paths("runs/experiment-1/") == ["runs/experiment-1/"] == paths("runs/experiment-1")
    assert paths("runs/*.json") == ["runs/experiment-1/out.json", "runs/experiment-2/out.json", "runs/top.json"]
    assert paths("runs/exp*") == ["runs/experiment-1/", "runs/experiment-2/"]
    assert paths("runs/top.json", "runs/nothing", "runs/../.gitignore", "runs/experiment-1/../log.txt") == ["runs/top.json"]
    assert paths("runs/experiment-1/", "runs/*out.json") == ["runs/experiment-1/", "runs/experiment-2/out.json"]
    # A glob does not reach into a path left to be rebuilt; its exact name does.
    assert paths("*.json") == ["runs/experiment-1/out.json", "runs/experiment-2/out.json", "runs/top.json"]
    assert paths(".venv/lib/") == [".venv/lib/"]
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    done = handoff.carry(repo, str(dest), base="base", include=["runs/experiment-1/"], yes=True)
    assert (dest / "runs/experiment-1/out.json").exists() and not (dest / "runs/experiment-2").exists()
    assert not (dest / "runs/experiment-1/.env").exists() and not (dest / "runs/top.json").exists()
    assert done["paths"] == ["runs/experiment-1/"] and done["skipped"]["key"] == ["runs/experiment-1/.env"]
    listed = run(repo, "ignored", "--json", "--base", "base", "--include", "runs/*.json")
    assert [e["path"] for e in json.loads(listed.stdout)] == paths("runs/*.json")


def test_pull_from_another_host_narrows_the_listing_on_that_host(repo, tmp_path, monkeypatch):
    ignored_files(repo)
    write(repo, ".gitignore", ".venv/\nruns/\n.env\n*.duckdb\n__pycache__/\ntarget/\n")
    calls = []
    real = subprocess.run

    def fake(argv, **kw):
        if argv[0] not in {"ssh", "rsync"}:
            return real(argv, **kw)
        calls.append(argv)
        listing = [{"path": "runs/a/", "kind": "carry", "bytes": 4099, "files": 2},
                   {"path": "target/", "kind": "carry", "bytes": 9, "files": 1, "keys": ["target/private.pem"]},
                   {"path": ".venv/", "kind": "carry", "bytes": 9, "files": 1}]
        return subprocess.CompletedProcess(argv, 0, json.dumps(listing), "")

    monkeypatch.setattr(handoff.subprocess, "run", fake)
    plan = handoff.pull(repo, "oldbox:~/work/repo", base="base", include=["runs/a/", "target", "it's*"])
    assert calls[0][-1].endswith("ignored --json --include runs/a/ --include target --include 'it'\"'\"'s*'")
    # A rebuildable path is taken only under the name that was asked for, and a path the other
    # host adds to what was asked for is dropped.
    assert plan["paths"] == ["runs/a/", "target/"] and plan["exclude"] == ["target/private.pem"]
    assert plan["skipped"]["rebuild"] == [] and ".venv/" not in plan["paths"]


def test_show_prints_one_json_document_when_asked(repo):
    path = handoff.write_note(repo, base="base")
    write(repo, path.relative_to(repo).as_posix(), path.read_text() + "key sk-ant-" + "a" * 30 + "\n")
    shown = json.loads(run(repo, "show", "--json", "--base", "base").stdout)
    assert shown["path"] == ".planning/handoffs/feature.md" and shown["note"].startswith("---\n")
    assert handoff.REMOVED in shown["note"] and "sk-ant-" not in shown["note"]
    assert "handoff/secret" in {f["check"] for f in shown["findings"]}
    path.unlink()
    missing = json.loads(run(repo, "show", "--json", "--base", "base").stdout)
    assert missing["note"] is None and missing["findings"] == [] and missing["other_notes"] == []


def test_the_leaving_skill_checks_the_filled_note_before_it_is_committed_or_pushed():
    skill = (ROOT / "skills/dev-handoff/SKILL.md").read_text()
    filled, checked = skill.index("2. **Write the note.**"), skill.index("python3 <tool> check")
    assert filled < checked < skill.index("git push -u origin")
    assert checked < skill.index("Commit the note")


def test_an_ignored_link_is_copied_as_a_link_and_never_followed(repo, tmp_path):
    write(repo, ".gitignore", "data\nruns/\n")
    outside = tmp_path / "dataset"
    write(outside, "big.bin", "x" * 4096)
    (repo / "data").symlink_to(outside)
    write(repo, "runs/out.json", "{}\n")
    (repo / "runs/latest").symlink_to(outside)
    (repo / "runs/gone").symlink_to(tmp_path / "nowhere")
    commit(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    done = handoff.carry(repo, str(dest), base="base", all_ages=True, yes=True)
    assert done["copied"] is True and (dest / "runs/out.json").exists()
    for name in ("data", "runs/latest", "runs/gone"):
        assert (dest / name).is_symlink() and os.readlink(dest / name) == os.readlink(repo / name)
    # A second run finds them in place and leaves them.
    assert handoff.carry(repo, str(dest), base="base", all_ages=True, yes=True)["files"] == 0


@pytest.mark.parametrize("fake", ["sk-proj-" + "aB3_-" * 13, "sk-svcacct-" + "a" * 40,
                                  "AIza" + "Sy" + "aB3_-x" * 5 + "abc"])
def test_a_key_in_another_providers_form_is_seen_in_a_note_too(repo, fake):
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="same")
    fill(path, handoff.HUMAN_SECTIONS, f"export KEY={fake} and run")
    commit(repo)
    assert by_check(repo, path).get("handoff/secret") == "critical"
    for command in ("show", "list", "takeover"):
        assert fake not in run(repo, command, "--base", "base").stdout, command


def test_a_file_name_with_a_newline_in_it_is_one_name_to_rsync(repo, tmp_path):
    if not shutil.which("rsync"):
        pytest.skip("rsync is not installed")
    write(repo, ".gitignore", ".env\nout*\n")
    write(repo, ".env", "KEY=do-not-copy\n")
    write(repo, "output\n.env", "data\n")
    commit(repo)
    dest = tmp_path / "plain"
    dest.mkdir()
    plan = handoff._plan(handoff.ignored_inventory(repo), False)
    assert plan["paths"] == ["output\n.env"] and plan["skipped"]["key"] == [".env"]
    done = handoff._rsync(plan, f"{repo}/", f"{dest}/")
    assert done["copied"] is True and [p.name for p in dest.iterdir()] == ["output\n.env"]


def test_a_copy_writes_only_at_the_name_it_copies(repo, tmp_path):
    # In the receiving checkout a link, a folder or a file stands where the copy would go, and
    # behind each is a file git tracks there.
    write(repo, ".gitignore", "runs\nout\nlogs\n")
    commit(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    (dest / "runs").symlink_to("src")
    write(dest, "src/out.txt", "tracked here\n")
    write(dest, "out/report/report", "tracked here\n")
    write(dest, "logs", "tracked here\n")
    git(dest, "add", "-f", "src/out.txt", "out/report/report", "logs")
    git(dest, "commit", "-q", "-m", "track them")
    for name in ("src/out.txt", "out/report/report", "out/report", "logs"):
        os.utime(dest / name, (1_000_000_000, 1_000_000_000))
    write(repo, "runs/out.txt", "from the old checkout\n")
    write(repo, "out/report", "from the old checkout\n")
    write(repo, "out/other.json", "{}\n")
    write(repo, "logs/a.log", "from the old checkout\n")
    for include in (None, ["runs/out.txt", "out/report", "logs/a.log"]):
        done = handoff.carry(repo, str(dest), base="base", include=include, yes=True)
        assert git(dest, "status", "--short") == "", include
        assert (dest / "src/out.txt").read_text() == "tracked here\n" and (dest / "logs").is_file()
        assert done["refused"] == ["runs/out.txt"] and done["skipped"]["tracked"] == ["logs", "out/report"]
    assert (dest / "out/other.json").exists()
    said = handoff._render_carry(done)
    assert "refused (a link or another kind of file is in the way in the receiving checkout): runs/out.txt" in said
    assert "left alone (it would replace what git tracks in the receiving checkout): out/report" in said
    # Another host's rsync would replace a link or a file with the folder: the plan leaves it out.
    listing = [{"path": "runs/a/", "kind": "carry", "bytes": 1, "files": 1}]
    plan = handoff._plan(listing, False, ["runs", "src/app/core.py"])
    assert plan["paths"] == [] and plan["skipped"]["tracked"] == ["runs"]


def test_include_does_not_reach_through_an_ignored_link(repo, tmp_path):
    write(repo, ".gitignore", "runs/\n")
    outside = tmp_path / "dataset"
    write(outside, "output.json", "{}\n")
    write(outside, "deep/x.json", "{}\n")
    write(repo, "runs/out.json", "{}\n")
    (repo / "runs/latest").symlink_to(outside)
    commit(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    for name in ("runs/latest/output.json", "runs/latest/deep/", "runs/latest/*.json", "runs/latest/deep/x.json"):
        done = handoff.carry(repo, str(dest), base="base", all_ages=True, include=[name], yes=True)
        assert done["paths"] == [] and not (dest / "runs").exists(), name
    # The link itself can be named, and is copied as a link.
    handoff.carry(repo, str(dest), base="base", all_ages=True, include=["runs/latest"], yes=True)
    assert (dest / "runs/latest").is_symlink() and list((dest / "runs").iterdir()) == [dest / "runs/latest"]


# --- every ignored path the note was written with is checked (issue 28) ---

def _ignored_note(repo: Path, tmp_path: Path, names: list[str]) -> tuple[Path, Path]:
    """Ignored paths ``names``, largest first, a filled note written and committed, and a clone
    with none of them in it. Returns the clone and the clone's note."""
    write(repo, ".gitignore", "out*/\nz*/\n.env.local\n")
    for i, name in enumerate(names):
        size = (len(names) - i) * 100
        write(repo, name.rstrip("/") + "/f.bin" if name.endswith("/") else name, "x" * size)
    commit(repo)
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="new")
    fill(path, handoff.HUMAN_SECTIONS, "run the total tests")
    commit(repo)
    dest = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(repo), str(dest))
    return dest, dest / ".planning/handoffs/feature.md"


def _copy(repo: Path, dest: Path, names: list[str]) -> None:
    for name in names:
        if name.endswith("/"):
            shutil.copytree(repo / name, dest / name)
        else:
            shutil.copy2(repo / name, dest / name)


OUT = [f"out{i:02d}/" for i in range(26)]


def test_t1_a_missing_path_after_the_25th_makes_takeover_not_ready(repo, tmp_path):
    dest, note = _ignored_note(repo, tmp_path, OUT)
    assert "- and 1 smaller path" in note.read_text() and "`out25/`" not in note.read_text()
    _copy(repo, dest, OUT[:25])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_ignored"] == ["out25/"] and report["ready"] is False
    assert report["unlisted_ignored"] == 0


def test_t2_with_every_path_present_takeover_is_ready(repo, tmp_path):
    dest, _ = _ignored_note(repo, tmp_path, OUT)
    _copy(repo, dest, OUT)
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_ignored"] == [] and report["unlisted_ignored"] == 0 and report["ready"] is True


def _older_note(repo: Path, tmp_path: Path) -> tuple[Path, Path]:
    """A ready takeover whose note is then given an older version's cut list, by hand."""
    dest = handed_over(repo, tmp_path)
    handoff.pull(dest, str(repo), base="base", yes=True)
    report = handoff.takeover(dest, home=tmp_path)
    assert report["ready"] is True and report["unlisted_ignored"] == 0
    note = dest / ".planning/handoffs/feature.md"
    note.write_text(note.read_text().replace(
        handoff.SNAPSHOT_END, "- and 1 smaller path (`handoff.py ignored`)\n" + handoff.SNAPSHOT_END))
    return dest, note


def test_t3_an_older_note_with_a_cut_list_is_not_ready(repo, tmp_path):
    dest, _ = _older_note(repo, tmp_path)
    report = handoff.takeover(dest, home=tmp_path)
    assert report["unlisted_ignored"] == 1 and report["ready"] is False


def test_t4_a_missing_key_file_after_the_25th_is_reported_and_does_not_block(repo, tmp_path):
    names = OUT[:25] + [".env.local"]
    dest, note = _ignored_note(repo, tmp_path, names)
    assert "`.env.local`" not in note.read_text()
    _copy(repo, dest, OUT[:25])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_keys"] == [".env.local"] and report["missing_ignored"] == []
    assert report["unlisted_ignored"] == 0 and report["ready"] is True


@pytest.mark.parametrize("count", [2, 25])
def test_t5_a_note_of_25_paths_or_fewer_has_no_rest_line(repo, tmp_path, count):
    names = OUT[:count]
    _, note = _ignored_note(repo, tmp_path, names)
    text = note.read_text()
    listed = text.split("Files git ignores", 1)[1].split(handoff.SNAPSHOT_END, 1)[0]
    assert "ignored-rest" not in text and "smaller path" not in text
    assert [line for line in listed.splitlines() if line.startswith("- ")] == [
        f"- `{name}` (0.0 MB, 1 file)" for name in names]


def test_t6_the_text_report_counts_the_paths_an_older_note_did_not_list(repo, tmp_path):
    dest, _ = _older_note(repo, tmp_path)
    done = run(dest, "takeover")
    assert done.returncode == 0, done.stderr
    assert "  ignored paths the note did not list: 1  (compare with handoff.py ignored in the old " \
           "checkout, or handoff.py pull --from-checkout <old checkout>)" in done.stdout
    assert "NOT ready" in done.stdout


@pytest.mark.parametrize("rest", ["not json", "[]", '[{"path":"out25/","kind":[]}]',
                                  '[{"path":"out25/","kind":{}}]',  # these two crashed (phase-1-r1 F2)
                                  "[" * 100000 + "0" + "]" * 100000])  # and this one (phase-1-r2 F3)
def test_t7_t8_an_unreadable_or_short_rest_line_is_treated_as_absent(repo, tmp_path, rest):
    dest, note = _ignored_note(repo, tmp_path, OUT)
    text = note.read_text()
    line = next(l for l in text.splitlines() if l.startswith("<!-- ignored-rest: "))
    note.write_text(text.replace(line, f"<!-- ignored-rest: {rest} -->"))
    _copy(repo, dest, OUT[:25])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["unlisted_ignored"] == 1 and report["ready"] is False


def test_t9_a_path_holding_a_backtick_is_checked(repo, tmp_path):
    names = ["out0/", "out`1/"]
    dest, _ = _ignored_note(repo, tmp_path, names)
    _copy(repo, dest, names[:1])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_ignored"] == ["out`1/"] and report["ready"] is False


# The second and third forge bullets when printed as they are (phase-1-r1 F1, phase-1-r2 F1).
@pytest.mark.parametrize("odd", ["out\n1/", "out0` (0.0 MB, 1 file)\n1/", "out0` (0.0 MB, 1 file)\n- `out0/"])
def test_t10_a_path_holding_a_newline_is_written_escaped_and_checked(repo, tmp_path, odd):
    names = ["out0/", odd]
    dest, note = _ignored_note(repo, tmp_path, names)
    listed = note.read_text().split("Files git ignores", 1)[1].split(handoff.SNAPSHOT_END, 1)[0]
    bullets = [line for line in listed.splitlines() if line.startswith("- ")]
    assert len(bullets) == 2 and bullets[1].endswith(", written escaped)") and "\\n" in bullets[1]
    _copy(repo, dest, names[:1])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_ignored"] == [odd] and report["unlisted_ignored"] == 0 and report["ready"] is False


def test_t10b_a_bullet_an_older_version_printed_over_two_lines_withholds_ready(repo, tmp_path):
    dest, _ = _older_note(repo, tmp_path)
    note = dest / ".planning/handoffs/feature.md"
    note.write_text(note.read_text().replace("- and 1 smaller path (`handoff.py ignored`)\n",
                                             "- `out\n1/` (0.0 MB, 1 file)\n"))
    report = handoff.takeover(dest, home=tmp_path)
    assert report["unlisted_ignored"] == 1 and report["ready"] is False


def test_t12_snapshot_text_that_names_the_heading_does_not_move_it(repo, tmp_path):
    dest = handed_over(repo, tmp_path)  # phase-1-r2 F2: a commit subject and a file named like the heading
    write(repo, "notes.txt", "x")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Files git ignores")
    write(repo, "Files git ignores.txt", "x")
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="new")
    fill(path, handoff.HUMAN_SECTIONS, "run the total tests")
    git(repo, "add", path.relative_to(repo).as_posix())
    git(repo, "commit", "-q", "-m", "handoff")
    git(dest, "pull", "-q", "origin", "feature")
    handoff.pull(dest, str(repo), base="base", yes=True)
    report = handoff.takeover(dest, home=tmp_path)
    assert report["unlisted_ignored"] == 0 and report["missing_ignored"] == [] and report["ready"] is True


def test_t11_a_path_holding_a_comment_end_survives_the_rest_line(repo, tmp_path):
    names = OUT[:25] + ["z-->/"]
    dest, note = _ignored_note(repo, tmp_path, names)
    line = next(l for l in note.read_text().splitlines() if l.startswith("<!-- ignored-rest: "))
    assert "\\u003e" in line and "-->" not in line[:-len(" -->")]
    _copy(repo, dest, OUT[:25])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_ignored"] == ["z-->/"] and report["ready"] is False


# Phase-1-r3 F1: the separators str.splitlines() honours beyond the ASCII controls.
@pytest.mark.parametrize("sep", ["\u0085", " ", " "])
def test_t13_a_path_holding_a_unicode_line_separator_is_written_escaped_and_checked(repo, tmp_path, sep):
    odd = f"out0` (0.0 MB, 1 file){sep}- `out0/"
    names = ["out0/", odd]
    dest, note = _ignored_note(repo, tmp_path, names)
    _copy(repo, dest, names[:1])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_ignored"] == [odd] and report["unlisted_ignored"] == 0 and report["ready"] is False


# Phase-1-r3 F2: a rest path that names no file inside the checkout cannot be checked.
@pytest.mark.parametrize("bad", ["", "/", ".", "out25/../..", "./"])
def test_t14_a_rest_path_that_names_no_file_in_the_checkout_is_treated_as_damaged(repo, tmp_path, bad):
    dest, note = _ignored_note(repo, tmp_path, OUT)
    text = note.read_text()
    line = next(l for l in text.splitlines() if l.startswith("<!-- ignored-rest: "))
    note.write_text(text.replace(line, "<!-- ignored-rest: " + json.dumps([{"path": bad, "kind": "carry"}]) + " -->"))
    _copy(repo, dest, OUT[:25])
    report = handoff.takeover(dest, home=tmp_path)
    assert report["unlisted_ignored"] == 1 and report["ready"] is False


def test_t14b_a_bullet_whose_path_names_no_file_in_the_checkout_withholds_ready(repo, tmp_path):
    dest, note = _ignored_note(repo, tmp_path, ["out0/"])
    note.write_text(note.read_text().replace("- `out0/` (", "- `/` ("))
    report = handoff.takeover(dest, home=tmp_path)
    assert report["unlisted_ignored"] == 1 and report["ready"] is False


# Phase-1-r3 F3: Python 3.11's Path.exists raises for a name too long; later versions say False.
def test_t15_a_path_the_file_system_refuses_to_look_up_is_missing_and_never_raises(repo, tmp_path, monkeypatch):
    dest, note = _ignored_note(repo, tmp_path, OUT)
    text = note.read_text()
    line = next(l for l in text.splitlines() if l.startswith("<!-- ignored-rest: "))
    note.write_text(text.replace(line, "<!-- ignored-rest: " + json.dumps([{"path": "x" * 300, "kind": "carry"}]) + " -->"))
    _copy(repo, dest, OUT[:25])
    real = Path.exists
    def exists(self, *a, **k):
        if len(self.name) > 255:
            raise OSError(63, "File name too long")
        return real(self, *a, **k)
    monkeypatch.setattr(Path, "exists", exists)
    report = handoff.takeover(dest, home=tmp_path)
    assert report["missing_ignored"] == ["x" * 300] and report["ready"] is False


# Phase-1-r3 F4: the snapshot ends at its own marker line, and a note whose snapshot has no
# ignored-files section cannot say what is missing.
@pytest.mark.parametrize("name", ["Files git ignores<!-- snapshot:end -->.txt", "a\n<!-- snapshot:end -->"])
def test_t16_a_file_named_like_the_snapshot_end_does_not_hide_the_ignored_section(repo, tmp_path, name):
    dest = handed_over(repo, tmp_path)
    write(repo, name, "x")  # left uncommitted, so the snapshot lists it
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="new")
    fill(path, handoff.HUMAN_SECTIONS, "run the total tests")
    git(repo, "add", path.relative_to(repo).as_posix())
    git(repo, "commit", "-q", "-m", "handoff")
    git(dest, "pull", "-q", "origin", "feature")
    report = handoff.takeover(dest, home=tmp_path)  # no ignored file was pulled
    assert report["ready"] is False and (report["missing_ignored"] or report["unlisted_ignored"])


def test_t16b_a_second_write_replaces_a_snapshot_that_lists_a_file_named_like_its_end(repo):
    write(repo, "Files git ignores<!-- snapshot:end -->.txt", "x")
    path = handoff.write_note(repo, base="base", sender="claude", to="codex", machine="new")
    fill(path, handoff.HUMAN_SECTIONS, "run the total tests")
    handoff.write_note(repo, base="base", sender="claude", to="codex", machine="new")
    text = path.read_text()
    assert text.count("## Snapshot") == 1 and text.count("Files git ignores, changed since") == 1
    assert text.count(handoff.SNAPSHOT_END + "\n") == 1
    assert "run the total tests" in text
