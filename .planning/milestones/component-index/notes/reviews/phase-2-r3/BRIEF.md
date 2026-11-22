# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 3. Do the repairs of round 2 (notes/reviews/phase-2-r2/FINDINGS.md, repaired at 882aa52) hold, and where can the claims below be shown false, by a settings file, a folder layout or a command? Rounds 1 and 2 are notes/reviews/phase-2-r1 and phase-2-r2.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. With count_extra_dirs absent or false, every command of components_index.py prints and exits exactly as it does at ca6712a, for any spelling of package_dir and extra_source_dirs that ca6712a accepts.
- C2. With count_extra_dirs true, --check --strict, stats, draft, changed and review name a module under extra_source_dirs that no component covers, and show prints a module section for one that has a component.
- C3. draft gives a stub for any module counted_modules returns and never raises, whatever spelling extra_source_dirs and package_dir use: relative, with a leading ./, absolute, or nested.
- C4. draft's ids for a package module are the ids ca6712a gives, whatever the package's name.
- C5. A value of count_extra_dirs that is not a JSON boolean stops the script with 'count_extra_dirs must be true or false'.
- C6. plugins/ is rebuilt from skills/ at 0.1.5 and nothing under plugins/ was edited by hand.

## The change under review

The work from `ca6712a` to the working tree at `a7bc35c47524`. Its diff is `.planning/milestones/component-index/notes/reviews/phase-2-r3/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/component-index/notes/reviews/phase-2-r3/diff.patch` | `ce9d42b8e3280521f3a9a3c7e278db494e2703f349d44d8f9bd6f3fa012d08b7` |
| `.planning/milestones/component-index/003-phase-2.md` | `b8aa7fba44e8a384390ebd06329fec6b99409d5cd48c28dba030bce83acedf19` |
| `.planning/milestones/component-index/README.md` | `ba216f2b0bc6eb4b833426a85f98d489c4a7f71eefeb42b197b4b0422354ea0a` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r1/BRIEF.md` | `5803d2e106ec7ac34e3c88699d37c4118367cadc4b69bcf43f7e73667a72f4d0` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r1/FINDINGS.md` | `caca54f89a9bfea201e468a36f6a5d599bf315f789bbacff181817c6a58918c7` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r1/brief.json` | `975f9a5b72b158731099a0ddf0e1707024d4ebe20cbb2a67fb1c44ea4a762e4a` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r1/diff.patch` | `150edc5fcdfee21375f9bc0c18a878c403bc2fa9928cd89fbb9872fa59ec5eed` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r1/review.md` | `922431c27090b0dd425447d4c42a328ddcf23a67923e39b5945333b784df39c9` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r1/run.json` | `4e7fef71e23f9d66da832a49072ba01f34350c4e1b4490af2ecfd6c14493acb4` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r2/BRIEF.md` | `d2cafd834ca66cd8d1351c5d95da99c4ef2902ac5b1f688d9cfe55b3982d9737` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r2/FINDINGS.md` | `4d56592a573d8afe0cc0be15e31cbac77f2e635f8c9f53f2a201ad9754a660ff` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r2/brief.json` | `1cf75c93849f5843fe03937c1ab1f2991702785a72ba3352566364605581527d` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r2/diff.patch` | `374857c9fad97c42b2874789c11abca5afdd24f614dee73970a2dd0726860e8b` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r2/review.md` | `032db4a2cb66193dca5276f8fbb647ea49c5b2f4a400ae9b9a889ed84eafe1e1` |
| `.planning/milestones/component-index/notes/reviews/phase-2-r2/run.json` | `da333bfba3b3d2e808ea68f745d67171851abaa2344c9923e4150d2f21e705fa` |
| `devtools/PLUGIN_VERSION` | `800cf1c0392b24de7c0a1c6ea6778ecb433dec71c49a150bce96a98477527b2f` |
| `docs/adopt.html` | `82fbf18d3138cee2acecc760218b02dd5ec97fb8dc326b85da4e1f932bbe2e37` |
| `docs/components.html` | `cee6abaf6d2eb176487a16ef48f6d3c5c0953a757b772b46793c02b9ec31a976` |
| `examples/phase-project.devtools.toml` | `af7c9ba367e74745fbe582fdd4d2788ca85b46aebd8ff512b638d6aadbedeae1` |
| `plugins/dvt-milestone/.claude-plugin/plugin.json` | `45246108b8375f6611f5bcb69f9b648a0277079ea868fad3ae2ae34ef4e77037` |
| `plugins/dvt-milestone/skills/components/SKILL.md` | `2c2749ca50f13a5bc7c3c04c8495977f6f0298365d276c39d1c1679af7d80182` |
| `plugins/dvt-milestone/skills/components/references/build.md` | `176eb03fc41690ae96dce99b507bd4ae456ccf41da16af88b87565a5a191a17e` |
| `plugins/dvt-milestone/skills/components/scripts/components_index.py` | `3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14` |
| `plugins/dvt-phase/.claude-plugin/plugin.json` | `eb0ef4b7304dab31dec56c2db48978bdd0600baed88631180846f4531f33ace6` |
| `plugins/dvt-phase/skills/components/SKILL.md` | `1d5ca3a23d20cf658b4ff636c42382de8f599c2ca56c36ea72ea57c5b937816a` |
| `plugins/dvt-phase/skills/components/references/build.md` | `176eb03fc41690ae96dce99b507bd4ae456ccf41da16af88b87565a5a191a17e` |
| `plugins/dvt-phase/skills/components/scripts/components_index.py` | `3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14` |
| `skills/components/SKILL.md` | `1232e277b0b9b116325956b0084027963491aa02065d441392698eb5013d1e10` |
| `skills/components/references/build.md` | `f01ae0b3865c4f5028a2075b988a3a84ec4665436d2120a7df97a1c82562fb32` |
| `skills/components/scripts/components_index.py` | `3b76af42ff825159ae80a445fbd69a11ae13c935e93793aa79888e6dd5ce4d14` |
| `tests/test_tools.py` | `8453af3f28b0c1fa31d35f563fa71b5e99409253488bee247d53fa574ef31df8` |
| `.planning/milestones/component-index/notes/phase-2-spec.md` | `da85aa946edfe4fd8435cfd6e06518db2ef22e2f4b02d8965c5e4f7c1247df16` |
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
