# Milestone Records and Commits

**The normative contract** for how a project records completed units of work and commits them — the `{{devtools:planning_dir}}/` directory, the per-unit record file, and the commit grammar. Every workflow skill links here at its gate; none restates this text.

**Scope — who this binds.** This contract binds the **driving agent** working in the project. The record and the commit are the driving agent's acts, performed after a skill's own gate has spoken — they add no authority to any gate result and change no claim.

## When a record is due — the two lanes

Not every unit of work earns a record. The driving agent works in one of two lanes, chosen by risk, and names the lane in one line at the gate when it matters:

**Fast lane — the default for routine, reversible work.** Direct edits, focused tests, a smoke run where one applies. No record, no record commit, no experiment, no review round. The evidence is the working tree and the validators' own exit codes. Ask the user for a decision only when a choice materially changes scope or is hard to reverse.

**Evidence lane — entered when risk justifies it.** A full experiment for genuine uncertainty about behavior; a drift check when a generated or derived surface may have diverged from its source; the project's review instrument (`references/project.md`) for destructive, ambiguous, security-sensitive, or high-blast-radius decisions; and a durable milestone record for each such **material event** — a completed phase, a closed experiment, an accepted change of contract, a review run, a refusal that taught something.

Two rules keep the lanes honest:

- **Prefer milestone-level records over per-unit ones.** A run of routine work that ends in one material event takes one record citing the run, not a record per unit. A suite of like cases takes **one batched record** naming every case and its exit verbatim — never one record and commit per case.
- **A commit needs the user's explicit go-ahead.** The record and the commit are the driving agent's acts, performed only on the user's authorization — never implied by a green exit.

The lane choice gates the *record*, not the discipline: whichever lane a unit of work ran in, its own gate command and exit are what they are, and neither lane adds authority to a claim or waives a skill's Limits.

## The `{{devtools:planning_dir}}/` directory

`{{devtools:planning_dir}}/` sits at the project root and holds all planning artifacts. It is created exactly once, by the project's own scaffold step (`references/project.md`) — no other skill creates it, and a skill that finds it absent reports the prerequisite rather than scaffolding ad hoc. A repository may carry other planning directories belonging to other frameworks, and they must never be confused — these artifacts go under `{{devtools:planning_dir}}/`, nowhere else.

Layout:

```
{{devtools:planning_dir}}/
  PROJECT.md                          # one-pager: the problem, in the user's words
  milestones/
    <milestone-name>/                 # e.g. v1, v2-search
      001-phase-1.md                  # one record per material event (evidence lane)
      002-phase-2.md
      003-phase-3.md
      ...
```

The directory is **append-only**. A record is never edited after its commit — a correction is a **new** record, with the next number, citing the record it corrects by path and sha256. Deleting or rewriting a record destroys evidence the same way editing a retained attempt would.

## Record file naming

`NNN-<scope>.md`, where `NNN` is monotonic within the milestone (001, 002, …) and `<scope>` is the same scope token the commit uses (below). The number orders records within a milestone; the scope names the unit of work. Two runs of the same unit produce two records with two numbers — never a second write to the first.

## Record file shape

```markdown
---
milestone: v1
station: "phase-3"        # which unit of work produced this record: a step of a
                          # project-defined workflow (`references/project.md`), or
                          # a free-form string for other work (a milestone phase, a
                          # repair pass) -- e.g. "phase-6a". Free-form names the
                          # work; it is never a substitute for the scope token
skill: <owning skill>     # the skill that owned the work, or "n/a -- <why>"
scope: phase-3            # == the commit scope token and the filename token
date: <YYYY-MM-DD>
gate:
  command: "pytest tests/test_settings_loader.py"
  exit: 0
evidence:
  - path: src/settings/loader.py
    sha256: <64 hex, recomputable with shasum -a 256>
  - path: tests/test_settings_loader.py
    sha256: <64 hex>
---

# Claim

One sentence, in the gate's own vocabulary. Never an adjective standing in
for an exit code -- write "exited 0", not "passed"; "exited 3", not "failed".

## Gate output (verbatim)

    <the exact stdout/stderr lines and the exit code, unedited>

## Boundary -- what this result did NOT establish

- Mandatory, at least one clause. Copy the owning skill's own Limits
  language rather than inventing softer wording.

## Open questions

- Frontier items this run surfaced. The section is required; an empty
  list is allowed and means "this run surfaced none".

## Refuted premises

- Only when a run killed a belief the work was resting on. Cite the
  evidence that killed it by path + sha256. Omit the section otherwise.

## Refactoring review

- Required for phase-scoped records (station: "phase-N"); optional
  elsewhere. Exactly two honest answers: refactors EXECUTED, each named
  and behavior-preserving, or "none needed" argued from what the work
  actually touched. A deferred refactor is an open question with a named
  target, never silent debt.
```

Rules the shape carries:

