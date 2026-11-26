# Review brief: the milestone close

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the evidence of this milestone support closing it: does each completion predicate P1 to P7 of the close record hold on the code as it stands, and does the code changed in 24003fd, which no review round has read, do what 004-pr-51-r2.md says it does, without breaking what the earlier records say?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. C1. Each predicate P1 to P7 in 005-close.md holds on the code, tests and records as they stand at this commit.
- C2. C2. Each of the nine repairs of 24003fd (F1 to F9 as 004-pr-51-r2.md describes them; see git show 24003fd) does what that record says, and each has a test in tests/test_tools.py that fails on the code before 24003fd (git show 24003fd^:skills/components/scripts/components_index.py).
- C3. C3. 24003fd breaks none of the behaviour that 001 to 003 record and their tests hold: build a legal catalog and change of the class each repair touches (paths spelled differently, entries ending at a heading or a comment, names git would quote, files moved between components) that the tests lack, run components_index.py changed and review on it, and report a wrong result with the input.
- C4. C4. The question sweep holds every open question and every deferred refactor that 001 to 004 raise, once each, with a disposition that is true.
- C5. C5. Nothing in the records or the README says a gate exited 0, a review ran, or something was pushed, posted, merged or tagged where it did not.

## The change under review

The files below, as they stand at `d82c87ed449c`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.planning/milestones/reread-answers/005-close.md` | `ec3b9918673179b63706feffbc58f1d1172dc3bceebcf910ee51a336e2114bba` |
| `.planning/milestones/reread-answers/README.md` | `da08a9223721d086e463a9cce0a786944cb804a4bea699608c620d099c892daf` |
| `.planning/milestones/reread-answers/001-issue-50.md` | `7b4b36272a1b399125d71ef96f4af82e1decc678745d81b507b883fc25c90d2a` |
| `.planning/milestones/reread-answers/002-pr-51-r1.md` | `39948ff1e752e3e14b45a1077d78f30f1cf1db5130ca138f1b7c2b990e6e4703` |
| `.planning/milestones/reread-answers/003-rulings.md` | `2e1947e0dde94f4075802cf17737a3e7c1da9a6ca2d4066a0b4f7a5e056c19c8` |
| `.planning/milestones/reread-answers/004-pr-51-r2.md` | `c255e30ae1edf1dec1651a5b39a8cc4e09de57256ac96b0308c995c0ef52cf95` |
| `.planning/milestones/reread-answers/notes/issue-50.md` | `b9e52bbfa75d714c492d8d082eb8dae109d92a4cd393c56e33690b8b7c944bea` |
| `.planning/reviews/pr-51-r1/FINDINGS.md` | `1fe8e39151fd27601e90f77eae01e70fc9358698999753af59aee917688a4a13` |
| `.planning/reviews/pr-51-r2/FINDINGS.md` | `dd1a542d02afa7eada6fa694784e46360ac352a1dad40b247905395d1e13aad8` |
| `skills/components/scripts/components_index.py` | `b1131276e324cfbcfaf8620db8b0e5e8c0e9eebf119aaa54204fceadbedf2811` |
| `tests/test_tools.py` | `9d648b58f9108fdbad3480840414f30f509cbfe365dbf03c5738d7408c1d5ba2` |
| `skills/components/SKILL.md` | `a6dd3b7fe863b31a37c429e15989cfec1d60f99f32de50529c387da733845056` |
| `skills/milestone/process-phase/SKILL.md` | `103e6f5482493fd631971a89bfb0262c2de7d38b19ad2a91f3e88bff440c12bd` |
| `skills/phase/process-phase/references/close.md` | `cc5dc9512acf930ffa9099c2f4e4edea88109a0b23def26ed5b27689b52575f1` |

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
