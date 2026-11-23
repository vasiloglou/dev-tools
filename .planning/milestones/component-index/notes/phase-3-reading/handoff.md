# Reading: skills/dev-handoff/scripts/handoff.py

## 1. Header

- Path: `skills/dev-handoff/scripts/handoff.py`
- Lines (`wc -l`): 1266
- Blob SHA (`git hash-object`): `6900a5e83285518548bd11beb6f48639ad6cdcd9`
- Read at commit `3963a46`.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `plugin_root` | 45 | Returns the folder three levels above the script when it is `<plugin>/skills/<skill>/scripts/` beside a `.claude-plugin/plugin.json`, else None. |
| `checkout_root` | 54 | Returns the nearest folder at or above the working directory holding `.git`, else the working directory. |
| `load_settings` | 86 | Merges the settings JSON over `DEFAULT_SETTINGS` (no file, or no script file, gives the defaults) and raises `SystemExit(<message>)` on an unknown key. |
| `_git` | 154 | Runs `git <args>` in `root` with optional stdin and returns stripped stdout, or `""` when git fails. |
| `_relative` | 160 | Returns a path relative to `root` in POSIX form, or the path unchanged when outside it. |
| `_planning` | 167 | Returns `root / planning_dir`. |
| `note_dir` | 171 | Returns `<planning>/handoffs`. |
| `note_path` | 175 | Returns the note file for a branch, with runs of characters other than word, `.` and `-` turned into `-`. |
| `other_notes` | 179 | Lists the `.md` files in the hand-off folder other than `README.md`. |
| `current_branch` | 183 | Returns `git rev-parse --abbrev-ref HEAD`, or `HEAD` when that fails. |
| `_state` | 187 | Reads `current_phase`, `phase_status`, `active_step`, `phase_branch` and `base_branch` from `<planning>/STATE.md` lines by regex. |
| `_paused` | 199 | Lists `<planning>/phases/*/.continue-here.md` files relative to `root`. |
| `base_ref` | 203 | Returns `base` or `origin/<base>`, whichever resolves to a commit sharing history with HEAD, else `""`. |
| `default_base` | 212 | Returns the `base_branch` setting, else STATE.md's `base_branch` (not `null`), else origin's HEAD branch, else `main` or `master` when present, else `main`. |
| `snapshot` | 223 | Collects branch, base, short head, origin URL, upstream and unpushed count, commits ahead of the base (up to 15), uncommitted paths, stash count, STATE.md keys, ignored entries (not rebuild or old), paused phases and instruction files present. |
| `_size` | 253 | Returns bytes, file count, newest mtime and key-file paths for an ignored path without following links, leaving key files and key folders inside a folder out of the counts. |
| `branch_start` | 281 | Returns the commit time of `merge-base(base, HEAD)` as a float, or None. |
| `_rebuilt` | 288 | True when a path has a part in `REBUILD_NAMES`, ends in `.pyc`/`.egg-info`, or lies under `.claude/worktrees/` or a `rebuild_paths` setting. |
| `_max_bytes` | 294 | Returns the size limit in bytes from the argument or the `max_mb` setting. |
| `_key_path` | 298 | True when the path or any folder above it matches the key-file name pattern. |
| `_entry` | 304 | Classifies one ignored path as `rebuild` (unless asked by `--include`), `key`, `old` (newest mtime before `since`), `large` (over the limit) or `carry`, with sizes and inner key paths. |
| `_above` | 322 | Returns the path and each folder above it, outermost first. |
| `_named` | 328 | True when an `--include` name equals the path, is a folder above it, or matches it (or its contents) by `fnmatch`. |
| `_narrow` | 335 | Returns the parts of an ignored path that `--include` asks for: all of it when named, else safe named paths inside a folder (not through links) and glob matches found by walking it unless it is rebuildable, minus paths under a chosen folder. |
| `ignored_inventory` | 366 | Lists `git ls-files --others --ignored --exclude-standard --directory`, narrows by `--include`, classifies each with `_entry` and sorts largest first. |
| `_safe` | 389 | True when a string is a non-empty relative path without `..`, a leading `/`, `~` or `-`, newline or NUL, in normal form. |
| `_recheck` | 397 | Re-applies this checkout's rules to a listing from another host: drops unsafe or unasked paths and unknown kinds, reclassifies rebuild and key paths, keeps only safe inner keys, and marks paths `git check-ignore --no-index` does not ignore as `refused`. |
| `_mb` | 423 | Formats bytes as `N.N MB`. |
| `_n` | 427 | Formats a count with a singular or plural noun. |
| `_in_the_way` | 431 | True when the destination has a link or folder at the file's place, or a link or non-folder at any folder above it. |
| `_copy_local` | 440 | Copies files (links as links) under the chosen paths into the destination, skipping excluded paths, identical links, blocked places (returned as refused) and destination files at least as new. |
| `_is_remote` | 468 | True when a location looks like `host:path` and no local path of that name exists. |
| `_tracked` | 472 | Returns `git ls-files -z` of a checkout as a list. |
| `_clash` | 477 | Returns what a copy from `source` would put over a tracked path: the tracked path, the first non-folder above it, or None when the source has nothing there. |
| `_plan` | 489 | Chooses `carry` (and with keys `key`) entries, drops entries at or under a tracked path and inner paths that would replace tracked files, lists skipped paths by kind and the exclude list, and marks the plan a dry run. |
| `_refused` | 520 | Returns an empty, not-copied plan with a reason. |
| `_rsync` | 524 | Runs `rsync -a -r --update` with anchored, escaped `--exclude` entries and a NUL-separated `--files-from=-` list, recording success or the stderr tail. |
| `_remote_tracked` | 543 | Runs `ssh host "test -e <path>/.git || exit 3; git -C <path> ls-files -z"` and returns the tracked list or a reason string. |
| `carry` | 556 | Checks the destination is a checkout (over ssh for `host:path`, after a path-character check), plans the ignored files changed since the branch start (or all), and with `--yes` copies them by rsync or `_copy_local`. |
| `_remote_inventory` | 590 | Sends this script's own source over ssh to `python3 - ... ignored --json` on the other host and rechecks the JSON it returns, or returns a reason string. |
| `pull` | 608 | The reverse of `carry`: lists the source checkout's ignored files (remotely through `_remote_inventory`), plans against this checkout's tracked files, and with `--yes` copies them in by rsync or `_copy_local`. |
| `level` | 640 | Returns 3 unless `machine` is `same`, then 1 when sender equals receiver and is an assistant, else 2. |
| `detect_sender` | 647 | Returns `claude` when `CLAUDECODE` is set, else `unknown`. |
| `_frontmatter` | 652 | Parses `key: value` lines of a leading `---` block into a dict. |
| `_meta` | 658 | Builds the note's frontmatter: branch, base, date, and from/to/machine from the flag, else the old note's value (an old `unknown` sender is re-detected), else the default, plus the computed level. |
| `_files` | 672 | Formats names as a comma-separated list of code spans. |
| `_receiver_text` | 676 | Returns the snapshot's level-specific instructions for the receiver (instruction files, skills as documents, no approval carried over, the setup command and takeover on a new machine). |
| `_snapshot_text` | 699 | Renders the snapshot block between its markers: receiver lines, branch/head/base, remote and upstream, stashes, STATE.md, paused phases, commits, uncommitted files and up to 25 ignored paths (JSON-escaping control characters), with the rest on one `ignored-rest` JSON comment line. |
| `_head` | 738 | Renders the frontmatter block. |
| `_hint` | 742 | Returns a section's hint comment, marked optional when the level does not require it. |
| `_hints` | 747 | Rewrites every section hint in a note body for the current level. |
| `HandoffError` | 755 | Exception `main` reports on stderr with exit 1. |
| `_new_note` | 759 | Renders a whole note: frontmatter, title, read-first line, snapshot, and each human section with kept text or the placeholder and its hint. |
| `write_note` | 775 | Refreshes the frontmatter, snapshot and hints of a note that has both markers, keeping its text; otherwise rebuilds a note around the filled sections it still has, or raises `HandoffError` for a non-empty file with no sections and no `branch` key. |
| `_skill_names` | 803 | Lists skill folder names under `<root>/.claude/skills/*/SKILL.md` and the plugin's `skills/`. |
| `check_note` | 809 | Returns findings, most severe first: no note, required sections empty for the level, optional ones empty, slash commands of local skills when the receiver is not claude, a secret-looking string, uncommitted files, no upstream or unpushed commits, ignored paths and stashes, with severities lowered when the note's level is 1 or 2. |
| `add` | 818 | Nested in `check_note`: appends one finding dict. |
| `_main_checkout` | 871 | Returns the parent of `git rev-parse --git-common-dir` (the main checkout of a worktree), or `root`. |
| `doctor` | 877 | Returns rows for origin remote, base branch present, each `tools` command on PATH, each `env_paths` path in this or the main checkout, any of claude/codex/gemini on PATH, and `key_files` present under home. |
| `row` | 882 | Nested in `doctor`: appends one row, blanking `fix` when ok. |
| `_redact` | 916 | Replaces PEM private-key blocks and secret-looking tokens with `[removed: looks like a key]`. |
| `_section` | 921 | Returns a `## heading` section's body up to the next `## `, with HTML comments removed. |
| `_first_line` | 927 | Returns a section's first line, or `""` when empty or still the placeholder. |
| `available` | 932 | Reads, through `git cat-file --batch-check` and `git show`, the note of every local and `origin` branch, keeps those whose frontmatter `branch` matches, merges local and origin copies by newest `updated`, and sorts newest first. |
| `_ignored_rest` | 974 | Parses the `ignored-rest` comment line and returns its list only when it is valid JSON of `{path, kind}` items of kinds carry/large/key and exactly `count` long. |
| `takeover` | 990 | Runs `doctor`, reads the current branch's redacted note, checks its snapshot head against HEAD, reads back every listed ignored path (bullets, escaped bullets and the rest line) to find missing ones and missing keys, counts unreadable lines as unlisted, and sets `ready` from head, missing and unlisted paths, blocking rows and a filled next step. |
| `_render_findings` | 1081 | Formats check findings as text. |
| `_render_available` | 1092 | Formats the available hand-offs as text. |
| `_render_takeover` | 1105 | Formats the takeover report, with pull hints, blocking and non-blocking doctor rows and the next step. |
| `_render_ignored` | 1140 | Formats the inventory by kind, summarising old and rebuild entries. |
| `_render_carry` | 1159 | Formats a carry or pull plan with its skipped, refused and left-alone paths. |
| `_render_doctor` | 1176 | Formats doctor rows. |
| `main` | 1184 | Parses one positional command and shared options, resolves the root (`--repo` or the checkout), dispatches, and for write/check/show runs `check_note` and prints its findings, exiting 1 only for `check` with a critical or major finding. |
| `out` | 1214 | Nested in `main`: prints JSON or text and returns 0. |

