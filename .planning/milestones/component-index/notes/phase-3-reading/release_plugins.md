# Reading: devtools/release_plugins.py

## 1. Header

- Path: `devtools/release_plugins.py`
- Lines (`wc -l`): 221
- Blob SHA (`git hash-object`): `2cfb58162ac19da1450e6afab3b9d227525115df`
- Read at commit `3963a46`.

## 2. Definitions

| Name | Line | What the body does |
|---|---|---|
| `Stop` | 44 | Exception class `main` turns into an exit-2 message. |
| `git` | 48 | Runs `git <args>` in the repository root; raises `Stop` on failure when `check`, else returns `""` on failure and stripped stdout on success. |
| `released` | 55 | Lists local `plugins-v*` tags whose suffix is semver, sorted oldest first as `((major, minor, patch), tag)`. |
| `parse` | 65 | Turns `X.Y.Z` into an int triple or raises `Stop`. |
| `next_version` | 72 | Returns an explicit `X.Y.Z` above `current` (else `Stop`), or `current` raised by `major`, `minor` or `patch`; any other word raises `Stop`. |
| `only_version` | 87 | True when a `plugins/*/.claude-plugin/plugin.json` in the tree equals the tag's copy once `version` is removed from both. |
| `changed_since` | 103 | Lists files under `plugins/` that `git diff --name-only <tag>` reports against the working tree, dropping manifests whose only change is the version. |
| `cmd_status` | 110 | Prints the tree version and last release, rebuilds `plugins/` in memory to detect staleness, and exits 1 when there is no release, a changed plugin file or a stale build, else 0. |
| `cmd_bump` | 135 | Raises the higher of the tree version and the last tag by `part`, writes `devtools/PLUGIN_VERSION`, runs `build_plugins.main([])` and prints what to commit. |
| `notes` | 146 | Returns the tag message: "First release." with no earlier tag, else `git log --no-merges` subjects since the last tag over `SOURCES`. |
| `cmd_tag` | 155 | Refuses off `main` (unless `--any-branch`), on a dirty tree, a stale build, an existing or not-higher version, or no plugin change; then creates the annotated tag and optionally pushes it and runs `gh release create`. |
| `main` | 196 | Parses `status`, `bump [part]` and `tag [--push] [--github] [--dry-run] [--any-branch]`, runs the command and turns `Stop` or a string `SystemExit` into exit 2. |

Counted with
`python3 -c "import ast,sys; t=ast.parse(open(sys.argv[1]).read()); print(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(t)))" devtools/release_plugins.py`:
12.

## 3. Commands

| Command | Reaches | Writes |
|---|---|---|
| `status` | `cmd_status` 110 | Nothing; stdout the tree version, the release, stale and change counts and the next step; exit 1 with no tag (`:114-117`) or any change or stale file (`:132`), 0 otherwise (`:126`). |
| `bump [patch\|minor\|major\|X.Y.Z]` | `cmd_bump` 135 -> `build_plugins.main([])` | `devtools/PLUGIN_VERSION` (`:140`), then everything a build writes or deletes under `plugins/` and `.claude-plugin/marketplace.json` (`:141`); exit 0, or 2 on a bad part or a failed build. |
| `tag` | `cmd_tag` 155 | A local annotated tag `plugins-vX.Y.Z` (`:178`); exit 0, or 2 when a check fails. |
| `tag --dry-run` | `cmd_tag` 175-177 | Nothing; stdout the tag, the short head and the notes. |
| `tag --push` | `cmd_tag` 180-182 | The tag, then `git push origin <tag>`. |
| `tag --github` | `cmd_tag` 180-190 | The tag, the push, and a GitHub release through `gh release create` (exit 2 when `gh` is missing or fails, after the tag is pushed). |
| `tag --any-branch` | `cmd_tag` 157 | Lifts the `main` check only. |

