# Phase 3 reading

The first build of `.devtools/components/` (commit `2e48abf`) wrote 10 of its 12 entries
from module docstrings, command lines and documented functions, marked `checked: partial`.
Plan criterion P3.3 says every entry is read from the code. This folder holds the full
reading of those 10 modules, one file per module, made at commit `3963a46` by four reader
agents. The driving agent rewrites the entries from these files; the readers change
nothing else.

| Reader | Modules | Lines |
|---|---|---|
| 1 | `skills/phase/process-phase/scripts/phase_tool.py`, `skills/phase/process-phase/scripts/coder_pool.py` | 2,522 |
| 2 | `skills/components/scripts/components_index.py`, `skills/components/scripts/rules_check.py` | 2,732 |
| 3 | `devtools/from_gsd.py`, `devtools/sync.py` | 2,508 |
| 4 | `skills/dev-handoff/scripts/handoff.py`, `skills/milestone/process-phase/scripts/review_tool.py`, `devtools/build_plugins.py`, `devtools/release_plugins.py` | 2,601 |

## What each reading file holds

A file per module, `<module file name without .py>.md`, in this order:

1. **Header.** The module's path, its line count (`wc -l`) and its blob SHA
   (`git hash-object <path>`), so a later reader can tell whether the code moved.
2. **Definitions.** One row for every function, method and class in the module, in file
   order: name, line, and one sentence on what the body does (not what the docstring
   says). The row count equals the count of `ast.FunctionDef`, `ast.AsyncFunctionDef` and
   `ast.ClassDef` nodes in the module, stated under the table with the command that
   counted them.
3. **Commands.** Every command-line command and option, with the function it reaches and
   what it writes (files, stdout, exit codes).
4. **The entry, claim by claim.** Each claim of the entry's `does`, each verb in `verbs`
   and each sentence of `notes` in `.devtools/components/COMPONENTS.md`, with a verdict
   (true, false, overstated, vague) and the `file:line` that settles it.
5. **What the entry leaves out.** Capabilities a person might search for that the body has
   and `does` or `verbs` does not name, each with its `file:line`.
6. **Docstring against body.** Every place a docstring (module or function) says
   something the body does not do, or the body does something its docstring hides.
7. **Other scripts.** Every place the module runs or loads another script of this
   repository (`subprocess`, `runpy`, `importlib`, a path it builds to another script),
   with `file:line`; and every helper whose name another shipped script also defines
   (`plugin_root`, `checkout_root`, `load_settings`, `git`, `Stop`, others found).
8. **Proposed entry.** The `does`, `verbs` and `notes` lines the reader would write, in the
   catalog's form. The driving agent decides what goes in.

## Checked by the driving agent

Three claims per reader were checked at the cited lines before any entry was rewritten, 12
in all, and each held: `phase_tool.py` forces exit 0 for `status` (2044), calls the coder
pool only for a wave of more than one plan (1134) and runs the capabilities script with
runpy (1281); `components_index.py` runs no other script (its only subprocesses are git),
`rules_check.py suggest` runs `components_index.py facts` (`read_facts`, 389), and
`review`'s per-module leads read only `PACKAGE_DIR` (1317); `OTHER_PLANS` is byte for byte
the same in `from_gsd.py` and `sync.py`, `from_gsd.py`'s git calls only read, and `sync.py`
deletes a managed file no longer shipped (202); `release_plugins.py` loads
`build_plugins.py` at import (35), `takeover` runs no `git switch`, `checkout` or `fetch`,
and `review_tool.py`'s bad settings raise `SystemExit` with a message, exit 1.

`handoff.py` moved after it was read: the phase-1-r3 repair (`e2b2762`) changed its
`takeover`, `write` and `check`. The driving agent read that diff and wrote the entry from
both.

## Review of the reread

Declared before it runs: one round, `phase-3-r2`, Codex through the review helper, over the
rewritten entries and the modules they describe (base `caffae7`), also reading the phase
r1 repairs. One further round only if r2 returns a blocking finding, and none once the
self-inflicted ratio is above one half (`review-convergence.md`).
