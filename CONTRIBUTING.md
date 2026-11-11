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

4. **Open a pull request against `main`.** Say what changed and why, and link the issue
   if there is one. One purpose per pull request.
5. **Review.** You may be asked for changes before it is merged.

## What makes a change easy to accept

The skill text is the product: changing a sentence changes how an agent behaves in every
project that takes the next update. The bar is the same for prose as for code.

- **A script change comes with a test.** `devtools/sync.py` and the scripts under
  `skills/` are tested in `tests/`. A fix arrives with a test that fails without it.
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

## How `main` is protected

- Changes arrive by pull request with an approving review.
- `.github/CODEOWNERS` gives every path to the maintainer, and the review that counts is
  the owner's.
- The branch cannot be force-pushed or deleted.

The site at <https://vasiloglou.github.io/dev-tools/> is served from `docs/` on `main`,
so a merged change to a page is live a minute or two later.
