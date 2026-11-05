# The phase spec note

**What step 1 produces**, at `notes/phase-N-spec.md`. This is the artifact the
owner gates on and the reviewers read; it is also the design record the phase
record later cites. Written to be *scannable* — a reader looking for the exact
signature of one function should find it without reading prose.

## Required sections, in order

### 1. Status line

One line, stating exactly where the spec is: `awaiting owner review`,
`owner-decided (<date>)`, or `implementable once <the named thing> is signed
off`. A spec whose status a reader must infer is one an agent can start coding
against by accident.

### 2. Provenance

Where this spec derives from, by name and by revision — which plan section, which
prior phase records, which review rounds have run over which bytes. If a review
ran, state the reviewed digest and say plainly whether the current bytes are that
artifact. **Repaired bytes carry no review opinion of their own** and the spec
says so rather than implying the review covered them.

Mark applied changes at their site with a short tag (`(r1)` for a first review
round, `(o)` for an owner decision, and so on) so a later reader can tell a
reviewed sentence from an unreviewed one.

### 3. Obligations — the step 0 harvest

The table produced at step 0, inline. Every row from every source that assigns
this phase an obligation: the criteria, the residual, the section 9 row, the
ledger rows, the pin sites, the register classes, the inherited boundaries.

Each row names **where it is discharged in this spec**. A row with no discharge
column is an open item, not a completed harvest.

### 4. The standing rules, bound to this phase

Each of the plan's section 0 rules and the project's standing design rules
(`references/project.md`), bound to this phase's work **by name** — the
specific function, layer or document the rule constrains here, and the test
that shows it — or argued inapplicable in one sentence. See
[`standing-rules.md`](standing-rules.md).

### 5. Goal

One paragraph, in the vocabulary of the gate that will judge it. Exit codes and
bands, never adjectives: "exits 0", not "passes".

### 6. Design

Module by module. For each: the path, an honest line estimate, and the **exact**
surface — function signatures with keyword-only markers where they matter, schema
fragments as literal JSON, enum members spelled the way the schema spells them.

> A spelling that differs between the schema and the implementation is a
> *silent* defect, not a loud one: it presents as a legitimate failure verdict on
> input that satisfies the rule. Write both spellings in the spec so the
> divergence is visible on the page.

Where the phase adds semantics, state the **normative order** and state which
document is its one home. Two homes disagreeing is a defect, not an ambiguity —
if the phase's work makes a second home diverge, one of them yields in this
phase and the spec names which.

### 7. Decisions

A numbered table (D1, D2, …) of everything the owner must rule on: the ledger
rows harvested at step 0, plus any question the design surfaced. Each row:
the question, the readings that disagree, and **what each reading costs** — most
usefully, whether they differ on the *exit code* rather than only on wording.

At first write every row is open. After step 2 each carries a ruling with an
owner mark and a date. A decision whose justification later proves wrong is
**re-argued on its real cost**, not quietly kept because the conclusion was
convenient.

### 8. Tests

The list, each entry naming the file, the case, and the **expected exit**. Every
criterion harvested at step 0 maps to at least one entry; every entry maps back.

Two rules the list is checked against before the spec is submitted:

- **Every declared branch has a case that can fail it.** Walk the branch table,
  not the code. This is the protocol's defining defect class.
- **Coverage is counted per branch, not per class.** A class whose second half
  is unreachable with the chosen fixtures is half-covered — and reachability
  is a property of the fixture, so closing it may mean editing the fixtures
  themselves.

### 9. Out of scope for this phase

Short, explicit, and separate from the plan's milestone-wide section 7. This is
what a reviewer must not ask for, and what the record's boundary section will
later repeat.

### 10. Size

The honest figure — source lines and test lines, as an estimate at write time and
as a measurement at record time. A phase that lands at three times its estimate
is a finding about the estimate, recorded rather than smoothed over.

### 11. Approval instrument

Which instrument the owner gates on: this prose, or a fixture corpus authored
first. If a corpus, this section names its path, its entry-point README, and the
fact that the answer key is **split out** from the entry point — otherwise no
later independence pass is possible, because the blind reader can see the
answers.

## Sections that appear once the phase is running

These are appended during step 3. The spec is otherwise treated as append-only
after approval — a reviewed sentence is not rewritten in place.

### Implementation findings, recorded as they were found

Lane by lane, including the findings that refute this spec. A finding discovered
and then quietly designed around is indistinguishable from one never found.

### An experiment, recorded before it runs

Any measurement the phase performs — a scaling sweep, an independence pass, a
false-pass approximation — is designed and written down **before** it runs:
what it measures, what it cannot measure, where it is graded, its liveness
proofs (an instrument that cannot score both ends is vacuous), and its stated
limits.

Recording the limits afterwards is how a good number gets read as more than it
is. Recording them first is what lets a good number be reported honestly.

> A ceiling changed *after* seeing a measurement is exactly when a reader should
> be suspicious. If it must change, the arithmetic goes in the record rather than
> the change going in quietly — and the new ceiling is described as what it is,
> usually a calibrated assumption rather than a consequence of a general law.
