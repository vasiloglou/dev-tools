# Reading: skills/milestone/process-phase/scripts/review_tool.py

## 1. Header

- Path: `skills/milestone/process-phase/scripts/review_tool.py`
- Lines (`wc -l`): 871
- Blob SHA (`git hash-object`): `c8b13797a55f111da4789891b5b54453a3c8d464`
- Read at commit `3963a46`.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `plugin_root` | 64 | Returns the folder three levels above the script when it is `<plugin>/skills/<skill>/scripts/` beside a `.claude-plugin/plugin.json`, else None. |
| `checkout_root` | 73 | Returns the nearest folder at or above the working directory holding `.git`, else the working directory. |
| `Stop` | 117 | Exception class `main` turns into `error:` on stderr and exit 2. |
| `load_settings` | 121 | Merges the settings JSON over `DEFAULT_SETTINGS`, raising `SystemExit(<message>)` on an unknown key or a `reviewer` other than auto, codex or claude. |
| `now` | 134 | Returns the UTC time in ISO form, to the second unless `precise`. |
| `sha256` | 139 | Returns the hex SHA-256 of a file's bytes. |
| `git` | 143 | Runs `git -C <root> <args>` capturing UTF-8 output, raising `CalledProcessError` when `check`. |
| `repo_root` | 148 | Runs `git rev-parse --show-toplevel` in the working directory and returns it, or raises `Stop`. |
| `looks_secret` | 155 | True when a path matches the credential-name pattern and does not end in `.example`, `.sample`, `.template` or `.dist`. |
| `write_json` | 159 | Writes sorted, indented JSON to a `.tmp` sibling and renames it into place. |
| `read_json` | 165 | Returns a file's JSON, or `{}` when the file is absent. |
| `shown` | 169 | Returns a path relative to the repository root when inside it, else its absolute path. |
| `unquote` | 177 | Decodes a git C-quoted path (octal and backslash escapes) back to text; an unquoted path passes through. |
| `strip_prefix` | 197 | Unquotes a diff path and removes a one-letter `a/`-style prefix. |
| `header_paths` | 201 | Parses both paths of a `diff --git` line, handling quoted paths and unquoted paths that contain spaces. |
| `split_diff` | 214 | Splits a unified diff into `(paths, block)` per file, collecting paths from the header's `diff --git`, rename/copy and `---`/`+++` lines and skipping `/dev/null`. |
| `without_secrets` | 239 | Drops every diff block that names a credential path on either side and returns the rest with the dropped paths. |
| `cmd_brief` | 253 | Validates the options, gathers files (named, changed since `--base` plus all untracked, or the PR diff), writes `diff.patch`, `BRIEF.md`, `brief.json` and an empty `FINDINGS.md`, and prints left-out paths and the brief's SHA-256. |
| `add` | 271 | Nested in `cmd_brief`: adds one repository file with its SHA-256, refusing a named credential, folder, missing file or outside path, and silently leaving out, recording as deleted or skipping unnamed ones and files inside the round folder. |
| `brief_text` | 363 | Renders `BRIEF.md`: reviewer stance, question, claims to test, the change (PR head and checkout state, base, or files at head), notes, the file/SHA table, read-only rules and the required answer shape ending in `VERDICT:`. |
| `ledger_text` | 423 | Renders `FINDINGS.md` with the fill-in rules and an empty table of `LEDGER_COLUMNS`. |
| `load_brief` | 442 | Reads `<dir>/brief.json` or raises `Stop`. |
| `changed_files` | 450 | Lists brief files that are missing or whose SHA-256 differs; its `out` parameter is unused. |
| `pick_reviewer` | 461 | Returns `--reviewer` or the setting, resolving `auto` to codex under `CLAUDECODE`, claude when any `CODEX_*` variable is set, else `Stop`. |
| `command` | 472 | Builds the reviewer argv with `{dir}` placeholders: `codex exec --ephemeral` read-only with model/effort and `-o {dir}/review.md`, or `claude -p --permission-mode plan`, plus which file gets stdout. |
| `preconditions` | 486 | Reports a reviewer binary not on PATH, and for codex runs `codex login status` and reports a non-zero exit. |
| `cmd_run` | 496 | Refuses a round that has `run.json`, prints the command for `--dry-run`, checks file bytes and preconditions (exit 1 when either fails), writes `run.json`, then runs `watch` in the foreground (`--wait`) or spawns `review_tool.py _watch` detached. |
| `watch` | 527 | Marks the run running, rechecks file bytes, runs the reviewer with stdin closed and the timeout, appends stderr to `review.log`, and records done or failed (including exit 0 with an empty review) with the review's SHA-256. |
| `rounds` | 564 | Returns each path that holds `brief.json`, or every round folder found recursively under a folder; anything else raises `Stop`. |
| `alive` | 576 | True when `os.kill(pid, 0)` succeeds. |
| `run_state` | 584 | Returns the recorded state, or `stopped` when a starting/running run's pid is dead. |
| `split_row` | 591 | Splits a Markdown table row into trimmed cells, honouring escaped pipes and optional outer pipes. |
| `ledger_rows` | 599 | Returns the rows of the first table whose header starts with `Id`, up to the next heading or the next table. |
| `says_none` | 624 | True when a line of the ledger is exactly `No findings.`. |
| `ledger_problems` | 628 | Checks every ledger row: first five cells filled, Reproduced yes/no, Class and Disposition from the lists, not open, fixed needs reproduced, a resolvable `Repaired at` commit and Notes, deferred/rejected need Notes; an empty finished ledger needs `No findings.`. |
| `cmd_status` | 669 | For each round (oldest first) reports run state, ledger problems, review.md and BRIEF.md digests against `run.json`, a home path in review.md and the round's own `diff.patch`; then marks each file reviewed, unreviewed or missing by the latest round that listed it; exit 1 on any problem. |
| `run_gh` | 741 | Runs `gh <args>` with stdin closed and returns stdout, raising `Stop` when `gh` is missing or fails. |
| `pr_view` | 750 | Returns a PR's number, url, title, head and base SHAs from `gh pr view --json`. |
| `cmd_post` | 756 | Requires a done run, a PR number, no earlier `posted.json` (unless `--again`) and a review.md matching a recorded digest; builds the comment with the PR's current head, prints it without `--yes`, else posts it with `gh pr comment --body-file` and writes `posted.json`. |
| `cmd_sanitize` | 800 | Replaces the repository root with `<repo>` and the home folder with `<home>` in review.md and review.log, prepends a comment to review.md and records `sanitized_sha256` in `run.json`. |
| `main` | 830 | Parses `brief`, `run`, `status`, `post`, `sanitize` and the hidden `_watch`, loads settings (not for `_watch`) and maps `Stop` to exit 2. |

