# Step 4 — Implement (reference)

Implement makes the locked acceptance tests pass without changing them. It needs `phase_status: plan_approved`, and no code is written while `phase_status` is `gaps_found` until the gap plan is approved.

**Roles.** The supervisor coordinates the resolved coder pool (§1.1), scope and commits.
Use focused red/green results directly; a supervisor, reviewer or handoff does
not rerun the same tests merely to establish independence. Independent code
review is optional, not part of every write round. The validation policy in
`../SKILL.md` supersedes older review/rerun requirements.

## 1. Orchestration

- **Test-driven, no replanning.** Once the plan is approved, implement to the locked tests and the approved plan. Do not redesign, re-plan, rewrite plans or open new design decisions. When a plan detail turns out wrong (a file list, a home, a task split), take the smallest change that turns the locked tests green, and record it as a deviation in the SUMMARY. Only a **critical** issue — a locked test that cannot go green as written, or an invariant (goldens, locked CX, or a project invariant in `references/project.md`) that the plan would break — goes to the user, as one short question with a recommendation, before anything else changes.

- **Budget checkpoint.** At 50% of the phase's time budget (set in CONTEXT), and at every subsequent 25%, stop starting new plans and report: the metric now against `prove.md`, the plans still open, and the proposed deferrals. The user decides. The exemption for work a locked test needs no longer applies: a locked test whose plan is deferred moves to `NN.1` under a DEC. This scope review is the sanctioned exception to the no-replanning rule; record deferrals in `.planning/todos/NN.1-<topic>.md` and the SUMMARY.

- **3× stop rule.** If a paid run of a step exceeds its proven `prove.md` cost or time by more than 3×, stop fixing forward. Compare the implemented method with the proven one, replace or simplify it, and tell the user in one line. After any failed paid run, and before the second fix to the same step, write one retro line: "is this still the proven method?" The budget is the method-record row on the same asset; a step also stops with a retro line when it used under a third of that budget while items it was given stayed unprocessed (the driver records `coverage = items reviewed / items given`), and when any previously passing item is lost.

- Plans run in `wave` order; tasks within a plan run strictly in sequence.
- **Parallel tracks first.** Before starting a wave, look for work that can run now: whole plans, or single tasks of later plans whose inputs already exist. Never run more tracks at once than `effective_tracks` (§1.1). Run each track in its own git worktree (`git worktree add ../<repo>-<track> -b <track-branch>`; run tests there with `PYTHONPATH=<worktree>/src .venv/bin/pytest …` from the worktree), with its own coder session and scope check. Bring the commits back to the phase branch by cherry-pick, regenerate shared generated files after the merge, and test only the affected integration seams on the merged branch.
- **Parallel plans.** Two or more remaining plans may run concurrently when they are independent: no shared files, and no task in one names a file, module or tool another produces. Each has its own coder session and scope/testlock check restricted to its own files; commits stay one per task.
- Before the first task resolve the coder pool (§1.1). The supervisor never writes task code itself.

### 1.1 Coder pool and limits

