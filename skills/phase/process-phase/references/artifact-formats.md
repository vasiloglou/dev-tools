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

Acceptance directories replace `-` with `_` in the phase slug: slug `data-import` in phase 4 gives `p04_data_import`.

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

No other `## Phase` headings may appear anywhere in the file.

## REQUIREMENTS.md rows

- `| U04b | <user requirement> |`
- `| REQ-IN-001 | <text> | U04b, U18 | 2 | Planned |`

The last column is `Planned` or `Validated`. `req-coverage` checks both directions: every U row is referenced by at least one REQ, and every REQ lists at least one roadmap phase.

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