Counted with
`python3 -c "import ast,sys; t=ast.parse(open(sys.argv[1]).read()); print(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(t)))" skills/milestone/process-phase/scripts/review_tool.py`:
41.

## 3. Commands

| Command and options | Reaches | Writes |
|---|---|---|
| `brief DIR --subject plan\|spec\|phase\|close\|pr --question TEXT [--file PATH ...] [--claim TEXT ...] [--base REF] [--pr N]` | `cmd_brief` 253 | `DIR/BRIEF.md`, `DIR/brief.json`, `DIR/FINDINGS.md`, and `DIR/diff.patch` with `--base` or `--pr` (`:333-355`); stdout `left out:` lines, `wrote ... SHA-256 ...`, `next: ...`; exit 0, or 2 on a non-empty DIR, a missing per-subject option, `--base` with `--pr`, a named credential/folder/missing/outside file, a bad base, a PR that moved, or `gh` failing. |
| `run DIR [--reviewer codex\|claude]` | `cmd_run` 496 -> detached `_watch` | `DIR/run.json`; then (from `_watch`) `DIR/review.md`, `DIR/review.log`, final `run.json`; stdout `started ...`; exit 0, 1 when a file changed or a precondition failed, 2 when already run or no reviewer resolves. |
| `run DIR --wait` | `cmd_run` 518 -> `watch` 527 | As above in the foreground; exit 0 done, 1 failed. |
| `run DIR --dry-run` | `cmd_run` 504-506 | Nothing; stdout the reviewer command with the folder filled in; runs even when the round was already run. |
| `status PATH [PATH ...] [--format text\|json]` | `cmd_status` 669 | Nothing; stdout per-round lines and `problem:` lines and per-file `reviewed`/`unreviewed`/`missing`, or one JSON document with `rounds`, `coverage`, `ok`; exit 1 on any problem or non-reviewed file, 2 when no round is found. |
| `post DIR [--pr N] [--again]` | `cmd_post` 756 | Nothing; stdout the comment and `not posted: ...`; calls `gh pr view` (`:771`). |
| `post DIR --yes` | `cmd_post` 789-796 | A PR comment through `gh pr comment`, `DIR/posted.json`; stdout `posted: <url>`. |
| `sanitize DIR` | `cmd_sanitize` 800 | Rewrites `DIR/review.md` and `DIR/review.log` in place and `sanitized_sha256` in `DIR/run.json`; stdout one line per file. |
| `_watch DIR` (internal) | `watch` 527 | As `run --wait`, without loading settings. |
| any | `load_settings` 121 | A bad settings file raises `SystemExit(<message>)`: exit 1 (ran a temp copy under the scratchpad with `{"bogus": 1}` beside it: `status .planning` printed the message and exited 1). |

