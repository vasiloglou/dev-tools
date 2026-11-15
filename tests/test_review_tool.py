"""Tests for review_tool.py, the milestone workflow's review helper. Each test works in a new
project made by the sync from examples/milestone-project.devtools.toml, with fake codex,
claude and gh on PATH."""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync", ROOT / "devtools/sync.py")
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)
SCRIPT = ".claude/skills/process-phase/scripts/review_tool.py"

FAKE_CODEX = r'''#!/usr/bin/env python3
import json, os, sys, time
args = sys.argv[1:]
if args[:2] == ["login", "status"]:
    sys.exit(int(os.environ.get("FAKE_LOGIN", "0")))
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(json.dumps({"tool": "codex", "argv": args, "stdin": sys.stdin.read(), "cwd": os.getcwd()}) + "\n")
time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
print("codex log line")
if os.environ.get("FAKE_REVIEW", "x"):
    with open(args[args.index("-o") + 1], "w") as out:
        out.write(os.environ.get("FAKE_REVIEW", "F1. src/app.py:1 returns the wrong total.\nVERDICT: CHANGES_REQUESTED\n"))
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
'''
FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(json.dumps({"tool": "claude", "argv": sys.argv[1:], "stdin": sys.stdin.read()}) + "\n")
print("No defects found.\nVERDICT: APPROVE")
'''
FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
with open(os.environ["FAKE_LOG"], "a") as log:
    body = open(args[args.index("--body-file") + 1]).read() if "--body-file" in args else None
    log.write(json.dumps({"tool": "gh", "argv": args, "body": body}) + "\n")
if args[:2] == ["pr", "view"]:
    print(json.dumps({"number": 7, "url": "https://github.com/o/r/pull/7", "title": "Add totals",
                      "headRefOid": os.environ.get("FAKE_HEAD", "a" * 40), "baseRefOid": "b" * 40}))
elif args[:2] == ["pr", "diff"]:
    print("diff --git a/.env b/.env\n+TOKEN=hunter2\ndiff --git a/src/app.py b/src/app.py\n+def total(): return 2")
elif args[:2] == ["pr", "comment"]:
    print("https://github.com/o/r/pull/7#issuecomment-1")
'''


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "widget"
    (root / "src").mkdir(parents=True)
    (root / "src/app.py").write_text("def total():\n    return 1\n")
    (root / ".env").write_text("TOKEN=hunter2\n")
    (root / ".gitignore").write_text(".env\n")
    (root / "notes").mkdir()
    (root / "notes/plan.md").write_text("# Plan\n\nPhase 1 adds totals.\n")
    (root / ".devtools.toml").write_text((ROOT / "examples/milestone-project.devtools.toml").read_text())
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    assert sync.main(["apply", "--project", str(root)]) == 0
    commit(root, "start")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, text in (("codex", FAKE_CODEX), ("claude", FAKE_CLAUDE), ("gh", FAKE_GH)):
        (bin_dir / name).write_text(text)
        (bin_dir / name).chmod(0o755)
    return root


def commit(root, message):
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message],
                   check=True)
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def env_for(root, harness="claude", **extra):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE" and not k.startswith("CODEX_")}
    env["PATH"] = "%s%s%s" % (root.parent / "bin", os.pathsep, env["PATH"])
    env["FAKE_LOG"] = str(root.parent / "calls.jsonl")
    if harness == "claude":
        env["CLAUDECODE"] = "1"
    elif harness == "codex":
        env["CODEX_SANDBOX"] = "seatbelt"
    env.update(extra)
    return env


def review(root, *args, harness="claude", typed="", **extra):
    """Run the tool; ``typed`` is what its own stdin carries, which a reviewer must never read."""
    proc = subprocess.run([sys.executable, SCRIPT, *args], cwd=root, capture_output=True, text=True,
                          env=env_for(root, harness, **extra), input=typed)
    return proc.returncode, proc.stdout + proc.stderr


def calls(root):
    path = root.parent / "calls.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []


def plan_brief(root, name="reviews/plan-r1"):
    return review(root, "brief", name, "--subject", "plan", "--question",
                  "Can every phase of this plan be implemented and tested as written?",
                  "--file", "notes/plan.md", "--claim", "Phase 1 needs no new dependency.")


def sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fill(root, round_dir, *rows):
    ledger = root / round_dir / "FINDINGS.md"
    ledger.write_text(ledger.read_text() + "".join("| " + " | ".join(row) + " |\n" for row in rows))


def test_the_brief_lists_each_file_with_its_digest_and_forbids_credentials(project):
    code, out = plan_brief(project)
    assert code == 0, out
    brief = (project / "reviews/plan-r1/BRIEF.md").read_text()
    assert "Can every phase of this plan be implemented and tested as written?" in brief
    assert "| `notes/plan.md` | `%s` |" % sha(project / "notes/plan.md") in brief
    assert "- C1. Phase 1 needs no new dependency." in brief
    assert "Do not open `.env` files" in brief
    assert "VERDICT: APPROVE" in brief
    data = json.loads((project / "reviews/plan-r1/brief.json").read_text())
    assert data["files"] == [{"path": "notes/plan.md", "sha256": sha(project / "notes/plan.md")}]
    assert "| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |" in (
        project / "reviews/plan-r1/FINDINGS.md").read_text()


def test_a_named_credential_file_is_refused_and_a_round_is_never_rewritten(project):
    code, out = review(project, "brief", "reviews/x", "--subject", "plan", "--question", "q", "--file", ".env")
    assert code == 2 and "looks like a credential file" in out
    assert not (project / "reviews/x").exists()
    assert plan_brief(project)[0] == 0
    code, out = plan_brief(project)
    assert code == 2 and "never rewritten" in out


def test_a_phase_brief_carries_the_diff_and_new_files_but_no_credential(project):
    base = subprocess.run(["git", "-C", str(project), "rev-parse", "HEAD"], capture_output=True,
                          text=True).stdout.strip()
    (project / "src/app.py").write_text("def total():\n    return 2\n")
    (project / "src/new.py").write_text("X = 1\n")
    (project / "config").mkdir()
    (project / "config/secrets.json").write_text('{"key": "hunter2"}\n')
    code, out = review(project, "brief", "reviews/p1-r1", "--subject", "phase", "--base", base,
                       "--question", "Does phase 1 meet its criteria?")
    assert code == 0, out
    assert "left out: config/secrets.json" in out
    data = json.loads((project / "reviews/p1-r1/brief.json").read_text())
    assert [f["path"] for f in data["files"]] == ["reviews/p1-r1/diff.patch", "src/app.py", "src/new.py"]
    assert data["left_out"] == ["config/secrets.json"]
    diff = (project / "reviews/p1-r1/diff.patch").read_text()
    assert "+    return 2" in diff and "hunter2" not in diff
    brief = (project / "reviews/p1-r1/BRIEF.md").read_text()
    assert "new: src/new.py" in brief and "with uncommitted changes" in brief
    assert "hunter2" not in brief


def test_run_starts_codex_read_only_with_stdin_closed_and_keeps_the_review(project):
    plan_brief(project)
    code, out = review(project, "run", "reviews/plan-r1", "--wait", typed="the owner's answer\n")
    assert code == 0, out
    [call] = calls(project)
    assert call["tool"] == "codex" and call["stdin"] == "" and Path(call["cwd"]).resolve() == project.resolve()
    assert call["argv"][:2] == ["exec", "--ephemeral"]
    assert ["--sandbox", "read-only"] == call["argv"][call["argv"].index("--sandbox"):][:2]
    assert 'model_reasoning_effort="high"' in call["argv"]
    assert call["argv"][-1] == "Read %s/BRIEF.md and follow it." % (project / "reviews/plan-r1").resolve()
    run = json.loads((project / "reviews/plan-r1/run.json").read_text())
    assert run["state"] == "done" and run["exit"] == 0 and run["reviewer"] == "codex"
    assert run["brief_sha256"] == sha(project / "reviews/plan-r1/BRIEF.md")
    assert run["review_sha256"] == sha(project / "reviews/plan-r1/review.md")
    assert "{dir}" in " ".join(run["argv"]) and str(project) not in json.dumps(run)
    assert "codex log line" in (project / "reviews/plan-r1/review.log").read_text()
    code, out = review(project, "run", "reviews/plan-r1")
    assert code == 2 and "a new round is a new brief" in out


