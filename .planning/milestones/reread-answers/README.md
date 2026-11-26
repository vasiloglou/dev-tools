# Milestone: reread-answers

A `reread:` line from the component index's `changed` is answered in the entry, `changed`
and `review` read one rule for whether an entry was read, and `changed --strict` fails
while a component's line is left unanswered (issue 50, parts 1 to 3).

**This milestone was recorded after the fact.** The change was made as a fix, in pull
request vasiloglou/dev-tools#51, before any of this folder existed. The owner then ruled
that a change to what a gate refuses needs a milestone record
(`.devtools/project.md`, "Which lane a piece of work takes"), and
[001-issue-50.md](001-issue-50.md) is that record.

- **Plan:** none. No milestone plan was written, reviewed or gated.
- **Phase specs:** none. The code was written before any spec.
- **Review rounds:** one, of the pull request: `.planning/reviews/pr-51-r1/`, by Codex at
  `8475b62`, verdict CHANGES_REQUESTED, five findings. F1 and F2 (blocking) are fixed at
  `0c3e0b3`; F3, F4 and F5 are open. The repaired head has not been reviewed. No round
  preceded the code.
- **Ruled by the owner, 2026-11-26** (as relayed to the session that did the work): to
  file issue 50 and start fixing it; to keep `--strict` as the switch with subsystem lines
  advisory ("go og", in reply to that recommendation); to create a milestone record; to
  have F1 and F2 of the round repaired on the pull request ("yes").
- **Closed:** no. There has been no close review, question sweep or close record.
- **Next action:** the owner's: rule Q1 to Q4 of the first record (part 4 of issue 50,
  dev-tools' own gate, tagging 0.1.8, whether the milestone gets a close) and Q5 to Q7 of
  the second (F3 to F5, whether a module moved without an edit asks for a reread, a second
  review round), and merge or amend the pull request.
- **Records:** [001-issue-50.md](001-issue-50.md): what shipped in `95551f0` and
  `8ae1e84`, the reproduction, the gates with their exits, the decisions, and what the
  lane requires that this change does not have.
  [002-pr-51-r1.md](002-pr-51-r1.md): the review round, the repair of F1 and F2 in
  `0c3e0b3` with its tests red and green, the decisions, and the gates with their exits.
