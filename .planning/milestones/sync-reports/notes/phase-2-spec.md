# Phase 2 spec: the sync reads the latest dev-tools

## 1. Status

Owner-decided (2026-11-23), by delegated approval (auto=true); recorded below, under
"Owner gate". Phase 1 is recorded (`002-phase-1.md`). Implementation may begin.

## 2. Provenance

- Derives from `notes/sync-reports-plan.md`, approved at SHA-256 `cb58b499…b967`
  (`001-plan.md`): section 2 ("Phase 2"), section 4 ("Phase 2", P2.1 to P2.7, P2.3b),
  sections 5, 6 (K3 to K8) and 9; D8 (the owner's "Yes, by default"), D9, D10 and D12.
- Plan review r1 F5 added the configured-but-missing upstream (P2.3b); that repair is
  unreviewed.
- Phase 1 (`notes/phase-1-spec.md`): `check` against a source is where "not current" is
  printed; this phase changes which commit that source is.
- No review round has read this spec.

## 3. Obligations

| # | Obligation (source) | Discharged in this spec |
|---|---|---|
| O1 | Behind only: the upstream's files are delivered; the receipt holds the upstream commit; `HEAD`, branch and `git status` unchanged (P2.1, C4, S0.2) | Section 6, `resolve_source`; T1 |
| O2 | Behind with a commit of its own, or uncommitted changes: delivered as it is, the warning before any file is written (P2.2) | T2, T3, T4 |
| O3 | Level, ahead only, detached, no upstream, not a checkout: as today, no new line (P2.3) | T5 |
| O4 | Upstream configured, no ref: delivered as it is, one warning, exit 0 (P2.3b; r1 F5) | T6 |
| O5 | A fetch that fails: one warning, exit 0, decided from the refs already there (P2.4, K4) | T7, T8 |
| O6 | `--as-is`: no fetch; a checkout behind is delivered as it is (P2.5, D10) | T9 |
| O7 | `compare` and `apply --dry-run` name the same files (P2.6) | T10 |
| O8 | A source folder inside another repository is not fetched (P2.7, K8) | T11 |
| O9 | The tool older than the files it reads says so (plan section 2, K6) | T12 |
| O10 | No existing test is edited; the repository's own checkout is read as it is and never fetched in the suite (S0.4, K3, C2) | Section 8, the autouse fixture; T13 |
| O11 | `check` against a behind checkout compares with the upstream (plan section 2) | T14 |
| O12 | The pages say the sync fetches, what it reads, and `--as-is` (plan section 4) | Section 6, "Pages" |
| O13 | The component index is current | Section 8, gates |

## 4. The standing rules, bound to this phase

| Rule | Bound to |
|---|---|
| S0.1 Today's lines and exits stay | Every line this phase adds goes to standard error, as the sync's warnings do; standard output and the exits are unchanged. T5 compares standard output with main's |
| S0.2 The checkout is read, never changed | The `git` commands added: `rev-parse --show-toplevel`, `symbolic-ref -q --short HEAD`, `config --get branch.<b>.remote`, `config --get branch.<b>.merge`, `fetch --quiet <remote>`, `rev-parse --verify <upstream>^{commit}`, `rev-list --left-right --count HEAD...<upstream>`, `status --porcelain -- <paths>`, `archive --format=tar <commit>`. Only `fetch` writes, and only remote-tracking refs. T1 compares `HEAD`, branch and `git status --porcelain` before and after |
| S0.3 A report is rows before it is lines | `resolve_source` returns the decision as data (`state`, `commit`, `lines`); `main` prints the lines |
| S0.4 A test brings its own upstream | Every test of this phase builds an upstream and a clone under `tmp_path`, with `file://`-free local paths. The autouse fixture reads the repository's own checkout as it is, and fails a test that starts `git fetch` in it |
| S0.5 One file on the standard library | `tarfile` is added to the imports |
| A script change comes with a test | `devtools/sync.py`: `resolve_source`, `cmd_apply`, `cmd_check`, `cmd_compare`, `cmd_survey`, `main`. Section 8 |
| The plugins are rebuilt, and released under a new version | No plugin file changes; `build_plugins.py --check` shows it |
| A wording change says what prompted it | The owner's question of 2026-11-23, "shouldn't the sync skill run an install of the latest dev-tools?", and the baseline's checkout 54 commits behind (an inherited claim, plan section 3) |
| Shared skills stay general | `skills/adopt-devtools/SKILL.md` gains one sentence on what the sync reads, true for any project |
| Both agents read the same file | The sentence names commands only |
| Captures on the site are real output | The frames retaken in phase 1 run from a checkout with no upstream (a worktree branch), so they print nothing new; T5 holds that. No new frame |
| The page that describes it is updated too | `README.md`, `docs/adopt.html`, in this phase's commits |

## 5. Goal

With an upstream repository and a clone one commit behind it: `apply` exits 0, delivers
the upstream's files, prints one `note:` line on standard error, and leaves the clone's
`HEAD`, branch and `git status --porcelain` as they were. With the clone ahead as well,
or dirty, `apply` delivers the clone's files and prints one `warning:` line. `--as-is`
starts no `git fetch`. `pytest tests -q`, `build_plugins.py --check` and the built
`components_index.py --check --strict` each exit 0.

## 6. Design

### Reuse

| Capability | Searches run | Found | Decision |
|---|---|---|---|
| Know a checkout's upstream and how far behind it is | `search fetch upstream git ref` (plan); `search ahead behind upstream branch` | `handoff.base_ref`, `components_index.git` in scripts that stand alone; `sync.source_identity` runs `git -C <source> rev-parse HEAD` | new in `sync.py`: the scripts import nothing from each other (component-index R0.1); `source_identity` is reused for the dirty check's style |
| Read a commit's files | `search file text at a commit` | `components_index.files_at` reads text by path with `git cat-file --batch` | new: the sync needs every file of a commit with its mode, which `git archive` gives in one call |

### `devtools/sync.py` (about 120 lines added)

```python
def resolve_source(path: Path, *, as_is: bool) -> dict:
    """Which files a run reads for the dev-tools source at ``path``. Starts ``git fetch`` unless
    ``as_is``; changes nothing else. Returns {"root": Path, "commit": str | None,
    "state": str, "lines": [str], "cleanup": callable}."""
```

`state` is one of these, spelled so in the code and the tests:

| `state` | When | `root` | `lines` (standard error) |
|---|---|---|---|
| `"folder"` | `path` is not the top level of a git checkout (not a checkout, or a folder inside another repository) | `path` | none |
| `"detached"` | `HEAD` is not on a branch | `path` | none |
| `"no-upstream"` | the branch has no `branch.<b>.merge` | `path` | none |
| `"upstream-missing"` | `branch.<b>.merge` is set, and `<remote>/<branch>` (or, for remote `.`, the local branch) has no commit after the fetch | `path` | `warning: this dev-tools branch's upstream, <name>, was not found; delivering the checkout as it is` |
| `"current"` | behind is 0 | `path` | none |
| `"as-is"` | behind > 0 and `--as-is` | `path` | `warning: dev-tools here is <n> commit(s) behind <name>; delivering the checkout as it is (--as-is)` |
| `"own-work"` | behind > 0, and ahead > 0 or `git status --porcelain -- skills agents devtools examples` prints anything | `path` | `warning: dev-tools here is <n> commit(s) behind <name> and has work of its own (<k> commit(s) ahead, <d> uncommitted path(s)); delivering the checkout as it is` |
| `"upstream"` | behind > 0, ahead 0, nothing uncommitted under those paths | a temporary folder holding `git archive` of the upstream commit | `note: dev-tools here is <n> commit(s) behind <name>: delivering <name> at <sha7>; the checkout is not changed (git pull in <path> updates it)` |
| `"upstream-unreadable"` | as `"upstream"`, but `git archive` or its extraction fails | `path` | `warning: could not read <name> at <sha7> (<error>); delivering the checkout as it is` |

The order of the checks is the order of the table. One more line can be added to any
state but the first three:

- **The fetch.** Unless `as_is`, and only for a branch with `branch.<b>.remote` other
  than `.`: `git -C <path> fetch --quiet <remote>`, with `GIT_TERMINAL_PROMPT=0` in its
  environment and a timeout of 60 seconds. On a non-zero exit, a timeout or an `OSError`:
  `warning: could not fetch <remote> (<first line of the error>); deciding from the refs
  already fetched`, and the table is applied as usual.
- **The tool.** In state `"upstream"`, when the archive holds `devtools/sync.py` and its
  bytes differ from the running file's: `note: the sync.py that runs differs from the one
  at <name>; git pull in <path> updates it`.

`commit` is the commit read: the upstream's in `"upstream"`, `HEAD`'s otherwise (None
for `"folder"`). `cleanup` removes the temporary folder; `main` calls it after the
command, also on an error.

**The paths a dirty check reads** are `skills`, `agents`, `devtools` and `examples`:
what the sync reads and runs. An untracked file elsewhere in the checkout (notes, a
build) does not stop the upstream from being read (S4).

**Where it is called.** `main` resolves `args.source` for `apply`, `compare` and
`survey`, and for `check` when a source is used, before the command runs, prints
`lines` on standard error, and passes `root` on. `source_identity` is then asked only
for `dirty`; the receipt's commit is `resolve_source`'s `commit`. `--as-is` is added to
the four commands.

**Reading the archive.** `git archive --format=tar <commit>` into `tarfile.open(fileobj=…,
mode="r|")`, extracted with the `"data"` filter where the Python has it (3.11.4 and
later) and without a filter otherwise; the archive is the source's own commit.

### Pages

- `README.md`, "How a project takes it": the sync fetches the checkout's upstream first
  and reads the upstream's files when the checkout is only behind; `--as-is`.
- `docs/adopt.html`, "Updates that respect your changes": one row, "Your dev-tools
  checkout is behind", and one sentence in the section head.
- `skills/adopt-devtools/SKILL.md`, step 2.2 (the dev-tools commit the record names): the
  commit is the one `apply` prints on its `note:` line when it reads the upstream.

## 7. Decisions

| # | Question | Readings and their cost | Proposed |
|---|---|---|---|
| S1 | Where the new lines go | **Standard error,** like every warning of the sync: standard output is unchanged (S0.1). **Standard output:** a project's script that reads `applied:` from the last line breaks | Standard error |
| S2 | Which uncommitted changes keep the checkout as it is | **Under `skills`, `agents`, `devtools`, `examples`:** what the sync reads; untracked notes elsewhere do not block. **Anywhere:** one stray file keeps every sync on old files, the silence this phase removes | Those four |
| S3 | The fetch's time limit | 60 seconds. A shorter one fails on a slow network; no limit can hang a CI job | 60 |
| S4 | What is archived | **The whole commit:** a config may name any path of dev-tools. **Only the four folders:** smaller, and a source path outside them would read as missing | The whole commit |

## 8. Tests

All in `tests/test_sync.py`. A fixture `behind` builds, under `tmp_path`: `upstream`, a git
repository with `skills/demo/SKILL.md` and one commit; `clone`, `git clone` of it; then a
second commit in `upstream` that changes `skills/demo/SKILL.md`. `clone` is one commit
behind once it fetches. A project with `[[sync]] source = "skills/demo"`.

| # | Case | Expected |
|---|---|---|
| T1 | `apply --source clone` | Exit 0; the project's `SKILL.md` is the upstream's second version; the receipt's commit is the upstream's second commit; the `note:` line; `git -C clone rev-parse HEAD`, `symbolic-ref HEAD` and `status --porcelain` equal before and after |
| T2 | A commit in `clone` too (ahead 1, behind 1) | Exit 0; the clone's version delivered; the `own-work` warning |
| T3 | `skills/demo/SKILL.md` edited in `clone`, uncommitted | As T2 |
| T4 | As T2, with a project file edited by hand so `apply` refuses (exit 3) | The warning is on standard error although nothing is written |
| T5 | Level (no second commit); ahead only; detached (`checkout --detach`); a new branch with no upstream; the folder copied out of git | Exit 0; standard error has no `note:` and no `warning: dev-tools here`; standard output equals the output of the same run with `--as-is` |
| T6 | `branch.<b>.merge` set to `refs/heads/gone` | Exit 0; the `upstream-missing` warning; the clone's version delivered |
| T7 | `remote.origin.url` set to a path that does not exist, after a first fetch that saw the second commit | Exit 0; the fetch warning; the upstream's version delivered (decided from the refs already there) |
| T8 | `sync.subprocess.run` raises `TimeoutExpired` for `fetch` | Exit 0; the fetch warning |
| T9 | `--as-is` on T1's setup, with `subprocess.run` recorded | No call holds `fetch`; the clone's version delivered; no `note:`. After one fetch by the test, `--as-is` prints the `own-work`-free warning `warning: dev-tools here is 1 commit(s) behind origin/<b>; delivering the checkout as it is (--as-is)` |
| T10 | T1's setup: `compare` and `apply --dry-run` | Both name `.claude/skills/demo/SKILL.md` as changed; `compare` shows the upstream's line as the shipped one |
| T11 | The source is `skills-holder/` inside a repository, with an upstream | No call holds `fetch`; state `"folder"` |
| T12 | The upstream's second commit also adds `devtools/sync.py` with other bytes | The `note: the sync.py that runs differs` line |
| T13 | Any example applied from the repository with the autouse fixture | No `git fetch` against the repository's checkout (the fixture raises if one starts) |
| T14 | `check --source clone` after an apply at the first commit, with the clone behind | `not current: an apply would update 1 file(s) (synced from dev-tools at <first7>; this source is at <second7>)` |
| T15 | `resolve_source` on each of T1, T2, T5, T6, T11, and with `--as-is` on T1 after a fetch (`"as-is"`) | `state` is `"upstream"`, `"own-work"`, then `"current"`, `"current"`, `"detached"`, `"no-upstream"`, `"folder"`, then `"upstream-missing"`, `"folder"`; `cleanup` removes the temporary folder of `"upstream"` |
| T16 | `git archive` fails | Exit 0; the clone's version delivered; the `upstream-unreadable` warning |

**Branches, walked against the table of section 6.** `folder`: T5, T11. `detached`: T5.
`no-upstream`: T5. `upstream-missing`: T6. `current`: T5 (level, ahead only). `own-work`:
T2 (ahead), T3 (dirty). `upstream`: T1. Fetch failure: T7 (exit), T8 (timeout). No fetch:
T9, T11. Tool line: T12, and absent in T1.

**Existing tests.** None edited. The autouse fixture is extended: `resolve_source` called
with the repository's own root reads it as it is, and a `git fetch` started in that root
fails the test.

**Verification selection.** As phase 1's, with `--base` the commit phase 2 begins from
for `changed`. A by-hand run: a scratch clone of a scratch upstream, one commit behind,
`python3 devtools/sync.py apply --project "$SCRATCH/project" --source "$SCRATCH/clone"
--dry-run`, then `git -C "$SCRATCH/clone" status --short` and `rev-parse HEAD` before and
after; the lines go into the record.

## Owner gate

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/sync-reports/notes/phase-2-spec.md (the bytes of the
      commit that adds this block; its SHA-256 is in the phase 2 record)
    date: 2026-11-23
    authorization: the owner's "Milestone, auto=true" for sync-reports (001-plan.md)
    instrument: this prose (section 11); no review over the spec bytes
    decisions: S1 to S4 as proposed
    implementability sweep: each state of section 6 walked against T1 to T16 by the
      agent, 2026-11-23; it added the states "as-is" and "upstream-unreadable" and T16
      before this ruling

## 9. Out of scope for this phase

- Running the fetched `sync.py` (plan Q3).
- Changing the checkout in any way but the fetch.
- A source given as a URL.

## 10. Size

Estimate: `devtools/sync.py` about 120 lines; tests about 220; pages about 15.

## 11. Approval instrument

This prose.

## Implementation findings, recorded as they were found

1. **The upstream's name was built by hand** (2026-11-23, self-review before the review
   round). `refs/remotes/<remote>/<branch>` is wrong for a remote whose fetch refspec
   maps branches elsewhere: such a clone kept comparing with the stale ref the clone
   wrote. Now `<branch>@{upstream}` is asked of git, for the commit and for the name.
   New test T17, red before the change.
2. **The retaken frames of phase 1 print the same under phase 2**: re-run from this
   checkout, whose branch has no upstream (state `no-upstream`), the first-sync and
   hand-edit frames' output was byte for byte the same (`diff` exited 0).
