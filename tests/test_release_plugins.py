"""Tests for devtools/release_plugins.py. Each test runs the script in a copy of this
repository with its own git history, so no tag or push reaches the real one."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COPIED = ["devtools", "skills", "agents", "plugins", ".claude-plugin"]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    for name in COPIED:
        shutil.copytree(ROOT / name, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__"))
    # Start every test from 0.1.0 with no release, whatever version this repository is at.
    (tmp_path / "devtools/PLUGIN_VERSION").write_text("0.1.0\n")
    subprocess.run([sys.executable, str(tmp_path / "devtools/build_plugins.py")], cwd=tmp_path, check=True,
                   capture_output=True)
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.com", "add", "-A")
    git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "start")
    return tmp_path


def release(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(repo / "devtools/release_plugins.py"), *args],
                          cwd=repo, capture_output=True, text=True)


def commit(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", message)


def change_a_skill(repo: Path) -> None:
    skill = repo / "skills/milestone/review-pr/SKILL.md"
    skill.write_text(skill.read_text() + "\nOne more line.\n")
    subprocess.run([sys.executable, str(repo / "devtools/build_plugins.py")], cwd=repo, check=True,
                   capture_output=True)


def test_the_first_release_tags_the_version_in_the_tree(repo):
    assert release(repo, "status").returncode == 1
    preview = release(repo, "tag", "--dry-run")
    # The history before the first release predates the plugins: the notes do not list it.
    assert preview.stdout.rstrip().endswith("- First release.") and "start" not in preview.stdout.split("\n\n", 2)[-1]
    done = release(repo, "tag")
    assert done.returncode == 0, done.stderr
    version = (repo / "devtools/PLUGIN_VERSION").read_text().strip()
    assert git(repo, "tag", "--list") == f"plugins-v{version}"
    assert "not pushed" in done.stdout
    assert release(repo, "status").returncode == 0


def test_a_change_needs_a_bump_before_it_can_be_tagged(repo):
    release(repo, "tag")
    change_a_skill(repo)
    commit(repo, "Change review-pr")
    status = release(repo, "status")
    assert status.returncode == 1 and "run `release_plugins.py bump`" in status.stdout
    assert "exists" in release(repo, "tag").stderr
    assert release(repo, "bump").returncode == 0
    assert (repo / "devtools/PLUGIN_VERSION").read_text().strip() == "0.1.1"
    assert '"version": "0.1.1"' in (repo / "plugins/dvt-phase/.claude-plugin/plugin.json").read_text()
    commit(repo, "Release 0.1.1")
    done = release(repo, "tag", "--dry-run")
    assert done.returncode == 0 and "would tag plugins-v0.1.1" in done.stdout and "Change review-pr" in done.stdout
    assert "plugins-v0.1.1" not in git(repo, "tag", "--list")
    assert release(repo, "tag").returncode == 0
    assert "plugins-v0.1.1" in git(repo, "tag", "--list")


def test_bump_takes_a_part_or_a_higher_version(repo):
    assert release(repo, "bump", "minor").returncode == 0
    assert (repo / "devtools/PLUGIN_VERSION").read_text().strip() == "0.2.0"
    assert release(repo, "bump", "0.1.5").returncode == 2
    assert release(repo, "bump", "1.0.0").returncode == 0
    assert release(repo, "bump", "major").returncode == 0
    assert (repo / "devtools/PLUGIN_VERSION").read_text().strip() == "2.0.0"


def test_tag_refuses_a_dirty_tree_a_stale_build_or_another_branch(repo):
    skill = repo / "skills/milestone/review-pr/SKILL.md"
    skill.write_text(skill.read_text() + "\nchanged\n")
    assert "working tree has changes" in release(repo, "tag").stderr
    commit(repo, "Change without a rebuild")
    assert "stale" in release(repo, "tag").stderr
    git(repo, "checkout", "-q", "-b", "feature")
    assert "tag releases from main" in release(repo, "tag").stderr


def test_nothing_to_release_without_a_plugin_change(repo):
    release(repo, "tag")
    (repo / "devtools/PLUGIN_VERSION").write_text("0.2.0\n")
    subprocess.run([sys.executable, str(repo / "devtools/build_plugins.py")], cwd=repo, check=True,
                   capture_output=True)
    commit(repo, "Bump only")
    # The manifests carry the version, but a bump with nothing else in it is no release.
    done = release(repo, "tag", "--dry-run")
    assert done.returncode == 2 and "nothing to release" in done.stderr
    assert release(repo, "status").returncode == 0
    change_a_skill(repo)
    commit(repo, "Change review-pr")
    assert release(repo, "tag", "--dry-run").returncode == 0