Counted with
`python3 -c "import ast,sys; t=ast.parse(open(sys.argv[1]).read()); print(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(t)))" skills/dev-handoff/scripts/handoff.py`:
74 (the lambda in `_hints` at `:751` is not a `FunctionDef`).

## 3. Commands

One parser: the command is a positional choice and every option is accepted with every command (`:1185-1208`). `--json` prints the same data as JSON (`:1215`). `--repo DIR` sets the checkout (`:1210`); not a git checkout exits 2 (`:1211-1212`).

| Command and options | Reaches | Writes |
|---|---|---|
| `write [--to claude\|codex\|gemini\|human\|any] [--from WHO] [--machine same\|new] [--base REF]` | `snapshot` 223, `write_note` 775, `check_note` 809 | `<planning>/handoffs/<branch>.md`; stderr `wrote <path>`; stdout the check findings; exit 0, or 1 when the file in the note's place is not a note (`:1246-1248`). |
| `check [--base REF]` | `check_note` 809 | Nothing; stdout findings; exit 1 on a critical or major finding (`:1261-1262`). |
| `show [--base REF]` | `check_note` 809, `_redact` 916 | Nothing; stdout the redacted note then findings, or "no hand-off note" with the other notes; exit 0. |
| `ignored [--all] [--include GLOB ...] [--max-mb N] [--base REF]` | `ignored_inventory` 366 | Nothing; stdout the inventory by kind; exit 0. |
| `carry --dest PATH\|HOST:PATH [--include ...] [--with-keys] [--all] [--max-mb N] [--base REF] [--yes]` | `carry` 556 | Without `--yes` nothing; with it, files in the other checkout (rsync or local copy); stdout the plan; exit 0 even when not copied; no `--dest` exits 2 (`:1233-1235`). |
| `pull --from-checkout PATH\|HOST:PATH [same options]` | `pull` 608 | Without `--yes` nothing; with it, files in this checkout; stdout the plan; exit 0; no source exits 2. |
| `list` | `available` 932 | Nothing; stdout the hand-offs on local and origin branches; exit 0. |
| `takeover` | `takeover` 990 | Nothing; stdout the report ending "ready to continue" or "NOT ready"; exit 0 either way. |
| `doctor` | `doctor` 877 | Nothing; stdout one row per check; exit 0 either way. |
| any | `load_settings` 86 at import (`:97`) | An unknown setting raises `SystemExit(<message>)`: exit 1 (same pattern confirmed on a temp copy of review_tool.py; not run for this script). |

