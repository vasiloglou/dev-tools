# Step 1 — Discuss (reference)

Discuss turns a ROADMAP block into decisions that the tests and plans can rely on. It produces `NN-CONTEXT.md`, `NN-DISCUSSION-LOG.md` and `NN-EVIDENCE/prove.md`. No tests or plans; prototype scripts belong to the evidence gate (§5).

## 1. Find the gray areas

A gray area is a choice where:
- the ROADMAP block, the MANIFESTO and the normative docs do not decide it;
- two reasonable implementations would lead to different acceptance tests or different code structure.

Scout the code before asking. First list the capabilities the phase will need, as verbs and data, and run the `components` skill's Consult steps for each (`scripts/components_index.py search <verbs>`, the matching `docs/components/COMPONENTS.md` entries and `docs/components/external/`). Write the hits into `NN-CONTEXT.md` as a **Components in scope** table (capability, component id or external name, status, reuse / adapt / reject candidate) before any architecture decision. Start from the `subsystem.*` hits: their `flow:` is the call order the phase changes. For each component the phase will change, add its `used_by:` callers (full list in `docs/components/graph.md`) as the blast radius, so the Discuss gate sees what already exists in the project and in its dependencies. Then use Grep and Read on those modules and the ones listed in **Reuses**, or an Explore subagent, so every question comes with concrete options grounded in the current implementation. For example: "`<function>` in `src/<package>/<module>.py` already validates its input; keep that in the new backend?"

## 2. Ask in batches

- Use AskUserQuestion with 3–5 related questions per batch. Each question has 2–4 options, and your recommendation comes first, marked "(recommended)".
- Offer shortcuts: "accept all recommendations", "reject all", "decide individually".
- `--mode fast`: one batch for the whole phase. Anything left unanswered becomes a `DISCRETION` item with your stated default.
- If AskUserQuestion is unavailable (for example in another assistant), write the questions into `NN-DISCUSSION-LOG.md` as a review sheet and stop until the user answers.
- In an eval sandbox (`.planning/.eval-answers.yaml` exists), read answers from that file and append each question to `.planning/.eval-questions.log`.

## 3. Record decisions

Each answer becomes one row in the CX table of `NN-CONTEXT.md`:

| Tag | Meaning | Consequence downstream |
|---|---|---|
| `LOCKED` | Binding for this phase | Specify writes tests that encode it; plans must follow it |
| `DEFERRED` | Explicitly not decided now | Names the phase or the OQ id that will decide it; no test depends on it |
| `DISCRETION` | Implementer's choice within stated bounds | The SUMMARY records what was chosen and why |

Format: `| CX-03 | LOCKED | Record ids use the prefix r: (r:Customer) | Q2 in log |`.

A decision that contradicts a DEC entry, a manifesto thesis or the software contract is not a CX item. It is a proposed amendment: a DEC draft plus a human gate, and it may change the ROADMAP.

## 4. Scope guardrail

Scope follows the MVP direction.

- Discussion clarifies **how** the phase delivers its block. It never decides **whether** to add scope.
- A new capability the user mentions goes to the phase whose block owns it, or to `.planning/todos/NN-<topic>.md` with a one-line pointer in the CONTEXT under "Not in this phase".
- Persistent configuration changes (`.claude/settings.json`, hooks, CI) are separate CX items and need an explicit "yes" in chat.

## 5. Goals, prototype and scope gate

Phases are prototype-first: goals with measurable targets, a prototype on a real
asset, then straight to locked tests. When `NN-CONTEXT.md` has
`evidence_gate: required` (the template default), this gate is mandatory, not
reserved for a material unknown. Write `NN-EVIDENCE/prove.md` from
`templates/PROVE.md`; the user approves it together with CONTEXT, in the same
gate. Older phases without the marker are unaffected; `--override DEC-NNN` waives
the artifact check.

1. **Goals and targets.** Each goal names its metric, the frozen real asset, a
   numeric target and how it is measured. Copy the table into CONTEXT
   "Goals and targets".
