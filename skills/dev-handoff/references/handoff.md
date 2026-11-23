# Hand-off reference

What the `dev-handoff` and `dev-takeover` skills both rely on. It works for any
branch at any time; nothing in it depends on a particular workflow.

| Part | Where |
|---|---|
| Script (stdlib only, Python 3.9 and git) | `scripts/handoff.py`: `write`, `check`, `ignored`, `carry` for leaving; `list`, `takeover`, `show`, `pull`, `doctor` for arriving |
| Note, one per branch, committed on the work branch | a file named after the branch in `<planning>/handoffs/`, with each `/` of the branch name written `-` (`phase/03-cache` is `phase-03-cache.md`); `write` and `show` print the path. `<planning>` is `.planning` unless the settings name another folder |
| Settings | `handoff.settings.json` beside the script |

The script commits, pushes and deletes nothing. `carry` and `pull` copy only with
`--yes`, only ignored files, and only between existing checkouts. Every command
takes `--json`, and `--base <branch>` where the base matters. `check` exits 1
while a critical or major finding stands, and `write` exits 1 when the file in
the note's place is not a note (it is left as it is); every other command
exits 0. With `--json`, `show` prints one document: the note's `path`, the
`note` text and the `findings` of the check. A note that lost either snapshot
marker, or both, is rebuilt around the sections it still has. `show`, `list`
and `takeover` never print what looks like a key in a note: it is replaced
with `[removed: looks like a key]`.

## How much to hand over

The effort depends on who continues and where. Say it when you write the note:
the script records it, marks the sections that level needs, and sets how strict
`check` is.

```bash
python3 <tool> write --from claude --to claude --machine same    # level 1
python3 <tool> write --from claude --to codex --machine same     # level 2
python3 <tool> write --from claude --to codex --machine new      # level 3
```

`--to` is `claude`, `codex`, `gemini`, `human` or `any`. `--from` names who is
leaving; without it the script knows only a Claude Code session. With no flags
the note is level 3, the strictest. A later `write` keeps the recorded receiver
unless a flag changes it.

| Level | Case | What the receiver already has | What the note must add |
|---|---|---|---|
| 1 | The same assistant on the same machine: another account of the same tool, or a fresh session | The checkout with its worktrees and uncommitted files, the project's files, the skills | Goal, done so far, next step, open decisions. The other four sections are optional. No push needed |
| 2 | Another assistant or a person, same machine | The checkout. Not your skills, not your private memory, not the session | Every section, written so it stands alone: full instructions instead of "as discussed", file paths and commands instead of skill names |
| 3 | Another machine, any assistant, including a cloud session | Only what is pushed | Level 1 or 2 by assistant, plus everything committed and pushed, and "Outside git" complete. The receiver runs `takeover` |

What differs between assistants:

| | Claude Code | Codex | Another assistant |
|---|---|---|---|
| The project's instruction file | `CLAUDE.md`, which usually takes in `AGENTS.md` | `AGENTS.md` | its own file; point it at both |
| Skills | load by name where they are installed for it | the same, where they are installed for it | plain documents: open the `SKILL.md` a step names |
| Private memory and session history | under its configuration home, per account when accounts use separate homes | under `CODEX_HOME`, per account | its own home |

Two cases that look like level 1 and are not:

- **Another account with a separate configuration home.** The project's files
  and skills still load, but the private memory, the user-level instruction file
  and the session history of the first account are not visible. Either copy the
  project's memory to the new home, or write what matters into "Standing
  instructions". A session can be resumed only by an account that can see its
  history; do not count on it.
- **A cloud session.** It starts from a fresh clone, so it is level 3 even with
  the same assistant and account.

## What check reports

| Finding | Severity | Meaning |
|---|---|---|
| `handoff/secret` | critical | the note contains what looks like a key or token |
| `handoff/missing` | major | the branch has no note |
| `handoff/unfilled` | major | a section the level requires is missing, blank or still the placeholder |
| `handoff/dirty` | major at level 3, else minor | uncommitted files |
| `handoff/no-upstream`, `handoff/unpushed` | major at level 3, else info | the branch, or some of its commits, is not pushed |
| `handoff/ignored` | minor at level 3, else info | ignored paths this branch changed are not in git |
| `handoff/claude-only` | minor | the note for a receiver other than Claude Code names a skill as a slash command |
| `handoff/stash` | minor | stashes exist on this machine only |
| `handoff/optional-empty` | info | an optional section was left empty |

