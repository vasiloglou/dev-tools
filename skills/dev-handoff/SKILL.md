---
name: dev-handoff
description: The leaving side of moving work on a branch to another coding assistant (Claude Code, Codex, Gemini), another account of the same assistant, another developer, another machine or a second checkout. Commits the work, writes and checks the branch's hand-off note in the planning folder (goal, verified progress, next step, decisions, standing instructions, jobs and data outside git), pushes when the work changes machine, and copies the files git ignores (run output, transcripts, local data) to the other checkout, over ssh for another machine. The effort follows three levels -- same assistant on the same machine, another assistant, another machine. Use when the user says to hand off, switch assistant, account or machine, continue elsewhere, pause for later, or move a phase or milestone in progress. The receiving side uses dev-takeover. Not for preparing or reviewing a pull request.
argument-hint: "[branch] [--to claude|codex|gemini|human|any] [--machine same|new] [--dest path-or-host:path]"
---

# Hand work to another assistant or machine

Git carries the code. It does not carry what this session knows: the goal, what
was verified, the next step, decisions settled with the user, jobs still running
elsewhere, and anything held in one assistant's private memory. The hand-off note
carries those. This skill is the leaving side; the receiving side follows
`dev-takeover`.

The script is `.claude/skills/dev-handoff/scripts/handoff.py`, run with `python3`
from the project root; below, `<tool>` is that script. It needs only Python and
git, commits and pushes nothing, and copies files only with `--yes`. Levels, the
kinds of ignored files, a phase or milestone in progress and the project's
settings are in [references/handoff.md](references/handoff.md). If
`./references/project.md` exists beside this file, read it first: a project can
name what its runs leave outside git and where its other machines are.

## What was asked

| Said | Values | Default | Meaning |
|---|---|---|---|
| a branch | a branch name | the current branch | the branch to hand over |
| `--to` | `claude`, `codex`, `gemini`, `human`, `any` | `any` | who continues |
| `--machine` | `same`, `new` | `new` | where the work continues |
| `--dest` | a path, or `host:path` | none | the receiving checkout; ignored files are sent there |

All of it can be said in plain words ("hand this to codex on the build machine").
With nothing said, the current branch is handed over at level 3, the strictest.
Do not ask which branch: it is the current one unless the user names another. The
script works on the checked-out branch, so for another branch switch to it first,
and only with a clean tree. If who continues or where is unclear and it changes
the level, ask in one line.

## Level

| Level | Case | Flags | Note |
|---|---|---|---|
| 1 | the same assistant on this machine: another account, or a fresh session | `--to <you> --machine same` | goal, done so far, next step, open decisions |
| 2 | another assistant or a person on this machine | `--to <them> --machine same` | every section, standing alone |
| 3 | any other machine, or a cloud session | `--machine new` | level 1 or 2, plus pushed and "Outside git" complete |

Pass `--from` with your own name (`claude`, `codex`, `gemini`, `human`) on every
`write`: the script cannot always tell who is running it, and without it the
level is 2 where 1 was meant.

At level 1, check that the other account sees this project's memory. If it uses a
separate configuration home, it does not: copy the memory lines that bear on this
work into "Standing instructions". At level 2 the receiver loads none of your
skills and none of your memory: write paths and commands, not skill names, and
copy the instructions in full.

## Procedure

Do the whole procedure; do not stop at the note.

1. **Commit the work** on its branch. Unfinished work goes in a `wip:` commit; a
   stash or an untracked file stays on this machine. A phase paused mid-task is
   paused the way its workflow says first (the phase workflow's
   `.continue-here.md` and `wip(NN): pause at <task>`). Ask before committing
   files that are not yours.
