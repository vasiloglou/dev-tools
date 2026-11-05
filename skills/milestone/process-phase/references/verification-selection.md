# Verification selection and inheritance

Use this reference when authoring a phase's verification contract and when
executing step 3. Its purpose is to make the repository health check
proportional to the phase without turning an old green result into evidence for
changed bytes.

Opt-in gates ([`architect-overrides.md`](architect-overrides.md)) are opt-in
here too. Do not add them as `run` or `cadence` merely because a source changed,
a phase or milestone ended, or an older plan prescribed a recurring run.
Only an explicit current owner request for a named subject and scope selects
one. Record the owner ruling as the amendment when an older plan clause would
otherwise mandate a run. This does not waive direct or affected-consumer tests;
earlier evidence continues to describe only its original bytes.

## Focused selection

Ordinary phase verification uses a reduced selection: the phase's direct tests
and focused downstream tests selected by changed behavior, under the project's
default test configuration, run with the project's test command
(`references/project.md`). For example:

```bash
pytest tests/<phase-tests>.py tests/<affected-consumer-tests>.py
```

Do not override the default test configuration to bring excluded lanes — broad
evidence, census, historical or other special lanes the project sets apart —
into an ordinary gate.
If a necessary changed contract has only an excluded historical test, select
a bounded current-behavior successor and record the old claim as unavailable
on changed bytes. Explicitly requested special-lane work retains its own scope.
The owner or a separately configured CI job must explicitly select a full
default run, a broad-lane run or an exhaustive historical replay. Source
changes, phase completion, milestone completion and old plan defaults do not
select those runs; this supersedes automatic broad-run clauses in older plans.

## Required selection ledger

Before the owner gate, the spec records one row per logical verification gate:

| Field | Required content |
|---|---|
| Obligation | The plan clause, phase criterion, changed contract, or downstream risk the gate discharges |
| Disposition | `run`, `inherit`, or `cadence` |
| Command or evidence | Exact command and expected exit for `run`; path, SHA-256, source identity, command, and result for `inherit`; named CI or milestone-close lane for `cadence` |
| Input boundary | Files, schemas, fixtures, configuration, toolchain, environment, and generated inputs whose change can affect the result |
| Justification | Why this gate and the other selected gates close the impact surface without an unlisted replay |
| Invalidation | The concrete changes that force reconsideration or execution of the gate |

An inherited or cadence row is not omitted work. It is an explicit statement of
what the phase is and is not claiming.

## Selection rules

1. **Run plan-mandated gates verbatim unless the owner amends them.** Record an
   explicit owner amendment at the original gate's site in the phase spec,
   marked as [`spec-note-contract.md`](spec-note-contract.md) requires of a
   change made in place after approval. If
   a mandated command is invalid, unavailable, or contradicts the phase,
   record a refuted premise and return to the owner gate. Do not silently
   substitute a narrower command.
2. **Run the phase's direct tests.** Every new or changed branch, refusal,
   serialization, public behavior, and regression finding needs a case capable
   of failing it.
3. **Close the impact surface.** Add focused tests for downstream consumers of
   changed production code, schemas, package data, build rules, shared helpers,
   fixtures, or generated artifacts. Test selection follows dependencies and
   contracts, not filename vintage.
4. **Record the selected gate, not an implicit full-suite replay.** On each
   edit, run the direct tests and affected consumers. A phase record's `gate`
   (or `gates`, when several were selected) names the exact selected command
   and its exit. Use the reduced
   selection above. A full default or broad-lane run requires
   explicit owner or separately configured CI selection. When impact cannot
   be bounded, report the missing assurance and the specific additional gate
   needed; do not automatically launch the broader lane. A phase that does not
   run the broad lane records `slow_cadence` with the command, trigger, and
   reason. If it runs the broad lane, it records `slow_gate` with its actual
   exit. Collection-only checks establish selection, never a run outcome.
5. **Review the claim before moving a test.** Runtime and age alone justify
   neither selection nor removal. Keep direct current-behavior checks in the
   ordinary lane. Reserve the broad lanes for exhaustive tracked-tree
   assertions, historical bytes, fixed-commit replays, and retained-output
   pins. A broad gate omitted from the phase must have a named `cadence`
   disposition, such as milestone close. If one of its tests covers an affected
   contract, include that relevant test in the phase's impact closure even
   when the remainder stays on its broader cadence. Delete or consolidate a
   redundant assertion only after identifying the surviving protective case.

## Exhaustive historical replays — explicit request only

An exhaustive historical replay is outside the reduced phase selection. Changes
to its inputs invalidate old evidence; they do not automatically select the
replay. Run focused current-behavior controls from the reduced selection and
state the limits of their current-byte claim.

When a replay is expressly selected, run the whole of it: a refused digest, a
missing or extra job, a malformed observation or a changed mismatch set fails
that explicitly selected claim; do not silently substitute a subset. The
reduced current-behavior gate is a different, narrower claim. Run the replay in
isolation and record worker count, elapsed time, case count, command count and
exit separately.

## Inheritance and invalidation

`inherit` is admissible only when durable evidence identifies the exact prior
command, result, source or artifact identity, and every input in the declared
boundary. Confirm that none of those inputs changed. Cite the evidence by path
and SHA-256.

Never describe inherited evidence as a verdict over changed bytes. When a phase
changes an input to a prior gate, either run that gate, replace it with a
justified current-commit impact closure, or give it a cadence disposition that
makes clear it is not part of phase acceptance.

At minimum, reconsider the selection ledger when the phase changes:

- global test configuration, markers, collection rules, plugins, or shared
  fixtures;
- dependency locks, build backends, package manifests, generated-file rules, or
  supported runtime/toolchain identities;
- a public schema, common loader, shared evaluator, CLI dispatch, or other
  surface with consumers beyond the named phase tests;
- an input, classifier, normalizer, expected-answer source, or environment used
  by inherited evidence.

If those effects cannot be bounded, state the missing assurance and name the
additional gate for explicit selection. A convenient focused set is not evidence
of bounded impact by itself; uncertainty does not authorize a broad replay.

## Parallel execution

Independent gates may run concurrently only when their state is isolated. Use
separate clean checkouts, containers, or CI jobs for tests that can share fixed
paths, caches, ports, mutable environment variables, or load-sensitive timing.
Do not introduce a parallel test runner as a semantic change merely to make a
health check faster.

Keep each gate's exact command, exit, output, duration, and evidence separate.
Dependencies remain serial: a consumer gate cannot begin before the artifact it
consumes exists. Parallel scheduling does not merge unlike claims.

## Phase record

Copy the final selection ledger into the completion record. For every `run`,
record the actual command and exit verbatim. For every `inherit`, record the
evidence digest and the unchanged-input check. For every `cadence`, name the
lane that retains the test and state why it is outside this phase's acceptance
claim.