Ran `python3 devtools/release_plugins.py status` read-only at `3963a46`: printed "version in the tree: 0.1.5", "released: 0.1.2 (plugins-v0.1.2)", "19 plugin file(s) changed since plugins-v0.1.2", "0.1.5 is ready ..."; exited 1; `git status --porcelain` unchanged afterwards.

## 4. The entry, claim by claim

`plugins.release`:

| Claim | Verdict | Settled by |
|---|---|---|
| does: Release the plugins | true | `release_plugins.py:155-193` |
| does: status says whether a release is due | true | `release_plugins.py:110-132`; it also reports a stale `plugins/` (`:121-123`). |
| does: bump raises the version and rebuilds | true | `release_plugins.py:138-141` |
| does: tag makes plugins-vX.Y.Z on main | true | `release_plugins.py:156-158`, `:165`, `:178`; `--any-branch` lifts the branch rule. |
| verb: release plugins | true | `release_plugins.py:155` |
| verb: plugin version | true | `release_plugins.py:112-113`, `:136` |
| verb: bump version | true | `release_plugins.py:135` |
| verb: raise version | true | `release_plugins.py:139` |
| verb: patch version | true | `release_plugins.py:82-83`, `:201` (the default). |
| verb: tag release | true | `release_plugins.py:178` |
| verb: plugins-v tag | true | `release_plugins.py:38` |
| verb: release notes | true | `release_plugins.py:146-152` |
| verb: is a release due | true | `release_plugins.py:116`, `:129` |
| verb: release status | true | `release_plugins.py:110` |
| verb: publish plugin | vague | Nothing is published to a registry; the nearest is `git push origin <tag>` (`:181`) and `gh release create` (`:186`). |
| verb: github release | true | `release_plugins.py:183-190` |
| verb: PLUGIN_VERSION | true | `release_plugins.py:140` through `build_plugins.VERSION_FILE`. |
| notes: Read: the module docstring, the function list and the command line. | stale | A process note; this reading replaces it. |
| notes: bump loads build_plugins.py at run time (subsystem.release). | false | The module loads build_plugins.py when it is imported (`:35-37`), and every command uses it: `status` (`:112`, `:121`), `bump` (`:136`, `:140-141`), `tag` (`:161`, `:164`); `released`, `parse` and `next_version` use its `SEMVER` (`:59`, `:66`, `:73`). |

`subsystem.release` checked against the body:

| Claim | Verdict | Settled by |
|---|---|---|
| does: release_plugins.py bump writes the version and rebuilds plugins/ through build_plugins.py | true | `release_plugins.py:140-141` |
| components: plugins.release, plugins.build | true | `release_plugins.py:35-37` |
| flow: plugins.release -> plugins.build | true | `release_plugins.py:35-37`; nothing in build_plugins.py reaches back. |
| verbs: release flow, bump and rebuild plugins | true | `release_plugins.py:135-143` |
| notes: A run-time load, which the import graph cannot see: release_plugins.py loads build_plugins.py with importlib. | true, incomplete | `release_plugins.py:35-37` load at import time; the subsystem's `does` names only bump, while `status` and `tag` also call `build_plugins.build()` and `stale()` in memory (`:121`, `:161`) and all three read `version()`/`SEMVER`. |

## 5. What the entry leaves out

- `tag` refuses a dirty tree, a stale `plugins/`, an existing tag, a version not above the last release and a release with no plugin change (`:159-173`).
- `tag --dry-run` prints the tag and its notes and changes nothing (`:175-177`).
- `tag --push` pushes the tag to origin; `--github` pushes and creates the GitHub release with `gh` (`:180-190`).
- `--any-branch` tags from a branch other than `main` (`:157`, `:206`).
- A manifest whose only change is its version does not count as a change, so an empty bump is no release (`:87-107`).
- `bump` counts from the higher of `PLUGIN_VERSION` and the last tag, and `bump X.Y.Z` must be above that (`:138-139`, `:73-76`).
- `bump` accepts `minor`, `major` or an explicit version (`:78-81`, `:73-76`).
- Release notes list the commit subjects since the last tag that touched `plugins`, `skills`, `agents`, `devtools/build_plugins.py` or `devtools/PLUGIN_VERSION` (`:41`, `:151`).
- `status` reports a stale `plugins/` (`:121-123`).
- Exit codes: 1 a release is due, 2 the step cannot run (`:117`, `:132`, `:212`, `:217`).

