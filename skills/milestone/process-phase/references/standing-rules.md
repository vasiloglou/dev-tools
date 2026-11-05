# The rules that bind every phase

Two lists. The first is the plan's section 0 together with the project's
standing design rules in `references/project.md` — design rules earlier phases
**already paid for with reproduced defects**, which bind every remaining phase.
The second is the failure classes a phase can re-commit — the plan's section 6
risk register plus the protocol's own classes below — so each is a thing to
check for rather than a thing to hope about.

A spec discharges every standing rule **by name** — naming the specific
function, the specific layer, the specific document the rule constrains in this
phase — or argues it inapplicable in one sentence. Silence on a rule is a
review finding.

## The format of a standing rule

The project owns its rules; this file ships none of them. Each rule, wherever
it lives, carries three things:

- **A name** — a short statement a spec can cite verbatim.
- **The failure class it prevents** — the general defect, in one clause, so a
  reader can tell whether this phase's work can commit it.
- **How a spec discharges it by name** — what the spec must name (the function,
  layer, boundary or document) and the test or evidence that shows the rule
  holds there.

A rule enters the list when a reproduced defect has paid for it, and it binds
every remaining phase from then on.

## Two illustrative rules

These show the format. They bind a phase only when the plan's section 0 or
`references/project.md` adopts them.

### Totality belongs to the function, not the caller

- **Prevents:** a consumer that crashes or reports a wrong verdict on input its
  current callers happen never to send.
- **Discharged by:** naming each new consumer of untrusted input this phase
  adds, with a hostile-input test over that function.

### Normative prose has exactly one home

- **Prevents:** one rule stated in two documents that drift apart, so a
  divergence reads as an ambiguity rather than a bug.
- **Discharged by:** naming the one home of each normative statement the phase
  adds; everything else cites it. When a phase's work makes two homes disagree,
  one of them yields in that phase, and the spec names which.

## The failure classes a phase can re-commit

### A declared branch with no case that can fail it

**The defining defect.**

- Walk the **branch table**, not the code.
- A test asserting that a string appears in a source file cannot fail when the
  behaviour is wrong. It is not a case.
- A guard that returns silently when its control invocation raises counts a
  broken control as a success.
- An exemption consulted only on a path that never names it is dead code
  reporting green.

### A class credited when only one half of it has a case

Count coverage **per branch**, not per class. A finding class whose second half
is unreachable with the chosen fixtures is half-covered — and reachability is a
property of the fixture, so closing the gap can mean editing the **fixtures**,
not adding cases.

### The repair round is itself a hazard

A repair pass over a reviewed artifact introduces defects of its own. Any
repair pass re-checks the neighbours of every edit, and repaired bytes carry no
review opinion until they are re-reviewed.

### A single reviewer mistaken for a multi-reviewer bar

Records say "one reviewer is one reviewer." The project's plan-review bar
(`references/project.md`; default: one independent reviewer in a different
tool) remains the bar for plan review and milestone close.
