---
name: move-from-gsd
description: Move a project that was planned and built with GSD (get-shit-done, gsd-core) to the dev-tools phase workflow, keeping its phases, requirements, decisions and history. Use when asked to move, migrate, transition or convert a GSD project to dev-tools, or to stop using GSD in a repository whose .planning/ folder GSD wrote. Surveys the GSD planning folder (the root plan and any workstreams), installs the phase skills, converts STATE.md, ROADMAP.md and REQUIREMENTS.md to the dev-tools format, carries decisions and constraints, archives GSD's own files, removes GSD's install from the project and checks the result with the phase tool. Not for a project that already keeps its own copies of the dev-tools skills (use adopt-devtools) or for a new project (use the example .devtools.toml and phase_tool.py setup).
---

# move-from-gsd

GSD and the dev-tools phase workflow keep a project's plan in the same place,
`.planning/`, and name a phase folder the same way, `phases/NN-<slug>/`, with the same
file names inside (`NN-CONTEXT.md`, `NN-MM-PLAN.md`, `NN-MM-SUMMARY.md`,
`NN-VERIFICATION.md`). So the folder of a finished phase stays exactly as it is. What
changes:

| GSD has | dev-tools has | What the move does |
|---|---|---|
| `STATE.md` (milestone, progress, a long session log) | `STATE.md` (current phase, its status, completed phases, lessons) | Rewritten; the phase tool owns it from then on |
| `ROADMAP.md` (a checklist, then `### Phase N` sections) | `ROADMAP.md` (`## Phase N` blocks with fixed fields) | Rewritten: same numbers, titles, goals, dependencies and success criteria |
| `REQUIREMENTS.md` (`- [x] **AUTH-01**: …` under group headings) | `REQUIREMENTS.md` (needs `U01`, requirements `REQ-AUTH-01` in a table) | Rewritten: one need per GSD group, `REQ-` in front of each id |
| `PROJECT.md` (what it is, constraints, key decisions) | `MANIFESTO.md`, `DECISIONS.md` | Constraints become manifesto rules, key decisions become decision rows; both are drafts for the owner |
| `config.json` | Settings in `.devtools.toml` | Archived; nothing in it carries over |
| A phase GSD did not finish (plans, summaries, perhaps a verification) | The same phase, taken up from its discussion | Carried as `context_approved` at most. GSD's plans, summaries and verification move to `gsd/` inside the phase folder, as input to a new plan |
| Phases marked PAUSED, DEFERRED or BACKLOG, and backlog entries `999.x` | Nothing: an open phase is in the queue | Listed at the end of the new roadmap, not as phases |
| Workstreams (`.planning/workstreams/<name>/`, each a plan of its own) | One plan | The move reads one plan: the root's or one workstream's. The owner says which |
| Milestones, `MILESTONES.md`, `milestones/`, `RETROSPECTIVE.md` | No milestone layer: a roadmap of phases | Left in place as history. Each phase block names the GSD milestone it belonged to |
| `codebase/` (a map of the code) | The component index | Left in place; the index replaces it (step 7) |
| `/gsd-*` commands and `gsd-*` agents | `/process-phase` and the `phase-*` agents | GSD's install inside the project is removed (step 6) |

What a project gains is what GSD does not do: acceptance tests written and locked before
the code, one state tool that refuses a step whose files are missing, and a search of
existing code before anything new is built. What it gives up is GSD's milestone
ceremony, its many commands, and autonomous runs across phases.

This skill is read from the dev-tools checkout, not copied into the project. Below,
`<dev-tools>` is the checkout that holds this file, commands run from the project's
root, `gsd` stands for `python3 <dev-tools>/devtools/from_gsd.py` and `sync` for
`python3 <dev-tools>/devtools/sync.py` (Python 3.11 or newer for both).

| Command | What it does | Writes? |
|---|---|---|
| `gsd survey --project .` | What GSD left: the plans it keeps, phases and the status each will get, requirements, decisions, GSD's install, and what needs a decision first | No |
| `gsd survey --project . --installed` | Every path of GSD's own files inside the project | No |
| `gsd convert --project . --dry-run` | The files a conversion would write and move | No |
| `gsd convert --project . [--owner NAME]` | Archives GSD's files, writes the dev-tools ones, and writes the record | Yes |

