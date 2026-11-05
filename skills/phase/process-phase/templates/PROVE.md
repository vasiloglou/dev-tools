# Phase {{PHASE}} — Goals, prototype and scope

## 1. Goals and targets
<!-- Each goal is measurable. Copy this table into CONTEXT "Goals and targets". Verdict comes from §3; a Pivot keeps the original target here and names the measured replacement target in the Verdict cell ("Pivot: <replacement target>"). -->

| Goal id | Goal | Metric | Asset | Target | How measured | Verdict |
|---|---|---|---|---|---|---|
| G1 | | | | | | Go / Pivot / Kill |

## 2. Baseline on the real asset
<!-- Identify the frozen real asset by an immutable revision, content hash or retained snapshot path, not a mutable path alone (for example `data/sample.db sha256:3f9c…`, or a git revision for code or doc assets), the existing tools used, and each goal's metric before any change, with evidence paths. Reuse an existing measurement on the same frozen asset when one exists. If no real asset exists, explain why and cite the user-approved DEC waiver. -->

## 3. Timeboxed prototype
<!-- Default timebox: 2 hours. Apply the core idea by hand or with a $0 script on the same asset; record the timebox, elapsed time, what was done, each goal's metric after the prototype and its evidence. Measure once: no before/after replay campaign, no review rounds. Verdict per goal: Go (target met), Pivot (original target, replacement target or approach, measured result and evidence, all within this timebox; an untried alternative goes to §6, no second prototype round), Kill (dropped). All three are valid. Spikes go here, with their LOCKED CX ids. -->

## 4. Validated oracle cases
<!-- Each counter, census rule or reference builder the tests will rely on, run once on a known-good and a known-bad real case from the prototype. Helpers cite these case ids in docstrings. -->

| Case id | Check | Real case (good/bad) | Expected | Actual | Evidence |
|---|---|---|---|---|---|

## 5. Smallest outcome contract
<!-- Only the targets that held (Go, or a Pivot whose measured replacement target held in §3) and the observable outcomes the prototype showed matter. Specify locks exactly these; NN-01 automates this prototype on the same asset and metric. -->

### Method record (required)
<!-- One row per goal with verdict Go or Pivot: exactly what the run that met the target used. Every cell is filled (write `none` where a column does not apply, as for a hand-run or $0 script with no model, turns or spend); "To fill" or an empty cell fails `phase_tool check --prove NN`, and the gate from tests_approved on cannot be waived by --override. A promoted step's plan, brief, budget and parity file are taken from its row. For a phase that inherits an earlier proof, copy the earlier row and name its evidence folder. -->

| Goal | Asset (hash) | Metric before → after; items lost | Inputs given (paths) | Tools allowed | Instruction file (path, sha256) | Model, effort | Turns | Wall | Spend | Evidence folder |
|---|---|---|---|---|---|---|---|---|---|---|
| G1 | | | | | | | | | | |

## 6. Deferrals
<!-- Every ROADMAP/CONTEXT item the evidence does not need, and every Killed goal: reason and destination (NN.1 or todo). No locked test in this phase. If an item removes or changes a ROADMAP exit criterion, name the user-approved DEC that amends the criterion in CONTEXT and ROADMAP; without it the criterion stays and Specify tests it. -->

| Deferred item | Reason | Destination |
|---|---|---|
