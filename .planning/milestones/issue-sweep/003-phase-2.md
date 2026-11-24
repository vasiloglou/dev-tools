---
milestone: issue-sweep
station: "phase-2"
skill: "n/a -- repository development, not a run of a project workflow skill"
scope: phase-2
date: 2026-11-23
gates:
  - command: "uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_own_index.py tests/test_plugins.py tests/test_index_cache.py -q"
    exit: 0
    output: "141 passed in 110.16s (0:01:50)"
  - command: "uv run --no-project --with pytest python -m pytest tests -q"
    exit: 0
    output: "500 passed in 283.67s (0:04:43)"
    note: "the run before the review repairs printed 1 failed, 494 passed (J10), then 496 passed after the tie repair"
  - command: "python3 devtools/build_plugins.py --check"
    exit: 0
  - command: "python3 devtools/release_plugins.py status"
    exit: 1
    output: "0.1.7 is ready: after the merge, run `release_plugins.py tag` on main"
    note: "exit 1 is the spec's expected value: a release is due"
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict"
    exit: 0
  - command: "python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base 361b2cc --strict"
    exit: 0
    output: "changed against 361b2cc (361b2cc): 32 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml skills/components/scripts/rules_check.py plugins/dvt-phase/skills/components/scripts/rules_check.py plugins/dvt-milestone/skills/components/scripts/rules_check.py"
    exit: 0
    output: "All checks passed!"
  - command: "ruling: delegated (auto=true) approved .planning/milestones/issue-sweep/notes/phase-2-spec.md sha256 7e8c54f8f4f33e4a32b0a0b126eded7996539e2eafea75ec85bd34eba6f56262"
    exit: "n/a -- ruling"
slow_cadence:
  command: "none beyond the full suite"
  trigger: "n/a"
  reason: "the full suite is the repository's only test lane, and it ran (above)"
evidence:
  - path: skills/components/scripts/components_index.py
    sha256: 7dec1e7712c271f1d2e8c44d2abcec163b080b7d6805e784f8e43e9675180d8a
  - path: skills/components/scripts/rules_check.py
    sha256: 2d80e2f9c4bb33802e979a509bc0343002529324cda24e1be175e2e495ebcc77
  - path: skills/components/SKILL.md
    sha256: 7651579672099fa296d2b55667b79e54e2500bedef1c00d8dba98e56c696e1fc
  - path: skills/components/references/build.md
    sha256: 7709021f8ce3c350a9451885656055b2ac457117b902625fcaebb4d0f8682c61
  - path: skills/components/references/review.md
    sha256: 7fdc105d616b8c4c51cfd0ac38615efaf61eb7155eeca3db3ca1cf525226e12d
  - path: docs/components.html
    sha256: 1cc1a1e794e6e37d0996050d31f5a679ec392854f4352fc978781779739e5c0a
  - path: tests/test_tools.py
    sha256: b2b1ddcbe81c63bba643ffc592ce282b60686edc22f832d92d1c72d03b08c690
  - path: tests/test_own_index.py
    sha256: a8d971fd544d93af956c7305e03b6f0e3fd238ba9eb6f9179e379c827ce6d3d5
  - path: .devtools/components_index.settings.json
    sha256: 0ab385e6a6975d8f1906f4b57039255e0c56562b6a46471e8f6802310d23b83f
  - path: .devtools/project.md
    sha256: fd2ec297396724924d180254c66e25b7534cd29dfdc32cb738f6aad3d3f8104d
  - path: .devtools/components/COMPONENTS.md
    sha256: 4c045ee969069caac4b2fc6e98511f2319172352300aa0fa0d7bf678cdeb47c3
  - path: .devtools/components/modules/skills.md
    sha256: a4baca65cc027bb6bc9aed194cda958465bef9b30db8e3c55974d23bba059520
  - path: devtools/PLUGIN_VERSION
    sha256: ba57e7c7f71876d645bcdd9fb070f2dea8e6db5ed284a7e3d85c6b7d2409fef1
  - path: .planning/milestones/issue-sweep/notes/phase-2-spec.md
    sha256: 67ab21cb211951dff411dd829e50482d0a1af872a5d38b460191038a6be19532
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-2-r1/BRIEF.md
    sha256: eb7a86756fa77ee04171505dbf662a701a9ff59653519463ed1a92385f8231d6
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-2-r1/diff.patch
    sha256: ac796ef659659b9df8c1c1bc093585e95273827311677c9ea76ea0325f1fad46
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-2-r1/review.md
    sha256: c7472e223d2b4c873f1e01a402f262ed4e12823314b85cc05f0ae54092145480
  - path: .planning/milestones/issue-sweep/notes/reviews/phase-2-r1/FINDINGS.md
    sha256: 8e1223ca89b2ba25e7fa4aff7733c5b5941daffe955879f02ae7064a676f873a