## 4. The entry, claim by claim

| Claim | Verdict | Settled by |
|---|---|---|
| does: Hand a branch to another assistant, developer or machine | true | `handoff.py:775-800`, `:139-148` |
| does: and take one over | overstated | `takeover` checks and reports (`:990-1078`); it does not switch, fetch or pull the branch, and reads the note of the branch already checked out (`:997-998`). |
| does: write the note | true | `handoff.py:775` |
| does: check it | true | `handoff.py:809` |
| does: carry ignored files | true | `handoff.py:556` |
| does: takeover says ready or not | true | `handoff.py:1071-1077`, `:1135` |
| verb: hand off | true | `handoff.py:775` |
| verb: handoff note | true | `handoff.py:171-176` |
| verb: take over | overstated | As the `does` row above (`:990`). |
| verb: takeover ready | true | `handoff.py:1071` |
| verb: continue on another machine | true | `handoff.py:147`, `:693-695` |
| verb: switch assistant | true | `handoff.py:640-644`, `:1191` |
| verb: carry ignored files | true | `handoff.py:556` |
| verb: pull ignored files | true | `handoff.py:608` |
| verb: what would be lost | true | `handoff.py:811`, `:1083` |
| verb: list handoffs | true | `handoff.py:932` |
| verb: doctor | true | `handoff.py:877` |
| verb: snapshot of the checkout | true | `handoff.py:223`, `:699` |
| verb: key files | true | `handoff.py:127-130`, `:902-908` |
| verb: ignored inventory | true | `handoff.py:366` |
| verb: resume work elsewhere | vague | No body names it; nearest are `takeover` (`:990`) and `pull` (`:608`). |
| notes: Read: the module docstring and the documented functions, and during phase 1 of component-index the snapshot and takeover code. | stale | A process note; this reading replaces it. |
| notes: carry and pull are dry runs until --yes. | true | `handoff.py:581-582`, `:631-632`, `:516` |

