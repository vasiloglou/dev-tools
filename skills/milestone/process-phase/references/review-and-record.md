# Review, refactoring review, and the record

Steps 4, 5 and 6 of the protocol.

## Step 4 — Adversarial review of the diff

### Invocation

Use the project's review instrument (`references/project.md`) where it defines
one for a phase diff. Where none is defined: one reviewer in a different tool,
at high reasoning effort, reading the diff with the repository read-only,
prompt on **stdin** rather than argv:

```
codex exec --ephemeral --model <model> \
    --config model_reasoning_effort="xhigh" --sandbox read-only \
    --color never --skip-git-repo-check -  < review-prompt-pN.txt
```

Prompt on stdin is not a style preference: argv exposes reviewed-artifact bytes
to shell quoting, argument-length limits and the process list.

### What the prompt carries

The diff's boundaries (the commit the phase began from), the spec, the criteria
the phase claims to have met, and an explicit instruction to try to **refute**
them. A prompt that asks "review this" gets a summary; a prompt that asks "find
where this claim is false" gets findings.

### The rules that make a review evidence

- **Reproduce before believing.** Every finding is reproduced against the code
  before it is accepted as one. A reviewer's plausible reading is not a defect.
- **Every fix carries a regression test proven to fail pre-fix.** Not "a test
  covering the area" — the specific test, run against the pre-fix code, observed
  red. Without that step a fix has no evidence it fixed anything.
- **Retain the findings verbatim**, in `notes/phase-N-<reviewer>-review.md`.
- **State that one reviewer is one reviewer.** The record says so in its boundary
  section. A single-reviewer read mistaken for a multi-reviewer bar is a named
  register risk.
- **State what the reviewer could not do.** Under a read-only sandbox a reviewer
  typically cannot run the suite, so its verification of the tests is by reading.
  A review record that omits this overstates its own coverage.

### Retained evidence has a trap

Reviewer output routinely contains absolute paths from the machine it ran on.
Committing it verbatim writes the operator's home directory into the milestone's
evidence. Sanitize to a
placeholder, and **say in the file's own header that it was edited** — retained-
verbatim evidence that was modified must declare the modification.

### Record what the review confirmed, not only what it found

A review record that lists only faults says nothing about coverage. List the
claims the reviewer checked and found true. Then do the thing a review cannot do
for you:

> **Audit your own coverage against the declared branch table, not against the
> code.** A reviewer reads what is there; only the branch table shows what is
> missing, so a declared class with no case that could fail it survives an
> adversarial review that did not flag it.

### Findings about your reasoning stand as written

Some findings are about an argument rather than a defect — a gate that cannot
fail, a claim whose premise does not support it. Those are recorded and corrected
**in place**, at their original site, not softened. An overreaching argument that
gets quietly narrowed later reads to a future reader as though it was always
careful.

## Step 5 — The refactoring review

One question, asked explicitly and answered in the record:

**What did this phase's work reveal about existing structure that should change?**

Exactly two honest answers:

1. **Refactors EXECUTED** — each named, each behavior-preserving, each landed
   behind the same green gates as the phase's own work. Good candidates:
   - the same question answered in two places at two moments (authoring time and
     evaluation time), which is how the two answers drift
   - a re-implemented primitive, usually found by a duplicate detector rather
     than by review, that re-derives a canonical form with no guarantee its
     arguments stay in step with the original
   - a third copy of a report line about to be added by this phase
   - a document that claims to be generated and is hand-maintained
2. **"None needed"**, argued from what the phase actually touched. An asserted
   negative fails record review the same way an unfalsifiable gate does.

A refactor **seen but deferred** becomes an open-questions row with a named
target milestone and the reason it is blocked. Never silent debt. A criterion
that forbids touching a module is itself deciding a module-ownership question,
and if that ownership deserves a public home, the honest move is a named future
refactor rather than a private import.

## Step 6 — The record

### Base contract

