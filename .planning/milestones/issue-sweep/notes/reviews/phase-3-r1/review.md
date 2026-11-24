<!-- Edited by review_tool.py sanitize: 6 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 33 SHA-256 values match the brief. No files were changed. Reproductions below used in-memory settings reads.

1. **F1 — Invalid setting values can still prevent `phase_tool.py` from loading.** At [phase_tool.py:125](<repo>/skills/phase/process-phase/scripts/phase_tool.py:125), the fallback catches only the validations performed by `load_settings`; other invalid values reach module-level expressions.

   Reproduced with `{"package_prefix": 7}` and `{"process_skill": null}`. Running `--format json status` raises an uncaught `TypeError`, producing no envelope; importing the module also fails. This contradicts C5 and leaves the corrected docstring inaccurate. Validate these settings before deriving constants, then use the existing fallback and `SETTINGS` envelope.

2. **F2 — The four text-reporting scripts still accept unusable setting values and then crash.** The updated loaders check JSON structure and unknown keys but leave value types partly unchecked. These cases all produced uncaught exceptions, corresponding to CLI exit 1 with a traceback rather than the required exit 2 and reason:

   | Location | Settings JSON | Command |
   |---|---|---|
   | [components_index.py:108](<repo>/skills/components/scripts/components_index.py:108) | `{"verb_list": []}` | `--check` |
   | [rules_check.py:244](<repo>/skills/components/scripts/rules_check.py:244) | `{"index_script": 7}` | `init --print` |
   | [handoff.py:105](<repo>/skills/dev-handoff/scripts/handoff.py:105) | `{"planning_dir": 7}` | `list` |
   | [review_tool.py:161](<repo>/skills/milestone/process-phase/scripts/review_tool.py:161) | `{"codex_model": 7}` | `run <existing-round> --reviewer codex --dry-run` |

   These are gaps in C4’s “wrong value” requirement. The changed tests cover malformed JSON, non-objects and unknown keys, but omit these value-type cases. The generated plugin copies contain the same defects.

3. **F3 — The settings-error branch guesses command-line meaning instead of using the parser.** At [phase_tool.py:2043](<repo>/skills/phase/process-phase/scripts/phase_tool.py:2043), the new early return uses the preceding raw-token matchers.

   With an unknown setting:
   
   - `--for=json status` is accepted by `build_parser()` as JSON format, but prints Markdown.
   - `--format json --root status check --roadmap` prints `"tool": "phase_tool.status"` instead of `"phase_tool.check"`.
   - `--format=json status --format md` prints JSON despite the parser selecting Markdown.

   These legal inputs demonstrate the standing check’s concern about matching structured command lines. Parse valid arguments before constructing the settings error response.

What I checked and found true:

- `build_plugins.py --check` exited 0.
- The strict component-index check, with caching disabled, exited 0.
- Ruff **0.16.2**, with the specified local configuration, reported no findings across the required scripts and plugin copies.
- All five updated loaders refused malformed JSON, non-object JSON and a Unicode unknown key with exit 2. For those inputs, phase-tool imports succeeded and tested commands returned one `SETTINGS` envelope.
- The `about == "plans"` matcher correctly handled an arbitrary rule id and JSON-escaped `"pla\u006es"`. Skipped rules were excluded from the model supplied to the stubbed synthesis boundary.
- Non-plan examples naming an unknown fact remained wrong with and without the phase tool.
- In a controlled comparison with the phase tool present, output, exit and synthesized model matched the baseline. Representative working settings produced identical loader results.
- The `coder_pool.py` fallback branches and retained exit-1 convention support D1. Inspection confirmed that `from_gsd.py`’s git commands only read.

I could not run fresh-project integration tests, the full pytest suite, or filesystem-based mutation tests because they create files, which the brief forbids. Test potency was inspected, but I did not establish that every changed test fails under its corresponding mutation or verify the claimed red-before-green history.

VERDICT: CHANGES_REQUESTED