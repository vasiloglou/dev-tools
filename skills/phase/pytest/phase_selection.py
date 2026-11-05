"""Select acceptance tests by roadmap phase (pytest plugin for the process-phase skill).

    pytest               everything except the acceptance tests of phases that are not complete
    pytest --phase 03    only the acceptance tests of phase 03 (tests/acceptance/p03_*/)
    pytest --phase 6.1   an inserted phase (tests/acceptance/p06_1_*/)
    pytest tests/acceptance/p03_x/test_y.py   a path inside the acceptance directory given
                         on the command line always runs, whatever the phase's status

Use it as the project's root ``conftest.py``, or keep it beside one that contains
``pytest_plugins = ["phase_selection"]``. The two paths can be changed in the pytest
configuration: ``phase_planning_dir`` (default ``.planning``) and ``phase_acceptance_dir``
(default ``tests/acceptance``).
"""
import re
from pathlib import Path


def pytest_addoption(parser):
    parser.addoption("--phase", default=None, help="run only the acceptance tests of phase NN")
    parser.addini("phase_planning_dir", "planning directory, relative to the root", default=".planning")
    parser.addini("phase_acceptance_dir", "acceptance tests directory, relative to the root",
                  default="tests/acceptance")


def phase_id(value: str) -> str:
    """'3' -> '03', '6.1' -> '06.1'."""
    whole, _, part = str(value).strip().partition(".")
    return "%02d" % int(whole) + ("." + part if part else "")


def completed_phases(planning: Path) -> set:
    state = planning / "STATE.md"
    text = state.read_text(encoding="utf-8") if state.is_file() else ""
    line = re.search(r"^completed_phases:(.*)$", text, re.M)
    return {phase_id(p) for p in re.findall(r"\d+(?:\.\d+)?", line.group(1))} if line else set()


def pytest_collection_modifyitems(config, items):
    root = Path(str(config.rootdir))
    acceptance = (root / config.getini("phase_acceptance_dir")).resolve().as_posix().rstrip("/")
    package = re.compile(re.escape(acceptance) + r"/p(\d{2})(?:_(\d+))?_")
    wanted = phase_id(config.getoption("--phase")) if config.getoption("--phase") else None
    done = completed_phases(root / config.getini("phase_planning_dir"))
    named = [Path(str(config.invocation_params.dir), arg.split("::")[0]).resolve().as_posix()
             for arg in config.args]
    named = [path for path in named if path.startswith(acceptance + "/")]
    keep, drop = [], []
    for item in items:
        path = Path(str(item.fspath)).as_posix()
        match = package.match(path)
        phase = match.group(1) + ("." + match.group(2) if match.group(2) else "") if match else None
        if any(path == given or path.startswith(given + "/") for given in named):
            selected = True
        else:
            selected = phase == wanted if wanted else (phase is None or phase in done)
        (keep if selected else drop).append(item)
    if drop:
        config.hook.pytest_deselected(items=drop)
        items[:] = keep
