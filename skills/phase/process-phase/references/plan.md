# Step 3 — Plan (reference)

Plan runs after the acceptance tests are locked. It turns the red tests into an ordered set of tasks, where every task names the tests it turns green. It needs `phase_status: tests_approved`, or `gaps_found` when writing gap-closure plans.

## 1. Research, only where the plan depends on an unknown

Spawn `phase-researcher` subagents (read-only), one topic each. Good topics:

| Topic | Where to look |
|---|---|
| Current behaviour to reuse | The project's source package: the modules listed in **Reuses** and the component index hits |
| Dependency APIs and behaviour | The dependency's source and docs at the pinned version; `docs/components/external/` |

Synthesize the results in `NN-RESEARCH.md` (`templates/RESEARCH.md`): findings with sources (file paths, doc URLs), options, a recommendation, baseline measurements, and open questions marked resolved or deferred. Do not cite academic papers; describe ideas plainly.

## 2. Spikes

Spikes whose verdict changes what the acceptance tests assert already ran in Discuss; their verdicts are LOCKED CX items and Plan does not reopen them. Every other RISKS row this phase owns gets a spike here before the plan relies on it.

- The spike code lives in `.planning/phases/NN-<slug>/spikes/<rk-id>/`, is timeboxed, and is never imported by `src/`.
- The verdict is recorded in NN-RESEARCH.md as **Go**, **Pivot** (with the changed approach) or **Kill** (with evidence).
- A Kill stops the step. Propose a ROADMAP amendment, such as moving the capability or inserting a phase, at a human gate.

## 3. Write the plans

`NN-MM-PLAN.md` from `templates/PLAN.md`. MM is two digits, and plans are ordered by `wave`.

Reuse before build: follow the `components` skill's Consult steps for every capability a task builds. Search the component index by capability (`.venv/bin/python scripts/components_index.py search <verbs>`), read the matching `docs/components/COMPONENTS.md` entries and `docs/components/external/` (the project's dependencies), then any capability list the project keeps (`references/project.md`), and `git grep` on earlier phase branches (`git grep <pattern> <branch> -- <paths>`). Every plan needs a `## Reuse` section with a `searched:` line (queries and sources), an `external:` line (dependency names checked), and a `reuse:` line naming existing component ids or a `new_component: <id> because <reason>` line. `check --plan` enforces this section; `check --all` does not recheck historical plans. `reuse:` may also name a `subsystem.*` id when the plan extends a whole flow. For every component a plan changes, read its `used_by:` (and `graph.md`): those callers go into `read_first`, and their tests into the task's focused test run. A plan that adds a module also adds or extends its component entry (`components` Update); a plan that changes the order of an end-to-end flow also updates that subsystem's `flow:`.

**The prove round wins over reuse.** When `prove.md` holds a proven method for a step, the plan implements that method. Existing code is reused only when it does the same thing at about the same cost and time. A same-named, heavier step is not reuse. Every plan task, wave track and coder brief names the `prove.md` section it automates, plus that run's measured cost, time and agent turns as its budget. A plan that automates a step carries `prove_method: <goal id>` and `budget_basis: same-asset | scaled from <goal id> (<formula>)` in its frontmatter: a method-record row measured on a smaller asset is a per-unit rate, never a budget for the larger one. Content the proven run had and the plan drops (an input, a tool, an instruction clause) is listed with a reason. For every plan that carries `prove_method`, write `NN-EVIDENCE/parity/<goal id>.md` before the step's first run, paid or not: inputs, tools, instruction clauses and budget of the proven run and of the automated step side by side, with a reason for every difference; `advance --to implemented` checks that the file exists. A $0 parity check is neither a replay nor a redesign. A wave plan made outside this step still applies this rule before any coder brief goes out.

Required frontmatter keys:
- `phase`, `plan`, `wave`, `depends_on`;
- `requirements[]` (non-empty REQ ids);
- `turns_green[]`: the union of the test ids its tasks claim;
- `manifesto_refs[]` (T ids);
- `skills[]`;
- `migration{shims_added, modules_frozen, modules_deleted}`;
- `golden_impact: none | regenerate(<reason>)`;
- `metrics_expected{}` (mandatory for data phases and numeric exits);
- `llm_dependency: none|fake|replay`;
- `gap_closure: false|true`.

Each task in `<tasks>` has:

| Field | Content |
|---|---|
| `id` | `NN-MM-T<k>` |
| `turns_green` | Locked acceptance test ids, e.g. `tests/acceptance/p01_<slug>/test_<capability>.py::<test>` |
| `unit_tests` | New unit test files written first, e.g. `tests/unit/<package>/test_<topic>.py` |
| `files` | Files created or modified |
| `read_first` | Files to read before editing |
| `action` | What to do, concretely |
| `verify` | A command, e.g. `.venv/bin/pytest tests/unit/<package> -q && .venv/bin/pytest --phase 01 -k <capability>` |
| `acceptance` | Checkable statements (grep-able or test-backed) |
| `type` | `auto`, `checkpoint:decision` or `checkpoint:human-verify` |

**Coverage rule.** Every contract test id in NN-TESTS.md appears in the `turns_green` of at least one task; a `guard` row is green from the start and needs no task. `check --plan` catches the mechanical failures: unfilled `{{…}}` placeholders, a stub plan (under 200 characters) and a plan that names no test (`tests/…` or `test_…`). The coverage rule and non-empty `verify` / `requirements` are checked by you and by the plan review.

