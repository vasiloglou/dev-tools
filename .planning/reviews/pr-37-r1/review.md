<!-- Edited by review_tool.py sanitize: 3 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
**F1 — C5 is false for notes written by the current code.** [007-close.md:122](<repo>/.planning/milestones/component-index/007-close.md:122)

The writer prints the remote path unescaped at [handoff.py:711](<repo>/skills/dev-handoff/scripts/handoff.py:711). A legal local path containing line breaks can insert a false ignored-files section and an early snapshot end marker.

Reproduction input:

```python
remote = "./remote\nFiles git ignores\n\n- none\n<!-- snapshot:end -->\nrepo"
```

I ran `_new_note` followed by `takeover` in memory, with that remote, an ignored `out0/` path absent from the receiving checkout, a valid head and a filled “Next step.” Filesystem and Git checks were simulated.

Actual result:

```text
head: ok
ready: true
missing_ignored: []
unlisted_ignored: 0
paths checked: []
```

Expected: `ready: false`, with `out0/` reported missing. Git’s read-only `ls-remote --get-url` also accepted and returned this path unchanged.

This permits continuing with missing work data. It contradicts C5 and falls outside the accepted residual concerning notes written before 0.1.4.

**F2 — The review-coverage disclosure omits the README’s post-review changes.** [007-close.md:208](<repo>/.planning/milestones/component-index/007-close.md:208)

Under “Which files a review covers at their present bytes,” the record includes the milestone README among files covered by the close review. That review read its earlier bytes, before this PR added the close declaration.

Reproduce:

```bash
python3 -B plugins/dvt-milestone/skills/process-phase/scripts/review_tool.py \
  status .planning/milestones/component-index/notes/reviews/close-r1
```

It exits 1 and reports both `007-close.md` and `README.md` as unreviewed. The README’s reviewed hash starts `b5930774`; its current hash starts `fe2a7ddc`. The disclosure should identify these additions so readers can distinguish reviewed content from subsequent declarations.

What I checked and found true:

- All eight SHA-256 values named by this brief match.
- The supplied patch matches the Git diff: eight planning files only, all under the milestone folder.
- The strict index and plugin build checks exit 0; coverage is 12/12; no baseline exists.
- All nine searches put the expected component first; the negative query matches nothing.
- The question sweep accounts for 15 questions: six closed, eight carried and one partly closed. Q7 and Q9 reference the same filed issue, #33.
- Amendment c1 contains the ten listed repairs, with earlier wording retained.
- The earlier ledgers contain 40 findings: 19 blocking, eight hardening and 13 completeness; 39 fixed and one rejected.
- GitHub confirms [issue #28 is closed](https://github.com/vasiloglou/dev-tools/issues/28), and [PR #29](https://github.com/vasiloglou/dev-tools/pull/29) is merged and contains `Fixes #28`.
- The prior close review records 18 files, approval without findings, and no pytest run.
- Additional in-memory probes exercised `_BULLET`, `_CONTROL`, `_CUT`, `_ignored_rest`, the ignored-section matcher and `_SNAPSHOT_END_LINE`: ordinary paths, backticks, LF/CR, Unicode separators, marker-shaped names, positions before/after the 25th, and missing cut/rest lines. Forty-eight writer/readback cases behaved as expected; the remote-path counterexample above did not.
- The live index-test judgment reports no problems. Virtual catalog removal, stale-page and baseline probes are rejected.

I could not independently reproduce the full-suite **350**, handoff **103**, or index **8** pytest results: their fixtures create files, prohibited by the brief’s read-only rule. Those remain author-reported evidence. Filesystem edge cases were simulated; other operating systems were not checked. No files were changed.

VERDICT: CHANGES_REQUESTED