## Files git ignores

Run output, assistant transcripts, local data and reports are ignored by git, so
a push does not move them. The script finds them and copies them to the other
checkout directly, over ssh with rsync for another machine. Nothing ignored is
ever added to git.

```bash
python3 <tool> ignored                                   # what exists here, by kind
python3 <tool> carry --dest buildbox:~/work/app          # the plan (dry run)
python3 <tool> carry --dest buildbox:~/work/app --yes    # copy with rsync over ssh
python3 <tool> carry --dest ../app-second --yes          # another checkout, same machine
```

| Kind | Meaning | Carried |
|---|---|---|
| `carry` | changed since the branch left the base, so this work produced or touched it | yes |
| `old` | unchanged since the branch started | only with `--all` |
| `large` | over `max_mb` (200 MB unless the settings say otherwise) | only with a higher `--max-mb` |
| `key` | looks like a credential file (`.env`, `.keys`, `*.pem`, names with secret, token or credential) | only with `--with-keys`, and only to the user's own machine |
| `rebuild` | environments, caches, build output, other worktrees, and the project's `rebuild_paths` | only when `--include` names the path exactly: it then gets the kind its name, size and age give it. The receiver rebuilds the rest |

- `--include <path or glob>` (repeatable) narrows the copy to what the next step
  needs, and `ignored --include` shows what it selects. A name selects that
  path whole (`runs` is `runs/`, not `runs-private/`) and may lie inside an
  ignored folder (`runs/experiment-1/`). A glob is matched the way Python's
  `fnmatch` does, so `*` also crosses `/`: `runs/*.json` selects every JSON
  file under `runs/`. A glob selects a matching folder whole, else the
  matching files, and does not reach into a `rebuild` path. Neither reaches
  through a link: an ignored link can be named and is copied as a link, what
  lies behind it cannot. Whatever is selected keeps its kind: a key file named
  by its own path is still `key`.
- A copy never replaces what the receiving checkout tracks, even when the
  sending checkout ignores it: not a tracked file of the same name, and not a
  tracked file or link standing where a folder of the copy would go, or inside
  a folder standing where a file would go. The plan names what it left alone.
  For another host the script asks that checkout over ssh what it tracks.
- The destination must already be a checkout: clone it, or add the worktree,
  first. For another host the script asks over ssh before it plans a copy.
- A newer file at the destination is kept; nothing is deleted there. A copy
  on this machine writes a file at its own name or not at all: where a link or
  another kind of file is in the way in the receiving checkout (a link where a
  folder belongs, a folder where the file goes), the file is refused and
  named. To another host the copy is rsync's, which puts a folder in the place
  of an untracked link or file of the same name.
- A key file inside an ignored folder is left out of the folder's copy, and
  `ignored` says how many such paths a folder holds. `--with-keys` sends them.
  This holds for a `rebuild` folder that `--include` names, too.
- `ignored` names the paths it treats as rebuildable. If one of them is data
  (a results folder called `target/` or `dist/`), `--include <that path>`
  carries it.
- The note's snapshot lists the `carry`, `large` and `key` paths, so the receiver
  sees what exists on the old machine even when it was not sent. `check` reports
  them until they are sent or "Outside git" says they are not needed.
- `pull --from-checkout <path or host:path>` is `carry` in the other direction,
  run by the receiver. For another host it sends this script over ssh to list
  the files there, so the old machine needs python3 and git and no copy of the
  script. What that host lists is held to this checkout's rules: a path that
  leaves the checkout or names the checkout itself is dropped, a path this
  checkout does not ignore is refused, and a key file stays a key file.
