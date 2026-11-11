---
name: move-from-gsd
description: Move a project that was planned and built with GSD (get-shit-done, gsd-core) to the dev-tools phase workflow, keeping its phases, requirements, decisions and history. Use when asked to move, migrate, transition or convert a GSD project to dev-tools, or to stop using GSD in a repository whose .planning/ folder GSD wrote. Surveys the GSD planning folder, installs the phase skills, converts STATE.md, ROADMAP.md and REQUIREMENTS.md to the dev-tools format, carries decisions and constraints, archives GSD's own files, removes GSD's install from the project and checks the result with the phase tool. Not for a project that already keeps its own copies of the dev-tools skills (use adopt-devtools) or for a new project (use the example .devtools.toml and phase_tool.py setup).
---

# move-from-gsd

GSD and the dev-tools phase workflow keep a project's plan in the same place,
`.planning/`, and name a phase folder the same way, `phases/NN-<slug>/`, with the same
file names inside (`NN-CONTEXT.md`, `NN-MM-PLAN.md`, `NN-MM-SUMMARY.md`,
`NN-VERIFICATION.md`). So the phase folders stay exactly as they are. What changes:

| GSD has | dev-tools has | What the move does |
|---|---|---|
| `STATE.md` (milestone, progress, a long session log) | `STATE.md` (current phase, its status, completed phases, lessons) | Rewritten; the phase tool owns it from then on |
| `ROADMAP.md` (a checklist, then `### Phase N` sections) | `ROADMAP.md` (`## Phase N` blocks with fixed fields) | Rewritten: same numbers, titles, goals, dependencies and success criteria |
| `REQUIREMENTS.md` (`- [x] **AUTH-01**: …` under group headings) | `REQUIREMENTS.md` (needs `U01`, requirements `REQ-AUTH-01` in a table) | Rewritten: one need per GSD group, ids keep the old id inside the new one |
| `PROJECT.md` (what it is, constraints, key decisions) | `MANIFESTO.md`, `DECISIONS.md` | Constraints become manifesto rules, key decisions become decision rows; both are drafts for the owner |
| `config.json` | Settings in `.devtools.toml` | Archived; nothing in it carries over |
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
| `gsd survey --project .` | What GSD left: phases and the status each will get, requirements, decisions, GSD's install, and what needs a decision first | No |
| `gsd survey --project . --installed` | Every path of GSD's own files inside the project | No |
| `gsd convert --project . --dry-run` | The files a conversion would write | No |
| `gsd convert --project . [--owner NAME]` | Archives GSD's files, writes the dev-tools ones, and writes the record | Yes |

## Rules

- Work on a new branch of the project, from a clean working tree. Never on its base
  branch. If `git status --short` shows changes to tracked files, stop and ask.
- You may change only: the planning folder's top-level files; `.devtools.toml`, the
  receipt and the synced paths; GSD's own files inside the project (step 6); the
  instruction files, where they speak of GSD; and the project-owned `project.md`.
  No product code, no test, and nothing inside a phase folder: those are the record of
  work done under GSD.
- Never edit a synced file by hand. Never change a status in `STATE.md` or
  `ROADMAP.md` by hand after the conversion: `phase_tool.py` owns them.
- An install of GSD in the user's home folder (`~/.claude`, `~/.codex`) is not the
  project's. Do not touch it; other projects use it.
- Do not push, merge or open a pull request unless the user asked for it.
- **Running unattended.** Where a step says to ask the user and nobody is there, take
  the choice that changes least, go on, and put the question first in your report. Two
  cases have a fixed answer: a phase that is under way is carried as it is (not marked
  finished), and GSD's install inside the project is left in place.

## 1. Survey

```bash
python3 <dev-tools>/devtools/from_gsd.py survey --project .
```

| Line | Meaning | What to do |
|---|---|---|
| `Phases: N (…)` and the list under it | Every phase and the status it will get. Finished phases are listed only when something is unusual about them | Read the list against what the user believes is done |
| `Current phase after the move` | The phase the phase tool will work on next | If it says "under way", see step 2 |
| `Requirements: … without a phase` | Requirements GSD tracks that no phase of the roadmap names | They are kept as a list, not table rows; the owner assigns or deletes them later |
| `Requirement ids: A -> REQ-A` | How ids change. The old id is inside the new one, so a search still finds both | Nothing, unless the project's code or tests cite requirement ids: then say so in the report |
| `Setting for the phase tool … phase_gaps` | `true` when the phase numbers do not start at 1 or skip some | Write it in `.devtools.toml` in step 3 |
| `GSD installed inside the project` | Folders of GSD's own files that are checked in here | Step 6 |
| `<file> mentions GSD …` | The project's instruction files speak of GSD or of `.planning/PROJECT.md` | Step 6 |
| `To settle:` | What the script cannot decide | Step 2 |

If the survey stops with "not a GSD project" or "already in the dev-tools format",
there is nothing to move. If the project also has its own copies of the dev-tools
skills, run `adopt-devtools` for those after this.

## 2. Settle what the survey could not

Ask the user each of these that applies, with the survey's lines in front of them.

1. **A phase under way.** GSD's steps and dev-tools' steps do not line up, so the
   simplest move is between phases. If the current phase is `plan_approved` or
   `implemented`, offer two choices: finish it under GSD first and move afterwards
   (recommended when little is left), or carry it. A carried phase has no locked
   acceptance tests, and `advance` will ask for them: the user either has them written
   now (the Specify step, run late) or approves a decision row that waives them
   (`advance --to … --override DEC-NNN`). A phase carried as `context_approved` needs
   nothing: its next step is Specify.
