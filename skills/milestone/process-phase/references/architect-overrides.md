# Opt-in gates and architect override

An **opt-in gate** is an assurance run a project defines beyond a phase's own
verification -- a repeat of an expensive proof, audit or acceptance matrix
(`references/project.md` names any). Opt-in gates are not automatic phase or
milestone gates. Run one only when the owner explicitly requests it for a
particular subject and scope. A changed source, completed phase, milestone
close, or historical plan clause is not such a request. Do not ask for a waiver
each time: absent the explicit request, there is no prerequisite to waive.
Focused tests, owner gates, and other applicable completion criteria remain in
force.

Earlier evidence stays bound to its original bytes. If changed bytes cause a
tool to withhold assurance, report that state; do not call the older result
current or bypass the tool. Record a decision to omit a formerly planned run in
the phase or close record with the source and claim boundaries stated.

The rest of this reference applies only when a currently requested,
scope-specific opt-in gate is later explicitly overridden.

## Authority and effect

The repository architect may explicitly override the prerequisite such a
request created. The project identifies who holds that role. An applicable
architect override makes the prerequisite **satisfied for process
sequencing**: stop requesting that run and continue with the next
otherwise-authorized phase step.

The architect accepts the residual risk carried by the changed bytes. The
override is a governance decision, not a new technical proof. Keep the earlier
evidence bound to the bytes it actually covered; do not call it current,
regenerated, or broadened. Downstream records cite the earlier evidence and
the override separately.

## Valid override instrument

An override is valid when the architect explicitly uses `override` or `waive`
and identifies the run being skipped with enough context to avoid confusing it
with another gate. Record, before continuing:

- architect role and identity as the project defines them;
- exact architect wording and date;
- earlier evidence or completed phase being relied upon;
- known changed files or change class that triggered the request;
- boundary: the run was skipped by architect decision and the prior
  evidence still speaks only for its original bytes.

No new review, proof run, impact analysis, or repeated confirmation is required
unless the architect's override asks for one. Existing read-only facts already
known may be recorded, but they are not preconditions that can silently defeat
the override.

## Scope and lifecycle

Never infer an override of an explicitly requested run from `approved`,
`continue`, cost concerns, or a request to clean up an attempted run. It is
instance-specific unless the architect explicitly names a broader class. A
later source change outside its scope does not create an automatic
prerequisite under the default policy; the owner may request a new run. The
architect may withdraw an override explicitly, restoring only the specific
prerequisite that override had set aside.