**An advisory check.** `phase_tool.py check --plans NN` looks at the plans of a phase together and lists what it finds: a contract test id in the Traceability table of NN-TESTS.md that no task claims, a plan with no task, a plan whose `requirements` names no REQ id, a task with an empty `verify`, a requirement a plan names that is not the phase's, and a requirement of the phase that no plan names. It is not a gate: it has not yet been run on the plans of real projects, and no step requires it. Run it when you check coverage, read each line against the plan, and treat a line as a place to look, not as a block; if a line is wrong about a plan that is right, say so to the user and go on. What it reads: the test ids of the Traceability table (not the locked files, so a test missing from the table is not seen); for coverage, only what tasks claim, not the frontmatter list (the two are compared, below); a test id with a bare file name as being in the `test_dir` of NN-TESTS.md, so `test_scan.py::test_x` and `tests/acceptance/p01_scan/test_scan.py::test_x` are the same test; a task field written `- **name:** value`, with paths and test ids in backticks, which may run on over indented lines.

The same check reads how the plans are ordered, and it is advisory there too. It lists:
- a `depends_on` that names no plan of the phase, forms a loop, or points to a plan in a later wave;
- a `wave` that is not a whole number from 1 up, when the phase has several plans;
- a plan whose frontmatter `turns_green` differs from what its tasks claim (one test whatever its parameters);
- two plans of one wave, neither after the other through `depends_on`, that both name a file.

Two entries name the same file when they are the same path, when one is a folder (ending in `/`) that holds the other, or when a pattern with `*` matches the other. Two patterns, or a pattern and a folder, count when the text before the first `*` of one starts the other's, so a pair that never meets can be listed. A shared generated file is not listed: the component index, the capabilities file, anything under the planning folder, and what the project names in the `shared_files` setting of `phase_tool.settings.json`. To clear a line, name the files more exactly, add the `depends_on` edge, move one plan to a later wave, or put a generated file under `shared_files`. One warning, which fails nothing: a wave with more plans that can start at once than `coder_pool.py show` gives as `effective_tracks` on this machine. A plan's id is the `NN-MM` its file name starts with; `depends_on` may write it in full, as `MM`, or as the file name.

### 3.1 Parallel tracks

Plan for parallelism explicitly. A strictly sequential chain is the most expensive shape a phase can have.
- **Tracks.** Group the work into tracks that touch disjoint files and do not consume each other's outputs. Give each plan a `wave`. Plans in the same wave with no `depends_on` edge between them run in parallel worktrees. `check --plans NN` lists two such plans that name the same file (the advisory check above).
- **Split to parallelise.** When a plan mixes a critical-path part with a leaf part, such as a skill, docs, a catalog, or a tool that only needs an earlier plan's data format, split the leaf part into its own plan so it can start earlier.
- **Shared files.** When two tracks must both touch a shared generated file such as a generated index, name the file in both plans and regenerate it after the merge. Do not serialise the tracks for it.
- **Track cap.** A wave never has more parallel tracks than the developer's `effective_tracks` (`implement.md` §1.1; team default 4). Extra independent work goes to the next wave. Implement re-resolves the pool and never runs more tracks than its own cap, so a plan stays valid for any developer.
- **Show the waves.** The plan gate shows the waves and tracks, and the cap they were planned for. The user approves the parallel shape together with the plans.

### 3.2 Multiscale MVP

- Plan `NN-01` is the thin end-to-end slice that automates the `prove.md` §3 prototype on the same asset and metric, turning the targets that held green. No other plan starts until it is green, except leaf work such as docs or catalogues with no shared files. Corner cases, security hardening and production readiness (packaging polish, performance tuning, rare-input validation, error-message polish, hardening of untrusted inputs) go to a follow-up milestone `NN.1` (`.planning/todos/NN.1-<topic>.md`) unless a locked test or a critical invariant (goldens, secrets, or a project invariant in `references/project.md`) needs them.
- Each plan lists its deferred items in a `deferred` section, so a later budget checkpoint (`implement.md` §1) can cut further without a redesign.
- A task should normally land within one to two hours.

## 4. Constitution check

Check each plan against the manifesto's theses and the software contract. Fail the plan if any of these holds:

| Violation | Thesis / rule |
|---|---|
| A locked acceptance test is modified | tests are the phase contract |
| A project invariant is broken | `references/project.md` |

Every touched legacy module (see **Reuses**) needs a MIGRATION row and a strategy: keep, shim, freeze or move.

## 5. Plan review and gate

Plan only tasks that serve the MVP direction.

1. Run `phase_tool.py check --plan <file>` for every plan (deterministic).
2. Check coverage and scope once in the current session (`phase_tool.py check --plans NN` lists what it can see of this; it is advisory): every test is claimed; no two plans of one wave name the same file; no task contradicts a LOCKED CX; plans list in `files` every existing test file their change affects. If the project keeps rules about plans (`"about": "plans"` in the components skill's `rules.json`) and the user asked for that check, run `python3 .claude/skills/components/scripts/rules_check.py check --phase NN` as well: it is a trial, needs GND, and prints `skip:` without it. A separate reviewer or review round is optional, not a gate. Verification commands must follow focused TDD and one final full regression, with no replay/evidence-review loops.
3. **Gap closure** (`gap_closure: true`): the plan lists every open G-id from NN-VERIFICATION.md with a disposition `fix | DEC | logged`. No code changes while `phase_status` is `gaps_found` until this plan is approved.
4. Show the user waves, tasks, `turns_green` coverage and the prototype verdicts per goal. After approval:

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py advance --to plan_approved
git add .planning/phases/NN-<slug>/ .planning/STATE.md .planning/ROADMAP.md
git commit -m "docs(NN): plan phase (M plans)"
```

A relock needed by a plan is its own `test(NN): re-lock …` commit, never bundled into `feat`.