## 4. The entry, claim by claim

| Claim | Verdict | Settled by |
|---|---|---|
| does: Run one independent review round | true | `review_tool.py:253`, `:496`, `:527` |
| does: brief writes the question and file hashes | true | `review_tool.py:338-354`, `:405` |
| does: run starts the other tool as reviewer | true | `review_tool.py:461-469`, `:472-483`, `:520-522` |
| does: status | true | `review_tool.py:669-736` |
| does: post | true | `review_tool.py:756-797` |
| does: sanitize | true | `review_tool.py:800-827` |
| verb: independent review | true | `review_tool.py:365-367` |
| verb: review round | true | `review_tool.py:256-257` |
| verb: review brief | true | `review_tool.py:363` |
| verb: findings ledger | true | `review_tool.py:423-437`, `:628-666` |
| verb: run reviewer | true | `review_tool.py:496` |
| verb: codex review | true | `review_tool.py:474-481` |
| verb: claude reviewer | true | `review_tool.py:482-483` |
| verb: reviewed or unreviewed | true | `review_tool.py:710-722` |
| verb: review status | true | `review_tool.py:669` |
| verb: post review to pull request | true | `review_tool.py:792` |
| verb: sanitize review | true | `review_tool.py:800` |
| verb: plan review | true | `review_tool.py:97`, `:266-267` |
| verb: phase diff review | true | `review_tool.py:99`, `:264-265`, `:299-324` |
| verb: close review | true | `review_tool.py:100`, `:266-267` |
| verb: pr review | true | `review_tool.py:101`, `:262-263`, `:325-329` |
| notes: Read: the module docstring and the documented functions. | stale | A process note; this reading replaces it. |
| notes: A brief refuses a credential file it is asked to name | true | `review_tool.py:277-279` |
| notes: and leaves out one a diff would bring in | true | `review_tool.py:312-319`, `:327`, `:280`, `:335`; renames to or from a credential name are left out too (`:245`, `:312`). |

## 5. What the entry leaves out

- `run` refuses to start when a listed file's bytes changed since the brief, and `watch` rechecks just before launch (`:507`, `:531-536`).
- `run` refuses a round already run: a new round is a new brief (`:500-501`).
- `run --dry-run` prints the reviewer command; `--wait` runs in the foreground (`:504-506`, `:518-519`).
- The reviewer runs detached with a timeout (`timeout_minutes`, default 60) and is recorded failed when it exits 0 with no review (`:520-522`, `:543-553`).
- `auto` picks the reviewer from the environment: codex under Claude Code, claude under Codex (`:465-468`).
- Codex runs `--sandbox read-only`, claude `--permission-mode plan`; codex login is checked first (`:478`, `:482`, `:490-492`).
- Settings: reviewer, codex_model, codex_effort, claude_model, timeout_minutes, in `review_tool.settings.json` or `.devtools/` under a plugin (`:82-95`).
- `--claim` lists claims for the reviewer to try to break (`:369-373`).
- `--base` takes renames into account and adds every untracked file as "new" (`:305-306`, `:320-324`).
- The brief records head and dirty state and tells the reviewer how to read the PR's bytes when the checkout is elsewhere (`:296-297`, `:379-389`).
- `status` validates the ledger row by row: reproduced, class, disposition, `Repaired at` resolves to a commit, Notes for fixed, deferred and rejected (`:628-666`).
- `status` flags a review.md that is not the reviewer's output, a BRIEF.md changed after the review, a home path in review.md and a changed `diff.patch` (`:692-706`).
- `status --format json` (`:724-726`).
- `post` notes when the PR head moved after the review, includes the ledger, refuses a comment over 60,000 characters and records `posted.json` (`--again` to repost) (`:776-784`, `:765-766`, `:795`).
- `brief --pr` refuses when the PR head moves while the brief is written (`:326-329`).
- Credential-name pattern and sample suffixes that are not credentials (`:109-114`).

## 6. Docstring against body