## 5. What the entry leaves out

- Three hand-off levels (same assistant and machine, other assistant, other machine) set which sections are required and how severe findings are (`:139-148`, `:640-644`, `:827-828`, `:850-858`).
- `check` flags a note containing what looks like a key or token, as critical (`:846-848`).
- `check` flags slash commands of local skills when the receiver is not Claude Code (`:838-845`).
- Notes and listings are printed with keys redacted (`:916-918`, `:951`, `:1019`, `:1257`).
- `show` prints the note and its check (`:1251-1259`).
- The base branch is found from the setting, STATE.md, origin's HEAD, then main/master (`:212-220`).
- The snapshot reads STATE.md phase keys and paused phases (`.continue-here.md`) (`:187-200`, `:712-715`).
- Ignored files are sorted into carry, rebuild, key, old (unchanged since the branch started) and large (`:304-316`); `--all` lifts the age filter (`:575`, `:1219`).
- `--include` narrows to paths or globs, even inside an ignored folder (`:335-363`).
- A copy never replaces a file the receiving checkout tracks, and never writes through a link (`:489-517`, `:431-437`, `:454-461`).
- A remote listing is rechecked here, and paths this checkout does not ignore are refused (`:397-420`).
- Pull from another host runs this script there over ssh on stdin, needing only python3 and git there (`:590-605`).
- Remote copies go by rsync over ssh (`:524-536`, `:539`).
- `doctor` checks configured tools, environment paths (also in the main checkout of a worktree), assistants on PATH and key files under home (`:877-909`, `:871-874`).
- Takeover reads back every listed ignored path, including ones past the 25th and JSON-escaped ones, and blocks on unreadable lines (`:1029-1062`, `:974-987`).
- Settings: planning_dir, base_branch, max_mb, rebuild_paths, tools, env_paths, setup_command, key_files (`:66-83`).

## 6. Docstring against body

- Module docstring (`:21-22`) says "no key is read"; with `--with-keys`, `carry` and `pull` copy key files (`:497`, `:463`, `:531`).
- Module docstring (`:10`) shows `write` as writing the note; `main` then runs `check_note` and prints its findings, and `write` exits 0 whatever they say (`:1255-1262`).
- Module docstring (`:23-24`) lists exit codes 0, 1 (check, write) and 2; an unknown setting exits 1 at import (`:92`, `:97`).
- `--from` help says "default: detected" (`:1192`); `detect_sender` detects Claude Code only and records `unknown` under Codex or Gemini (`:647-649`), which makes such a note level 2 or 3, never 1 (`:644`).
- `takeover`'s docstring (`:993-995`) names head, absent ignored files and doctor; the body also blocks on ignored lines it cannot read back (`:1042`, `:1057`, `:1074`) and on a missing remote only at level 3 (`:1067-1070`), and never blocks on missing keys or the base branch (`:1064-1066`).
- `list` (`:14`) and `available` (`:935`) read local and `origin` refs only; nothing fetches (`:938`).
- Under a plugin install the settings file is found from the working directory at import (`:63-65`, `:97`), not from `--repo` (`:1210`), so `--repo` with a plugin reads the settings of the checkout the command runs in.
- On the other host of a remote `pull` the script has no file, so it runs with default settings there (`:42`, `:63`); the local `_recheck` reapplies this checkout's rebuild and key rules (`:408-409`).
- Module docstring (`:6-7`) says the snapshot holds "ignored files"; it holds only those not rebuildable and changed since the branch started (`:233-234`), and shows at most 25 as bullets (`:727-733`).