2. **Phases GSD left unticked that are in fact finished.** The script trusts the tick
   in GSD's roadmap, and failing that a passed `VERIFICATION.md`. Where the user says a
   phase is done, pass `--complete 3,12`. Do not pass it on your own judgment.
3. **A roadmap that restarted its numbers.** "uses phase numbers twice" means a
   milestone began again at phase 1. The phase tool needs each number once. Find which
   run of numbers has its folders in `.planning/phases/` (GSD moves the earlier run's
   folders to `milestones/<version>-phases/`) and pass `--numbering first` or
   `--numbering last`. The other run stays readable in the archived roadmap.
4. **More than one phase started.** The phase tool works on one phase at a time. The
   lowest started phase becomes the current one; the others keep the status their files
   support, and each is taken up later with `activate`.
5. **A plan not named `NN-MM-PLAN.md`** in a phase that will go on. Older GSD wrote
   `NN-PLAN.md`; the phase tool counts only the numbered form. Rename it with `git mv`
   (`03-PLAN.md` to `03-01-PLAN.md`, and its summary the same way). This is the one
   change allowed inside a phase folder, and only for a phase that is not finished.

Run the survey again with the options you settled on until "To settle" holds only what
the user has answered. Then create the branch.

## 3. Install the phase skills

Copy `<dev-tools>/examples/phase-project.devtools.toml` to `.devtools.toml` and set:

- `package_prefix` to the project's Python package, or `""`;
- `phase_gaps` to what the survey printed;
- `acceptance_dir` and the test settings to where the project's tests live;
- `dest = "phase_selection.py"` for the pytest plugin if the project has a root
  `conftest.py` (the comment in the example says how);
- a second entry per skill for each other agent runtime the project serves
  (`.codex/skills/…`), as GSD's install shows which it used;
- `skill_roots` to the skill folders whose skills should be held to the phase tool's
  skill rules (a `SKILL.md` under 500 lines, every file it names present beside it).
  The project's own skills were not written to those rules: leave the list as it is,
  see in step 7 whether they pass, and let the user choose between fixing them and
  `skill_roots = []`;
- remove the component index entries if the user does not want the index yet.

Leave `planning_dir = ".planning"`: the planning folder does not move.

```bash
python3 <dev-tools>/devtools/sync.py apply --project . --dry-run
```

```bash
python3 <dev-tools>/devtools/sync.py apply --project .
```

A file the sync refuses already exists in the project. If it is GSD's, it goes in step
6 and the sync is run again; if it is the project's own, give that entry another `dest`.

## 4. Convert

```bash
python3 <dev-tools>/devtools/from_gsd.py convert --project . --dry-run
```

```bash
python3 <dev-tools>/devtools/from_gsd.py convert --project . --owner "<the user's name>"
```

Add `--numbering`, `--complete` and `--base-branch` as settled. The script:

- moves GSD's `STATE.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `PROJECT.md` and
  `config.json` to `.planning/archive/gsd/`, unchanged;
- writes the three files in the dev-tools format;
- creates `MANIFESTO.md`, `DECISIONS.md`, `README.md` and the smaller files, and
  leaves alone any that already exist;
- writes `.planning/archive/gsd/CONVERSION.md`: what needs the owner, every file, every
  phase with its status and the reason, and the table of requirement ids.

It does not call git. Run `git add -A .planning` afterwards so that the moves show as
renames.

## 5. Read what was written

The script carries text; it does not judge it. Read each of these and fix what is wrong
by editing the file (these are the project's files, not synced ones):

- **`ROADMAP.md`**: each open phase has the goal, dependencies and requirements the
  GSD roadmap gave it. A phase that says `Requirements: none recorded` and has not
  started needs its requirements named before it is planned.
- **`REQUIREMENTS.md`**: the `U` rows are GSD's group headings ("Authentication").
  Reword each as what a user needs, with the user. The two lists at the end
  (requirements without a phase, requirements put off) are for the owner to assign or
  delete.
- **`MANIFESTO.md`**: `T1` and `T2` are the workflow's own rules. The rules after them
  are GSD's constraints, word for word. Keep the ones the project truly does not bend,
  delete the rest, and renumber. This file needs the owner's approval.
- **`DECISIONS.md`**: `DEC-001` (the move) and `DEC-002` (phases finished under GSD
  stand without acceptance tests) need the owner's name. The rows after them are GSD's
  key decisions; delete any that is not a decision.
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
   leave it and say so.
2. **Hooks and settings.** `.claude/settings.json` (and the other runtimes' settings)
   may run GSD's hooks or status line. Remove those entries, and only those.
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
   answer.
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
  set; an `agent name must equal file stem` issue names a GSD agent file still in the
  project (step 6); a `rule-dec` issue means `DEC-001` is missing from `DECISIONS.md`.
  `[skill]` issues on the project's own skills are not about the move: show them to
  the user, who either has them fixed or takes those folders out of `skill_roots`.
- `status` names the phase and status the survey promised, and the folder GSD used.
- `git status --short` shows no change under `.planning/phases/`, apart from a rename
  made in step 2.
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
- how many phases, requirements and decisions were carried, and what was archived;
- what was removed of GSD's and what was left;
- what they do differently from now on: one command (`/process-phase`) in place of
  GSD's discuss, plan, execute and verify commands; tests agreed before code; no
  milestone commands, since a new stretch of work is new phases added to `ROADMAP.md`.