- Module docstring (`:42-43`) gives exit 2 for "the command could not run"; a bad settings file raises `SystemExit(<message>)` (`:127`, `:130`), which exits 1, the code the docstring keeps for "a check found something" (confirmed on a temp copy, section 3).
- Module docstring (`:37-38`) says `post` "shows the comment" and posts only with `--yes`; the preview already calls `gh pr view` (`:771`), so it needs `gh` and the network.
- Module docstring (`:17-19`) says `--base` adds "every changed or new file"; the body adds every untracked, not-ignored file of the whole repository (`:320-322`), whether the phase made it or not.
- Module docstring (`:32-35`) says `status` reports files whose bytes changed after the last round that read them; the body also marks a file unreviewed when that latest round is not done (`:718-720`), reports `missing` (`:713-714`), and "last" means latest by brief `created` among the rounds under the paths given (`:677-678`, `:708`).
- Module docstring (`:39-40`) says `sanitize` replaces "this machine's absolute paths"; the body replaces only the repository root and the home folder (`:803`) and also records `sanitized_sha256` in `run.json` (`:821-825`).
- Module docstring (`:25-30`) does not say `run` refuses a round already run (`:500-501`), checks `codex login status` (`:490-492`) or fails a run that exited 0 with an empty review (`:552-553`).
- Module docstring (`:45-46`) says the plugin settings are in "the project's" `.devtools/`; the project is the checkout found from the working directory by `.git` (`:73-76`, `:82`).
- `changed_files` takes `out` and never uses it (`:450-458`).
- `--help` lists the internal `_watch` command among the choices (`:856`).

## 7. Other scripts

- `review_tool.py:520-522`: `subprocess.Popen([sys.executable, <this file>, "_watch", <dir>])`, the script running itself detached.
- `review_tool.py:542-543`: `subprocess.run` of the reviewer, `codex exec ...` or `claude -p ...` (`:474-483`).
- `review_tool.py:490`: `subprocess.run(["codex", "login", "status"])`.
- `review_tool.py:144`, `:149`: `subprocess.run(["git", ...])`.
- `review_tool.py:744`: `subprocess.run(["gh", ...])` for `pr view`, `pr diff`, `pr comment`.
- Runs no other script of this repository; the brief and ledger point at `review-convergence.md` in text only (`:429`).
- Same-named helpers in other shipped scripts:
  - `plugin_root` (`:64`): same body in `skills/components/scripts/components_index.py:94`, `skills/components/scripts/rules_check.py:230`, `skills/dev-handoff/scripts/handoff.py:45`, `skills/phase/process-phase/scripts/coder_pool.py:50`, `skills/phase/process-phase/scripts/phase_tool.py:47`.
  - `checkout_root` (`:73`): same body in the same five scripts (`components_index.py:103`, `rules_check.py:239`, `handoff.py:54`, `coder_pool.py:59`, `phase_tool.py:56`).
  - `load_settings` (`:121`): also in those five; review_tool's body is its own (it adds the reviewer check).
  - `Stop` (`:117`): also `devtools/release_plugins.py:44`, `devtools/from_gsd.py:71`.
  - `git` (`:143`): also `components_index.py:980`, `codex_gate.py:14`, `phase_tool.py:221`, `devtools/from_gsd.py:428`, `devtools/release_plugins.py:48`; each body differs.
  - `read_json` (`:165`): same body in `devtools/sync.py:174`.
  - `shown` (`:169`): also `devtools/from_gsd.py:85`, a different function (formats a phase id).
  - `cmd_status` (`:669`): also `phase_tool.py:471`, `release_plugins.py:110`.
  - `main` (`:830`): every shipped script has one.

## 8. Proposed entry

```
- does: Run one independent review round in its own folder: brief writes the question, claims and every file's SHA-256 (a phase's diff from --base, a PR's from gh), run starts the other harness read-only after checking the bytes, status checks the run, the findings ledger and which files are unreviewed, post shows then (with --yes) comments on the PR, sanitize strips local paths (review_tool.py)
- verbs: independent review, review round, review brief, findings ledger, run reviewer, codex review, claude reviewer, reviewed or unreviewed, review status, post review to pull request, sanitize review, plan review, phase diff review, close review, pr review, claims to test, brief sha256, bytes changed since brief, reviewer timeout, auto reviewer, ledger validation, repaired at commit, pr head moved, credential files left out
- notes: A brief refuses a credential file it is asked to name, and leaves out one (or a rename of one) a diff would bring in. run spawns itself as _watch in the background; a round is never run twice. post's preview already calls gh. A bad settings file exits 1, not 2.
```
