# Step 0 — Orient (reference)

Orient always runs, even when the user asks for a specific step with `--step`. It is cheap and it prevents the most expensive mistakes: working on the wrong branch, discarding someone's changes, or building on a red baseline.

## 1. Ask phase_tool where you are

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py status --phase NN --format md
```

Read these fields:

| Field | Meaning | Action |
|---|---|---|
| `current_phase`, `phase_status`, `active_step` | Position in the status machine | Pick the step: `next_step` unless `--step` overrides it |
| `missing[]` | Artifacts expected for the status already reached (e.g. `NN-CONTEXT.md`, `NN-TESTLOCK.json`, `NN-EVIDENCE/red.txt`) | Produce them in the right step; from `plan_approved` on, `advance` refuses to move while any is missing (only a DEC can waive one) |
| `blockers[]` / `blocked_on` | Set by a previous step or a human | Stop and show them. Only the human clears `blocked_on` |
| `deps_complete` | All phases in **Depends on** are `complete` | If false, stop |
| `dirty` | Working tree has changes | Apply the dirty-tree policy below |
| `branch` | Current git branch | Must equal `phase/NN-<slug>` (or the bootstrap exception); switch or create (below) |
| `gates_applicable[]` | PG ids for this phase (from `scripts/gates.json`) | Copy them into NN-CONTEXT and NN-VERIFICATION |

When the last phase of the roadmap is completed, the state rests on it with `phase_status: complete`. Add the next phase's block to `ROADMAP.md` and `status` names that phase as the current one, `not_started`; `advance` then writes it to `STATE.md`.

`--step X` is honoured only when the status machine allows it. For example, `--step implement` with `phase_status: context_approved` is refused, and you must say why: Specify and Plan come first.

## 2. Reading order (load only what the phase needs)

1. `.planning/STATE.md`: frontmatter, digest, lessons `LS-NN`. Lessons are cheap to read and often decisive.
2. `phase_tool.py roadmap get NN`, the phase block. Treat **Acceptance tests (written first)** and **Exit criteria** as the contract you will turn into tests.
3. `.planning/MANIFESTO.md`, only the sections and theses (T ids) listed in **Manifesto refs**.
4. `.planning/REQUIREMENTS.md`, only the REQ rows listed in **Requirements**.
5. `.planning/DECISIONS.md` (all LOCKED DEC entries that mention this phase), then `.planning/RISKS.md` (the RK ids in **Risks**), then `.planning/OPEN-QUESTIONS.md` (rows whose blocking phase is NN).
6. `.planning/MIGRATION.md`, the rows for the modules listed in **Reuses**.
7. The previous phase's `NN-MM-SUMMARY.md` files and `NN-VERIFICATION.md`, including any deferred gaps.
8. Normative docs in `.planning/docs/` cited by the block.
9. `references/project.md` in this skill directory, if it exists. The project owns it; it lists the project's invariants, extra gates and tool commands, and it governs project-specific matters.

Do not read the whole `.planning/` tree. Context is a budget.

## 3. Branch policy

- `base_branch` and `release_branch` are set in the STATE frontmatter.
- Each phase works on `phase/NN-<slug>`, for example `phase/02-<slug>`:

```bash
git switch phase/02-<slug> 2>/dev/null || git switch -c phase/02-<slug> <base_branch>
```

- Never commit on `base_branch` or `release_branch` during a phase; Close merges the phase branch back. The only exception is a bootstrap phase, whose STATE records `phase_branch` equal to `base_branch`.
- `phase_branch` is not a status field and `advance` does not change it. After creating the phase branch, run `phase_tool.py branch --set phase/NN-<slug>`, the only writer of that key, and include `STATE.md` in the Discuss commit. Never edit STATE's frontmatter by hand.

## 4. Dirty-tree policy

| Situation | Action |
|---|---|
| Clean tree | Continue |
| Dirty, and `.continue-here.md` lists exactly the dirty files | Resume from `.continue-here.md` (next task, open decisions) |
| Dirty otherwise | Ask the user: (a) WIP commit `wip(NN): <summary>` on the phase branch, (b) `git stash push -m "process-phase NN"`, (c) stop |

Never run `git checkout -- .`, `git reset --hard` or `git clean`, and never delete untracked files. Changes that are not yours belong to the user.

## 5. Existing baseline

Reuse an existing baseline or CI result if one is available. Record its revision
and known failures; do not run a new full baseline suite at Orient. If a failure
is suspected to predate the work, use a focused base-revision reproduction only
when needed. Otherwise say the baseline is unknown rather than inventing one.

Known failures need exact causal dispositions. A previously failing ID is not
permission to introduce another cause. The single final full regression run is
performed in Verify after focused tests and fixes are complete.

Always use the repository `.venv` Python. In a worktree without its own venv, put
worktree src first on PYTHONPATH so an editable install cannot select other code.

## 6. Hand-off

- If `.planning/` itself does not exist, this is a new project: run `phase_tool.py setup`, fill in the first roadmap phase with the user, commit, and stop until `check --all` is clean.
- If the phase directory does not exist, run `phase_tool.py init --phase NN`. It creates `.planning/phases/NN-<slug>/` with `NN-CONTEXT.md`, `NN-DISCUSSION-LOG.md`, `NN-TESTS.md` and `NN-DEFERRED.md` copied from `templates/` (placeholders `{{PHASE}}`, `{{TITLE}}`, `{{SLUG}}` filled), plus `NN-EVIDENCE/.gitkeep`. Other templates (PLAN, SUMMARY, VERIFICATION, UAT, RESEARCH, continue-here) are copied by hand when their step starts; `check --context` / `--plan` flag any placeholder left unfilled.
- Announce, in two or three lines: the phase, the status, the step you are about to run, and the gates that apply.
- Continue with the step. Orient itself commits nothing, apart from an optional WIP commit the user chose.
