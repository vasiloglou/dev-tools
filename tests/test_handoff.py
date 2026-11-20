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
    assert "level: 2" in text and "`AGENTS.md`, `CLAUDE.md`" in text and ".claude/skills/" in text
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
    assert "sections still empty" in done.stdout
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


def test_a_listing_from_another_host_is_held_to_this_checkouts_rules():
    sent = [{"path": "runs/", "kind": "carry", "bytes": 10, "files": 2},
            {"path": "../outside", "kind": "carry", "bytes": 1, "files": 1},
            {"path": "/etc/passwd", "kind": "carry", "bytes": 1, "files": 1},
            {"path": "--delete", "kind": "carry", "bytes": 1, "files": 1},
            {"path": "conf/.env", "kind": "carry", "bytes": 1, "files": 1},
            {"path": ".venv/", "kind": "carry", "bytes": 1, "files": 1},
            {"path": "x", "kind": "anything", "bytes": 1, "files": 1}, "not an entry"]
    kept = {e["path"]: e["kind"] for e in handoff._recheck(sent)}
    assert kept == {"runs/": "carry", "conf/.env": "key", ".venv/": "rebuild"}
    assert handoff._recheck({"not": "a list"}) == []


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
    assert ssh[:4] == ["ssh", "-o", "BatchMode=yes", "oldbox"]
    assert ssh[4] == "python3 - --repo ~/work/repo --base base --max-mb 200 ignored --json"
    assert program == SCRIPT.read_text()
    done = handoff.pull(dest, "oldbox:~/work/repo", base="base", yes=True)
    rsync, files = calls[-1]
    assert rsync[0] == "rsync" and rsync[-2:] == ["oldbox:~/work/repo/", f"{dest}/"] and files == "runs/\n"
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