def test_under_codex_the_reviewer_is_claude_in_plan_mode_and_auto_needs_a_harness(project):
    plan_brief(project)
    code, out = review(project, "run", "reviews/plan-r1", "--dry-run", harness=None)
    assert code == 2 and "pass --reviewer" in out
    code, out = review(project, "run", "reviews/plan-r1", "--wait", harness="codex", typed="y\n")
    assert code == 0, out
    [call] = calls(project)
    assert call["tool"] == "claude" and call["stdin"] == ""
    assert call["argv"][:6] == ["-p", "--model", "opus", "--permission-mode", "plan", "--add-dir"]
    assert (project / "reviews/plan-r1/review.md").read_text() == "No defects found.\nVERDICT: APPROVE\n"


def test_run_refuses_bytes_that_changed_after_the_brief_and_a_codex_that_is_not_logged_in(project):
    plan_brief(project)
    code, out = review(project, "run", "reviews/plan-r1", "--wait", FAKE_LOGIN="1")
    assert code == 1 and "codex login status exited 1" in out and "nothing was launched" in out
    (project / "notes/plan.md").write_text("# Plan\n\nPhase 1 adds totals and averages.\n")
    code, out = review(project, "run", "reviews/plan-r1", "--wait")
    assert code == 1 and "changed since the brief: notes/plan.md" in out
    assert calls(project) == [] and not (project / "reviews/plan-r1/run.json").exists()


def test_run_in_the_background_returns_at_once_and_status_follows_it(project):
    plan_brief(project)
    started = time.monotonic()
    code, out = review(project, "run", "reviews/plan-r1", FAKE_SLEEP="2")
    assert code == 0 and "in the background" in out and time.monotonic() - started < 2
    code, out = review(project, "status", "reviews")
    assert code == 1 and ("running" in out or "starting" in out), out
    deadline = time.monotonic() + 20
    while json.loads((project / "reviews/plan-r1/run.json").read_text())["state"] != "done":
        assert time.monotonic() < deadline, "the background review never finished"
        time.sleep(0.2)
    code, out = review(project, "status", "reviews")
    assert "reviews/plan-r1: plan review by codex (codex default), done, 0 finding(s)" in out
    assert "the ledger has no rows" in out and code == 1


def test_a_failed_or_empty_review_is_recorded_as_failed(project):
    plan_brief(project)
    plan_brief(project, "reviews/plan-r2")
    assert review(project, "run", "reviews/plan-r1", "--wait", FAKE_EXIT="3")[0] == 1
    assert review(project, "run", "reviews/plan-r2", "--wait", FAKE_REVIEW="")[0] == 1
    code, out = review(project, "status", "reviews")
    assert code == 1
    assert "the review failed (exit 3)" in out
    assert "the review failed (the reviewer exited 0 and wrote no review)" in out
    assert "unreviewed: notes/plan.md (reviews/plan-r2 has no finished review)" in out


def test_the_ledger_needs_every_cell_and_a_fixed_finding_needs_reproduction_and_a_commit(project):
    plan_brief(project)
    review(project, "run", "reviews/plan-r1", "--wait")
    fill(project, "reviews/plan-r1",
         ["F1", "wrong total", "", "blocking", "fixed", "", ""],
         ["F2", "typo", "no", "completeness", "fixed", "abc123", ""],
         ["F3", "race", "yes", "severe", "deferred", "", ""],
         ["F4", "unclear", "yes", "hardening", "open", "", ""])
    code, out = review(project, "status", "reviews/plan-r1")
    assert code == 1
    assert "F1: fill Reproduced" in out
    assert "F2: fixed, but not reproduced" in out and "F2: Repaired at 'abc123' is not a commit or tag here" in out
    assert "F3: Class is one of blocking, hardening, completeness, not 'severe'" in out
    assert "F3: deferred, with no target in Notes" in out
    assert "F4: still open" in out