Coders and parallelism are per developer. Resolve them once per Implement session with the project's coder-pool command (`references/project.md`). It merges the team configuration with the developer's local, gitignored one (a worktree without one reads the main checkout's) and prints:

- **`coders:`** the pool, one line per `tool/account`, in preference order, with its `model`, `effort`, `risk` and `env`. Each line is a pool you can send tracks to. Prefix the account's `env` to every command of that pool, resume included; a track keeps its account for all its rounds.
- **`parallel:`** `max_tracks`, `max_sessions_per_account`, `capacity` and `effective_tracks = min(max_tracks, capacity)`. At most `max_sessions_per_account` concurrent sessions per account and at most `effective_tracks` tracks in total.
- **Assignment.** High-risk and critical-path tracks (goldens, project invariants) go to the first pool entry with `risk = any`; a pool with `risk = medium` takes medium-risk tracks only, and a task stuck there after 2 rounds moves to the first `any` pool (record the move in the SUMMARY).
- **Fallback.** When no configured coder is on PATH, the pool is `claude`. Tell the user in one line and continue with §2.2's Claude Code coder. When the pool is empty (`claude` missing too), stop and ask the user. Check each coder once before its first task (`codex --version`, `gemini --version`, `claude --version`).
- Team defaults: `coders = ["codex"]`, 4 tracks, 4 sessions per account. Accounts, homes and other personal paths go in the local file only.

## 2. Per-task loop (red → fix → focused green → commit)

### 2.1 Prompt

A coder has no Skill tool and no session context: inline or point to everything. Keep every coder or agent brief under `NN-EVIDENCE/briefs/<task>-<round>.md`, secrets excluded; a brief for a promoted step quotes its method-record row and lists each proven input or tool it drops, with a reason. One task is one red test: the brief names the test, a file allowlist and a line budget, and `.claude/skills/process-phase/scripts/codex_gate.py` rejects a round of any coder that touches other files or exceeds the budget (rejected, not repaired). Forbidden in a task unless listed: new flags, config keys or environment variables; fallbacks and broad `try/except`; new helper modules; edits to other tests; refactors. The supervisor never codes a promoted step without a parity test.

1. **Orientation:** "You are implementing task `NN-MM-Tk` of roadmap phase NN. Read the files below before writing anything."
2. **Required reading:** the project's required reading (`references/project.md`), `NN-CONTEXT.md`, `NN-MM-PLAN.md`; plus the `components` skill's `SKILL.md` and the plan's `## Reuse` component ids, with their module paths, so the coder calls them instead of rewriting them, and the `duplicate-of` modules it must not import; for a component the task changes, its `used_by:` callers, which must keep working. A task that adds a module to the project's source package lists `docs/components/COMPONENTS.md` in `files` and assigns the module to a component.
3. **The task** verbatim: `action`, `files`, `read_first`, `acceptance`.
4. **Locked tests** it must turn green (`turns_green` ids and paths): read-only; if one looks wrong, stop and explain.
5. **Hard rules:**
   - unit tests first in `tests/unit/<package>/test_<topic>.py`, seen failing, then the smallest implementation;
   - touch only `files` plus new `tests/unit/**` files; edit an existing unit test file only if it is in `files`;
   - no `importlib.import_module` or `__import__` to route around layering;
   - never touch `pyproject.toml`, `uv.lock` or extras: codex runs offline, the supervisor makes those changes;
   - never edit `tests/acceptance/pNN_*/` or `NN-TESTLOCK.json`;
   - no `TODO`, `FIXME`, `NotImplementedError` or stubs (PG14);
   - the project's hard rules (`references/project.md`);
   - do not commit.
6. **Report back:** the exact output of `verify` and the `turns_green` run.

### 2.2 Invoke the coder

This file is the only owner of the coder command lines. Use the line for the pool's tool, with the pool's `model`, `effort` and `env` from §1.1. Every coder gets the same brief (§2.1) and the same scope check (§2.3).

#### codex

```bash
codex exec -m <model> \
  -c model_reasoning_effort=<effort> \
  -c sandbox_workspace_write.network_access=false \
  --approve-for-me \
  -C <repo-root> --json \
  -o <scratch>/NN-MM-Tk-round1.last.txt \
  - < <scratch>/NN-MM-Tk-round1.prompt.md \
  | tee .planning/phases/NN-<slug>/NN-EVIDENCE/codex/NN-MM-Tk-round1.jsonl

codex exec resume --last -c model_reasoning_effort=<effort> \
  -c sandbox_workspace_write.network_access=false "<verbatim failure or review list>" \
  | tee .planning/phases/NN-<slug>/NN-EVIDENCE/codex/NN-MM-Tk-round2.jsonl
```

- Network stays off. Relaxing it for one task needs the user's sign-off, noted in the SUMMARY. Pass the `network_access=false` override on every call, resume included: `resume` does not inherit the first round's `-c` flags and falls back to `config.toml`.
- **Stuck task.** A task is stuck when it cannot resolve the same failing focused test, or when codex asks for help. **Ask the user before any round on the stuck-task model** (show the task, the failure and the rounds so far); never start one without their explicit yes. With approval, start a *fresh* round with `-m <stuck-task model> -c model_reasoning_effort=<effort>` (`resume` keeps the original model), then return to the pool's `<model>` for the next task. Record the approval and the switch in the SUMMARY rounds table.
- Model ids: the coding model and the stuck-task model come from the project's coder configuration (§1.1).
- **More accounts.** A second codex account is a pool entry whose `env` sets its own `CODEX_HOME` (a separate CLI home); it runs the same line with that prefix and the same model. `resume` needs the same `CODEX_HOME`. No other coding CLI writes project code unless the user explicitly asks.

#### gemini

  ```bash
  cd <track-worktree> && gemini -m <model> --approval-mode yolo \
    -p "$(cat <scratch>/NN-MM-Tk-round1.prompt.md)" \
    | tee .planning/phases/NN-<slug>/NN-EVIDENCE/gemini/NN-MM-Tk-round1.log
  ```

  - The worktree must sit in a folder the CLI trusts.
  - Do not use `-s`: the seatbelt sandbox loses the API key and drops trust.
  - Gemini has network access and runs shell commands, so the per-round scope check (§2.3) is the guard. Revert anything outside `files`.
  - A follow-up round is a fresh `-p` call. The CLI has no `resume`, so the prompt carries the failure or review list together with the original task.
  - Configure gemini with `risk = "medium"` for medium-risk tracks only (§1.1).

#### Claude Code (fallback, or when configured)

```bash
cd <track-worktree> && claude -p --model <model> --effort <effort> \
  --permission-mode acceptEdits \
  --allowedTools "Read Edit Write Bash(.venv/bin/python -m pytest *) Bash(git status *) Bash(git diff *)" \
  --output-format json < <scratch>/NN-MM-Tk-round1.prompt.md \
  | tee .planning/phases/NN-<slug>/NN-EVIDENCE/codex/claude-NN-MM-Tk-round1.json

cd <track-worktree> && claude -p --resume <session_id> --permission-mode acceptEdits \
  --allowedTools "…same…" --output-format json "<verbatim failure or review list>" \
  | tee .planning/phases/NN-<slug>/NN-EVIDENCE/codex/claude-NN-MM-Tk-round2.json
```

- A fresh process in the track worktree, never the supervisor session; drop `--model`/`--effort` when empty (CLI default). Take `session_id` from round 1's JSON for `--resume`.
- It has network access (the API needs it), so the per-round scope check (§2.3) is the guard, as for gemini. It does not commit.
- Its transcripts go under `NN-EVIDENCE/codex/` (gitignored, listed in `MANIFEST.md`, §5).

### 2.3 Focused verification and scope

For each fix, first reproduce the defect with a focused failing test. Run that
test and directly affected tests after the smallest implementation change.
Reuse the result while relevant code/inputs are unchanged; record command,
result and tested diff/revision. Do not run whole phases, earlier phases or the
full suite automatically after each task, merge or handoff.

Run `.claude/skills/process-phase/scripts/codex_gate.py --allow <file> … --max-added <budget>` in the track worktree after every round of any coder, then `git status --short` and `check --testlock NN`. Preserve unrelated work.
An unexpected edit needs inspection, not an indiscriminate reset or cleanup.
The only full regression run belongs at the end of Verify, after focused fixes.

### 2.4 Corrective work

A failing test drives the next focused fix. Normal fixes within approved scope
do not require escalation because a write-round counter was reached. Escalate
an unresolved repeated cause or a real scope, locked-contract, cost or safety
decision, with a concise failure and proposed action. Never weaken tests.

If the final full regression finds a defect, return to focused tests and report
that result. Do not silently run another whole suite or claim stale coverage.

### 2.5 Optional review

No per-task/per-plan review or independent evidence audit is mandatory. If the
user requests review, or there is a concrete correctness concern that inspection
can resolve, use `phase-code-reviewer` once on the relevant diff. Reuse valid
test results; reproduce only the uncertain behavior with a focused test.

Only actual correctness/acceptance failures need fixes. Style, size and speculative
hardening are logged briefly. A reviewer must not create another full-suite,
replay, oracle-validation or evidence-review round.

### 2.6 Commit

Commit when the focused tests are green and the task is in scope: `git add <task files + new tests/unit/**>` then `git commit -m "feat(NN-MM): <task>"`. Types: `feat|fix|refactor|test|perf|chore|docs`. Never `--no-verify`, never `git add -A`.

## 3. Locked acceptance tests

`check --testlock NN` covers every file in `tests/acceptance/pNN_<slug>/` (helpers too) and every declared fixture. If a locked test looks wrong, stop and show the evidence. The only way forward: a DEC (test id, problem, replacement) → the user approves → you (not codex) edit the test → `phase_tool.py testlock --phase NN --write --relock --dec DEC-NNN` → its own commit `test(NN): re-lock acceptance tests (DEC-NNN)`, never bundled into a `feat` commit.

**Oracle correction.** When an independent check shows that a locked test's helper or expected value is wrong while the product is right (a counterexample run on real data, attached), the supervisor writes the DEC with the counterexample. Such DECs are batched: the user approves them together at the next status line, then there is one re-lock and one commit. A change to what the product must do (a contract change) is never an oracle correction. It keeps the per-DEC gate.

## 4. Project-specific steps

- Steps that depend on the project's own tooling (for example regenerating a generated index and committing it with the change that caused it) follow `references/project.md`.

## 5. LLM, network, secrets, spend

- LLM and other external-service calls take an injected provider; tests use `fake` or replay cassettes, recorded once with the user's approval.
- Never put a secret in a codex prompt or log; keep transcripts under `NN-EVIDENCE/codex/` local and git-ignored. Never force-add transcripts.
- Maintain `.planning/phases/NN-<slug>/NN-EVIDENCE/codex/MANIFEST.md` instead: one row per transcript with its file name relative to the manifest, size in bytes, SHA-256 of the exact file bytes, and task id.
- Sort manifest rows by file name, refresh them after each round, and commit the manifest. For historical files whose names encode no task id, record `unspecified (historical)` rather than guessing. Previously committed transcripts remain in history; do not rewrite it.
- Spend beyond codex and review runs (paid APIs, paid compute) is a `checkpoint:decision` task.

## 6. Summary, pausing, leaving

- Record material deviations briefly. One that changes a LOCKED CX, a thesis or a test needs a human gate. DISCRETION choices get a one-line rationale.
- Per plan, write `NN-MM-SUMMARY.md` (`templates/SUMMARY.md`): commits, focused tests/results, material deviations and unresolved failures. Do not create per-round evidence packets. Commit `docs(NN-MM): summary`.
- To pause, fill `.continue-here.md` (include the coder session id and its pool) and commit `wip(NN): pause at NN-MM-T<k>`.
- To leave: required acceptance/focused results are current and green, `check --testlock NN` clean, then `advance --to implemented`. Verify reuses these results and performs the one final full regression run; no fresh verifier is mandatory.
