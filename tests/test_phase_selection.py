"""Tests for the pytest plugin that selects acceptance tests by phase
(skills/phase/pytest/phase_selection.py). Each test makes a small project with the plugin as its
conftest.py, runs pytest there as a project would, and checks which tests were kept.

tests/test_tools.py has one more test of the plugin, as the sync delivers it
(test_plain_pytest_leaves_out_phases_that_are_not_complete); this file holds its other branches.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# PHASE_SELECTION_PLUGIN names another copy of the plugin. It is for one check only: showing that these
# tests fail on a copy with a line broken.
PLUGIN = Path(os.environ.get("PHASE_SELECTION_PLUGIN") or ROOT / "skills/phase/pytest/phase_selection.py")
TESTS = {"tests/acceptance/p01_done/test_done.py": "test_done",
         "tests/acceptance/p02_open/test_open.py": "test_open",
         "tests/acceptance/p06_1_inserted/test_inserted.py": "test_inserted",
         "tests/unit/test_unit.py": "test_unit"}


class Project:
    """A project with a complete phase 1, an open phase 2, an inserted phase 6.1 that is open, and a unit test."""

    def __init__(self, root: Path):
        self.root = root
        self.write("conftest.py", PLUGIN.read_text())
        for path, name in TESTS.items():
            self.write(path, "def %s():\n    assert True\n" % name)
        self.complete("1")

    def write(self, path: str, text: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def complete(self, phases: str, planning: str = ".planning") -> None:
        self.write(planning + "/STATE.md", "current_phase: 2\ncompleted_phases: %s\n" % phases)

    def pytest(self, *args: str) -> subprocess.CompletedProcess:
        env = {key: value for key, value in os.environ.items() if key != "PYTEST_ADDOPTS"}
        return subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
                              cwd=self.root, capture_output=True, text=True, env=env)

    def kept(self, *args: str) -> set:
        """The names of the tests pytest would run: with --collect-only it lists a test only when the plugin kept it."""
        done = self.pytest("--collect-only", "-q", *args)
        assert done.returncode in (0, 5), done.stdout + done.stderr  # 5: nothing was collected
        return {line.rsplit("::", 1)[1] for line in done.stdout.splitlines() if "::" in line}


@pytest.fixture
def selection(tmp_path):
    return Project(tmp_path / "widget")


def test_plain_pytest_leaves_out_the_phases_that_are_not_complete(selection):
    assert selection.kept() == {"test_done", "test_unit"}


@pytest.mark.parametrize("phase, expected", [("02", {"test_open"}), ("2", {"test_open"}), ("01", {"test_done"})])
def test_phase_option_runs_that_phase_only(selection, phase, expected):
    assert selection.kept("--phase", phase) == expected, "complete or not, and nothing outside the acceptance folder"


def test_an_inserted_phase(selection):
    assert selection.kept("--phase", "6.1") == {"test_inserted"}
    selection.complete("01, 6.1")
    assert selection.kept() == {"test_done", "test_inserted", "test_unit"}


@pytest.mark.parametrize("args", [
    ("tests/acceptance/p02_open/test_open.py",),
    ("tests/acceptance/p02_open",),
    ("tests/acceptance/p02_open/test_open.py::test_open",),
    ("tests/acceptance/p02_open/test_open.py", "--phase", "01"),
])
def test_a_named_acceptance_path_always_runs(selection, args):
    assert selection.kept(*args) == {"test_open"}, "its phase is not complete, and --phase names another"


def test_naming_the_acceptance_folder_itself_keeps_the_selection(selection):
    assert selection.kept("tests/acceptance") == {"test_done"}


@pytest.mark.parametrize("state", [None, "current_phase: 2\n"])
def test_no_state_means_no_phase_is_complete(selection, state):
    path = selection.root / ".planning/STATE.md"
    path.unlink() if state is None else path.write_text(state)
    assert selection.kept() == {"test_unit"}


def test_the_two_folders_can_be_configured(selection):
    (selection.root / "pytest.ini").write_text("[pytest]\nphase_planning_dir = plan\nphase_acceptance_dir = checks\n")
    (selection.root / "tests/acceptance").rename(selection.root / "checks")
    (selection.root / ".planning/STATE.md").unlink()
    selection.complete("1", planning="plan")
    assert selection.kept() == {"test_done", "test_unit"}
    assert selection.kept("--phase", "2") == {"test_open"}


def test_the_plugin_beside_a_conftest_that_names_it(selection):
    (selection.root / "conftest.py").rename(selection.root / "phase_selection.py")
    (selection.root / "conftest.py").write_text('pytest_plugins = ["phase_selection"]\n')
    assert selection.kept() == {"test_done", "test_unit"}
    assert selection.kept("--phase", "2") == {"test_open"}


def test_a_real_run_counts_what_it_left_out(selection):
    done = selection.pytest("-q")
    assert done.returncode == 0, done.stdout + done.stderr
    assert re.search(r"^2 passed, 2 deselected in ", done.stdout, re.M), done.stdout
    selection.complete("1, 2, 6.1")
    done = selection.pytest("-q")
    assert done.returncode == 0, done.stdout + done.stderr
    assert re.search(r"^4 passed in ", done.stdout, re.M) and "deselected" not in done.stdout, done.stdout