## 7. Other scripts

- `handoff.py:600-601`: `subprocess.run([ssh, host, "python3 - --repo <path> ... ignored --json"], input=<this script's source>)`, running itself on another host.
- `handoff.py:546`: `subprocess.run([ssh, host, "test -e <path>/.git || exit 3; git -C <path> ls-files -z"])`.
- `handoff.py:531`: `subprocess.run(["rsync", "-a", "-r", "--update", ...])`.
- `handoff.py:156`: `subprocess.run(["git", ...])` for every git read.
- Builds no path to another script of this repository; `_skill_names` reads `SKILL.md` file names only (`:805-806`).
- Same-named helpers in other shipped scripts:
  - `plugin_root` (`:45`): same body in `skills/components/scripts/components_index.py:94`, `skills/components/scripts/rules_check.py:230`, `skills/milestone/process-phase/scripts/review_tool.py:64`, `skills/phase/process-phase/scripts/coder_pool.py:50`, `skills/phase/process-phase/scripts/phase_tool.py:47`.
  - `checkout_root` (`:54`): same body in `components_index.py:103`, `rules_check.py:239`, `review_tool.py:73`, `coder_pool.py:59`, `phase_tool.py:56`.
  - `load_settings` (`:86`): also in those five; handoff's body is its own (it accepts `path=None`).
  - `main` (`:1184`): every shipped script has one.
  - `_git` (`:154`) has no namesake; the scripts' `git` helpers are listed in review_tool.md and release_plugins.md.

## 8. Proposed entry

```
- does: Hand a branch to another assistant, developer or machine: write the note with a regenerated snapshot of the checkout, check what would be lost at its hand-off level, list the ignored files by kind, carry or pull them (dry run until --yes; rsync over ssh for host:path), list the notes on local and origin branches, and on the receiving side takeover and doctor say whether this checkout and machine are ready (handoff.py)
- verbs: hand off, handoff note, takeover ready, continue on another machine, switch assistant, carry ignored files, pull ignored files, what would be lost, list handoffs, doctor, snapshot of the checkout, key files, ignored inventory, hand-off level, show note, redact keys in note, secret in note, slash commands in note, paused phase, base branch detection, rebuild paths, include glob, tracked files never replaced, ssh pull, rsync, machine check
- notes: takeover checks and reports; it does not switch or fetch the branch. carry and pull are dry runs until --yes and never replace a file the receiving checkout tracks. A pull from another host sends this script over ssh on stdin. Only Claude Code is detected as the sender.
```


## Addendum: the phase-1-r3 repair

Written by the driving agent after `e2b2762`, which added three definitions (77 now, by the
same count) and changed `takeover`, `write_note` and `check_note`:

| Name | Line | What the body does |
|---|---|---|
| `_inside` | 992 | True when a path, as a note wrote it, is relative and has no empty, `.` or `..` part, a folder's trailing `/` aside. |
| `_split_end` | 1000 | Splits a text at its first line that is the snapshot end marker alone, or returns None. |
| `_exists` | 1007 | `Path.exists()`, with a lookup the file system refuses read as False. |

`takeover` now ends the snapshot with `_split_end`, counts a snapshot without its ignored
section as unlisted, refuses a bullet or rest path that `_inside` rejects, and checks with
`_exists`; `write_note` and `check_note` find the end marker with `_split_end`.

## Addendum: the phase-1-r4 repair

Written by the driving agent after `22d6258`, which added one definition (78 now):

| Name | Line | What the body does |
|---|---|---|
| `_one_line` | 740 | A path as the snapshot prints it outside the ignored list: JSON-escaped when it holds a control character or line separator, else as it is. |

`_snapshot_text` prints uncommitted and paused-phase paths through `_one_line`. `takeover`
reads the paths from the note before redaction and redacts only what it reports, counts a
rest line without its cut line as unlisted, and `doctor` checks `env_paths` and
`key_files` with `_exists`.
