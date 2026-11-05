# Step 6 — Close (reference)

Close turns a verified phase into a completed one. It updates the bookkeeping, checks the manifesto for drift, and merges the phase branch back into `base_branch`. It needs `phase_status: verified`.

## 1. Bookkeeping through phase_tool

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py complete --phase NN
```

`complete` is the only way to reach `complete`. It:
- sets `**Status:** complete` on the phase in `ROADMAP.md`;
- adds `NN` to `completed_phases` in `STATE.md`, moves `current_phase` to the next phase with `phase_status: not_started` and `active_step: null`, and updates `last_activity`;
- marks the phase's REQ rows `Validated` in `REQUIREMENTS.md`.

Consequence: from now on the plain `pytest` run collects `tests/acceptance/pNN_*`. Phase NN's acceptance tests become part of the regression suite that every later phase must keep green.

Update the rest by hand, and show each change to the user:
- `DECISIONS.md`: append the DEC entries made during the phase, if not already there.
- `MIGRATION.md`: set the status for modules moved, shimmed or frozen.
- `RISKS.md`: record the spike verdicts, and the new status of each RK row this phase owned.
- `STATE.md` digest: add lessons `LS-NN`, one line each, phrased as a rule for the next phases.
- `docs/components/` (`components` skill, Update): every module the phase added is assigned to a component; duplicates found during the phase are marked `duplicate-of` with a consolidation todo; any capability the phase rebuilt by mistake gets a `retrieval-cases.toml` case. Subsystems whose flow the phase changed get their `flow:` and `components:` updated; a new end-to-end flow gets a `subsystem.*` entry. Regenerate with `scripts/components_index.py`, confirm `--check` is clean, and run the project's component check against the phase base (`references/project.md`): fix every major, and remove or justify each `new caller of` a deprecated or duplicate component.

## 1b. Reuse verification

Close does not rerun the full suite, replays or evidence reviews. Reuse current
verification results. If a bookkeeping row is absent, inspect only
the missing item and update the summary; do not restart PG1–PG3. An actual
product failure is reported as a gap and fixed with focused tests.

## 2. Manifesto drift check

Compare the realized shape with `.planning/MANIFESTO.md`:
- package list and layers;
- tools and skills;
- the theses;
- the final repo tree.

| Drift | Action |
|---|---|
| None | Note "no drift" in the close commit body |
| Wording or detail (PATCH) | Amend; bump `x.y.Z` |
| New tool, package or skill within the theses (MINOR) | Amend; bump `x.Y.0`; DEC entry |
| A thesis changes (MAJOR) | Amend; bump `X.0.0`; DEC entry; archive the old version in `.planning/archive/MANIFESTO-<version>.md` |

- Every amendment is a **human gate**.
- `manifesto_version` in STATE changes only as part of an approved amendment.

## 3. Commit

```bash
git add .planning/
git commit -m "docs(NN): complete phase — <one-line outcome>"
```

## 4. Merge back into base_branch

- Ask the user to approve merging `phase/NN-<slug>` into `base_branch` (STATE frontmatter). On yes: `git switch <base_branch> && git merge --no-ff phase/NN-<slug> -m "merge: phase NN <title>"`, then `phase_tool.py branch --set <base_branch>`. This is local; nothing is pushed.
- If the user prefers a PR, offer one from `phase/NN-<slug>` to `base_branch` with the summary, tests turned green, gates and evidence links. `git push` and `gh pr create` are deliberately **not** in the skill's `allowed-tools`, so they always prompt. Push only after the user says yes, for this push.

## 5. Release to main (separate gate)

A merge to `release_branch` (STATE frontmatter, normally `main`) is a release, not routine. It requires:
1. PG1 green on the exact merge commit;
2. the user's explicit "yes, release";
3. a release note listing any behaviour change that affects downstream consumers;
4. any release gate in `references/project.md`.

Never propose the release as part of routine closing. Mention it as an option at most.

## 6. Offer the next phase

Show `status` for the next phase and ask whether to start `/process-phase next`.

## Bootstrap exception

A phase that ran by hand before this skill was in place may have worked on `base_branch` directly. STATE then records `phase_branch` equal to `base_branch`, the one allowed exception to "never commit on base_branch".
- If its red run was not recorded (no `NN-EVIDENCE/red.txt`), `advance --to verified` reports the missing `red.txt`; the verifier states this in `NN-VERIFICATION.md` and waives exactly that artifact with `advance --to verified --override DEC-NNN`. The override cannot waive a dirty lock or a failing `evidence-check`.
- From the next phase on, every phase uses its own `phase/NN-<slug>` branch.
