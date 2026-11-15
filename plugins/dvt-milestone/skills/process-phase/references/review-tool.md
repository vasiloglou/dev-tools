# The review helper

The milestone workflow requires an independent reviewer in a different harness
for the plan, every phase diff and the milestone close, and allows one over a
spec or a pull request. `scripts/review_tool.py`, beside this skill, is the
default instrument for all of them: it writes the brief, runs the reviewer, and
keeps the findings ledger. A project whose `.devtools/project.md` names an
instrument of its own uses that one; a project that takes this one names it
there, with any settings it changed. Below, `<skill>` is this skill's folder in
the project, for example `${CLAUDE_PLUGIN_ROOT}/skills/process-phase`. A request to review a
pull request is taken by the `review-pr` skill, which runs these steps in order
and follows this file.

Using the helper is not consent to a review. The owner's choice of instrument,
and of a paid model, still comes first (`review-convergence.md`, the project's
plan-review bar); the helper only makes the chosen review the same every time.

## One round is one folder

Put each round in its own folder under the milestone's notes, named for its
subject and round, for example
`.planning/milestones/<milestone>/notes/reviews/phase-3-r1/`.
A pull request that belongs to no milestone has its rounds under
`.planning/reviews/`, for example
`.planning/reviews/pr-42-r1/`.
`brief` creates the folder, refuses one that already holds files, and nothing
afterwards rewrites the brief: a second round is a second folder.

```bash
python3 <skill>/scripts/review_tool.py brief <dir> --subject phase \
    --base <the phase's base commit> --question "<the question>" --claim "<a criterion>"
```

| Subject | Needs | The reviewer reads |
|---|---|---|
| `plan`, `spec`, `close` | `--file` for each file | the files named |
| `phase` | `--base`, the commit the phase began from | `diff.patch` (base to the working tree) and every changed or new file |
| `pr` | `--pr N`; `gh` logged in | `diff.patch`, the PR's diff, and its head SHA |

Any subject also takes `--file` for context (the spec beside a phase diff, say)
and `--claim` once per claim the reviewer should try to refute: a phase's
criteria, the plan's completion predicates.

**The question states what to judge, never the answer.** "Can every phase be
implemented and tested as written?" is a question; "check that the plan is
complete" carries the author's conclusion, and a reviewer handed a conclusion
tends to return it confirmed. The brief has no place for the author's opinion,
and none is added by hand.

The brief lists every file with its SHA-256 and tells the reviewer to check
them before relying on one, forbids opening credential files or printing the
environment, and asks for numbered findings with file, line, consequence and
reproduction, what was checked and found true, what could not be checked, and
a verdict line. A file that looks like a credential file (`.env`, keys,
`auth.json`, `secrets.json`; not `.env.example`) is refused when named and left
out of a diff, with a note in the brief saying so. A diff block that names one
on either side is dropped whole, and a credential renamed to an innocent name is
not listed under its new name either. A PR that
moves while its brief is written is refused: the diff must be the head's.

## Running the reviewer

```bash
python3 <skill>/scripts/review_tool.py run <dir>
```

- **The other harness.** With `reviewer = "auto"` (the default setting), Claude
  Code driving gets Codex, read-only (`codex exec --sandbox read-only`), and
  Codex driving gets Claude Code in print mode, in plan mode (`claude -p
  --permission-mode plan`). A fresh session of the same tool is not independent
  (`agent-delegation.md`). `--reviewer` overrides it for one run.
- **Preconditions first.** `run` checks that every listed file still has the
  bytes the brief names, and that the reviewer's CLI is on PATH (and, for Codex,
  `codex login status`). If either fails, nothing is launched; tell the owner.
  The background watcher checks the bytes once more just before it starts the
  reviewer, and records a failed run if they moved.
  Each CLI uses its own login; the helper reads no `.env` and passes no key.
- **In the background, stdin closed.** A review takes minutes, so `run` starts
  it detached and returns; `--wait` keeps it in the foreground. The reviewer's
  stdin is closed, or it can wait for input forever. The prompt names only the
  brief's path, so no reviewed bytes pass through argv.
- **Word for word.** The answer is `review.md`, unedited; the reviewer's log is
  `review.log`. `run.json` holds the command (the folder written as `{dir}`), the
  model, the exit, and the SHA-256 of the brief and of the review. A reviewer
  that exits non-zero, writes nothing, or outlives `timeout_minutes` is recorded
  as failed, and a failed review is not a review.

Settings, in `.devtools/review_tool.settings.json` (the sync writes it from the
project's `.devtools.toml`): `reviewer`, `codex_model` (empty: Codex's
default), `codex_effort` (default `high`), `claude_model` (default `opus`) and
`timeout_minutes` (default 60). `run --dry-run` prints the command and starts
nothing.

## The findings ledger

`FINDINGS.md`, written empty with the brief, is filled by whoever dispositions
the review, never by the reviewer: one row per finding, under the reviewer's id.

| Column | Values |
|---|---|
| Reproduced | `yes` or `no`: reproduced against the bytes before it is believed (`review-and-record.md`) |
| Class | `blocking`, `hardening` or `completeness` (`review-convergence.md`) |
| Disposition | `fixed`, `deferred`, `rejected` or `open` |
| Repaired at | for `fixed`: the commit or tag that holds the repaired bytes |
| Notes | the regression test (`fixed`), the target (`deferred`), the reason (`rejected`) |

A review that found nothing gets the line `No findings.` in place of the table.
The ledger is per round; across rounds over one artifact the convergence ledger
of `review-convergence.md` still decides whether another round pays.

## What is reviewed, and what is not

```bash
python3 <skill>/scripts/review_tool.py status <the reviews folder>
```

`status` reports every round under the path: its run (a round not run or
still running is unfinished), and each ledger row that is incomplete, still
open, fixed without being reproduced, fixed with nothing in Notes, or
fixed at a commit that does not exist. Then, for every file any round read, the latest round that
read it decides: `reviewed` when the file still has those bytes and that round's
review finished, `unreviewed` otherwise. **A repaired file is unreviewed until a
later round's brief lists its new bytes and that round finishes**, which is the
standing rule that repaired bytes carry no review opinion, made mechanical. It
exits 1 while anything is unreviewed or unfinished; a record cites a review
only for the files `status` calls reviewed.

## Committing and posting

The round folder is the retained evidence: commit `BRIEF.md`, `brief.json`,
`diff.patch`, `review.md`, `run.json` and `FINDINGS.md`, and cite them by path
and SHA-256 from the record. Reviewer output names absolute paths of the machine
it ran on; `status` flags it, and `sanitize <dir>` replaces them with `<repo>`
and `<home>` and says so at the top of `review.md`, since retained-verbatim
evidence that was edited must declare the edit. `run.json` keeps the original's
digest.

For a PR round, `post <dir>` prints the comment it would add: the reviewer, the
reviewed head SHA, the review word for word and the ledger, with a warning when
the PR's head has moved since. **Posting is publishing on the owner's behalf:**
show the owner the text, and pass `--yes` only on their approval for this PR.
A round is posted once; `--again` posts it a second time.
