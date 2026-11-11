# Artifact formats (reference)

These formats are parsed by `phase_tool.py`. Keep them exact.

## Directory layout

```text
.planning/
  STATE.md  ROADMAP.md  REQUIREMENTS.md  MANIFESTO.md  DECISIONS.md  RISKS.md
  OPEN-QUESTIONS.md  GLOSSARY.md  MIGRATION.md  README.md  planned-paths.txt
  docs/*.md            normative docs (frontmatter normative_for)
  research/            archived research reports (read-only)
  todos/               deferred ideas, one file per idea
  archive/             superseded MANIFESTO versions
  phases/NN-<slug>/    NN = two digits, slug from ROADMAP **Slug:**
    NN-CONTEXT.md  NN-DISCUSSION-LOG.md  NN-TESTS.md  NN-TESTLOCK.json
    NN-RESEARCH.md  spikes/  NN-MM-PLAN.md  NN-MM-SUMMARY.md
    NN-VERIFICATION.md  NN-UAT.md  uat/  .continue-here.md (only while paused)
    NN-EVIDENCE/
      baseline.txt  red.txt
      runs/        test and gate logs (pytest.txt, pytest-phase.txt, pgN-*.txt|json)
      artifacts/   produced data evidence (card.json, metrics.json)
      skill-evals/ one JSON per skill
      llm-replay/  committed cassettes for LLM or other external-service calls
      code-review.md
tests/acceptance/pNN_<slug_with_underscores>/   test_<capability>.py, pNN_helpers.py, conftest.py
```

Acceptance directories replace `-` with `_` in the phase slug: slug `data-import` in phase 4 gives `p04_data_import`. Give test files names that are unique across phases (for example `test_p04_import.py`), or give each package an `__init__.py`: pytest otherwise refuses two test files with the same base name.

## STATE.md

The file starts with flat `key: value` frontmatter and no nesting:

```yaml
---
current_phase: "01"
phase_status: not_started
active_step: null
completed_phases: "00"
base_branch: develop
phase_branch: phase/01-<slug>
release_branch: main
last_activity: 2026-10-01
blocked_on: null
manifesto_version: 1.0.0
---
```

- `completed_phases` is a quoted, comma-separated list of two-digit ids (`"00,01"`).
- `phase_status` takes one of `not_started, context_approved, tests_approved, plan_approved, implemented, verified, gaps_found, complete`.
- `active_step` takes one of `orient, discuss, specify, plan, implement, verify, close, null`.
- After the frontmatter comes a digest of at most 80 lines: where we are, the next step, and lessons `LS-NN`.

## ROADMAP.md phase block

The heading is exactly `## Phase N: <Title>`, where N is an integer (`N.M` for an inserted phase). The bullets are:

```markdown
- **Slug:** data-import
- **Status:** not_started
- **Depends on:** 1
- **Requirements:** REQ-IN-001, REQ-IN-002
- **Manifesto refs:** T1, T5
- **Goal:** …
- **Reuses:** `src/<package>/<module>.py` (`<function>`, `<function>`)
- **Delivers:**
  - …
- **Acceptance tests (written first):** `tests/acceptance/p02_data_import/`
  - `test_import.py`: every sample row is imported exactly once
- **Exit criteria:** …
- **Risks:** RK-NN, RK-NN
```

No other `## Phase` headings may appear anywhere in the file. Whole-number phases are numbered without gaps, starting at 0 or 1 (a project that sets `phase_gaps`, below, keeps whatever rising numbers it has); `N.M` phases are inserted between them later. Only **Depends on** decides what may start.

## REQUIREMENTS.md rows

- `| U04b | <user requirement> |`
- `| REQ-IN-001 | <text> | U04b, U18 | 2 | Planned |`

The last column is `Planned` or `Validated`. `req-coverage` checks both directions: every U row is referenced by at least one REQ, and every REQ lists at least one roadmap phase.

## Other top-level files

- `DECISIONS.md`: one table row per decision, starting `| DEC-NNN |` (three digits), with the date, the decision, the reason and who approved it. `activate`, `--override` and `--relock` accept only a DEC id that has a row.
- `MIGRATION.md`: a table of modules being replaced (`| Module | Status | Replaced by |`); empty when nothing is. `migration-check` reads it.
- `planned-paths.txt`: one path per line that the roadmap will create; `#` starts a comment. `check --ignored` fails if `.gitignore` would hide one.
- `MANIFESTO.md`, `RISKS.md`, `OPEN-QUESTIONS.md`, `GLOSSARY.md`, `README.md`: free text and tables using the ids below.

