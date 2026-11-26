# Milestone: reread-answers

A `reread:` line from the component index's `changed` is answered in the entry, `changed`
and `review` read one rule for whether an entry was read, `changed --strict` fails while a
component's line is left unanswered, and the line names the public names the entry leaves
out (issue 50, parts 1 to 4).

**This milestone was recorded after the fact.** The change was made as a fix, in pull
request vasiloglou/dev-tools#51, before any of this folder existed. The owner then ruled
that a change to what a gate refuses needs a milestone record
(`.devtools/project.md`, "Which lane a piece of work takes"), and
[001-issue-50.md](001-issue-50.md) is that record.

- **Plan:** none. No milestone plan was written, reviewed or gated.
- **Phase specs:** none. The code was written before any spec.
- **Review rounds:** two, of the pull request, both by Codex, both CHANGES_REQUESTED.
  `.planning/reviews/pr-51-r1/` at `8475b62`: five findings, F1 and F2 (blocking) fixed at
  `0c3e0b3`, F3, F4 and F5 at `c6d55ca`. `.planning/reviews/pr-51-r2/` at `6751dbd`: nine
  findings, all fixed at `24003fd`. **No round has read `24003fd`**: the owner ruled that
  no third round is run before the merge. No round preceded the code.
- **Ruled by the owner, 2026-11-26** (as relayed to the session that did the work): to
  file issue 50 and start fixing it; to keep `--strict` as the switch with subsystem lines
  advisory ("go og", in reply to that recommendation); to create a milestone record; to
  have F1 and F2 of the round repaired on the pull request ("yes").
- **Ruled by the owner, 2026-11-26** (said to the session that did the work, in its own
  conversation): "yes to all" to repairing F3, F4 and F5, a second review round, and
  merging the pull request and releasing 0.1.8; "Change: ask both" for a module moved from
  one component to another without an edit; "Now, in pull request 51" for part 4 of
  issue 50.
- **Ruled by the owner, 2026-11-26** (the same way, after the second round came back):
  "Repair all nine (Recommended)", and "No, merge after gates (Recommended)" to whether a
  third round reads the repairs before the merge.
- **Closed:** no. There has been no close review, question sweep or close record.
- **Next action:** as the owner ruled, the merge of the pull request and the 0.1.8 tag,
  once the gates and `devtools/ci_local.sh` exit 0 on its head. Left to the owner: Q8 to
  Q11 of the third record (which removed names the line lists, dev-tools' own gate, whether
  the milestone gets a close, closing issue 50) and Q12 and Q13 of the fourth (a folder
  named without its `/`, declaring the stop rule for review rounds).
- **Records:** [001-issue-50.md](001-issue-50.md): what shipped in `95551f0` and
  `8ae1e84`, the reproduction, the gates with their exits, the decisions, and what the
  lane requires that this change does not have.
  [002-pr-51-r1.md](002-pr-51-r1.md): the review round, the repair of F1 and F2 in
  `0c3e0b3` with its tests red and green, the decisions, and the gates with their exits.
  [003-rulings.md](003-rulings.md): the owner's rulings of 2026-11-26 and what follows
  from them in `c6d55ca`: F3, F4 and F5 repaired, a module regrouped without an edit asks
  both components, and part 4 of issue 50, with the tests red and green and the gates.
  [004-pr-51-r2.md](004-pr-51-r2.md): the second review round, its nine findings as
  reproduced and classed, the count of the two rounds against the stop rule, the owner's
  rulings on it, and the repair in `24003fd` with its tests red and green and the gates.
