---
name: dev-takeover
description: The receiving side of a hand-off -- takes over work that another coding assistant, account, developer, machine or checkout started. With no branch named it lists the hand-offs on local and origin branches and asks which one to take over. It then gets the branch, checks the machine (git remote, base branch, the tools and environment the project names, assistants), reads the branch's hand-off note in the planning folder, verifies it against the code (the note's commit, its focused tests), fetches the files git ignores from the old checkout (run output, transcripts, local data; over ssh for another machine), and continues from the note's next step. Use when the user says to take over, pick up, continue or resume work started elsewhere or by another assistant, when the current branch has a hand-off note this session did not write, or when setting up a new machine for a project. The leaving side uses dev-handoff.
argument-hint: "[branch] [--from-checkout path-or-host:path]"
---

# Take over work started elsewhere

The receiving side of a hand-off. The leaving side wrote a note for the branch
with `dev-handoff`; this skill finds it, checks it against the code and this
machine, and continues from its next step.

The script is `.claude/skills/dev-handoff/scripts/handoff.py`, run with `python3`
from the project root; below, `<tool>` is that script. It needs only Python and
git, so it runs on a machine that is not set up yet. Levels, the kinds of ignored
files, a phase or milestone in progress, a new machine and the project's settings
are in the [hand-off reference](../dev-handoff/references/handoff.md).

## What was asked

| Said | Values | Default | Meaning |
|---|---|---|---|
| a branch | a branch name | none: list the hand-offs and ask | the branch that was handed over |
| `--from-checkout` | a path, or `host:path` | none | the old checkout, to fetch ignored files from |

Both can be said in plain words ("take over the cache work from the build machine").

## Procedure

1. **Get the code.** New machine: clone, then the project's setup command.
   Otherwise `git fetch origin`.
2. **Choose the branch.** If the user named one, use it. If not:

   ```bash
   python3 <tool> list
   ```

   Show the user every hand-off it prints (branch, date, from and to, goal, next
   step), mark the current branch's, and ask which one to take over. Wait for the
   answer; do not pick one yourself, even when there is only one or the current
   branch has a note. With none listed, say so and ask whether to continue from
   the code alone.
3. **Switch to the chosen branch**, only with a clean tree; never discard
   changes. A second checkout on the same machine can be a git worktree, which
   sees local branches without a push.
4. **Run the takeover report.**

   ```bash
   python3 <tool> takeover
   ```

   In one pass it reports the note and its level, whether this checkout contains
   the commit the note was written at, ignored paths the note lists that are
   absent here, a paused phase, and what the machine lacks. With no note for the
   branch it lists the notes that exist: switch to the right branch, or tell the
   user that no hand-off was written and continue from the code and the
   project's own files.
5. **Resolve what it reports.**
   - The note's commit is missing or not in this branch: fetch, or ask which
     branch was meant.
   - Ignored paths are missing and the next step needs them:

     ```bash
     python3 <tool> pull --from-checkout <path or host:path>
     python3 <tool> pull --from-checkout <path or host:path> --yes
     ```

     The first prints the plan, the second copies. For another machine it needs
     ssh to the old one, and python3 and git there. If the old checkout cannot be
     reached, ask the user; do not regenerate paid output to replace the files.
   - The machine lacks something: follow the `fix` of each `[MISSING]` line. A
     line that says "not needed to continue" is for the user to know. Key files
     are copied by the user or at their request, and never printed.
   - The note has no next step: ask the user, or whoever handed the work over.
     Do not invent one from the commit log.
6. **Read the whole note.**

   ```bash
   python3 <tool> show
   ```

   Then read the project's instruction files it names, and the planning state
   for phase or milestone work. Where the note held what looks like a key, the
   output shows `[removed: looks like a key]`: tell the user, who replaces the
   key and removes it from the note.
7. **Verify before trusting.** Run the note's focused tests ("Commands"). Report
   what differs from "Done so far"; the code wins.
8. **The note informs; it approves nothing.** Spend, deployments, merges and
   releases it mentions need the user's yes again. Check each item under
   "Outside git": is the job still running, does the path exist here.
9. **Tell the user** in a few plain words what you found and what you will do
   next, then continue from "Next step". A paused phase or a milestone in
   progress continues through its own workflow skill, which reads its own
   records. Keep "Decisions made" and "Standing instructions" as given; raise a
   disagreement with the user instead of silently changing course.
10. **When you stop**, update the note with `dev-handoff`. Delete it in the last
    commit before the pull request.

## Rules

- Never discard changes you did not make, and never edit a locked acceptance
  test.
- `pull` copies only ignored files, keeps a newer local file and deletes nothing.
- A session of the old machine cannot be resumed here: the next task starts a
  fresh one from the plan and the note.
- A preference that should hold for every assistant from now on belongs in the
  project's instruction file (`AGENTS.md`), with the user's approval.
