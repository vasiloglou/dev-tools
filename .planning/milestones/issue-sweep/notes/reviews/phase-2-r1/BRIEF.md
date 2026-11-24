# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff do what the phase 2 spec says for issues 44, 45 and 46, does a project with default settings see the lines and exits it saw before, and can each new test fail when the behaviour it names is wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. P2.1. With allow_baseline false and a baseline file, --check --strict exits 1 and names the file, and stats --write-baseline writes nothing; without the setting a project with a baseline exits as before.
- C2. P2.2. A local base strictly behind its configured upstream is compared through that upstream with one note: line before the summary; every other state of the base (level, ahead, diverged, no upstream, a commit, a remote-tracking branch, a tag, a name only the remote has) prints what it printed before this diff.
- C3. P2.2b. facts --base in the stale state writes on standard output, and to --out, exactly the document that facts --base <upstream> writes, with the note on standard error only; rules_check.py check --base judges against that base.
- C4. P2.3. No command of either script starts git fetch, pull, push or remote, in any state.
- C5. P2.4. An entry whose reread: line was committed after the last commit to its modules is not listed as older than its code, also when the commits share one second; after a later commit to a module it is listed again; a second reread: line is refused.
- C6. P2.5. With count_extra_dirs on, the same-name, no-docstring, over-12-modules groups, the defines-main label and the summary's count cover the extra folders; with it off every line of review is what it was before this diff.
- C7. P2.6. dev-tools' own check that no baseline is kept is --check --strict alone, and tests/test_own_index.py holds it through the setting.
- C8. The skill, its references, docs/components.html and .devtools/project.md describe what the code now does, and nothing they say is false of it.

## The change under review

The work from `361b2cc` to the working tree at `47dc420fa636`. Its diff is `.planning/milestones/issue-sweep/notes/reviews/phase-2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/issue-sweep/notes/reviews/phase-2-r1/diff.patch` | `ac796ef659659b9df8c1c1bc093585e95273827311677c9ea76ea0325f1fad46` |
| `.devtools/components/COMPONENTS.md` | `4c045ee969069caac4b2fc6e98511f2319172352300aa0fa0d7bf678cdeb47c3` |
| `.devtools/components/modules/skills.md` | `6bb486b61c9632bb47535e5770b4bda16d7505525eedc3bc6d80353d1be57f07` |
| `.devtools/components_index.settings.json` | `0ab385e6a6975d8f1906f4b57039255e0c56562b6a46471e8f6802310d23b83f` |
| `.devtools/project.md` | `fd2ec297396724924d180254c66e25b7534cd29dfdc32cb738f6aad3d3f8104d` |
| `.planning/milestones/issue-sweep/notes/phase-2-spec.md` | `d1e6f5dedf8570152021aeabd711db6ef9cdaf88e2ab5b4f213b48f157369513` |
| `devtools/PLUGIN_VERSION` | `ba57e7c7f71876d645bcdd9fb070f2dea8e6db5ed284a7e3d85c6b7d2409fef1` |
| `docs/components.html` | `1cc1a1e794e6e37d0996050d31f5a679ec392854f4352fc978781779739e5c0a` |
| `plugins/dvt-milestone/.claude-plugin/plugin.json` | `ba49d7a134b03f75dbaa4fb140deecf56257bfc6a27d1c64c44b1f9a910d4b48` |
| `plugins/dvt-milestone/skills/components/SKILL.md` | `fdaa2b5840c8f2f14888b530b5afa52ac058191d52aafb45cf098d35b38432f0` |
| `plugins/dvt-milestone/skills/components/references/build.md` | `8611a48655783b8ef93aadfb242d2ff5faffb06e86e20b77cf4bc9a7931c2b5b` |
| `plugins/dvt-milestone/skills/components/references/review.md` | `cb28509de7384be701dd6aa74ae6045cd81667173d89f1b3a3ba8e1729191473` |
| `plugins/dvt-milestone/skills/components/scripts/components_index.py` | `c2c576e2012b85d6ba7239c40fba745caf00287dd5f4d8f9bb0bcaabf3d781c1` |
| `plugins/dvt-milestone/skills/components/scripts/rules_check.py` | `2d80e2f9c4bb33802e979a509bc0343002529324cda24e1be175e2e495ebcc77` |
| `plugins/dvt-phase/.claude-plugin/plugin.json` | `cb13a5176a3da1b2391dd70e2f9eeda0cbb46f795664bc6a9c73f13aad08dd32` |
| `plugins/dvt-phase/skills/components/SKILL.md` | `25f8bc277866fe2852dc248747242967053d508dad0302d2f85db477b7ddb8a8` |
| `plugins/dvt-phase/skills/components/references/build.md` | `8611a48655783b8ef93aadfb242d2ff5faffb06e86e20b77cf4bc9a7931c2b5b` |
| `plugins/dvt-phase/skills/components/references/review.md` | `cb28509de7384be701dd6aa74ae6045cd81667173d89f1b3a3ba8e1729191473` |
| `plugins/dvt-phase/skills/components/scripts/components_index.py` | `c2c576e2012b85d6ba7239c40fba745caf00287dd5f4d8f9bb0bcaabf3d781c1` |
| `plugins/dvt-phase/skills/components/scripts/rules_check.py` | `2d80e2f9c4bb33802e979a509bc0343002529324cda24e1be175e2e495ebcc77` |
| `skills/components/SKILL.md` | `7651579672099fa296d2b55667b79e54e2500bedef1c00d8dba98e56c696e1fc` |
| `skills/components/references/build.md` | `7709021f8ce3c350a9451885656055b2ac457117b902625fcaebb4d0f8682c61` |
| `skills/components/references/review.md` | `7fdc105d616b8c4c51cfd0ac38615efaf61eb7155eeca3db3ca1cf525226e12d` |
| `skills/components/scripts/components_index.py` | `c2c576e2012b85d6ba7239c40fba745caf00287dd5f4d8f9bb0bcaabf3d781c1` |
| `skills/components/scripts/rules_check.py` | `2d80e2f9c4bb33802e979a509bc0343002529324cda24e1be175e2e495ebcc77` |
| `tests/test_own_index.py` | `a8d971fd544d93af956c7305e03b6f0e3fd238ba9eb6f9179e379c827ce6d3d5` |
| `tests/test_tools.py` | `1ad93e01664157f642d476a1f0d5c636e67540b5302dd1b342f92e9ef5d80fb1` |
| `.planning/milestones/issue-sweep/notes/issue-sweep-plan.md` | `309c6e556ac85f24e71f3c63f79356421392e570cdf143472b02f1acd90481a4` |
| `.planning/milestones/issue-sweep/notes/issues-2026-11-23.md` | `7584fec3d861c1113450fa58207fbc671f1ad9e77f2db673d6b1df1f575dc84c` |

