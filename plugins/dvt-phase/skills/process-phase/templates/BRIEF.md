# Brief {{TASK}}

- **Spec rule:** <rule from the phase's normative doc>
- **Method record row:** <prove.md §5 goal id, quoted>; proven inputs or tools dropped here, each with a reason: <none | list>
- **Red test:** <path::test> (the only failing test this task turns green)
- **File allowlist:** <paths>; **line budget:** <N added lines>
- **Budget:** <turns / wall / spend, from the row; same-asset or scaled with formula>
- **Forbidden:** new flags, config keys or environment variables; fallbacks and broad try/except; new helper modules;
  edits to other tests; refactors; anything outside the allowlist.
- **Report:** the red and green output of the test and `scripts/codex_gate.py` output.
