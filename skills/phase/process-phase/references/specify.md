# Step 2 — Specify (reference)

Specify writes the phase contract as executable acceptance tests before any implementation. It ends with the tests red, the red run recorded, the files locked in `NN-TESTLOCK.json`, and the user's approval. The thesis "tests are the phase contract" is enforced here.

The `phase-tests` skill has the detailed writing guide. This file covers the process.

## 1. Inputs

- The ROADMAP block's **Acceptance tests (written first)** bullets and **Exit criteria**.
- The `LOCKED` CX decisions from `NN-CONTEXT.md`. Each one either becomes an assertion or is explicitly marked "not testable" in NN-TESTS.md with a reason.
- `NN-EVIDENCE/prove.md`: the targets that held (§5), the validated oracle cases (§4) and the evidence files it cites; the tests lock these numbers and cases.
- Fixtures in `tests/fixtures/`.

## 2. Who writes

- Small phase: the main context reads `prove.md` and the evidence it cites, then follows the `phase-tests` skill.
- Larger phase: spawn `phase-test-writer`. Give it:
  - the ROADMAP block;
  - the CONTEXT;
  - `NN-EVIDENCE/prove.md` and the paths of the evidence it cites;
  - the target directory `tests/acceptance/pNN_<slug_with_underscores>/`;
  - the instruction to return the red log.

## 3. Rules for the tests

| Rule | Why |
|---|---|
| ≥1 test per target that held in `prove.md` §5 (its metric, asset and target from §1) and per retained exit criterion | Specify locks what the prototype proved. A Killed goal or a ROADMAP bullet deferred by `prove.md` §6 gets no locked test in this phase; NN-TESTS.md lists it as deferred, with the reason. An exit criterion is removed or changed only by a user-approved DEC amending it in CONTEXT and ROADMAP before this step (`discuss.md` §5); every exit criterion still in CONTEXT is tested |
| Directory `tests/acceptance/pNN_<slug>/`, files `test_<capability>.py` | The `--phase` plugin selects by directory prefix `pNN_` |
| Basenames unique across `tests/` | `tests/` has no `__init__.py`; pytest's default import mode needs unique module names |
| Helpers in `pNN_helpers.py`, fixtures re-exported from a small `conftest.py` | Avoids clashing helper module names between phases |
| Public API only: the CLI or documented package entry points | Tests must not pin private helpers the plan may reshape |
| Fake or replay providers only; no network; deterministic seeds | Reproducible gates |
| Assertions name the behaviour, e.g. `assert env["error"]["code"] == "UNKNOWN_MEMBER"` | Red and green are both informative |

Each helper's docstring names the `prove.md` §4 oracle case it was validated against. Every helper that can affect a verdict (inputs, expected answers, scoring or reference builders) stays locked.

## 4. Red for the right reason

```bash
.venv/bin/pytest --phase NN -q -rA -p no:cacheprovider 2>&1 | tee .planning/phases/NN-<slug>/NN-EVIDENCE/red.txt
```

Classify every failure:

| Outcome | Verdict |
|---|---|
| `ModuleNotFoundError: No module named 'myapp.reports'` (module the phase creates) | Right reason |
| `AssertionError` about missing behaviour, e.g. a result lacks a required field | Right reason |
| The CLI reports a usage error (exit 2) for a command the phase adds | Right reason |
| `SyntaxError`, `ERROR collecting`, `fixture 'x' not found`, `NameError` in the test | Wrong: fix the test |
| Test passes | Wrong, unless it pins existing behaviour that must not regress. Label it as "guard (green at red)" in NN-TESTS.md |

Collection errors are worst, because they hide every other test in the file. Import modules that do not exist yet **inside** the test function or through a helper, not at module top level. Example:

```python
def test_report_totals_match(sample_orders):
    from myapp.reports import totals  # ImportError until the phase lands
    ...
```

## 5. Traceability: NN-TESTS.md

Use `templates/TESTS.md`, one row per criterion:

| Criterion (ROADMAP / CX) | Test ids | Red reason |
|---|---|---|
| Report totals match on 100% of sample orders | `test_reports.py::test_report_totals_match` | ImportError `myapp.reports` |

Every target in `prove.md` §5 (by goal id) and every retained exit criterion has ≥1 test id; Killed goals and deferred ROADMAP bullets are listed with their reasons and no locked tests; an exit criterion removed or changed by a DEC is listed with the reason, the DEC id and its destination. Every test id appears in at least one row.

## 6. Lock

Before locking, apply the vacuity check in `.claude/skills/phase-tests/references/checklist.md`: for each test, name the trivial implementation that would pass it and show that it fails.

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py testlock --phase NN --write \
    --fixture tests/fixtures/data --fixture tests/fixtures/golds   # every fixture path the tests read
python3 .claude/skills/process-phase/scripts/phase_tool.py check --testlock NN
```

`NN-TESTLOCK.json` has this shape:

```json
{"phase": "02", "created": "2026-10-01",
 "files": {"tests/acceptance/p02_reports/test_reports.py": "<sha256>",
           "tests/acceptance/p02_reports/p02_helpers.py": "<sha256>"},
 "fixtures": {"tests/fixtures/data/orders.json": "<sha256>",
              "tests/fixtures/replay/orders_summary.json": "<sha256>"}}
```

It covers every file in the phase's acceptance directory (data files too, caches excluded) and every declared fixture. A second `--write` refuses (`LOCK_EXISTS`). From now on, `check --testlock NN` (gate PG3) reports any change as rule `testlock`.

## 7. Gate and commit

- Show the user:
  - the NN-TESTS.md table;
  - the red summary line (for example "12 failed");
  - the classification from section 4.
- The user approves, or asks for changes. A change means edit, re-run red, and re-lock.

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py advance --to tests_approved
git add tests/acceptance/pNN_<slug>/ .planning/phases/NN-<slug>/{NN-TESTS.md,NN-TESTLOCK.json,NN-EVIDENCE/red.txt} .planning/STATE.md .planning/ROADMAP.md
git commit -m "test(NN): acceptance tests (red)"
```

## 8. Changing a locked test later

Only with all of:
1. a DEC entry: the test id, why it is wrong, and what replaces it;
2. the user's approval at a human gate;
3. `testlock --phase NN --write --relock --dec DEC-NNN`;
4. a commit `test(NN): re-lock acceptance tests (DEC-NNN)`.

Weakening an assertion so that the implementation passes is never a valid reason.