## 6. Docstring against body

- Module docstring (`:15`) shows `tag [--push] [--github] [--dry-run]`; the body also has `--any-branch` (`:206`).
- Module docstring (`:16-18`) lists the tag checks as clean tree, fresh build and version not released; the body also refuses off `main` (`:157-158`), a version not above the last release (`:169-170`) and a release with nothing changed (`:172-173`).
- Module docstring (`:11-12`) says bump "writes devtools/PLUGIN_VERSION"; the body counts from the last tag when it is higher than the file (`:138`), which the docstring does not say.
- `cmd_bump` writes `PLUGIN_VERSION` before the build (`:140-141`); a build that fails exits 2 and leaves the new version written.
- `cmd_tag` creates the local tag before pushing (`:178-181`); a failed push or `gh` call exits 2 with the tag already made (and, for `gh`, pushed), which the docstring's "Without them nothing leaves this machine" does not cover.
- `cmd_status` prints "0 plugin file(s) changed since ..." and exits 1 when only the build is stale (`:120-132`); the docstring (`:8-9`) names only "whether plugins/ changed".

## 7. Other scripts

- `release_plugins.py:35-37`: loads `devtools/build_plugins.py` with `importlib.util.spec_from_file_location` and `exec_module`, at import, under the name `build_plugins`.
- `release_plugins.py:141`: calls `build_plugins.main([])`, a full build that writes `plugins/`.
- `release_plugins.py:121`, `:161`: calls `build_plugins.stale(build_plugins.build())` in memory.
- `release_plugins.py:49`: `subprocess.run(["git", ...])` (tag list, diff, show, log, status, rev-parse, tag, push).
- `release_plugins.py:186`: `subprocess.run(["gh", "release", "create", ...])`.
- Same-named helpers in other shipped scripts:
  - `Stop` (`:44`): also `skills/milestone/process-phase/scripts/review_tool.py:117`, `devtools/from_gsd.py:71`.
  - `git` (`:48`): also `skills/components/scripts/components_index.py:980`, `skills/milestone/process-phase/scripts/review_tool.py:143`, `skills/phase/process-phase/scripts/codex_gate.py:14`, `skills/phase/process-phase/scripts/phase_tool.py:221`, `devtools/from_gsd.py:428`; six different bodies.
  - `parse` (`:65`): also `skills/components/scripts/components_index.py:387`.
  - `cmd_status` (`:110`): also `skills/milestone/process-phase/scripts/review_tool.py:669`, `skills/phase/process-phase/scripts/phase_tool.py:471`.
  - `main` (`:196`): every shipped script has one.

## 8. Proposed entry

```
- does: Release the plugins: status says whether a release is due or plugins/ is stale, bump raises the version from the higher of PLUGIN_VERSION and the last tag and rebuilds, tag checks main, a clean tree, a fresh build and a real change, then makes plugins-vX.Y.Z with notes, --push and --github send it (release_plugins.py)
- verbs: release plugins, plugin version, bump version, raise version, patch version, minor version, major version, tag release, plugins-v tag, release notes, is a release due, release status, push release tag, github release, dry run tag, PLUGIN_VERSION, version-only manifest change
- notes: Loads build_plugins.py with importlib when imported, and every command uses it (subsystem.release). Nothing leaves the machine without --push or --github; a failed push or gh call leaves the local tag made. bump writes PLUGIN_VERSION before the build runs.
```

Proposed `subsystem.release` notes: `A load at import, which the import graph cannot see: release_plugins.py loads build_plugins.py with importlib; bump runs its main, status and tag its build and stale in memory, and all read its version and SEMVER.`
