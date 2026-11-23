<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
1. **F1 — Configured filenames can disable the entire dirty check.** [devtools/sync.py:387](<repo>/devtools/sync.py:387)

   Configured sources are literal filesystem paths, but the fix passes them to Git as pathspecs. A legal filename such as `:(unknown)one.py` makes both `status` and `ls-files` exit 128. The resolver treats these failures as empty results and selects upstream despite local edits.

   Reproduce with a checkout one commit behind, a locally edited `devtools/sync.py`, and this config, with both source files present:

   ```toml
   [[sync]]
   source = "devtools/sync.py"
   dest = "tool.py"

   [[sync]]
   source = ":(unknown)one.py"
   dest = "one.py"
   ```

   Real read-only Git commands confirmed the pathspec error. An in-memory reproduction through `main("apply", …)` showed:

   - Before the fixes: exit 0, delivered local bytes, warned about own work.
   - At head: exit 0, delivered upstream bytes, omitted the own-work warning.

   This refutes C1 and C3. Pass literal pathspecs and handle failed dirty queries explicitly.

2. **Checked and found true**

   - All three named SHA-256 hashes match; HEAD matches the brief.
   - An ordinary configured source outside the four default folders (`docs/why.html`) now preserves local edits and warns.
   - For missing sources and regular-file sources, check exits 0 with “not compared,” strict check exits 5, and apply exits 2. Existing drift still exits 1.
   - A plain-folder, empty-config comparison preserved output and exits across apply, check, survey and compare.
   - Standing matcher checks covered Git pathspecs (`:(unknown)one.py`, `:(exclude)skills`, `scripts/[one].py`, `:`); `git_line` with trailing spaces/newlines; `covers`, `takes` and `workflow_folder` with Unicode, repeated separators and prefix collisions; `names_in` with Unicode, embedded newlines, bare names and longer names; and `TOKEN` identifiers. Only the Git pathspec handling produced a finding.
   - Plugin consistency and strict component-index commands both exited 0.

3. **Could not check**

   The full pytest suite and physical scratch-checkout reproductions create files, which the brief forbids; pytest is also unavailable. Behavioral reproductions used in-memory substitutions, supplemented by real read-only Git commands. No files were changed or credentials opened.

VERDICT: CHANGES_REQUESTED