- **The claim never merges families.** A record about one gate's outcome cites another gate's result by digest if it needs to; it never presents the two as one verdict.
- **The boundary section is not optional.** A green exit is a narrow claim; the record states what it is narrow about. Every skill's Limits section is the source text.
- **Digests are computed from bytes on disk** after the last write, with `shasum -a 256`, never copied from memory or an earlier run.
- **A citation names committed bytes -- and an exception declares itself.** A record cites an artifact by path AND digest, and the digest of an uncommitted working-tree file is NOT a citation, because the reader must be able to check the claim out of history. The one admitted exception is run evidence deliberately kept out of the tree (a large run log, a retained attempt): its digest may be recorded, but the record must say plainly that the bytes live outside history and the claim is correspondingly weaker -- checkable only by whoever holds the bytes. An undeclared exception is an overclaim.

Project-specific front-matter fields, where a project defines any, are listed in `references/project.md`.

## Why there is no index and no status field

Completion **is** the record's existence plus its commit. An index file would be a second source of truth that drifts; ordering and inventory are recomputable from `ls` and `git log --oneline -- {{devtools:planning_dir}}/`; every digest is recomputable from the named path. A `status:` field would claim something the evidence already proves or contradicts: no record carries an adjective where a reader can recompute the fact.

## The commit

One commit per **recorded** gate — evidence lane, on the user's explicit go-ahead — made **after** the record file is written so the record rides in the same commit as the artifacts it binds. Fast-lane work commits through the repository's ordinary development flow, un-narrated by this contract.

### Grammar

```
<type>(<scope>): <imperative subject, <= 65 chars, no trailing period>

<body, wrapped ~72-80 columns:
 - what the gate established, with exit codes verbatim
 - what it did NOT establish (the boundary clause, compressed)
 - the record file path on its own closing line>
```

Body conventions: use `--` rather than em-dashes; **never put backticks in a commit message** (shells perform command substitution on them, which garbles the message); reference files by bare path.

### Type selection

- **`feat`** — the work produced or changed working artifacts (code, a schema, a corpus, a generated surface, a closed experiment).
- **`docs`** — the work produced *evidence about* existing artifacts (a drift-check result, a review run, a retained non-accepted attempt worth recording).
- **`fix`** — a mid-unit repair (an artifact corrected after its gate exited non-zero).
- **`chore`** — scaffolding.

A record of a refuted premise is `docs`, with the refutation in the body.

### Scope tokens

The scope token names the unit of work and is the same in the record's `scope:` field, its filename and the commit. A milestone phase uses its phase token (`phase-N`). The tokens, types and record triggers for a project's own workflow steps are listed in `references/project.md`. The lane rule above decides whether a record is due at all.

### What is staged

Stage **by explicit path**: the unit's declared artifacts plus the record file. Never `git add -A`, never `git add .` — a record commit that sweeps in unrelated worktree changes binds the record to bytes it never claimed. The record file is always the last path staged.

### When

After the gate, and only after. Work whose gate refused has produced no completion to record as `feat` — record the refusal honestly as `docs` if it taught something, or fix and re-run. For work with a declared write set, see the next section.

## Sequencing for work with a declared write set

Some skills run a bounded transaction with a declared write set — no path outside it is read, written, moved or deleted — and **this contract does not loosen that rule**. The record write and the commit happen strictly **after** the transaction has closed and the skill's own report is complete. They are a separate act, over paths the operator chose — never a path an untrusted input names. During the transaction, the write set remains exactly what the skill declared; the record is not part of it.

## What a record never claims

- Never an adjective for an exit code — the code is quoted, the reader derives the meaning.
- Never a merged verdict across claim families — cite by digest, don't blend.
- Never authority the gate did not grant — a recorded green gate still says nothing about code it did not exercise; the record repeats that boundary, it cannot waive it.
- Never a substitute for retained evidence — retained run and review output stays where it is; the record cites it, it does not copy it.

## The milestone-close record

Closing a milestone is itself a material event with a record, and that record
owes two sections no phase record can discharge for it:

- **The open-questions sweep** -- REQUIRED. Every record in the milestone
  directory is re-read and every open question it raised is dispositioned:
  closed (citing the record that closed it), carried (naming the next owner),
  or retired (with the reason). A question that appears in no sweep row was
  missed, and the sweep exists so that is detectable.
- **Refactoring review** -- each phase record carries its own `Refactoring
  review` section with one of exactly two honest answers: refactors EXECUTED
  (each named and behavior-preserving) or "none needed" argued from what the
  phase touched. The close record confirms every deferred refactor has an
  open-questions row with a named target -- deferred structure work is never
  silent debt.

## Worked example commits

Ordinary unit of work, green gate:

```
feat(settings-loader): add the versioned settings loader

pytest tests/test_settings_loader.py exited 0. The loader reads both
format versions and refuses an unknown version with exit 2. The green
result establishes the listed cases over the committed fixtures -- it
says nothing about callers that bypass the loader and nothing about
load time on large files.

Record: {{devtools:planning_dir}}/milestones/v1/003-settings-loader.md
```

Evidence about existing artifacts, non-zero exit recorded honestly:

```
docs(compat-audit): read stored documents back at check exit 1

pytest tests/test_stored_documents.py exited 1 -- one stored document
fails the new reader, reported as it stands, not repaired; a failure
about existing data is never a signal to edit that data. The audit
wrote only its own report file; this record and commit happened after
the audit closed and stage only that report plus the record.

Record: {{devtools:planning_dir}}/milestones/v1/006-compat-audit.md
```
