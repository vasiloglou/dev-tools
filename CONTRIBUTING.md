# Contributing

Contributions are welcome. Every change reaches `main` through a pull request, and the
maintainer ([@vasiloglou](https://github.com/vasiloglou)) reviews and merges each one.
Nobody else can approve or merge.

## How a change gets in

1. **Open an issue for anything larger than a fix.** Say what went wrong or what is
   missing. For a defect, include the command you ran and what it printed.
2. **Fork the repository and branch from `main`.** You need no access to this
   repository.
3. **Make the change and run the tests** (Python 3.11 or newer):

   ```bash
   uv run --no-project --with pytest python -m pytest tests -q
   ```

   One test fails while dev-tools' index of its own code (`.devtools/components/`) is out
   of date, which a change to a script under `skills/` or `devtools/` usually makes it.
   The failure names the command that regenerates the index; commit the result with the
   change.

   In Claude Code, this repository's `.claude/settings.json` turns on the released
   `dvt-milestone` plugin (`/dvt-milestone:review-pr`, `/dvt-milestone:handle-issue` and the
   rest). Claude Code offers to add the `dvt` marketplace and install it the first time you
   trust the folder. It is the released version, not your branch: to try a changed skill,
   run `claude --plugin-dir plugins/dvt-milestone` after `python3 devtools/build_plugins.py`.

4. **Open a pull request against `main`.** Say what changed and why, and link the issue
   if there is one. One purpose per pull request. The `gates` workflow
   (`.github/workflows/gates.yml`) runs the tests, the plugin check and the index checks
   on the pull request, on Linux with Python 3.11 and 3.14 and on macOS with 3.14.
5. **Review.** You may be asked for changes before it is merged.

## dev-tools is developed with dev-tools

The maintainer's own larger work on this repository runs under the milestone workflow it
ships: each milestone has a plan, phase specs and numbered records in
`.planning/milestones/`. The project's rules for the skills are in `.devtools/project.md`,
and `AGENTS.md` lists the words the work uses (milestone, phase, spec, owner gate, record,
review round), which an agent working here reads first.

A contribution needs none of it. A fix is a pull request, as above; if a change is large
enough to need a plan, the issue is where that is agreed.

## What makes a change easy to accept

The skill text is the product: changing a sentence changes how an agent behaves in every
project that takes the next update. The bar is the same for prose as for code.

- **A script change comes with a test.** `devtools/sync.py` and the scripts under
  `skills/` are tested in `tests/`. A fix arrives with a test that fails without it.
- **The plugins are rebuilt, and released under a new version.** `plugins/` is generated:
  after changing a skill or an agent, run `python3 devtools/release_plugins.py bump`, which
  raises the plugin version and rebuilds `plugins/`, and commit both with the change. The
  tests fail while `plugins/` is stale. The maintainer tags the release after the merge
  (`release_plugins.py tag --github`).
- **A wording change says what prompted it.** Name the run where the agent went wrong,
  or the sentence it misread.
- **Shared skills stay general.** A rule that only makes sense in one project belongs in
  that project's own `references/project.md`, not here.
- **Both agents read the same file.** A skill is copied for Claude Code and for Codex
  byte for byte, so it has to be correct for either.
- **Captures on the site are real output.** If a change alters what a command prints,
  replace the capture in `docs/` with a new run. Do not edit the old one by hand.
- **The page that describes it is updated too.** The site is plain HTML in `docs/`, with
  no build step. A change in behaviour and its description go in the same pull request.

## License

The project is under the [Apache License 2.0](LICENSE). A contribution you submit is
taken under the same license, as its section 5 says, with no separate agreement to sign.

## How `main` is protected

- Changes arrive by pull request with an approving review.
- `.github/CODEOWNERS` gives every path to the maintainer, and the review that counts is
  the owner's.
- The branch cannot be force-pushed or deleted.

The site at <https://vasiloglou.github.io/dev-tools/> is served from `docs/` on `main`,
so a merged change to a page is live a minute or two later.
