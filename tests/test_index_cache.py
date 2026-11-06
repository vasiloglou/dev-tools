"""Tests for what the component index keeps between runs. Every command must answer the same with it,
without it, and after a file changed in a way that only its content shows."""
import os
import shutil

from test_tools import INDEX, catalog, commit, entry, project, tool  # noqa: F401  (project is a fixture)

COMMANDS = (["--check"], ["review"], ["changed", "--base", "main"], ["show", "core.report"], ["draft"],
            ["search", "walk", "folder"], ["stats"])


def kept(project):
    return list((project.parent / "cache/components-index").glob("*.json"))


def widget(project):
    """Three modules, one importing another, and a test file; indexed and committed."""
    src = project / "src/widget"
    (src / "scan.py").write_text('"""Walk a folder."""\ndef walk_folder(path):\n    """List files."""\n')
    (src / "sort.py").write_text('"""Sort rows."""\ndef by_size(rows):\n    """Largest first."""\n')
    # A docstring of nothing but spaces: the summary of `report` is "(no docstring)".
    (src / "report.py").write_text('"""Print a report."""\nfrom widget import scan\n\n\ndef report(path):\n    """\n    """\n')
    (project / "tests").mkdir(exist_ok=True)
    (project / "tests/test_scan.py").write_text('from widget.scan import walk_folder\n\n\ndef helper():\n    """\n    """\n')
    catalog(project, entry("core.scan", "Walk a folder and list its files.", "src/widget/scan.py"),
            entry("core.sort", "Sort rows by size.", "src/widget/sort.py"),
            entry("core.report", "Print a report.", "src/widget/report.py"))
    commit(project)


def test_every_command_answers_the_same_with_and_without_what_earlier_runs_kept(project):
    widget(project)
    # A changed file, a new one and a deleted one, so `changed` reads files as they were at the base.
    (project / "src/widget/report.py").write_text('"""Print a report."""\nfrom widget import scan, sort\n')
    (project / "src/widget/new.py").write_text('"""New."""\n')
    (project / "src/widget/sort.py").unlink()
    shutil.rmtree(project.parent / "cache")
    fresh = [tool(project, "--no-cache", *command, script=INDEX) for command in COMMANDS]
    assert not kept(project), "--no-cache saves nothing"
    first = [tool(project, *command, script=INDEX) for command in COMMANDS]
    assert kept(project), "a run saves what it parsed"
    again = [tool(project, *command, script=INDEX) for command in COMMANDS]
    assert fresh == first == again
    by_command = dict(zip((command[0] for command in COMMANDS), again))
    assert by_command["review"][0] == 0 and "review: " in by_command["review"][1]
    assert "file(s) differ" in by_command["changed"][1] and "no component: src/widget/new.py" in by_command["changed"][1]
    assert "src/widget/scan.py (core.scan)\n  imported by: (nothing in the package)" in by_command["show"][1]
    # A file saved by another version of the script, or a damaged one, only costs time.
    for text in ('{"stamp": [4], "written": 0, "modules": {}}', "[]"):
        for saved in kept(project):
            saved.write_text(text)
        assert tool(project, "review", script=INDEX) == by_command["review"]


def test_a_file_changed_without_a_new_size_or_time_is_still_read_again(project):
    widget(project)
    assert tool(project, "--check", script=INDEX)[0] == 0 and kept(project)
    path = project / "src/widget/report.py"
    before, text = path.stat(), path.read_text()
    path.write_text(text.replace("import scan", "import sort"))
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    after = path.stat()
    assert (after.st_size, after.st_mtime_ns) == (before.st_size, before.st_mtime_ns)
    code, out = tool(project, "--check", script=INDEX)
    assert code == 1 and "stale or missing: docs/components/graph.md" in out, out
    assert tool(project, "write", script=INDEX)[0] == 0
    catalog_text = (project / "docs/components/COMPONENTS.md").read_text()
    assert "- uses: core.sort" in catalog_text and "- uses: core.scan" not in catalog_text
