<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 17 SHA-256 values match the brief. No files were changed.

**F1 — Hardening: the proposed parser still permits false readiness for valid filenames.** [phase-1-spec.md:114](<repo>/.planning/milestones/component-index/notes/phase-1-spec.md:114)

The proposed `^- `(.+)` \(([^)]*)\)$` pattern does not match a path containing a newline: `re.MULTILINE` does not make `.` match newlines. The existing writer inserts paths verbatim. For an uncut list, there is no remainder comment or unlisted-count fallback, so takeover silently skips that missing path.

**Reproduction:** generate a snapshot containing one ordinary carry directory whose path is `"out\n1/"`. Leave that directory absent at the destination, with the head, next step and other readiness conditions satisfied. I ran the existing writer and takeover function in memory, substituting exactly the proposed regex and mocking checkout state. Results were:

| Missing path | `missing_ignored` | `ready` |
|---|---|---|
| `"out25/"` | `["out25/"]` | `false` |
| `"out`1/"` | `["out`1/"]` | `false` |
| `"out\n1/"` | `[]` | `true` |

This breaks claim C2 for both new and older uncut notes. The reader must handle multiline paths or withhold readiness when it cannot parse the inventory completely. Add a regression case alongside T9.

**Checked and found true**

- By inspection, the conditional writer change preserves snapshots containing at most 25 ignored paths.
- Remainder validation checks structure and length; its fallback addresses the earlier short-list counterexample. Missing keys remain nonblocking.
- Phase 2’s proposed enumeration preserves existing path ordering. An in-memory probe confirmed `a/z.py` precedes `a.py`.
- The repaired T4 supplies a baseline commit and regenerates pages after adding the module, addressing the two earlier failures.
- Dependencies require no later phase’s artifact. Completion predicates have gate or review/ruling routes.
- Section 9 defines the `INDEX` substitution, and the CLI forms agree with the parser, by inspection.
- `python3 -B devtools/build_plugins.py --check` exited 0.
- The cited scripts and test files have no differences from `c9648dd`.

**Could not check**

The implementations, generated index and search cases do not exist yet. I did not run pytest, clone workflows or write-producing gates because the brief requires read-only work. The claimed GND failure remains unverified; runtime probes used in-memory state.

VERDICT: CHANGES_REQUESTED