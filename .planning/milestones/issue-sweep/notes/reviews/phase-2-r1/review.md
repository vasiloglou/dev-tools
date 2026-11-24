All 29 SHA-256 digests match the brief.

**F1 — Tag comparisons can silently switch to a branch’s upstream.**  
[components_index.py:1103](skills/components/scripts/components_index.py:1103) checks whether a same-named local branch exists, without establishing that the requested ref resolved to that branch.

Reproduce with a tag named `main` and a local branch named `main` that is behind `origin/main`. Git resolves the bare name to the tag, but this function substitutes `origin/main` and prints a note. Consequently, `changed`, `facts`, and the rule checker can compare against the wrong history. C2 explicitly requires tags to retain their previous behavior.

An in-memory resolver probe, using real commit and ancestry reads with a simulated colliding branch, returned `origin/main` for the existing `v1.0` tag instead of retaining `v1.0`. The B2 parameters omit tags, so they miss this regression.

**F2 — The tie repair changes default review output without a `reread:` field.**  
[components_index.py:1316](skills/components/scripts/components_index.py:1316) applies ancestry tie-breaking to every dating field.

Reproduce with two successive commits sharing one timestamp: A writes the entry’s `does` and `verbs`; B changes its module and `verbs`. Include no `reread:` line. Running the old and new review functions against that blame input produced:

- Before: `Descriptions older than their code (1)`, with one lead.
- After: `Descriptions older than their code (0)`.

The newer result is reasonable, but it contradicts S0.1’s promised preservation of default output, whose declared exception concerns stale bases. The compatibility contract and tests need to address this broader change. This was reproduced in memory with synthetic blame records and real ancestry/count queries.

I checked and found true:

- Plugin consistency and the strict index check both exited 0. `git diff --check` exited 0.
- Release status exited 1 and reported `0.1.7 is ready`, as specified.
- On this checkout, stale `main` selected `origin/main`, with exactly one note immediately before the summary.
- The two actual `facts` outputs were byte-for-byte equal. Intercepting `--out` in memory confirmed identical document bytes, empty stdout, and the note on stderr.
- Baseline refusal, boolean validation, same-second and uncommitted reread dating, duplicate reread detection, and counted-folder review groups behaved as specified in in-memory probes.
- With extra-folder counting off and reread blame lines excluded, old and new review output matched on this checkout.
- Static inspection found only read-only Git commands. The documentation generally reflects the implementation.

For the matcher check, I exercised ref-name concatenation with qualified refs and colliding tag/branch names; reread-field matching with tabs and Unicode; blame matching with same-second commits and reordered fields; and note-prefix filtering with Unicode refs and multiple notes. Qualified `refs/heads/main` also retained the stale local base, unlike shorthand `main`.

I could not run the fixture tests or repeat their negative controls: they create files and repositories, which the brief forbids. Pytest is also unavailable in the current Python environment. Full rule-check integration and the lint gate were not rerun. No files were changed.

VERDICT: CHANGES_REQUESTED