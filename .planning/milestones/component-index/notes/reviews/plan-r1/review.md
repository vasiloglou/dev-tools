<!-- Edited by review_tool.py sanitize: 8 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All thirteen SHA-256 values match the brief. HEAD is `c9648dd177f4`. No files were changed.

**Findings**

1. **F1 — Blocking: missing-key behavior contradicts the completion contract.** [Phase 1 spec, line 136](<repo>/.planning/milestones/component-index/notes/phase-1-spec.md:136) explicitly keeps missing key files nonblocking. Plan C5 and the spec’s goal require `ready: false` when *any* ignored path is absent.  
   **Consequence/reproduction:** with every other condition satisfied and only an ignored key file missing, takeover returns `missing_keys: ["example.pem"]` and `ready: true`. I reproduced this using the existing function with mocked checkout state; D2 preserves that behavior. Amend the universal contract or change D2 and T4.

2. **F2 — Hardening: readable but incomplete remainder data can still report ready.** [Phase 1 spec, line 110](<repo>/.planning/milestones/component-index/notes/phase-1-spec.md:110) sets `unlisted_ignored` to zero whenever the remainder is readable, without checking its length against `N`.  
   **Consequence/reproduction:** retain `- and 1 smaller path …`, replace the remainder with `<!-- ignored-rest: [] -->`, and leave the omitted path absent. The empty list satisfies the stated grammar, so the prescribed checks allow readiness. This was demonstrated with an in-memory model of the proposed rules, not an implementation. Require the remainder to account for all `N` paths and add a test.

3. **F3 — Blocking: the default changes output ordering.** [Phase 2 spec, line 82](<repo>/.planning/milestones/component-index/notes/phase-2-spec.md:82) sorts deduplicated POSIX strings. Today `sources()` sorts `Path` objects.  
   **Consequence/reproduction:** for `src/widget/a/z.py` and `src/widget/a.py`, today’s order is:
   ```
   src/widget/a/z.py
   src/widget/a.py
   ```
   The proposed order is reversed, changing `stats`, `draft`, and baseline-file output even with the setting absent or false. I reproduced the ordering difference with the existing `sources()` and `coverage()` functions. Preserve today’s ordering in the default branch.

4. **F4 — Blocking: phase 2’s test expectations are inconsistent.** [Phase 2 spec, line 135](<repo>/.planning/milestones/component-index/notes/phase-2-spec.md:135) expects both `coverage: 0/1` and a successful strict check. The cited fixture creates an unassigned `src/widget/__init__.py`.  
   **Consequence/reproduction:** the strict check exits 1 naming that module. T2b also exits 1 after assigning only `tools/report.py`; T5 has two unassigned modules rather than one. I reproduced the strict-check results with existing functions and mocked filesystem reads. Assign the package module in the shared setup, then update the expected coverage to `1/1` and `1/2`.

5. **F5 — Completeness: `show` contains ownership logic omitted from the change.** [Phase 2 spec, line 89](<repo>/.planning/milestones/component-index/notes/phase-2-spec.md:89) excludes `show` as import-graph work. However, its package-only list also controls which owned modules receive detailed output.  
   **Consequence/reproduction:** an entry covering `tools/report.py` produces its catalog fields but no module section, symbols, or source details. I reproduced this using the existing `show()` function. Include the ownership enumeration in the enabled-setting design; import resolution can remain separately out of scope. C5 is therefore false as stated.

6. **F6 — Hardening: the strict gate does not enforce the no-baseline predicate.** [Plan, line 379](<repo>/.planning/milestones/component-index/notes/component-index-plan.md:379) uses `--check --strict` for C1, and phase 4’s proposed test runs that command. Neither explicitly rejects `unassigned-baseline.txt`.  
   **Consequence/reproduction:** place an uncovered module in the baseline and keep generated output current; strict checking exits 0. I reproduced that decision with existing `write_or_check()` and mocked reads. Add an explicit absence assertion to the gate/test so this part of C1 can fail independently.

7. **F7 — Completeness: section 9 commands cannot all run literally.** [Plan, line 380](<repo>/.planning/milestones/component-index/notes/component-index-plan.md:380) uses `…` as an executable placeholder, also used for strict checking, review, and changed checking.  
   **Consequence/reproduction:** running `… review` from the root exited 127: `command not found: …`. Expand every command and explain query substitution. This also discharges R0.3’s requirement for exact gate commands.

8. **F8 — Style/factual correction: the baseline misstates reachable `draft` behavior.** [Plan, line 165](<repo>/.planning/milestones/component-index/notes/component-index-plan.md:165) says an extra-folder module causes `draft()` to raise. Today coverage excludes that module, so normal drafting never reaches the failing `relative_to()` call.  
   **Reproduction:** with package and extra-folder modules, the existing function emitted only the package stub without raising. No separate implementation consequence; correct the baseline description.

**Checked and found true**

- The baseline counts are 4 modules under `devtools/`, 8 under `skills/`, and 23 under `.`.
- The existing hand-off writer cuts the visible list at 25; takeover checks only its listed bullets.
- Phase 1’s conditional writer change preserves snapshots with at most 25 paths **by inspection**.
- The phase dependencies have no dependency on an artifact produced by a later phase.
- Both draft specs name all seven standing design rules.
- `python3 -B devtools/build_plugins.py --check` exited 0.

**Could not check**

- Future implementations and generated index/search artifacts do not exist yet.
- I did not run pytest: its fixtures create files and repositories, contrary to the brief’s read-only instruction. The claimed GND failure exception remains unverified.
- Runtime probes used existing functions with in-memory mocks; they were not full clone-and-takeover runs.

VERDICT: CHANGES_REQUESTED