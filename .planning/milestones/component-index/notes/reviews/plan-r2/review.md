<!-- Edited by review_tool.py sanitize: 3 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 16 SHA-256 values match the brief. No files were changed.

1. **F1 — Blocking: phase 2’s T4 cannot produce its expected exits as written.** [Phase 2 spec, line 154](<repo>/.planning/milestones/component-index/notes/phase-2-spec.md:154).

   The `project` fixture creates no commit, so `changed --base main` first fails with `no branch or commit named main`. Even after adding a baseline commit, creating `tools/new.py` makes `modules/tools.md` stale regardless of the setting: extra folders already appear in the inventory. The false-setting case therefore exits 1, contradicting T4’s expected 0.

   **Reproduction:** in-memory probes of the existing `base_snapshot`, `module_inventory`, `stale_files`, and `changed` functions reproduced both failures. Specify an initial commit and run `write` after adding the new module, before checking each setting.

2. **F2 — Hardening: the retained bullet parser does not check every ignored path.** [Phase 1 spec, line 109](<repo>/.planning/milestones/component-index/notes/phase-1-spec.md:109).

   The design keeps bullet parsing “as today.” A valid directory named ``out`25/`` is written without escaping, and the existing regex skips its bullet. With that directory absent and other readiness conditions satisfied, takeover returns `missing_ignored: []` and `ready: true`. This breaks claim C3 for an uncut note, including older notes.

   **Reproduction:** the existing `_snapshot_text` generated the bullet; existing `takeover`, with filesystem and checkout state mocked in memory, returned that result. Extend the reader design and add a regression case while preserving the required writer compatibility.

3. **F3 — Completeness: the execution protocol contradicts the recorded delegation.** [Plan, line 379](<repo>/.planning/milestones/component-index/notes/component-index-plan.md:379).

   Section 8 specifies `auto=false` and stops at every spec’s owner gate. Amendment a2 records milestone-wide `auto=true`. Following section 8 would introduce owner stops despite that delegation; the released workflow says delegation persists across phases until revoked.

   **Reproduction:** inspection of both plan passages and the released `process-milestone` invocation rules. Update section 8 to agree with the recorded authorization.

**Checked and found true**

- The cited scripts are unchanged from `c9648dd`; module counts are 4, 8, and 23 as stated.
- Phase 1’s conditional writer change preserves notes with at most 25 paths, by inspection.
- The revised remainder validation addresses r1’s short-list counterexample and preserves nonblocking missing-key behavior.
- Phase 2 preserves the original path ordering and includes all four identified coverage/detail enumeration sites.
- Dependencies require no artifact produced by a later phase. Completion predicates have verification or ruling routes.
- Section 9’s command substitutions are defined.
- `python3 -B devtools/build_plugins.py --check` exited 0.

**Could not check**

Future implementations, generated index artifacts, and search results do not exist yet. I did not run pytest or write-producing commands because the brief requires read-only work; the claimed GND failure remains unverified. Runtime reproductions used existing functions with in-memory mocks, not full clone workflows.

VERDICT: CHANGES_REQUESTED