Both commands take the answers of step 2: `--planning-dir`, `--numbering`,
`--complete`, `--open`. `convert` also takes `--root-plan`, `--base-branch` and
`--ignored-plan`.

## Rules

- Work on a new branch of the project, from a clean working tree. Never on its base
  branch. If `git status --short` shows changes to tracked files, stop and ask.
- You may change only: the planning folder's top-level files; `.devtools.toml`, the
  receipt and the synced paths; GSD's own files inside the project (step 6); the
  instruction files, where they speak of GSD; and the project-owned `project.md`.
  No product code and no test.
- The folder of a finished phase is the record of work done under GSD: change nothing
  in it. In the folder of a phase GSD did not finish, `convert` moves GSD's plans,
  summaries and verification into `gsd/`; you move nothing yourself.
- Never edit a synced file by hand. Never change a status in `STATE.md` or
  `ROADMAP.md` by hand after the conversion: `phase_tool.py` owns them.
- An install of GSD in the user's home folder (`~/.claude`, `~/.codex`) is not the
  project's. Do not touch it; other projects use it.
- Do not push, merge or open a pull request unless the user asked for it.
- **Running unattended.** Where a step says to ask the user and nobody is there, take
  the choice that changes least, go on, and put the question first in your report.
  Four cases have a fixed answer: a project with workstreams is not converted (report
  the survey and stop); a phase GSD left unticked is not named finished; a phase GSD
  put off is not brought back; GSD's install inside the project is left in place.

## 1. Survey

```bash
python3 <dev-tools>/devtools/from_gsd.py survey --project .
```

| Line | Meaning | What to do |
|---|---|---|
| `Plans GSD keeps here` | GSD workstreams: each is a plan of its own, with phases of its own. The line marked "active" is the one GSD was working in | Step 2.1, before anything else |
| `Phases: N (…)` and the list under it | Every phase and the status it will get. Finished phases are listed only when something is unusual about them. `[under GSD: …]` says what GSD had done on an unfinished one | Read the list against what the user believes is done |
| `Put off under GSD` | Phases the GSD roadmap marks PAUSED, DEFERRED, BACKLOG or the like, and backlog entries `999.x` | They are not written as phases. Step 2.4 |
| `Current phase after the move` | The phase the phase tool will work on next | If GSD had started it, see step 2.2 |
| `Requirements: … without a phase` | Requirements GSD tracks that no phase of the roadmap names | They are kept as a list, not table rows; the owner assigns or deletes them later |
| `Requirement ids: A -> REQ-A` | How ids change | Nothing, unless the project's code or tests cite requirement ids: then say so in the report. The record lists every pair |
| `Base branch STATE.md will record` | The branch phases start from and return to | If it is not the project's integration branch, pass `--base-branch`. Step 2.7 |
| `Files git tracks … Python set up` | What the project is written in | If it is not a Python project, step 2.8 |
| `Settings for the phase tool` | Values for `.devtools.toml`: `phase_gaps`, and where they apply `planning_dir` and `skill_check` | Write them in step 3 |
| `GSD installed inside the project` | Folders of GSD's own files that are checked in here | Step 6 |
| `<file> mentions GSD …` | The project's instruction files speak of GSD or of `.planning/PROJECT.md` | Step 6 |
| `To settle:` | What the script cannot decide | Step 2 |

If the survey stops with "not a GSD project" or "already in the dev-tools format",
there is nothing to move. If the project also has its own copies of the dev-tools
skills, run `adopt-devtools` for those after this.

## 2. Settle what the survey could not

Ask the user each of these that applies, with the survey's lines in front of them. Run
the survey again with the answers until "To settle" holds only what the user has seen.
Then create the branch.