The record follows the milestone-record contract in
[`milestone-record-format.md`](milestone-record-format.md) — append-only
directory, `NNN-<scope>.md`, claim in the gate's vocabulary, verbatim gate output,
mandatory boundary section, open questions, refuted premises, digests computed
from bytes on disk with `shasum -a 256`.

### The phase extensions

A phase of a milestone plan is repository development, **not** a run of one of
the project's own workflow skills, and the record says so rather than leaving
the field blank:

```yaml
---
milestone: <milestone>
station: "phase-N"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-N
date: <YYYY-MM-DD>
gate:
  command: "pytest tests/<selected-test-file>.py"
  exit: 0
  output: "<verbatim test summary line>"
  note: >-
    The selected direct and downstream controls. Several selected gates: use
    `gates`, one entry per gate with its own exit (base contract).
slow_cadence:
  command: "<the project's broad-lane command>"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the unchanged broad controls are outside this phase's impact closure"
evidence:
  - path: <every file the claim rests on>
    sha256: <64 hex>
---
```

Every phase record carries `gate` and exactly one of `slow_gate` or
`slow_cadence`. `gate` records the focused command actually executed, with
its exit and a verbatim output summary; a verification selection with several
gates takes the base contract's `gates` list instead. Use `slow_gate` with the exact command,
exit, and a verbatim output summary when the broad lane ran; use `slow_cadence`
with a concrete trigger and reason
when it did not. A collection-only check never counts as a `slow_gate` result.
The full default lane and broad historical lane run only on explicit owner or
separately configured CI selection under the verification-selection reference.
Ordinary phase and milestone work uses the reduced selection; changed
behavior receives focused current-behavior controls. Any further record fields
the project defines are in `references/project.md`.

> **A known red is proven, not asserted.** If the suite exits non-zero for a
> reason that predates the phase, verify it in a throwaway worktree at the commit
> the phase began from and say that you verified it there. "This was already
> failing" is a claim like any other. The proof is owed when the red is first
> met -- normally step 3, before the phase builds on it -- not when the record
> is written.

Body sections, beyond the base contract:

- **What shipped** — module by module, with the design decisions that survived.
- **Gate output (verbatim)** — the exact commands and their exact output,
  including the project's lint command where `references/project.md` names one.
- **Any criterion that was measured** — with the measurement, the threshold, and,
  if the threshold moved, the arithmetic that moved it.
- **`Refactoring review`** — step 5's output, executed and deferred halves both.
- **Boundary — what this phase does NOT establish** — mandatory, plural. Every
  soundness limit, every unmeasured rate, every question a green gate does not
  answer. Copy the spec's own limits language rather than inventing softer
  wording.
- **Open questions** — including anything this phase inherited and did not close,
  and anything it discovered and deferred with a named target.
- **Refuted premises** — only when the phase killed a belief the work rested on,
  each citing the evidence that killed it. A plan sentence proven false is a
  refuted premise plus an open-questions row naming the repair; the plan is
  repaired at milestone close, not mid-phase.

### Discharging an owed obligation later

A record is append-only, but an obligation it declared owed can be discharged by
a later record. Annotate the original clause in place with the date and the
discharging record's path, and leave the boundary itself standing — a discharged
obligation does not retroactively widen what the phase established.

### The commit

The record contract's grammar with the phase scope token that contract defines
([`milestone-record-format.md`](milestone-record-format.md), Scope tokens):
`feat(phase-N): ...`, and `test(...)`,
`fix(...)`, `docs(...)` for the same phase as the work warrants — a phase is
normally several commits, each naming what it turned green.

- Subject imperative, <= 65 chars, no trailing period
- Body: what the gate established with exits verbatim, what it did NOT establish,
  and the record path on its own closing line
- `--` rather than em-dashes
- **No backticks anywhere in the message** — shells perform command substitution
  on them, which garbles the message
- Stage by explicit path. Never `git add -A`, never `git add .`
