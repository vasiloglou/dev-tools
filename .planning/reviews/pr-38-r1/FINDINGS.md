# Findings ledger: pr-38-r1

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

No findings.

Convergence: 0 findings, `VERDICT: APPROVE`, at head `17e63c6`. The reviewer ran the
writer and the `takeover` reader in memory over 121 injection cases and 44 repeated-write
cases, compared 290 control-free outputs with the base implementation, and ran `test_t22`
at the head and against the base. It did not run the full pytest suite or a real cloned
checkout, by the read-only rule.

It added one remark that is not a finding: `test_t22` listed 8 line breaks and left out a
lone CR, U+001D and U+001E, which Python also splits at; its own probes showed the fix
handles all three. Checked: Python's `splitlines` breaks at 10 characters, and the
pull request said "the 8 line breaks Python splits lines at". The test now takes the
list from Python and adds CR LF, 11 cases, at `acceaab`; all 11 fail on `main`'s
`handoff.py` and pass with the fix. `tests/test_handoff.py` at `acceaab` is unreviewed.