2. **Write the note.**

   ```bash
   python3 <tool> write --from <you> --to <who> --machine <same|new>
   ```

   It creates the note, or refreshes its snapshot and keeps what was filled, and
   prints the path: a file named after the branch, with each `/` written `-`.
   Then fill the sections that level requires from this session:
   what you know that the code does not show.

   | Section | Write |
   |---|---|
   | Goal | what the branch is for and what done means; link the issue, phase, milestone or request |
   | Done so far | what works, with the test command and its result |
   | Next step | one concrete action the reader can start without asking |
   | Open decisions and blockers | questions waiting on the user, failing tests, known defects |
   | Decisions made | choices settled with the user, so they are not reopened |
   | Standing instructions | the user's instructions for this work that sit only in this conversation or in your private memory |
   | Outside git | every job still running elsewhere (host, directory, how to check and stop it), data and model locations, open PRs and issues, spend so far and the budget it counts against, live deployments |
   | Commands | the exact commands for the focused tests and for continuing |

   Write `none` where nothing applies. Name the file that holds a key; never its
   value.
3. **Check the note, then commit it.**

   ```bash
   python3 <tool> check
   ```

   Run it before the commit, so that a key pasted into the note never reaches
   git history or the remote: remove what it reports as a key or token, and
   fill each section it names. The note itself still shows as uncommitted here,
   and at level 3 as unpushed; this step settles both. Commit the note. At
   level 3 push the branch (`git push -u origin <branch>`): a hand-off to
   another machine is the user's request to push this branch. Never push the
   base branch or a release branch.
4. **Send the ignored files the next step needs.**

   ```bash
   python3 <tool> ignored
   python3 <tool> carry --dest <path or host:path>
   python3 <tool> carry --dest <path or host:path> --yes
   ```

   `ignored` lists what git does not hold here, by kind, and names the paths it
   leaves to be rebuilt: if one of those is data, `--include <that path>`
   carries it. `carry` without `--yes` prints the plan; with `--yes` it copies.
   `--include <path or glob>` narrows it, also to a path inside an ignored
   folder (`--include runs/experiment-1/`). A key file inside an ignored folder
   is left out of the folder's copy, and a file the receiving checkout tracks
   is never copied over.
   Show the user the plan first when it is over 1 GB or uses `--with-keys` or
   `--all`. If the destination is not known or not reachable, say so; the
   receiver can fetch the files later with `pull`.
5. **Prepare the other side, when the user wants it ready** and it is reachable
   over ssh: clone or fetch there, switch to the branch, run the project's setup
   command, then `carry`, then `python3 <tool> takeover` on that host, and report
   what it prints.
6. **Check again**, now that everything is committed and sent.

   ```bash
   python3 <tool> check
   ```

   It exits 1 while a critical or major finding stands: a required section
   that is missing or empty, uncommitted files, unpushed commits at level 3, something that looks
   like a key. Fix those. Report the rest.
7. **Tell the user**, in a few plain words: the branch, the note's path, what was
   sent, what is still open, and the one line that continues on the other side.
   For an assistant that has these skills, that line is "use the dev-takeover
   skill". For any other reader, when the skills are files in the repository,
   it is "open the dev-takeover skill's `SKILL.md` and follow it", with that
   file's path. When they are not (the skills come from a plugin, which the
   other side does not have), it is "read the hand-off note first and follow
   its snapshot", with the note's path: the snapshot says what to do on arrival.

## Rules

- One note per branch, updated in place. It describes work in progress: it is not
  a plan, a decision record or evidence, and a phase's decisions still go in the
  phase's own files. Delete it in the last commit before the pull request.
- The note informs; it approves nothing. Spend, deployments, merges and releases
  it mentions need the user's yes again on the other side.
- Ignored files are copied checkout to checkout, never added to git. Key files go
  only to the user's own machine and only when the user asks.
- A preference that should hold for every assistant from now on belongs in the
  project's instruction file (`AGENTS.md`), with the user's approval, not in the
  note and not only in one assistant's memory.
- Never edit a locked acceptance test, and never discard changes you did not
  make.