2. **Baseline on the real asset.** Freeze the asset and identify it by an
   immutable revision, content hash or retained snapshot path, not a mutable
   path alone (a dataset's sha256; a git revision for code or doc assets).
   Measure each goal's metric with existing tools, or reuse an existing
   measurement on the same frozen asset. No real asset needs a user-approved
   DEC waiver (`advance --to tests_approved --override DEC-NNN`).
3. **Timeboxed prototype.** Apply the core idea by hand or with a $0 script on
   that asset (default timebox 2 hours) and measure the same metrics once.
   Record **Go**, **Pivot** or **Kill** per goal, with evidence; all three are
   valid. A Pivot records the original target, the replacement target or
   approach, its measured result and evidence, all within the same timebox;
   only a measured replacement that held is locked. An untried alternative is
   a deferral (item 6), not a second prototype round. A paid pipeline run is
   never the prototype: for a scale phase the prototype is the hand or
   $0 reproduction of the earlier method record on the scale asset or on its
   recorded result. Spikes whose verdict
   changes the tests fold in here; record their verdicts as LOCKED
   CX items.
4. **Validated oracle cases.** Run each check the tests will rely on (counters,
   census rules, reference builders) once on a known-good and a known-bad real
   case from the prototype, and record the expected and actual answers.
5. **Smallest outcome contract.** Only the targets that held and the outcomes
   the prototype showed matter. Specify locks exactly these. Fill the **method
   record**: one row per Go or Pivot goal with the asset hash, metric
   before and after, items lost, the inputs given, the tools allowed, the
   instruction file and its hash, the model and effort, turns, wall time, spend
   and the evidence folder. `phase_tool check --prove NN` checks it; plans,
   briefs, budgets and parity files are taken from these rows.
6. **Deferrals.** Everything in the ROADMAP block or CONTEXT the evidence does
   not need, and every Killed goal, with a reason and destination (`NN.1` or a
   todo); none of it gets a locked test in this phase. When a Killed goal or a
   deferral removes or changes a ROADMAP exit criterion, a user-approved DEC
   amends that criterion in CONTEXT and ROADMAP before Specify; Specify tests
   every retained exit criterion.

The prototype measures once. It is not a validation campaign: no before/after
full-model replays, no full-suite baseline run (Step 0 reuses an existing one),
no repeated or independent oracle reviews and no review rounds on `prove.md`
(validation policy, SKILL.md). Positive and negative controls become locked tests
and are reused during TDD. A product contract change remains a human decision;
ordinary corrective work does not reopen this gate.

## 6. Write the artifacts

`NN-CONTEXT.md` (from `templates/CONTEXT.md`) must contain:
- Concrete intent
- Expected outputs
- Goals and targets (from `prove.md` §1, with verdicts)
- Time budget (used for Implement scope checkpoints)
- Entry and exit criteria (copied from the ROADMAP, not paraphrased)
- The CX table
- Not in this phase
- Cross-phase dependencies
- Migration impact
- Data and eval impact
- Gates applicable
- Open questions

`NN-DISCUSSION-LOG.md` (from `templates/DISCUSSION-LOG.md`) records each question, the options, the answer, a verbatim quote of the user, and the resulting CX id.

## 7. Gate and commit

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py check --context .planning/phases/NN-<slug>/NN-CONTEXT.md
# human approves the CX table and NN-EVIDENCE/prove.md
python3 .claude/skills/process-phase/scripts/phase_tool.py advance --to context_approved
git add .planning/phases/NN-<slug>/NN-CONTEXT.md .planning/phases/NN-<slug>/NN-DISCUSSION-LOG.md .planning/phases/NN-<slug>/NN-EVIDENCE/prove.md .planning/STATE.md .planning/ROADMAP.md
git commit -m "docs(NN): capture phase context"
```

Exactly one commit leaves this step, and no PLAN or test files exist yet.
