"""devtools/ci_local.sh runs the jobs of .github/workflows/gates.yml on this machine. These
tests keep the two in step: the same gate commands, the same GND, the same jobs."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/gates.yml").read_text()
SCRIPT = (ROOT / "devtools/ci_local.sh").read_text()


def workflow_gates() -> list[str]:
    """The workflow's gate commands, written as the script writes them."""
    runs = re.findall(r"^\s+run: (.+)$", WORKFLOW, re.MULTILINE)
    gates = [run for run in runs if run.startswith(("python3 ", "uv run "))]
    return [gate.replace('"${{ matrix.python }}"', '"$PY"').replace("origin/${{ github.base_ref }}", "origin/main")
            for gate in gates]


def test_the_script_runs_every_gate_of_the_workflow():
    gates = workflow_gates()
    assert len(gates) == 4, gates
    body = SCRIPT.split("GATES='", 1)[1].split("'", 1)[0]
    for gate in gates:
        # The script adds `-p no:cacheprovider` so a run leaves no .pytest_cache in the clone.
        assert gate in body or gate + " -p no:cacheprovider" in body, gate


def test_the_script_installs_the_gnd_the_workflow_installs():
    pinned = re.search(r'"(get-nick-done\[synth\]==[0-9.]+)"', WORKFLOW).group(1)
    assert f"GND_PIN='{pinned}'" in SCRIPT


def test_the_script_has_a_job_for_each_job_of_the_matrix():
    matrix = re.findall(r"- os: (\S+)\n\s+python: \"([0-9.]+)\"", WORKFLOW)
    names = {f"{'macos' if os.startswith('macos') else 'linux'}-{python}" for os, python in matrix}
    assert names == {"macos-3.14", "linux-3.11", "linux-3.14"}
    for name in names:
        assert name in SCRIPT, name


@pytest.mark.skipif(not shutil.which("bash"), reason="needs bash")
def test_the_script_parses():
    done = subprocess.run(["bash", "-n", str(ROOT / "devtools/ci_local.sh")], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
