# Delegating to agents inside a phase

A phase involves a lot of mechanical reading across a large plan, several prior
records, and a live codebase. That is what parallel readers are good at, and it
is exactly where a single sequential pass silently skips a row.

## The one rule

**Agents gather and cross-check. They never decide, and nothing they return is
believed until it is reproduced.**

This is the same rule the adversarial review runs under, for the same reason: a
confident, plausible, wrong finding costs more than no finding at all, because it
arrives pre-argued. Every delegated result is checked against the bytes before it
enters the spec.

Three corollaries:

- **A summary is not evidence.** Every returned row carries a citation —
  `path:line`, a digest, or a quoted sentence. A row that cannot be located is
  dropped, not softened.
- **Say what was not covered.** If an agent bounded its search — top-N, one
  directory, first match — the bound is recorded. A silent cap reads as "covered
  everything" when it did not.
- **Delegation happens on the owner's go-ahead**, like every other step in this
  protocol. Fanning out is a real cost and the owner decides whether to spend it.
  The go-ahead is asked once, when the phase is invoked and before step 0
  begins, unless the request already carries it; `auto=true` delegates approval
  rulings, not this spend. Without a go-ahead — none given, or none answered —
  the default is one reader working through the same sources sequentially; a
  missing go-ahead never blocks step 0.

## Step 0 — harvest: the natural fan-out

The obligations table is assembled from sources that do not overlap, so one
reader per source is both the fastest and the most complete arrangement. Each
returns **rows with citations**, never prose.

| Reader | Reads | Returns |
|---|---|---|
| criteria | the phase's own plan section | every deliverable and every criterion, verbatim, one row each |
| verification | the plan's verification-story row for this phase | the row quoted, split into its separate clauses |
| ledger | the open-questions ledger | every row whose owner column names this phase, with its full text |
| standing rules | the plan's design-rules section | each rule, plus a first guess at what in this phase it binds -- a guess, marked as one |
| pins | the skill-surface table and the named pin-site test files | every pin site, with the current literal it holds and the line it holds it on |
| inheritance | every prior phase record in the milestone | boundaries still standing, open questions still open, obligations recorded as owed |

Run them together; they share no state and their outputs concatenate. Then
**reconcile**: a row two readers both found should agree, and where they disagree
the disagreement is the interesting part.

## What else is worth delegating

**Anchor verification (before the spec is submitted).** Every path, symbol,
function and test file the spec names is checked to exist at the base commit. A
spec that names a function that was renamed two phases ago produces an
implementation that invents it.

**Prior-art location.** "Where does this repository already do this?" — the
answer changes the design, and it is a search, not a judgement.

**A duplicate-primitive scan.** Before the refactoring review, ask what this
phase's new code re-implements. A helper re-derived at a second site is the
kind of duplication review tends to miss.

**A coverage audit against the branch table.** Give an agent the declared branch
table and the test list and ask which branches have no case that can fail them.
This is a mechanical cross-product, and it is the protocol's defining defect
class — worth a dedicated pass rather than a glance.

**A mutation sweep.** For each accepting fixture, does a one-token sibling exist
that is *not* accepted? Generating the candidate mutations is delegable;
confirming each sibling's actual exit is a run, not an opinion.

## What must not be delegated

- **Any owner decision.** The decisions table is ruled on by the owner at the
  gate. An agent may lay out the readings and what each costs; it may not pick.
- **The spec's design.** Signatures, normative order, and the finding table are
  authored, not collected.
- **The claim in the record.** A claim is made by whoever can defend it.

## The adversarial review is not a subagent

Step 4's reviewer runs in a **different harness**, with its own model, reading
the diff rather than the conversation that produced it.

A subagent of the same model, carrying the same context, is a second chance to
make the same mistake — the identical reason a document written alongside its
own implementation is not independent evidence. The independence is the
instrument; without it the review is a self-check wearing a reviewer's name.

## An independence pass, when a phase runs one

A blind pass measures whether the **shipped documents alone** determine the
behaviour, so the bundle the agent receives is the load-bearing design decision:

- It carries the normative documents and enough data to author cases.
- It carries **no implementation, no fixture case, and no expected result.**
  This is why a fixture corpus keeps its answer key in a separate file from its
  entry-point README — a corpus that explains itself in one file cannot be read
  blind afterwards.
- It runs where the agent cannot reach the repository. A read-only sandbox in the
  same checkout is not blindness.
- The grader is written and its **liveness is proven both ways before the real
  run**: a do-nothing agent must score zero and an oracle must score full. A
  grader that cannot score both ends is vacuous, and a vacuous grader returning a
  perfect score is the trap this instrument has.

**What the result means, stated before the run:** agreement is a disagreement
*locator*. An agreeing reader and an agreeing implementation can be wrong
together, and nothing in the pass separates that case. It is a probe, not a rate.
