# Review convergence — when repeated review stops paying

Repeated review rounds over one artifact are not monotone improvement: each
repair round can manufacture the next round's findings. `standing-rules.md`
records the repair-round hazard among its failure classes; this file is the
*quantified* version, and the stop rule it buys. A **seat** below is one
reviewer in the review instrument; a single reviewer is one seat.

## The stop rule

Track two numbers across repeated review rounds over one artifact, and compute
them — never estimate them:

- **the self-inflicted ratio** — findings attacking text the previous repair
  round created, over total findings;
- **the same-seat trend** — one seat's finding count, round over round.

**Stop when the self-inflicted ratio exceeds one half, or when same-seat counts
are flat-to-rising for two consecutive rounds while severity falls.** At that
point the review is measuring the repair process, not the artifact: each repair
round is manufacturing the next round's findings. The next instrument is code,
not another round.

A falling severity ceiling over flat-or-rising counts is the *signature* of the
stop condition, not a reason to continue. It means the design has stopped yielding and the prose has
not — and prose defects that only reading finds slowly are exactly the ones
implementation finds immediately.

A repeated review loop is a bounded search like any other and deserves the same
discipline: **declare the round budget and the stagnation criterion before
round two, in the artifact's own bytes.** A stop condition adopted after seeing
a round's results is the review-side twin of a ceiling changed after seeing a
measurement.

## Specify decisions, discover facts

A spec exists to pin **decisions** — an order, a schema, an exit band, a
boundary someone must own. **Facts about the runtime are not decisions**: what
an OS call does to an open file descriptor, which process group a signal
reaches, which exception a library raises, what an argument parser exits.
Reading is a bad instrument for facts: each is answerable by one test in
seconds, and neither assertion nor refutation settles it until one runs.

- When a review finding turns on a runtime fact, its discharge is a **test
  row**, never more prose. Do not adjudicate a fact by argument.
- Prefer stating the *required outcome* and letting the test list carry the
  mechanism; a spec sentence asserting a runtime mechanism is a liability
  whichever way the fact turns out.

This is where "how specific should the spec be" bottoms out: **the spec stops
where the runtime starts answering.**

## Every restatement is a staleness site

Disposition tables, decision rows, and review records restate rules in order to
discuss them, and each restatement can go stale when the rule moves — a rule
changed in its home, copies left behind. The one-home rule (each normative
statement has exactly one home; everything else cites it) applies to review
scaffolding with full force:

- discussion **cites by anchor**, never by copy;
- when a rule is retired, its exact wording is grepped over the artifact before
  the revision ships;
- a checker built for this must **assert, not print** — see the instrument rule
  below.

## A review that cannot come back empty measures nothing

An adversarial reviewer asked to find defects will find defects; at the margin
the review *generates* findings rather than detecting them. Consequences:

- a raw finding count is not a quality metric — only its trend, its severity,
  and the self-inflicted ratio are;
- reproduce-before-believe (`review-and-record.md`) is not optional at any
  round;
- a finding that names no observable consequence is style, and is triaged as
  style.

## Implementability is a gate precondition, not a review discovery

Before the owner gate is offered, walk the requirements once asking one
question: **can SOME implementation satisfy this as written?** A guard that
must red on content the same spec mandates, an injection that physically cannot
fire, a recomputation whose inputs the artifact does not carry — each takes
minutes to check, and each invalidates an approval retroactively when found
later, at a cost greater than the sweep.

## The instrument gets the artifact's treatment

Any checker, corpus, or harness a phase builds to verify itself is believed
**only after a negative control**: feed it a known-dirty artifact and watch it
red. A checker that reports clean without asserting launders an
unverified claim into a mechanical-sounding one — strictly worse than no
checker, because prose invites doubt and tool output does not.

## Prefer the executable instrument when bytes are in scope

When a phase's deliverables include a **serialized format, an exit-code
contract, or a validation predicate**, the approval instrument defaults to
corpus-first — golden bytes and expected exits authored, approved, and committed
RED before code — and choosing spec prose instead requires stating why. Writing
the expected bytes forces every value prose can leave vague: a version field's
value, a null's representation, an encoder's failure mode, a first index.

This does not repeal the owner-gate rule that the instrument is asked, never
inherited; it sets the default answer for these three phase shapes.

## Relevance is not severity — triage every finding before fixing any

**The standing priority: work that moves the product toward a demonstrable MVP
outranks work that increases completeness.** A defect that stops the software
from doing what it claims is not the same kind of thing as a defect that makes
the artifact more complete, and reviewers do not distinguish them — a
reviewer's severity rating (`low|medium|high|critical` or the instrument's
equivalent) rates *how bad the flaw is*, never *whether fixing it proves
anything works*.

Every finding is assigned one of three classes at disposition time, by whoever
dispositions it, not by the reviewer:

| Class | Test | Default handling |
|---|---|---|
| **blocking** | unfixed, the software does not demonstrably do what it claims — it crashes, computes a wrong answer, silently accepts bad input, or the claim cannot be run at all | fixed in-phase |
| **hardening** | a real defect with a real consequence, but the demonstration still stands: an unexercised branch, a reader untotal over bytes nobody sends yet, a race under conditions not yet reached | fixed in-phase **only** when this phase's own deliverable is the thing it hardens; otherwise an open-questions row with a named target |
| **completeness** | the artifact becomes more complete or more consistent, and no user-observable behaviour changes: wording normalized, a table restated, a census recounted, a boundary rephrased in the contract's exact words | **deferred by default**, batched to milestone close; fixing one in-phase costs a sentence saying why it could not wait |

Three consequences:

- **A round whose findings are majority completeness has hit the stop rule from
  the other side.** The artifact stopped yielding defects that matter and the
  reviewers kept finding text to improve. That is not a signal to repair and
  re-round; it is the same "next instrument is code" verdict the trend rule
  reaches by a different route.
- **Severity does not substitute for this.** A `critical` naming a doc
  inconsistency and a `critical` meaning the command exits 0 on invalid input
  arrive identically. Sort by class first, severity second.
- **The structural pressure runs the wrong way.** A reviewer who
  found nothing blocking and does not wish to approve must produce *something*,
  and completeness findings are the cheapest thing to produce. Expect the class
  to be over-represented, and triage before counting.

The same triage governs work the reviewers never touched. **A phase ships when
its deliverable is demonstrably working, not when every artifact around it is
internally consistent.** Completeness work is real work and it is not free; it
competes with the next thing that would prove the system does something it
could not do before, and it loses that competition by default.

## The convergence ledger

When a second round over one artifact is contemplated, add this table to the
artifact's review disposition and keep it current — the stop rule is computed
from it, and a round that cannot fill its row has not measured convergence and
does not get to claim it:

| Round | Seats | Per-seat counts | Self-inflicted / total | **Blocking / total** | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|

**`Blocking / total` is the column that decides whether the round paid.**
A round returning many findings and no blocking ones measured the prose,
not the product.