1. **Workstreams.** A GSD workstream is a whole plan under
   `.planning/workstreams/<name>/`. The move reads one plan, and `convert` stops until
   it is told which. Show the user the table (phase folders, last activity, which is
   active) and ask which plan is the project's roadmap from now on.
   - The root plan: pass `--root-plan`. The workstreams stay where they are, as history.
   - One workstream: pass `--planning-dir .planning/workstreams/<name>` to `survey` and
     `convert`, and set `planning_dir` to that folder in step 3. The project's
     `PROJECT.md` is read from the root; GSD's root plan and the other workstreams stay
     as GSD wrote them.
   - Work that is live in more than one plan cannot be carried by one move. Finish or
     park the others under GSD first, or tell the user that only one plan will be under
     the new workflow.
2. **A phase GSD did not finish.** GSD's steps after the discussion do not line up with
   this workflow's: here the acceptance tests are written and locked before the plan,
   and a plan names the tests each task turns green. So an unfinished phase is carried
   as `context_approved` when it has a `CONTEXT` file, otherwise `not_started`, and
   `convert` moves GSD's plans, summaries and verification for it into
   `phases/<folder>/gsd/`. They are input to the new plan; left in place they would
   pass for the files the new steps write. Offer the user three choices:
   - finish the phase under GSD first and move afterwards (best when little is left);
   - say it is in fact finished: step 2.3;
   - carry it as the survey shows. If GSD had already built part of it, the tests
     Specify writes may pass on their first run. The red run that step asks for is then
     waived by a decision row of its own that the user approves
     (`advance --to tests_approved --override DEC-NNN`). `DEC-002`, which the move
     writes, speaks of finished phases only and is not that row.
3. **Phases GSD left unticked that are in fact finished.** The script trusts the tick
   in GSD's roadmap, and failing that a passed `VERIFICATION.md`. Where the user says a
   phase is done, pass `--complete 3,12`. Do not pass it on your own judgment.
4. **Phases GSD put off.** The phase tool takes the lowest open phase next, so a phase
   that GSD had paused must not sit in the roadmap as an open phase. The survey lists
   what it read as put off; they go to a list at the end of the new roadmap. Where the
   user wants one in the queue, pass `--open 59,60`. A phase the survey shows as open
   that the user means to put off is deleted from `ROADMAP.md` by hand after the
   conversion, before anything is committed.
5. **A roadmap that restarted its numbers.** "uses phase numbers twice" means a
   milestone began again at phase 1. The phase tool needs each number once. Find which
   run of numbers has its folders in `.planning/phases/` (GSD moves the earlier run's
   folders to `milestones/<version>-phases/`) and pass `--numbering first` or
   `--numbering last`. The other run stays readable in the archived roadmap.
6. **Dependencies.** The survey notes a phase whose dependency line names a phase it
   did not carry as a dependency ("independent of Phase 9"), and a phase that depends on
   one GSD put off. Read each line with the user; a wrong dependency is corrected in
   `ROADMAP.md` after the conversion. One phase is current: a phase GSD had started
   goes first if its dependencies are finished, otherwise the phase it waits on.
7. **The base branch.** `STATE.md` records the branch phases start from and return to.
   The survey prints the one it found. If it "cannot be told", or it is not the
   project's integration branch (a project that merges to `develop` and releases from
   `main`), pass `--base-branch`, and `--release-branch` where the two differ.
8. **A project that is not Python.** The phase skills are written for Python and
   pytest: the commands, the plugin that selects tests by phase, and the guide for
   writing acceptance tests. The steps themselves are not tied to a language: the test
   lock hashes whatever files are under `tests/acceptance/pNN_<slug>/`. Before going
   on, agree with the user how an acceptance test is written and run in this project,
   and what a failing run looks like. That goes into `project.md` in step 6. If the
   project has no tests and none are wanted (a folder of documents), tell the user this
   workflow is the wrong one for it.
9. **A planning folder git ignores.** GSD can keep `.planning/` out of the repository.
   This workflow keeps its plan in the repository. Ask the user to take the folder out
   of `.gitignore` and commit it as it is, before the move, so that the move shows as a
   change. `--ignored-plan` converts it where it is, for an owner who wants that.