## Starting a new project

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py setup [--name NAME] [--base-branch B] [--release-branch B]
```

`setup` writes the eleven top-level files from `templates/planning/` with one placeholder phase, one requirement and a `DEC-001` row for adopting the workflow. It never overwrites a file that exists. Fill in the first phase, commit, and `check --all` is clean.

`setup` is for a project with no plan. It stops, writing nothing, when `STATE.md`, `ROADMAP.md` or `REQUIREMENTS.md` is already there in another format. A project planned with GSD is moved with `devtools/from_gsd.py` in the dev-tools checkout (the `move-from-gsd` skill there is the guide); any other plan is rewritten by hand in the formats above, or moved aside first.

`check --all` asks for a decision row whenever the skill's rule text changes against the base branch. That includes the first sync of the skill (covered by `DEC-001`), a later sync that brings changed text, and edits to the project's own `references/project.md`: add one DEC row for each such change.

## Settings

`scripts/phase_tool.settings.json` (written by the sync from `.devtools.toml`) holds the project's paths and names. `gated_from` sets the first status at which `advance` blocks on missing files: `context_approved` (default, every step enforced), or `tests_approved` / `plan_approved` for a project whose earlier phases were run when the first steps only warned. `skill_check` says which skills and agents `check` holds to the skill rules: `"all"` under `skill_roots` and `agents_dir` (default), or `"synced"` for only the ones the sync delivered, read from `.devtools-receipt.json`, for a project whose folders also hold skills or agents written to other rules. `phase_gaps = true` accepts a roadmap whose phase numbers do not start at 0 or 1 or skip some, for a project whose numbers come from an earlier process (one moved from GSD).

## Identifier formats

| Id | Format | Owner file |
|---|---|---|
| Thesis | `T<n>` | MANIFESTO.md |
| User requirement | `U<nn>` (optional letter suffix, e.g. `U04b`) | REQUIREMENTS.md |
| Requirement | `REQ-<FAM>-NNN`, FAM an uppercase family code | REQUIREMENTS.md |
| Decision | `DEC-NNN` | DECISIONS.md |
| Risk | `RK-NN` | RISKS.md |
| Open question | `OQ-NN` | OPEN-QUESTIONS.md |
| Process gate | `PG<n>` | `scripts/gates.json` |
| Phase decision | `CX-NN` | NN-CONTEXT.md |
| Lesson | `LS-NN` | STATE.md digest |
| Plan / task | `NN-MM` / `NN-MM-T<k>` | NN-MM-PLAN.md |

## Normative docs

Each `.planning/docs/*.md` starts with:

```yaml
---
normative_for: [topic-a, topic-b]
status: draft
---
```

A topic has exactly one owner doc (`check --all`). Other docs link to the owner instead of restating it.

## NN-TESTLOCK.json

```json
{"phase": "NN", "created": "YYYY-MM-DD",
 "files": {"tests/acceptance/pNN_<slug>/test_x.py": "<sha256 hex>", "tests/acceptance/pNN_<slug>/expected.json": "<sha256 hex>"},
 "fixtures": {"tests/fixtures/data/orders.json": "<sha256 hex>"},
 "relocks": [{"date": "YYYY-MM-DD", "dec": "DEC-NNN"}]}
```

Paths are repo-relative with forward slashes. `files` covers every file under the acceptance directory (caches excluded); `fixtures` covers what was declared with `--fixture`; `relocks` exists only after a re-lock. It is written only by `phase_tool.py testlock --phase NN --write` (first lock) or `--write --relock --dec DEC-NNN` (after a human-approved DEC).

## Evidence naming

- Evidence must be tracked by git. Check new paths with `phase_tool.py check --ignored` or `git check-ignore -v <path>`.
- Log names say which gate they belong to, e.g. `runs/pg6-layering.txt`.
- `NN-VERIFICATION.md` cites evidence as a path relative to the phase directory, e.g. `NN-EVIDENCE/runs/pytest.txt`, or as a repo-relative path.
- Large data stays outside git, in an ignored data directory. Evidence keeps hashes, cards and 5–10 quoted samples.

## Commit messages

| Step | Message |
|---|---|
| Discuss | `docs(NN): capture phase context` |
| Specify | `test(NN): acceptance tests (red)` |
| Re-lock | `test(NN): re-lock acceptance tests (DEC-NNN)` |
| Plan | `docs(NN): plan phase (M plans)` |
| Implement | `feat|fix|refactor|test|perf|chore(NN-MM): <task>`, `docs(NN-MM): summary` |
| Pause | `wip(NN): <summary>` |
| Verify | `docs(NN): verification (verified|gaps_found)` |
| Close | `docs(NN): complete phase — <one-liner>` |
