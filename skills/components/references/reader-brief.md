# Brief for a reader (fill in the brackets)

You are one of several readers helping to write a component index for [project]. You
read one group of modules and propose catalog entries for it. You do not edit the
catalog: one writer merges every reader's proposal.

## Your group

- Modules: [paths or folders, about 10,000 lines]
- Their stubs, with what each imports and what imports it: [scratch file from
  `draft --only <path>`]
- The generated inventory page: `docs/components/modules/[group].md`
- Read-only: change no file of the project. Write only your proposal file.

## What to read

For each module: the imports first (they show what it belongs with), then the public
functions and classes, then the tests that use it. For a module over about 300 lines,
read the outline before the body, and read in full the functions your `does` sentence
is about. Do not write an entry from a file name or a docstring alone.

## What to write

One entry per capability, in the format in `SKILL.md` ("Entry format"). The rules in
`build.md` sections 3 and 4 apply; the ones readers most often get wrong:

- Every module of your group goes under exactly one entry.
- A file with several jobs goes under its main job, with the other jobs in `does` and
  `verbs`.
- A module that only re-exports another goes with what it re-exports, with a sentence
  in `notes`. An `__init__.py` follows the rule in `build.md` section 3.
- Ids: `<area>.<capability>`, using these words: [the area names and the recurring
  capability names the writer chose].
- `tests`: up to about six files whose subject is the component. Find them by imports,
  then function names, then the command word.
- Line lengths: `does` about 120 characters, `notes` two sentences, `verbs` ten to
  twenty phrases.
- `checked: partial` on an entry whose code you did not read in full.

## What to return

Write to [scratch file outside `docs/components/`]:

1. The proposed entries, ready to paste.
2. **Questions for the writer**: a name, a placement or a merge you could not settle.
3. **Claims not verified**: each sentence in an entry that you wrote without reading
   the lines it is about, with the file and the line range you skipped.
4. **Flows**: the call paths that start or pass through your group, as component ids in
   order, with steps outside your group in brackets.
5. **Noticed**: capabilities written twice, code nothing calls, files worth splitting,
   code with no tests; each with the file and line.

Your reply is a summary of at most 150 words: how many entries, how many modules read
in full and in part, and the questions that block the merge. The detail stays in the
file.
