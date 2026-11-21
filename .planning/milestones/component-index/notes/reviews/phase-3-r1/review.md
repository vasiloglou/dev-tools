<!-- Edited by review_tool.py sanitize: 2 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 25 SHA-256 values match the brief.

**F1 — Incorrect condition for running acceptance tests.** [COMPONENTS.md:334](<repo>/.devtools/components/COMPONENTS.md:334) says tests run only after completion or with `--phase NN`. Explicitly naming an acceptance test path also runs it, regardless of phase status (`phase_selection.py:44–55`).

Reproduced by calling the collection hook in memory with no completed phases, no `--phase`, and an explicitly named `tests/acceptance/p99_example/test_example.py`: it retained the item. Without the explicit path, it deselected it. The entry hides a supported way to run an incomplete phase’s tests and overstates the completion restriction.

**F2 — The rule-check subsystem assigns loads to the wrong command and reverses their order.** [COMPONENTS.md:359](<repo>/.devtools/components/COMPONENTS.md:359) puts the index before the phase tool; the following note attributes the `importlib` load to `check --phase`.

An in-memory trace, stopping before writes or GND execution, showed:

- `check --phase`: `phase_tool.py facts` → `components_index.py facts`.
- `test`: `components_index.py facts` → `importlib` loads `phase_tool.py`.

These paths are implemented in `rules_check.py:732–744` and `:786–841`. Someone tracing an import failure from `test` would be directed to the wrong command. The spec repeats this mistaken mapping, so matching it does not establish C2.

What I checked and found true:

- The built plugin’s strict index check, `stats`, `review`, and plugin build check each exited 0. I disabled caching.
- Coverage is exactly **12/12**, with each source module assigned once, no counted files under `plugins/`, `tests/`, or `.claude/`, and no baseline.
- All nine positive searches return the expected component first. The negative search returns no component match. The queries are reasonable newcomer questions.
- `review` reports zero components importing each other; its four unresolved flow steps correspond to documented runtime connections.
- REVIEW.md’s duplicate-list observation, three largest-module counts, six shared-helper definitions, and absence of tests mentioning `phase_selection` are supported.
- All twelve source modules are unchanged from `f25d3a5`. I independently read both modules whose entries lack `checked: partial`.

What I could not check:

- The files cannot establish whether the original author previously read those two modules in full.
- I did not run `write`, the full pytest suite, or complete GND workflows: they create files and conflict with the brief’s read-only rule. The reproductions above used memory only.

VERDICT: CHANGES_REQUESTED