def test_a_repair_is_unreviewed_until_a_later_round_reads_its_bytes(project):
    plan_brief(project)
    review(project, "run", "reviews/plan-r1", "--wait")
    (project / "notes/plan.md").write_text("# Plan\n\nPhase 1 adds totals, with a test.\n")
    repaired = commit(project, "repair F1")
    fill(project, "reviews/plan-r1", ["F1", "no test", "yes", "blocking", "fixed", repaired[:12], "test_total"])
    code, out = review(project, "status", "reviews")
    assert code == 1
    assert "unreviewed: notes/plan.md (changed since reviews/plan-r1 read %s)" % (
        json.loads((project / "reviews/plan-r1/brief.json").read_text())["files"][0]["sha256"][:12]) in out
    assert "problem" not in out
    plan_brief(project, "reviews/plan-r2")
    review(project, "run", "reviews/plan-r2", "--wait", FAKE_REVIEW="Nothing found.\nVERDICT: APPROVE\n")
    ledger = project / "reviews/plan-r2/FINDINGS.md"
    ledger.write_text(ledger.read_text() + "\nNo findings.\n")
    code, out = review(project, "status", "reviews", "--format", "json")
    data = json.loads(out)
    assert code == 0 and data["ok"], out
    assert data["coverage"] == [{"path": "notes/plan.md", "state": "reviewed", "round": "reviews/plan-r2"}]


def test_a_pr_review_reads_the_diff_at_its_head_and_posts_only_with_yes(project):
    code, out = review(project, "brief", "reviews/pr7", "--subject", "pr", "--pr", "7", "--question",
                       "Does this PR do what its description says, and nothing else?")
    assert code == 0, out
    assert "left out: .env" in out
    brief = (project / "reviews/pr7/BRIEF.md").read_text()
    assert "at head `%s`" % ("a" * 40) in brief and "not in your checkout" in brief
    assert "hunter2" not in (project / "reviews/pr7/diff.patch").read_text()
    code, out = review(project, "post", "reviews/pr7")
    assert code == 2 and "no finished review" in out
    review(project, "run", "reviews/pr7", "--wait")
    fill(project, "reviews/pr7", ["F1", "wrong total", "yes", "blocking", "deferred", "", "phase 2"])
    code, out = review(project, "post", "reviews/pr7", FAKE_HEAD="c" * 40)
    assert code == 0 and "not posted" in out
    assert "The PR head is now `%s`. This review did not read it." % ("c" * 40) in out
    assert not any(c["argv"][:2] == ["pr", "comment"] for c in calls(project))
    code, out = review(project, "post", "reviews/pr7", "--yes")
    assert code == 0 and "posted: https://github.com/o/r/pull/7#issuecomment-1" in out
    [posted] = [c for c in calls(project) if c["argv"][:2] == ["pr", "comment"]]
    assert posted["argv"][2] == "7"
    assert "returns the wrong total" in posted["body"] and "| F1 | wrong total |" in posted["body"]
    assert "PR head is now" not in posted["body"]
    code, out = review(project, "post", "reviews/pr7", "--yes")
    assert code == 2 and "already posted" in out


def test_sanitize_replaces_this_machines_paths_and_says_so(project):
    plan_brief(project)
    home = str(Path.home())
    review(project, "run", "reviews/plan-r1", "--wait",
           FAKE_REVIEW="F1. %s/notes/plan.md:3 and %s/.codex are named.\n" % (project, home))
    code, out = review(project, "status", "reviews/plan-r1")
    assert "names this machine's home folder" in out
    code, out = review(project, "sanitize", "reviews/plan-r1")
    assert code == 0 and "review.md: replaced 2 absolute path(s)" in out
    text = (project / "reviews/plan-r1/review.md").read_text()
    assert text.startswith("<!-- Edited by review_tool.py sanitize")
    assert "F1. <repo>/notes/plan.md:3 and <home>/.codex are named." in text and home not in text


def test_settings_choose_the_model_and_an_unknown_setting_is_an_error(project):
    plan_brief(project)
    settings = project / ".claude/skills/process-phase/scripts/review_tool.settings.json"
    assert json.loads(settings.read_text())["reviewer"] == "auto"
    settings.write_text(json.dumps({"codex_model": "gpt-x", "codex_effort": "xhigh"}))
    code, out = review(project, "run", "reviews/plan-r1", "--dry-run")
    assert code == 0
    assert "codex exec --ephemeral -m gpt-x -c 'model_reasoning_effort=\"xhigh\"' --sandbox read-only" in out
    assert "-o reviews/plan-r1/review.md 'Read reviews/plan-r1/BRIEF.md and follow it.'" in out
    settings.write_text(json.dumps({"reviewr": "codex"}))
    code, out = review(project, "run", "reviews/plan-r1", "--dry-run")
    assert code == 1 and "unknown setting(s): reviewr" in out
