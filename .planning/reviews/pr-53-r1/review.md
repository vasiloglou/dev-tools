### Findings

**F1 · Blocking · A non-UTF-8 module name still makes plain `changed` exit 1.** The generated Markdown inventory contains the filesystem surrogate for the undecodable byte. Both `write` and the freshness check encode that inventory as strict UTF-8. With `src/widget/caf\xe9.py` under a component’s folder, I reproduced `write` exiting 1 with `surrogates not allowed`. With an existing inventory, plain `changed` exited 1 with the same error before printing the component. On a filesystem that accepts the name, the new test therefore fails inside `catalog()` before reaching its `changed` assertion. The inventory writer and freshness check need the same printable representation of the path. [Inventory writer, line 1046](skills/components/scripts/components_index.py#L1046) · [Freshness check, line 1015](skills/components/scripts/components_index.py#L1015) · [New test, line 2662](tests/test_tools.py#L2662)

**F2 · Blocking · Moving an ignored file between an explicit path and a folder asks only one owner.** I moved ignored, uncounted `tools/gen/out.py` from `core.alpha`, which named it explicitly, to `core.beta`, which took `tools/gen/`. Only `core.alpha` got a `reread:` line. After I updated alpha’s description, `changed --strict` exited 0 with beta still unanswered. Reversing the move asked only beta. The code gathers explicit names separately for each component, so the owner using the folder never sees the other owner’s candidate. [Ownership comparison, line 1292](skills/components/scripts/components_index.py#L1292)

**F3 · Blocking · Regrouping a tracked dangling symlink can now pass strict mode.** I compared base and head with `tools/gen/latest` as the sole tracked entry under a folder whose ownership moved from alpha to beta. The symlink’s target was absent. Base reported both owners and exited 1. Head reported zero rereads and exited 0. The new `is_file()` check follows the symlink and discards a path Git still tracks. [Working-tree filter, line 1294](skills/components/scripts/components_index.py#L1294)

**F4 · A line break in the project directory still breaks the base-blob lookup.** With `--root` pointing to a Git subdirectory named `team\nwidget`, I traced the request for the ordinary relative path `src/a.py`. The batch selector checked only `src/a.py`, then prepended the directory. Git’s line protocol received two requests, `abc:team` and `widget/src/a.py`, and the lookup failed. I also checked a leading-space prefix, which `.strip()` changed, and a non-UTF-8 prefix, which failed during text decoding. The whole repository-relative path needs byte-preserving handling. [Prefix and batch selection, line 1087](skills/components/scripts/components_index.py#L1087)

**F5 · Ordinary bulk changes now take quadratic time to partition.** For every changed Python path, `p not in batch` scans a list that normally contains every path. With Git I/O stubbed identically, `files_at` took 0.106, 0.426 and 1.671 seconds on head for 6,000, 12,000 and 24,000 ordinary names. Base took 0.006 seconds at 24,000. Checking `'\n' in p` directly removes the repeated scans. [Batch membership check, line 1094](skills/components/scripts/components_index.py#L1094)

**F6 · Help output can still stop on an encoding error.** With the executable name `café-index` and strict ASCII stdout, `--help` raised `UnicodeEncodeError` while printing the usage line. `argparse` prints help during `parse_args()`, before the stream is configured. The expected result is escaped help text and exit 0. [Argument parsing, line 1773](skills/components/scripts/components_index.py#L1773)

### What checked out

- The checkout matched head `0e241de9`, and the patch SHA-256 matched the brief. The plugin-build check, strict component-index check, and plain `changed` against the specified base each exited 0.
- In the in-memory base/head comparison, explicit-to-explicit moves of ignored files and folder-to-folder moves of counted ignored modules produced both rereads on head. I also tried `./tools//gen/out.py` to check path normalization.
- The NUL-field splitter round-tripped a name containing a tab, quote, backslash, CR, LF and byte `0xff`. With CR, LF and CRLF **inside the relative filename**, head read the changed module, attributed it to the correct component, reported its new public name and exited 0. Base exited 1 in each case.
- After argument parsing, an actual CLI diagnostic on an ASCII stream printed `caf\xe9` for `café`.

### Verification limits

The brief required read-only work. The pytest fixtures create repositories and commits, so I did not run pytest or a filesystem-backed Linux reproduction. I ran the base and head implementations with in-memory filesystem and Git responses for the edge cases, and ran the three read-only gates against the actual checkout.

VERDICT: CHANGES_REQUESTED