## 3. Install the phase skills

Copy `<dev-tools>/examples/phase-project.devtools.toml` to `.devtools.toml` and set:

- `package_prefix` to the project's Python package, or `""`;
- `phase_gaps`, and where the survey printed them `planning_dir` and `skill_check`, to
  what it printed. `skill_check = "synced"` keeps `check --all` to the skills and agents
  this file delivers; with `"all"` every skill and agent in those folders is held to
  the same rules, which the project's own, GSD's and other tools' rarely meet;
- `acceptance_dir` and the test settings to where the project's tests live;
- `dest = "phase_selection.py"` for the pytest plugin if the project has a root
  `conftest.py` (the comment in the example says how). In a project that is not
  Python, remove that entry;
- a second entry per skill for each other agent runtime the project serves
  (`.codex/skills/…`), as GSD's install shows which it used. If that runtime's skills
  folder is a link to the first one, add no second entry: the sync refuses two
  destinations that are one file;
- if the user does not want the component index yet, remove its entries and the
  `after_apply` line at the top, which runs the index script.

```bash
python3 <dev-tools>/devtools/sync.py apply --project . --dry-run
```

```bash
python3 <dev-tools>/devtools/sync.py apply --project .
```

A file the sync refuses already exists in the project. If it is GSD's, it goes in step
6 and the sync is run again; if it is the project's own, give that entry another `dest`.
Do not run `phase_tool.py setup`: it is for a project with no plan, and it stops on a
GSD planning folder.

## 4. Convert

```bash
python3 <dev-tools>/devtools/from_gsd.py convert --project . --dry-run
```

```bash
python3 <dev-tools>/devtools/from_gsd.py convert --project . --owner "<the user's name>"
```

Add the answers of step 2. The script:

- moves GSD's `STATE.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `PROJECT.md` and
  `config.json` to `.planning/archive/gsd/`, unchanged;
- writes the three files in the dev-tools format;
- moves GSD's plans, summaries and verification of each unfinished phase into `gsd/`
  inside that phase's folder;
- creates `MANIFESTO.md`, `DECISIONS.md`, `README.md` and the smaller files. A file
  that already exists is left alone, and what the move would have written to it goes to
  `.planning/archive/gsd/<name>-to-merge.md`;
- writes `.planning/archive/gsd/CONVERSION.md`: what needs the owner, every file, every
  phase with its status and the reason, what was put off, and the table of requirement
  ids.

It does not call git. Run `git add -A .planning` afterwards so that the moves show as
renames.

## 5. Read what was written

