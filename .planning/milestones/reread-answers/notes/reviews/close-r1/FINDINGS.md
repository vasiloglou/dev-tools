# Findings ledger: close-r1

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
| F1 | A module named one by one in `modules:` that git does not track (an ignored `tools/gen.py`) moves from one component to another without an edit and `changed --strict` asks neither (skills/components/scripts/components_index.py:1264) | yes | blocking | deferred | -- | Reproduced 2026-11-26 in a project made by the test helpers: at 24003fd^ exit 1, `reread: core.aa (only modules edited): tools/gen.py` and the same for core.bb; at 24003fd exit 0, `0 to reread`. A regression of 24003fd, which takes the candidates from `git ls-files` only; the owner's "ask both" covered such a file before it. Classed as pr-51-r2 F1 was. Proposed repair: take the tracked files and the paths a `modules:` line names one by one, as 24003fd^ did. Deferred to the owner: a proposed issue (005-close.md) |
| F2 | A file name git does not spell as UTF-8 text breaks `changed`: the text-mode read of `git ls-files -z` (components_index.py:1056, :1254) | yes | hardening | deferred | -- | Reproduced 2026-11-26, the carriage-return case only: at 24003fd, a tracked `src/widget/a\rfile.py` under a catalogued folder, edited, makes plain `changed` exit 1 with `git cannot read src/widget/a` / `file.py at <base>` (the carriage return read as a line break). A carriage return in an unrelated name on a clean tree exits 0. The byte 0xff case could not be built here: macOS refuses the name (`Errno 92`). Fails closed. Deferred with F1, the same reader |
| F3 | A field line under an indented `## ` heading, or inside a multi-line HTML comment, answers the preceding entry (components_index.py:164, :248) | yes | hardening | deferred | -- | Reproduced 2026-11-26: `  ## Release checklist` then `- reread: confirm release notes` after the last entry, the module edited: `changed --strict` exit 0, `0 to reread`, at 24003fd and at 24003fd^ alike. Not a regression. Deferred to the owner: a proposed issue (005-close.md) |
| F4 | `changed` and `review` still disagree on a `reread:` line whose words did not change (a space added) and on U+0085 inside it (components_index.py:271, :1427) | no | hardening | deferred | -- | Not rerun here. The ordinary whitespace case is the disagreement 002-pr-51-r1.md records under "Not done", carried in the close's refactoring rows; U+0085 is the same two-roads gap. Deferred with that row |
| F5 | A Python file in another coding (Latin-1 with a coding line; UTF-8 with a BOM) stops plain `changed`: the base import graph decodes as UTF-8 (components_index.py:1204, :715) | no | hardening | deferred | -- | Not rerun here; the reviewer reports the Latin-1 case on 24003fd^ too, so not a regression. Deferred to the owner: a proposed issue (005-close.md) |
| F6 | A public name that is not ASCII (`def 計測()`) is never listed by part 4: the tokenizer returns no words for it (components_index.py:916, :1280) | no | hardening | deferred | -- | Not rerun here; the reviewer reports it on 24003fd^ too. Deferred to the owner: a proposed issue (005-close.md) |
| F7 | P5 says every finding has a test that fails without the repair; 003-rulings.md says round 1's F4 has none, being a sentence | yes | completeness | fixed | (the close commit) | Read in 003-rulings.md. P5 now names the exception |
| F8 | The close record claims an owner ruling bound to README bytes and is full of placeholders; the README still says the merge and the tag are next | yes | completeness | fixed | (the close commit) | The draft was read before its gates were filled, as intended. The ruling now quotes the owner's words and binds the review it was conditioned on; the README is brought up to date |
| F9 | "Every test ran on macOS and Linux" overstates: the Linux jobs skip four tests (three on GitHub) | yes | completeness | fixed | (the close commit) | 004-pr-51-r2.md: `587 passed, 4 skipped` on each Linux job. The residual now says so |
