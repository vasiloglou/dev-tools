# Findings ledger: pr-48-r1

One row per finding the review returned, under the reviewer's own id. Fill every cell:

- Reproduced: yes or no. A finding is believed only once it is reproduced against the bytes.
- Class: blocking, hardening or completeness, assigned here, not by the reviewer
  (review-convergence.md).
- Disposition: fixed, deferred, rejected or open.
- Repaired at: for a fixed finding, the commit or tag that holds the repaired bytes. Those
  bytes are unreviewed until a later round reads them; `review_tool.py status` says which.
- Notes: the regression test for a fixed finding, the target for a deferred one, the reason
  for a rejected one.

If the review returned no findings, replace the table with the line: No findings.

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| C9 | The description's Compatibility section says that with default settings every line and exit is as before except three named changes; issue 33's change is not among them, though it changes `rules_check.py test`'s output and exit with default settings where the phase tool is absent | yes | completeness | fixed | PR 48 description, edited 2026-11-24 | Reproduced 2026-11-24 with the `dvt-milestone` plugin from `git archive` of the base (cecebc6) and of the head (f77923a), each in a fresh project after `components_index.py init` and `rules_check.py init`, default settings except `gnd_command`: the base printed two `wrong:` lines for `plan_names_the_components_it_touches` and `6 rule(s), 12 example(s); 2 wrong`, exit 1; the head printed one `skip:` line and `5 rule(s), 10 example(s); 0 wrong; 1 rule(s) about plans skipped`, exit 0. The change is intended and is stated in the description's own bullet for 33; only the Compatibility list omits it. The repair is to the PR description, not the code. Fixed on the owner's approval: the Compatibility list now names this change, with the before and after above. No code or file in the repository changed, so the reviewed head (f77923a) is unchanged and there is no regression test |
