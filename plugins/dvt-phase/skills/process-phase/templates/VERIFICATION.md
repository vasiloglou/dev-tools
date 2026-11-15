---
phase: "{{PHASE}}"
title: "{{TITLE}}"
status: passed              # passed | gaps_found | human_needed
verified_on: YYYY-MM-DD
verifier: current session or delegated verifier
---

# Phase {{PHASE}}: {{TITLE}} — Verification

Record existing results; do not rerun tests to write this document. Keep one
final full-suite log and enough focused red/green detail to explain the fixes.
The mechanical `phase_tool.py evidence-check` checks cited paths, not correctness.

## Commands and results

| Scope | Command / tested revision or diff | Result | Existing output |
|---|---|---|---|
| Focused fixes / acceptance | | | |
| One final full regression | | | `{{PHASE}}-EVIDENCE/runs/pytest.txt` |
| Remaining static checks | | | |

## Acceptance outcomes

| Outcome | Test/result | Status |
|---|---|---|

## Remaining failures and limitations

<!-- Exact failures/causes, any approved baseline disposition, or stale coverage after a fix. No separate evidence-review packet or speculative gap plan. -->

## Final status

<!-- Current required results justify verified, gaps_found or human_needed. A missing independent review/replay report is not itself a gap. -->
