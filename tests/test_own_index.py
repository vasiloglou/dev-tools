"""Tests that dev-tools' own component index (.devtools/components/) is current.

The check is the plugin's copy of components_index.py, run from the repository root as a
plugin install runs it, so it reads .devtools/components_index.settings.json. The first
test judges this checkout. The others copy the checkout, put the index out of date in one
way each, and show that the same judgment names what is wrong."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "plugins/dvt-milestone/skills/components/scripts/components_index.py"
INDEX = ".devtools/components"
BASELINE = INDEX + "/unassigned-baseline.txt"
# What the check reads: the index and its settings, the modules it counts, the test files
# the entries name, and the plugin that holds the script.
COPIED = (".devtools", "devtools", "skills", "tests", "plugins/dvt-milestone")
HOW_TO_FIX = (
    "dev-tools' component index is out of date. For a `no component:` line, first add the "
    f"module to an entry of {INDEX}/COMPONENTS.md. Then run `python3 devtools/build_plugins.py` "
    f"and `python3 {SCRIPT} write`, and commit {INDEX}/ with the change."
)


def index(root: Path, *args: str) -> subprocess.CompletedProcess:
    """Run the plugin's copy of the script in the checkout at `root`. --no-cache: the test
    reads and writes nothing outside that checkout."""
    return subprocess.run([sys.executable, str(root / SCRIPT), "--no-cache", *args],
                          cwd=root, capture_output=True, text=True)


def problems(root: Path) -> list[str]:
    """What is wrong with the index of the checkout at `root`; empty when it is current."""
    run = index(root, "--check", "--strict")
    found = []
    if run.returncode:
        found.append(f"components_index.py --check --strict exited {run.returncode}")
        found.extend(line for line in (run.stdout + run.stderr).splitlines() if line.strip())
    return found


def copy_of_the_checkout(folder: Path) -> Path:
    """A copy of what the check reads, as a checkout of its own."""
    root = folder / "checkout"
    for part in COPIED:
        shutil.copytree(ROOT / part, root / part, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    (root / ".git").mkdir()  # all the script looks for to find the project; no git command runs
    return root


@pytest.fixture
def checkout(tmp_path) -> Path:
    return copy_of_the_checkout(tmp_path)


def add_module(root: Path) -> str:
    path = "skills/example/scripts/example.py"
    (root / path).parent.mkdir(parents=True)
    (root / path).write_text('"""An example tool."""\n', encoding="utf-8")
    return path


def test_the_index_is_current():
    found = problems(ROOT)
    assert found == [], HOW_TO_FIX + "\n" + "\n".join(found)


def test_a_copy_of_the_checkout_is_current(checkout):
    assert problems(checkout) == []


def test_the_copy_and_the_check_run_without_git(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))  # no git on it: a user's git settings cannot reach these tests
    assert problems(copy_of_the_checkout(tmp_path)) == []


def test_a_module_no_entry_lists_is_named(checkout):
    catalog = checkout / INDEX / "COMPONENTS.md"
    text = catalog.read_text(encoding="utf-8")
    line = re.search(r"^- modules: (\S+\.py)$", text, re.MULTILINE)
    assert line, "no entry lists exactly one module"
    catalog.write_text(text.replace(line.group(0), "- modules:", 1), encoding="utf-8")
    assert [p for p in problems(checkout) if p.startswith(f"no component: {line.group(1)} ")]


def test_a_baseline_is_refused(checkout):
    # allow_baseline is false here: every module has a component, and the strict check keeps it so.
    path = add_module(checkout)
    assert index(checkout, "write").returncode == 0
    (checkout / BASELINE).write_text(path + "\n", encoding="utf-8")
    assert problems(checkout) == [
        "components_index.py --check --strict exited 1",
        f"baseline refused: {BASELINE} exists and allow_baseline is false (give its modules a component, then delete the file)",
        f"no component: {path} (add it to the modules of an entry in {INDEX}/COMPONENTS.md)"]


def test_no_baseline_can_be_written_here(checkout):
    add_module(checkout)
    assert index(checkout, "write").returncode == 0
    run = index(checkout, "stats", "--write-baseline")
    assert run.returncode == 1 and "allow_baseline is false" in run.stderr, run.stderr
    assert not (checkout / BASELINE).exists()


def test_a_new_module_is_named(checkout):
    path = add_module(checkout)
    assert [p for p in problems(checkout) if p.startswith(f"no component: {path} ")]


def test_a_changed_module_leaves_a_page_stale(checkout):
    module = checkout / "devtools/sync.py"
    module.write_text(module.read_text(encoding="utf-8") + "\n\ndef added_for_this_test():\n    return 1\n",
                      encoding="utf-8")
    assert [p for p in problems(checkout) if p.startswith(f"stale or missing: {INDEX}/modules/")]


def test_the_check_reads_this_projects_settings(checkout):
    (checkout / ".devtools/components_index.settings.json").unlink()
    found = problems(checkout)
    assert found[0] == "components_index.py --check --strict exited 1"
    assert [p for p in found if "COMPONENTS.md is missing" in p]