The script carries text; it does not judge it. Read each of these and fix what is wrong
by editing the file (these are the project's files, not synced ones):

- **`ROADMAP.md`**: each open phase has the goal, dependencies and requirements the
  GSD roadmap gave it. A phase that says `Requirements: none recorded` and has not
  started needs its requirements named before it is planned. The section "Put off
  under GSD" at the end is a list, not phases.
- **`REQUIREMENTS.md`**: the `U` rows are GSD's group headings ("Authentication").
  Reword each as what a user needs, with the user. The two lists at the end
  (requirements without a phase, requirements put off) are for the owner to assign or
  delete.
- **`MANIFESTO.md`**: `T1` and `T2` are the workflow's own rules. The rules after them
  are GSD's constraints, word for word. Keep the ones the project truly does not bend,
  delete the rest, and renumber. This file needs the owner's approval.
- **`DECISIONS.md`**: `DEC-001` (the move) and `DEC-002` (phases finished under GSD
  stand without acceptance tests) need the owner's name. The rows after them are GSD's
  key decisions, each column read by its heading; delete any that is not a decision.
- **A `-to-merge.md` draft** in the archive: the file it belongs to was already there.
  Merge it by hand with the user. `check --all` fails until `DECISIONS.md` has a row
  for the move.
- **`STATE.md`**: "Next step" says what the first `/process-phase` run will do.
- **`CONVERSION.md`**, "For the owner to read": every line there goes into your report.

Do not copy GSD's session log, performance metrics or accumulated context into
`STATE.md`. They stay in the archive.

## 6. Take GSD out of the project

Only what is checked in to this repository; ask the user before removing anything.

1. **GSD's install.** `gsd survey --project . --installed` prints every path. GSD's
   installer has an `--uninstall` option: where the project's notes say how GSD was
   installed here (often `.claude/GSD-SETUP.md`), run the same command with
   `--uninstall` in place of the install flags it does not need, then run the survey
   again to see what is left. Otherwise, and for whatever is left, `git rm` the listed
   paths. An agent or skill whose name does not start with `gsd-` is the
   project's own: leave it. A path git does not track is a developer's local install:
   leave it and say so. The survey looks in `.claude`, `.codex`, `.opencode`, `.gemini`
   and `.agents`; GSD can also install for other tools (`.cursor`, `.windsurf`,
   `.github` and more), so look there yourself.
2. **Hooks and settings.** `.claude/settings.json` and `.claude/settings.local.json`
   (and the other runtimes' settings) may run GSD's hooks or status line. Remove those
   entries, and only those. `settings.local.json` is each developer's own and is not in
   git: say in the report that every teammate has to remove the entries from theirs,
   or their sessions will call hook files that are gone.
3. **Instruction files.** In `CLAUDE.md`, `AGENTS.md` and the like, GSD writes blocks
   between `<!-- GSD:… -->` marks and the project may have added its own lines about
   `/gsd-*` commands. Replace them with a few lines: the plan is in `.planning/`, the
   workflow is `/process-phase`, statuses change only through `phase_tool.py`, and the
   project's own rules are in `references/project.md` of the process-phase skill. Point
   a reference to `.planning/PROJECT.md` at `.planning/MANIFESTO.md`.
4. **Rules the project kept in GSD's files.** If `PROJECT.md` or the instruction files
   hold working rules (a test command, a review bar, a release gate), move them to
   `references/project.md`, which the project owns and every step reads. Run
   `grep -rn 'project\.md' .claude/skills/process-phase` to see what it is expected to
   answer. In a project that is not Python, this is where the answers of step 2.8 go.
5. **The project's own skills that call GSD** (a skill that says "create a GSD
   milestone"). List them for the user; rewriting them is a task of its own.

## 7. Check

Stage the change first (`git add -A`): the phase tool reads what git tracks.

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py check --all
```

```bash
python3 .claude/skills/process-phase/scripts/phase_tool.py status
```

```bash
python3 <dev-tools>/devtools/sync.py check --project .
```

- `check --all` is clean. A `roadmap … not contiguous` issue means `phase_gaps` is not
  set; a `[skill]` or `[agent]` issue on a file the sync did not deliver means
  `skill_check` is not `"synced"`; a `rule-dec` issue means `DECISIONS.md` has no row
  for the move (step 5, the draft to merge).
- `status` names the phase and status the survey promised, with no blocker.
- `git status --short .planning/phases` shows renames into `gsd/` in the folders of
  unfinished phases, and nothing else.
- The project's own tests pass as they did before; nothing they read was changed. If a
  test lists the files of `.planning/` or of the skill folders, update that list and
  nothing else.

If the user wants the component index and the project has none, say that the
`components` skill's Build mode writes it, as a separate task; GSD's `codebase/` map is
a useful first read for it.

## 8. Finish

Commit on the branch, with a message that names the dev-tools commit. Show the user:

- where the project stands now: the current phase, its status, and the next command
  (`/process-phase <N>` or `/process-phase next`);
- the questions for the owner, first: everything under "For the owner to read", the
  drafts in step 5, and anything you left in place in step 6;
- how many phases, requirements and decisions were carried, what was put off, and what
  was archived;
- which plan was moved, and which of GSD's plans were left as history;
- what was removed of GSD's and what was left, and what each teammate has to remove
  from their own settings;
- what they do differently from now on: one command (`/process-phase`) in place of
  GSD's discuss, plan, execute and verify commands; tests agreed before code; no
  milestone commands, since a new stretch of work is new phases added to `ROADMAP.md`.