You may read anything else in the repository that helps you answer.

## A standing check: code fitted to its examples

Whatever the question above, also look in the code this change adds or changes for a
solution that handles the examples in its tests and fixtures, and not the whole class of
input it is given:

- a regular expression, string split, slice or index over structured text (JSON, YAML,
  TOML, source code, paths, command lines) that a parser or an existing reader in this
  repository already reads;
- a pattern over output this project renders itself (a report, a table, a log line), where
  the code could have been handed the data instead;
- a pattern fitted to the fixtures: it matches every committed example and fails on a
  legal input with other whitespace, quoting, casing, nesting, Unicode or a line break;
- a branch on one literal name, file or message, added to make one case pass;
- a second matcher for something an existing helper already does.

A regular expression is not a finding in itself: one that states the whole grammar of a
flat token (an identifier, a version number, a hex digest) is the right tool. For each
suspect, build a legal input that the tests and fixtures lack and run the code on it.
Report a finding only with that input: what the code returned and what it should have
returned. A suspicion with no breaking input is style: label it so. In your list of what
you checked, name each matcher you tried and the input you tried it with.

## Rules

- Read only. Do not edit, create, stage, commit, push or post anything.
- Do not open `.env` files, keys, tokens, `auth.json` or any other credential file, and do
  not print environment variables. If you need one, name it and go on without it.
- A finding names its file and line and the consequence someone would observe. Run what
  you can to show it; where you only read, say so.

## What to return

1. Findings, each with an id (F1, F2, ...), file and line, what is wrong, the observable
   consequence, and how to reproduce it. A finding with no observable consequence is
   style: label it so.
2. What you checked and found true.
3. What you could not check, and why.
4. A last line: `VERDICT: APPROVE` or `VERDICT: CHANGES_REQUESTED`.
