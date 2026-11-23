# Phase 4 spec: keep dev-tools' component index current

## 1. Status

Draft, 2026-11-23, written with `process-phase` (dvt-milestone 0.1.3) on the owner's
invocation `/dvt-milestone:process-phase 4 auto`. Its gate is a delegated approval
(auto=true), recorded in section 12. No review has run over these bytes.

Phases 1 to 3 are merged (vasiloglou/dev-tools#29, #30 and #32, on 2026-11-23). This
phase's branch, `claude/component-index-phase-4`, is cut from `main` at `827e766`.

## 2. Provenance

- **Plan.** `notes/component-index-plan.md` at SHA-256 `3cc5eb49…86a9`: phase 4 in
  section 4, C3 and C4, the section 9 rows for phase 4, R0.1 to R0.3 in section 0, D1 and
  D3 in section 10, R6 in section 6, and the section 5 row for
  `.devtools/project.md`, `AGENTS.md`, `README.md` and `docs/milestone.html`.
- **Records read.** `004-phase-3.md` (its boundary: "Nothing yet keeps the index current
  … That is phase 4") and `005-phase-3-reread.md` (Q9 to Q12, all for the close).
- **Code read.** `plugins/dvt-milestone/skills/components/scripts/components_index.py`:
  `plugin_root`, `checkout_root`, the settings block, `sources`, `counted_modules`,
  `cache_path`, `stale_files`, `write_or_check` and `main`. `tests/test_plugins.py`, for
  how a test here runs a plugin's script.
- **Runs before the gate** (the implementability sweep; none is a gate result):
  - In a copy of `.devtools`, `devtools`, `skills`, `tests` and `plugins/dvt-milestone`
    with `git init`, `--no-cache --check --strict` exited 0 and printed nothing. Without
    `tests/` in the copy it exited 1: the check also refuses an entry whose `tests:` path
    is missing.
  - In such a copy, each of these exited 1: a module path replaced in an entry
    (`no component: skills/phase/pytest/phase_selection.py …`); a new module
    (`no component: skills/newthing/scripts/new_tool.py …`); a public function added to
    `devtools/sync.py` (`stale or missing: .devtools/components/modules/_root.md`); the
    settings file deleted (`docs/components/COMPONENTS.md is missing …`).
  - With a new module, `write` and then `stats --write-baseline` exited 0, and
    `--check --strict` then exited 0 and printed nothing (plan-r1 F6, reproduced).
  - The built copy's `--no-cache --check --strict`, run under Python 3.11, 3.12, 3.13
    and 3.14 with `uv run --no-project --python <version>`, printed nothing each time.
  - The installed 0.1.3 copy, run from this checkout, printed
    `…/.devtools/components_index.settings.json: unknown setting(s): count_extra_dirs`
    and exited 1 (plan R6, reproduced).

## 3. Obligations (step 0 harvest)

| # | Obligation | Source | Discharged in |
|---|---|---|---|
| O1 | `tests/test_own_index.py` runs the built copy's `--check --strict` from the repository root | Phase 4 deliverables; D3 | Section 6, the test; T1 |
| O2 | The new test exits 0 on the phase's head | P4.1; section 9 row | G1 |
| O3 | With one entry's module path removed, the test fails and names the module | P4.2; section 9 row | T3; G2 |
| O4 | With an `unassigned-baseline.txt` present, the test fails | P4.3; plan-r1 F6; C1 | T4; G3 |
| O5 | The suite includes a test that fails while the index is stale, and the suite exits 0 | C3 | T5, T6; G5 |
| O6 | `.devtools/project.md` names the index, its folder and its two gates | C4; phase 4 deliverables | Section 6, `.devtools/project.md` |
| O7 | `.devtools/project.md` names the plugin version the index needs | Plan R6 | Section 6, `.devtools/project.md` |
| O8 | One line in `AGENTS.md`: search the index before writing a module or a function | Phase 4 deliverables | Section 6, `AGENTS.md` |
| O9 | A row naming `.devtools/components/` in `README.md` and `docs/milestone.html#own-use`; a pointer on `docs/components.html` | Phase 4 deliverables; C4; plan section 5 | Section 6, the pages |
| O10 | `changed --base main` exits 0 on the phase's head | Section 9 row | G4 |
| O11 | Every gate that uses the index tool runs the built copy from the repository root | R0.3 | Section 8, every command |
| O12 | Every contributor is affected: the full suite now checks the index | Section 9 row, "Affected consumers" | D2; section 6, `CONTRIBUTING.md` |
| O13 | "Nothing yet keeps the index current" | `004-phase-3.md`, boundary | Discharged by this phase; the record says so |

Plan section 10 assigns this phase no decision row. Q1, Q2 and Q7 to Q12 are for the
close sweep and are not touched here.

## 4. The standing rules, bound to this phase

| Rule | Bound here to |
|---|---|
| A script change comes with a test | No script under `skills/` or `devtools/` changes. The phase adds a test file; each line its judgment can return has a case that fails without it (section 8) |
| The plugins are rebuilt, and released under a new version | Does not apply: nothing under `skills/` or `agents/` changes, so there is no bump. G6 checks `plugins/` is still what the build makes |
| A wording change says what prompted it | No skill wording changes. The changed sentences are the project's own files and the site; each is listed in section 6 with what made it untrue or incomplete |
| Shared skills stay general | Nothing is written under `skills/`. What is true of dev-tools only goes in `.devtools/project.md` (R0.2) |
| Both agents read the same file | `AGENTS.md` is read by Codex directly and by Claude Code through `CLAUDE.md`. Its new command is a path in the repository, with no `${CLAUDE_PLUGIN_ROOT}` |
| Captures on the site are real output | No capture is added or replaced. The pointer on `docs/components.html` is a sentence and a link |
| The page that describes it is updated too | `README.md`, `CONTRIBUTING.md`, `docs/milestone.html`, `docs/components.html` and `docs/contribute.html`, in this phase's pull request |
| R0.1 A shipped script stands alone | No import is added between scripts. The test imports no script; it runs one as a subprocess |
| R0.2 The index is the project's | No file of the index is written outside `.devtools/`. The three pages of `docs/` describe dev-tools' own use as an example a reader can open; no dev-tools path or setting enters a skill |
| R0.3 The released plugin runs | The test and every gate in section 8 name `plugins/dvt-milestone/skills/components/scripts/components_index.py`, run from the repository root |

## 5. Goal

`uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q` exits 0
on the phase's head. In a checkout of that head with one entry's module path removed
from `.devtools/components/COMPONENTS.md`, the same command exits 1 and its output holds
`no component: <that module>`. In a checkout with
`.devtools/components/unassigned-baseline.txt` present, it exits 1 and its output names
that file. The full suite exits 0. `.devtools/project.md` names the index's folder, the
copy of the script that runs here, the plugin version it needs and two gate rows.

## 6. Design

**Reuse** (the index was searched with the built copy):

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Decide whether the catalog matches the code | `search check the component index is current`; `search stale index test fails when a module has no component` | `components.index`: `write_or_check`, behind `--check --strict` | reuse: the test runs that command and adds no checking logic of its own, except the baseline (below) |
| Refuse a baseline file | the same two searches; `git grep -n unassigned-baseline` | `write_or_check` reads the baseline to excuse the modules it names; nothing refuses the file | new: one `exists()` in the test. The script must go on excusing a baseline for projects that keep one |
| Run a plugin's script in a copy of a project, in a test | `search run a script from the repository root in a test` (no component: the index does not cover `tests/`); `git grep -n "^def run" tests` | `run` in `test_plugins.py`, `test_handoff.py`, `test_sync.py`, `test_from_gsd.py`: one per test file, each with its own arguments; there is no `conftest.py` | new: a helper of the same shape in the new file. Test files here share no helpers |

**The test** (`tests/test_own_index.py`, about 120 lines).

```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "plugins/dvt-milestone/skills/components/scripts/components_index.py"
INDEX = ".devtools/components"
BASELINE = INDEX + "/unassigned-baseline.txt"
COPIED = (".devtools", "devtools", "skills", "tests", "plugins/dvt-milestone")

def index(root: Path, *args: str) -> subprocess.CompletedProcess: ...
def problems(root: Path) -> list[str]: ...
```

- `index(root, *args)` runs `[sys.executable, root / SCRIPT, "--no-cache", *args]` with
  `cwd=root`, capturing its output as text. The script finds the project as the checkout
  that holds the working directory, and reads that checkout's
  `.devtools/components_index.settings.json`, because it sits in a plugin's folder.
  `--no-cache` keeps the test from reading or writing `~/.cache/components-index/`.
- `problems(root)` is the judgment, and has two parts:
  1. It runs `index(root, "--check", "--strict")`. On exit 0 this part gives nothing. On
     any other exit it gives one line, `components_index.py --check --strict exited <N>`,
     and then every non-blank line the command printed. A non-zero exit therefore always
     gives at least one line, whatever the script printed.
  2. If `root / BASELINE` exists, it adds one line naming that path and saying that no
     baseline is kept here. `--check --strict` excuses every module a baseline names, so
     only this line shows there is none (C1).
- `test_the_index_is_current` asserts `problems(ROOT) == []`. Its message lists the
  lines and says what to run:
  `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py write`
  after `python3 devtools/build_plugins.py`, then commit `.devtools/components/`; and for
  a `no component:` line, add the module to an entry of `COMPONENTS.md` first.
- A fixture, `checkout`, copies the folders of `COPIED` from `ROOT` into `tmp_path`
  (without `__pycache__` and `.pytest_cache`) and runs `git init -q` there. The other
  tests change that copy in one way each and assert on what `problems` returns
  (section 8).

The test file is not listed under any entry's `tests:` (D4).

**`.devtools/project.md`.**

- "What runs here", the *Component index* item, which says "None yet, so a phase skips
  the three component steps". New text, in substance:
  - the index is in `.devtools/components/`, with its settings in
    `.devtools/components_index.settings.json`, and covers the modules of `devtools/` and
    `skills/`;
  - a phase runs the three component steps with the copy of the script in `plugins/`,
    from the repository root (`python3 plugins/dvt-milestone/skills/components/scripts/components_index.py`);
  - not the copy under `skills/`, which reads its settings from beside itself; and not an
    installed plugin older than 0.1.5, which refuses the settings file with
    `unknown setting(s): count_extra_dirs` (O7; reproduced, section 2);
  - after a change to a module of `devtools/` or `skills/`: rebuild the plugins, run
    `write`, and commit `.devtools/components/` with the change.
- "Gates", two rows:

  | Gate | Command |
  |---|---|
  | The component index is current (when a phase closes; the test suite runs it too) | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict` |
  | The index against what a change touched (before a pull request) | `python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base main` |

**`AGENTS.md`**, under "Commands": one sentence, "Before writing a module or a function,
search the component index for what already exists", with the command
`python3 plugins/dvt-milestone/skills/components/scripts/components_index.py search <words>`.

**`CONTRIBUTING.md`** (D2), in step 3 of "How a change gets in", after the test command:
one paragraph. A test fails while dev-tools' own component index is stale, which a
changed script makes it; the failure names the command that regenerates it.

**The pages.**

| File | Change | What made the present text untrue or incomplete |
|---|---|---|
| `README.md`, "dev-tools is developed with dev-tools" | A bullet, *Where its component index is*, naming `.devtools/components/`. The intro's "No milestone has run here yet; the first one will leave the first records" is replaced (D3). "What it changes for a contributor. Nothing." becomes one thing: the stale-index test (D2) | The index exists since phase 3; the milestone has left five records; the new test |
| `README.md`, "What is here" | The `tests/` row and the `.planning/`, `.devtools/project.md` row name the index test and `.devtools/components/` | The same |
| `docs/milestone.html#own-use` | A table row for `.devtools/components/`. The intro's "No milestone has run there yet …" and the `.planning/milestones/` row's "Empty until the first milestone is planned" are replaced (D3). The list of gate commands gains "whether the component index is current" | The same; and the two new gate rows |
| `docs/components.html`, the Build feature | One paragraph: dev-tools keeps an index of its own code, written this way, with a link to `.devtools/components/COMPONENTS.md` on `main` | The plan asks for it as an example of a built index |
| `docs/contribute.html` | Step 3 gains the sentence of `CONTRIBUTING.md`. "Where things live": the `tests/` row and the `.planning/`, `.devtools/` row name the index | It mirrors `CONTRIBUTING.md` |

Every link added points at a path that is on `main` at `827e766`.

**The milestone's `README.md`** gains the phase 4 spec, the merged pull requests and the
new record.

## 7. Decisions

| # | Question | Readings, and what each costs | Proposed |
|---|---|---|---|
| D1 | Where the failing cases of P4.2 and P4.3 live | **(A)** As tests in the same file, each on a copy of the checkout, and once each on the real tree for the record (G2, G3). **(B)** Only the two runs for the record: after this phase nothing could fail if the judgment stopped naming the module or the baseline | (A) |
| D2 | What a contributor is told about the new test | **(A)** One paragraph in step 3 of `CONTRIBUTING.md` and of `docs/contribute.html`, the `README.md` bullet, and the failure message. **(B)** An eighth rule under "What makes a change easy to accept": those rules are the standing design rules, so the plan's "seven", `.devtools/project.md` and the site's count all change, and every later spec discharges one more. **(C)** The failure message alone: `README.md` then still says a contribution changes nothing | (A) |
| D3 | The sentences the milestone made untrue (`README.md` and `docs/milestone.html`: "No milestone has run here yet", "Empty until the first milestone is planned") | **(A)** Replace them here, beside the rows this phase adds. **(B)** Leave them to the close: the page then says no milestone has run, one row above the index that milestone built | (A) |
| D4 | Whether `tests/test_own_index.py` goes under an entry's `tests:` | **(A)** No: it tests the catalog's content, not a script. **(B)** Under `components.index`: the entry would then claim a test that passes or fails with dev-tools' catalog, which no other project's copy of the script has | (A) |

## 8. Tests and gates

`tests/test_own_index.py`. Each test asserts on the lines `problems` returns.

| # | Test | What it changes in the copy | Expected |
|---|---|---|---|
| T1 | `test_the_index_is_current` | Nothing; it reads `ROOT` | `problems(ROOT) == []` |
| T2 | `test_a_copy_of_the_checkout_is_current` | Nothing | `problems(copy) == []`. Without it, T3 to T7 could find a problem only because the copy is incomplete |
| T3 | `test_a_module_no_entry_lists_is_named` (P4.2) | Removes the path from the first `- modules:` line of `COMPONENTS.md` that names one `.py` file | a line starting `no component: <that path> ` |
| T4 | `test_a_baseline_is_refused` (P4.3) | Adds a module, runs `write` and `stats --write-baseline` | `index(copy, "--check", "--strict")` exits 0, and `problems(copy)` is exactly the baseline line |
| T5 | `test_a_new_module_is_named` | Adds `skills/example/scripts/example.py` | a line starting `no component: skills/example/scripts/example.py ` |
| T6 | `test_a_changed_module_leaves_a_page_stale` | Appends a public function to `devtools/sync.py` | a line starting `stale or missing: .devtools/components/modules/` |
| T7 | `test_the_check_reads_this_projects_settings` | Deletes `.devtools/components_index.settings.json` | the first line is `components_index.py --check --strict exited 1`, and a line holds `COMPONENTS.md is missing` |

Coverage, per line `problems` can return: the exit line (T7, by equality), the script's
own lines (T3, T5, T6, T7), the baseline line (T4), and nothing (T1, T2). T4 is the only
case where the script exits 0 and the judgment still fails; it is the branch plan-r1 F6
named.

Each of T3 to T7 is run once against a `problems` with the part it covers removed, and
is seen to fail (the record lists the runs).

**Gates**, run from the repository root, with
`C=plugins/dvt-milestone/skills/components/scripts/components_index.py`:

- G1: `uv run --no-project --with pytest python -m pytest tests/test_own_index.py -q`
  exits 0 (P4.1).
- G2 (P4.2): in a clean checkout of the phase's head, with one entry's module path
  removed from `COMPONENTS.md`, G1's command exits 1 and prints `no component:` with
  that module.
- G3 (P4.3): in a clean checkout of the phase's head, with an
  `unassigned-baseline.txt` present, G1's command exits 1 and prints that file's path.
- G4: `python3 $C changed --base main` exits 0. Also, as process-phase's step 6 asks,
  `python3 $C changed --base 827e766 --strict` exits 0.
- G5: `uv run --no-project --with pytest python -m pytest tests -q` exits 0 (C3).
- G6: `python3 devtools/build_plugins.py --check` exits 0.
- G7: `python3 $C --check --strict` exits 0, and
  `test ! -e .devtools/components/unassigned-baseline.txt` exits 0 (C1 on this head).
- G8: G1's command under each of Python 3.11, 3.12, 3.13 and 3.14
  (`uv run --no-project --python <version> --with pytest …`) exits 0.

**G8 is an experiment, written before it runs.** It measures whether the committed index
is what the script generates under each interpreter the project supports, on this
machine. It cannot measure another operating system: a checkout whose line endings git
rewrites would read as stale, and nothing here tries one. An exit other than 0 under any
version is a finding about the test's reach, recorded as such, not a reason to drop the
version.

**Verification-selection ledger.**

| Obligation | Disposition |
|---|---|
| Plan section 9, phase 4 rows | run: G1 with G2 and G3; G4 |
| Direct phase tests | run: G1 (T1 to T7) |
| Impact closure: the full suite gains a file | run: G5 |
| `plugins/` unchanged by this phase | run: G6 |
| C1 still true on this head | run: G7 |
| Broader historical suites | none exists beyond `tests/` |

## 9. Out of scope for this phase

- Any change to `components_index.py`, the `components` skill or any other script.
- CI (plan section 7).
- Rereading the three entries `review` lists as older than their code since
  vasiloglou/dev-tools#34 (`handoff.notes`, `components.rules`, `review.rounds`). That
  pull request says it changes no behaviour; whether an entry is reread after such a
  change is a question for the close.
- `docs/index.html`'s "Used on itself" line, which stays true.
- The close: its review, the question sweep and the plan repairs.

## 10. Size

- `tests/test_own_index.py`: about 120 lines.
- `.devtools/project.md`: about 15 lines changed; `AGENTS.md`: about 6 added;
  `CONTRIBUTING.md`: about 5 added.
- `README.md`, `docs/milestone.html`, `docs/components.html`, `docs/contribute.html`:
  about 20 lines changed in all.

## 11. Approval instrument

This prose, with the case table of section 8 as the corpus: each case states what it
changes and the line it expects, before the test is written. The phase adds a validation
predicate (`problems`), for which `review-convergence.md` makes a corpus the default;
the table is that corpus, kept in the spec because the cases are seven one-line changes
to a copy and have no files of their own.

## 12. Owner gate: delegated approval (auto=true), 2026-11-23

- **Authorization.** The owner's invocation `/dvt-milestone:process-phase 4 auto` on
  2026-11-23, within the milestone-wide delegation of 2026-11-21
  (`/dvt-milestone:process-milestone auto`). It covers this spec's ruling. It does not
  cover merging, tagging or posting to GitHub.
- **D1 to D4: as proposed.** These are the agent's rulings under the delegation, not the
  owner's reading of this spec.
- **Instrument.** This prose and the section 8 case table (section 11).
- **Budget.** One review round over the diff (`--subject phase`). A second only if the
  first has a blocking finding; the stop rule of `review-convergence.md` ends it sooner.
- **Compatibility.** No shipped file changes, so no project that takes dev-tools sees a
  difference. A contributor to this repository does: the full suite fails while the
  index is stale (D2).
- **Unreviewed.** No review round reads this spec before the code. The phase's diff
  review reads both.

## 13. Implementation findings

- **IF1, 2026-11-23: the base of the `changed` gate. Delegated amendment (auto=true) to
  section 6.** Section 6's second gate row, kept above, names `changed --base main`, as
  the plan does. Run as written at `076c91d`, it printed
  `changed against main (b685e82): 171 file(s) differ; 0 to fix, 0 warning(s), 0 to reread`
  and exited 0. In this checkout the local branch `main` is at `b685e82`, of 2026-11-15:
  a worktree does not move it, and nothing here pulls it. The command takes the merge
  base with what it is given, so an old `main` makes it judge every file changed since,
  not this change. That is more than was asked, never less, but its `reread:` lines would
  then name other people's changes. The row in `.devtools/project.md` therefore reads
  `changed --base origin/main`, after `git fetch origin`. Run at `076c91d`, that printed
  `changed against origin/main (827e766): 9 file(s) differ; 0 to fix, 0 warning(s), 0 to reread`
  and exited 0. The plan's wording is repaired at the close.
- **IF2, 2026-11-23: what T2 is for, measured.** With `tests` left out of the copy, T2
  and T4 fail and T3, T5, T6 and T7 still pass: each of those four finds its own line
  among the lines an incomplete copy adds. T2 is what notices the copy.
- **IF3, 2026-11-23: each case was seen failing.** With the judgment's parts removed one
  at a time (a pytest plugin kept outside the repository replaced `problems`):
  - without the exit line, T7 failed;
  - without the script's own lines, T3, T5, T6 and T7 failed;
  - without the baseline line, T4 failed;
  - with nothing returned, T3 to T7 failed and T1 and T2 passed.
