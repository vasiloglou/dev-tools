# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff do what notes/phase-2-spec.md requires of it, and where can its claims below be shown false, by a settings file, a folder layout or a command?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. With count_extra_dirs absent or false, every command of components_index.py prints and exits exactly as it does at ca6712a, the order of every list included.
- C2. With count_extra_dirs true, --check --strict, stats, draft, changed and review name a module under extra_source_dirs that no component covers, and show prints a module section for one that has a component.
- C3. draft gives a stub for any module counted_modules returns and never raises, whatever extra_source_dirs holds.
- C4. A value of count_extra_dirs that is not a JSON boolean stops the script with 'count_extra_dirs must be true or false'.
- C5. The import graph (package_imports, module_graph, changed's existed set, show's imports and outside importers) is unchanged: it stays inside package_dir.
- C6. Each new test fails at ca6712a except T1 and T10, which pin unchanged behaviour.
- C7. The docs/adopt.html caption says truly what the 0.1.5 survey prints, and the capture above it is unchanged.
- C8. plugins/ is rebuilt from skills/ at 0.1.5 and nothing under plugins/ was edited by hand.

## The change under review

The work from `ca6712a` to the working tree at `ca6712a1236a` with uncommitted changes. Its diff is `.planning/milestones/component-index/notes/reviews/phase-2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-2-r1/diff.patch` | `150edc5fcdfee21375f9bc0c18a878c403bc2fa9928cd89fbb9872fa59ec5eed` |
| `devtools/PLUGIN_VERSION` | `800cf1c0392b24de7c0a1c6ea6778ecb433dec71c49a150bce96a98477527b2f` |
| `docs/adopt.html` | `82fbf18d3138cee2acecc760218b02dd5ec97fb8dc326b85da4e1f932bbe2e37` |
| `examples/phase-project.devtools.toml` | `af7c9ba367e74745fbe582fdd4d2788ca85b46aebd8ff512b638d6aadbedeae1` |
| `plugins/dvt-milestone/.claude-plugin/plugin.json` | `45246108b8375f6611f5bcb69f9b648a0277079ea868fad3ae2ae34ef4e77037` |
| `plugins/dvt-milestone/skills/components/SKILL.md` | `2c2749ca50f13a5bc7c3c04c8495977f6f0298365d276c39d1c1679af7d80182` |
| `plugins/dvt-milestone/skills/components/references/build.md` | `176eb03fc41690ae96dce99b507bd4ae456ccf41da16af88b87565a5a191a17e` |
| `plugins/dvt-milestone/skills/components/scripts/components_index.py` | `820f0902253d69b5e0b101023774e3958db853b4c2b6c44032e47cc7d0301836` |
| `plugins/dvt-phase/.claude-plugin/plugin.json` | `eb0ef4b7304dab31dec56c2db48978bdd0600baed88631180846f4531f33ace6` |
| `plugins/dvt-phase/skills/components/SKILL.md` | `1d5ca3a23d20cf658b4ff636c42382de8f599c2ca56c36ea72ea57c5b937816a` |
| `plugins/dvt-phase/skills/components/references/build.md` | `176eb03fc41690ae96dce99b507bd4ae456ccf41da16af88b87565a5a191a17e` |
| `plugins/dvt-phase/skills/components/scripts/components_index.py` | `820f0902253d69b5e0b101023774e3958db853b4c2b6c44032e47cc7d0301836` |
| `skills/components/SKILL.md` | `1232e277b0b9b116325956b0084027963491aa02065d441392698eb5013d1e10` |
| `skills/components/references/build.md` | `f01ae0b3865c4f5028a2075b988a3a84ec4665436d2120a7df97a1c82562fb32` |
| `skills/components/scripts/components_index.py` | `820f0902253d69b5e0b101023774e3958db853b4c2b6c44032e47cc7d0301836` |
| `tests/test_tools.py` | `4657de24467e731a8fe21744430222f2c883009dd4a712b0bdb5f48971d3164f` |
| `.planning/milestones/component-index/notes/phase-2-spec.md` | `da85aa946edfe4fd8435cfd6e06518db2ef22e2f4b02d8965c5e4f7c1247df16` |
| `.planning/milestones/component-index/notes/component-index-plan.md` | `3cc5eb4924e69fb5584fd2613a0246718a27b5b3dd9e58f34afebabb97b886a9` |
| `.devtools/project.md` | `e2f5561d5449bd9136880b6fa1bf696322bc70bdd98d583bdaa2a15a2ce25a7a` |

You may read anything else in the repository that helps you answer.

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