---

# Claim

Phase 2's selected gates each exited 0 on the phase's head, except the release status,
which exits 1 as the spec expects: the index tool can refuse a baseline (issue 46),
compares with the upstream of a local base that is behind it and says so (issue 45), takes
a `reread:` line as the date of an entry (issue 45), and reviews the folders
`count_extra_dirs` counts (issue 44). The plugins are at 0.1.7.

## What shipped

Commits `47dc420` (the work; first committed as `ed88315` with a message that said the
suite had passed, then amended with the tie repair of J10 and a true message before
anything was built on it) and `ba1d686` (the review repairs), on the base `361b2cc` (the spec and its
delegated gate).

- **`skills/components/scripts/components_index.py`** (+91 -36).
  - `allow_baseline` (default true), validated as a boolean. With false, `--check
    --strict` prints `baseline refused: …` and excuses nothing while the file exists, and
    `stats --write-baseline` refuses with exit 1 (spec D1; the plan's P2.1 said 2).
  - `resolve_base`: the one home of the base rule. A name git reads as a local branch
    (`rev-parse --symbolic-full-name`) that is strictly behind its configured upstream is
    read as the upstream, with one line. `base_snapshot` returns the line; `changed`
    prints it as `note:` before its summary; `facts` hands it to `main`, which prints it
    on standard error. Every git command reads.
  - `entry_commits` dates an entry by its `does`, `verbs`, `flow` and `reread` lines,
    with ties within one second settled by history; `review` says "when it was last
    marked as reread" when that line decided. `reread` may appear once.
  - `review` reads `counted_modules` for the owners table, names, docstrings, size, the
    `defines main` label and its summary; the import-graph groups still read the package.
- **`skills/components/scripts/rules_check.py`** (+3): `read_facts` relays the index
  script's `note:` lines to standard error.
- **The skill** (`SKILL.md`, `build.md`, `review.md`) and **`docs/components.html`**: the
  setting, the note, nothing fetched, the `reread` field and when to write it, and the
  counted folders in `review`.
- **dev-tools' own files**: `allow_baseline: false`; `tests/test_own_index.py` relies on
  the tool's refusal and tests that no baseline can be written; `.devtools/project.md`
  names 0.1.7; four index entries edited or marked reread (J8).
- **The plugins**: 0.1.6 to 0.1.7 (`release_plugins.py bump`), rebuilt.
- **Tests** (`tests/test_tools.py` +325): A1 to A3, B1 to B5 (B2 with nine states), C1 to
  C3, D1 to D3 as the spec lists them, and three added on the way: the one-second tie
  with and without a `reread:` line, and a branch named in full.

Decisions that survived: D1 to D6 of the spec, as ruled; D5 to D8 of the plan.

## Gate output (verbatim)

    $ uv run --no-project --with pytest python -m pytest tests/test_tools.py tests/test_own_index.py tests/test_plugins.py tests/test_index_cache.py -q
    141 passed in 110.16s (0:01:50)
    $ uv run --no-project --with pytest python -m pytest tests -q
    500 passed in 283.67s (0:04:43)
    $ python3 devtools/build_plugins.py --check
    (no output; exit 0)
    $ python3 devtools/release_plugins.py status
    version in the tree: 0.1.7
    released: 0.1.2 (plugins-v0.1.2)
    30 plugin file(s) changed since plugins-v0.1.2
    0.1.7 is ready: after the merge, run `release_plugins.py tag` on main
    (exit 1)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
    (no output; exit 0)
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base 361b2cc --strict
    changed against 361b2cc (361b2cc): 32 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    $ uvx ruff@0.16.2 check --config ~/github-repos/gnd-public/pyproject.toml <the three copies of rules_check.py>
    All checks passed!
    $ python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base main   (by hand, in this worktree)
    note: main (b685e82) is 99 commit(s) behind origin/main (cecebc6): comparing with origin/main
    changed against origin/main (cecebc6): 36 file(s) differ; 0 to fix, 0 warning(s), 1 to reread

    ruling: delegated (auto=true) approved
    artifact: .planning/milestones/issue-sweep/notes/phase-2-spec.md, as committed at 361b2cc
    sha256: 7e8c54f8f4f33e4a32b0a0b126eded7996539e2eafea75ec85bd34eba6f56262
    date: 2026-11-23
    authorization: the owner's "process-milestone issue-sweep auto", for this milestone
    decisions: D1 to D6 of the spec, each as proposed
    instrument: the spec's prose; phase review by review_tool.py, at most r1 and r2
    not covered: pushing, the pull request, merging, tagging, anything posted to GitHub

This is an agent's ruling under the owner's delegation, not the owner's own reading. The
spec has since grown by its findings, its review round, and two corrections marked at
their sites (r1 F1, r1 F2); its digest now is in the evidence list.

## Criteria

| Criterion | Evidence | Met |
|---|---|---|
| P2.1 Refuse a baseline; the default as before | A1, A2, A3; the existing baseline tests unedited | yes, with exit 1 for the refused write (D1) |
| P2.2 A base strictly behind: its upstream and one line; every other state as before | B1; B2's nine states; the branch named in full; the negative control of J2 | yes |
| P2.2b `facts --base` and the rule check follow it | B4, B5 | yes; the rule check's summary names the base as given (J4) |
| P2.3 Nothing fetches | B3, and the negative control of J2 | yes |
| P2.4 A `reread:` line dates the entry; twice is refused | C1, C2, C3, and the one-second tie | yes |
| P2.5 `count_extra_dirs` reaches `review`'s module groups | D1 to D3, each with the setting on and off | yes |
| P2.6 dev-tools' "no baseline" check is `--check --strict` alone | E1, E2 in `tests/test_own_index.py` | yes |

## Review

One round of the review helper, `--subject phase --base 361b2cc`, reviewer Codex,
read-only, effort `high`. **One reviewer is one reviewer.**

| Round | Brief | Findings | Blocking | Self-inflicted | Verdict | Repaired at |
|---|---|---|---|---|---|---|
| phase-2-r1 | `eb7a8675…31d6` | 2 | 1 | 0 / 2 | CHANGES_REQUESTED | `ba1d686` |

- F1 (blocking): a tag and a branch of one name; the base rule took the branch. F2
  (hardening): the tie rule changes a default output in a narrow case. Both reproduced
  before they were believed; the ledger has each reproduction and regression test.
- The reviewer confirmed: the build and strict index checks exit 0; on this checkout the
  stale `main` is read as `origin/main` with one note before the summary; the two `facts`
  documents are byte for byte equal, with the note on standard error; the baseline, the
  boolean check, reread dating, the repeated field and the counted groups behave as the
  spec says in its in-memory probes; only read-only git commands.
- It ran no test and could not repeat the negative controls (read-only; no pytest in its
  environment). Those are this record's evidence, not the reviewer's.
- `review.md` needed no sanitizing; `review.log` had 35 paths replaced and stays out of
  history.

`review_tool.py status` reports as `unreviewed`, since each changed after the round read
it: `components_index.py` and its two plugin copies, `tests/test_tools.py`, the spec and
`.devtools/components/modules/skills.md`. No review opinion covers F1's repair or the
spec's corrections.

## Refactoring review

Refactors executed: none needed beyond the phase's own. `base_snapshot` held the base
rule inline; it now calls `resolve_base`, which `changed` and `facts` share through it,
so the rule has one home.

Seen and deferred: the 13 same-name leads `review` now prints for dev-tools (J7):
`cell`, `find_root`, `read_json`, `Stop` and others across the scripts of `skills/`.
Shipped scripts stand alone (S0.2), so most will be `distinct_from` rather than merged;
which is a review of the index, not this phase. Target: the close's question sweep, as
an offer to the owner.

## Boundary -- what this phase does NOT establish

- That the base rule is right for a repository with several remotes, or a branch whose
  upstream is another local branch. Only `origin` remotes under `tmp_path` were tested.
- That a project's CI, which may hold a stale local base, wants the upstream; it gets it,
  with a line, and `--base <commit>` keeps the old reading.
- That `rules_check.py`'s summary names the ref used. It names the ref asked for, with
  the commit used (J4).
- That the 13 new same-name leads in dev-tools are duplicates. They are leads.
- That the `reread:` lines added here are more than the agent's reading beside the
  commits named in them.
- The review repairs carry no review opinion. One reviewer is one reviewer, and it ran no
  test. Every run was on macOS. Nothing is pushed or posted.

## Open questions

- J4: should `rules_check.py check --base` name the ref the facts were read at? It would
  have to read its sibling's message, or `facts` would need a field the
  `devtools-facts/1` format does not have.
- J7: a review of dev-tools' index (the components skill's Review mode) for the 13 leads,
  and for `sync.copies` and `handoff.notes`, still listed as older than their code.
- Plan repairs for the close: P2.1's "exits 2" (D1); section 9 and the phase 1 spec's
  `uvx` command without `--isolated` (from `002-phase-1.md`).

## Refuted premises

- "B3 is seen red before its code exists" (spec, section 8). Refuted by the red run of
  J1, where B3 passed: the code before the phase fetched nothing. Held by a negative
  control instead (J2).
- "`rules_check.py check --base main` prints what `--base origin/main` prints" (spec,
  B5). Refuted by its summary line, which names the base as given (J4).