- Files outside the repository (datasets and models elsewhere on disk, another
  host's run directory) are not found by the script. List them under "Outside
  git".

## A phase or a milestone in progress

The note adds to a workflow's own records; it replaces none of them.

- **Phase workflow.** A phase's status is on its phase branch, not on the base:
  the `STATE.md` frontmatter, the phase directory with its locked tests, plans
  and summaries, and `.continue-here.md` when it is paused mid-task. Leaving:
  pause as `process-phase` says, then write the note, which links the pause file
  and adds what it does not hold (running jobs, spend so far, the user's
  instructions). Arriving: `takeover` names the paused phase; resume it through
  `process-phase`, which reads the pause file. The snapshot records the phase
  and its status from `STATE.md`.
- **Milestone workflow.** A milestone's records are in its own folder under the
  planning folder. Leaving: name the milestone, the phase and the step reached
  under "Goal" and "Next step", and what was approved under "Decisions made".
  Arriving: continue through `process-milestone` or `process-phase`, which read
  those records. An approval the note mentions is confirmed with the user before
  it is relied on.
- A coder or reviewer session of the old machine cannot be resumed elsewhere:
  the next task starts a fresh one from the plan.

## Another checkout on the same machine

- A git worktree (`git worktree add ../app-second <branch>`) shares the
  repository, so every local branch is there without a push. A branch can be
  checked out in one worktree at a time: switch the old one away first.
- A second clone sees only what is pushed, like another machine.
- Either way, uncommitted and ignored files stay in the old checkout: commit,
  then `carry --dest <the other checkout> --yes`.

## New machine

Clone, switch to the work branch, run the project's setup command, then
`python3 <tool> takeover`, which includes the machine checks (`doctor` runs them
alone). It reports the git remote, the base branch, which assistants are on
PATH, and what the project's settings name: tools, the environment the checkout
needs, and key files. It reports only whether a key file exists and never reads
one.

`takeover` says ready when the checkout holds the commit the note was written
at, no ignored path the note was written with is missing (the ones it lists, and
those after the 25th, which it keeps in one line at the end of the snapshot), the
note has a next step, and nothing it marks `[MISSING]` is left: a tool or an
environment path the settings name, and the git remote unless the note is for
the same machine (level 1 or 2). A note from before 0.1.4 that cut its list at
25, a listed path the report cannot read (one holding a line break) or one that
names no file inside the checkout (empty, absolute, or with a `.` or `..` part),
a snapshot without its ignored-files section, and a rest line whose "and N smaller
paths" line is gone count under "ignored paths the
note did not list", and the note is not ready until those paths are checked by
hand. The base branch, the assistants on PATH and key files are
reported as not needed to continue.

What does not come with the clone:

| Item | Where it lives | Action |
|---|---|---|
| Keys | files under the home directory | the user copies them; only the runs that read them need them |
| Assistant logins | each tool's own home | log in again |
| Per-developer settings the project ignores | the old checkout | `carry` or `pull`, or rewrite them |
| An assistant's private memory and session history | outside the repository, per assistant and per machine | not portable between assistants: what matters goes in the note or in the project's instruction file |
| Ignored files inside the checkout | the old checkout | `carry --dest` from the old machine, or `pull --from-checkout` from the new one |
| Data, models and run directories outside the checkout | other paths and hosts | the note's "Outside git" section says where; copy only what the next step needs |
| Git worktrees and stashes | the old machine | commit and push before leaving |

## Settings

Every key is optional; these are the defaults. A project that takes the skills
with the sync sets them in its `.devtools.toml`, in the settings block of the
`dev-handoff` entry.

| Key | Default | Meaning |
|---|---|---|
| `planning_dir` | `".planning"` | the notes are in `<planning_dir>/handoffs/`; the phase workflow's state is read from here too. Keep it the same as the workflow's planning folder |
| `base_branch` | `""` | the branch work branches start from. Empty: the `base_branch` in the phase workflow's `STATE.md`, else the default branch of `origin`, else `main` or `master` |
| `max_mb` | `200` | an ignored path over this size is reported as `large`, not carried |
| `rebuild_paths` | `[]` | more ignored paths the receiver rebuilds instead of copying (a path, or a folder ending in `/`) |
| `tools` | `[]` | commands `doctor` wants on PATH, such as `"uv"` or `"gh"`. A missing one makes `takeover` report not ready |
| `env_paths` | `[]` | paths the checkout has once it is set up, such as `".venv"`; a worktree may find them in the main checkout. A missing one makes `takeover` report not ready |
| `setup_command` | `""` | the command that creates them, such as `"uv sync --frozen"`; `doctor` prints it as the fix |
| `key_files` | `[]` | files under the home directory the project's runs read; `doctor` reports only whether each exists |
