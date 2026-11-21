# Phase 1 spec: takeover checks every ignored path the note was written with (issue 28)

## 1. Status

Draft, 2026-11-21. **Implementable once the plan gate is recorded and this spec's owner
gate rules D1 and D2.** No code has been written, and no review has run over these bytes.

## 2. Provenance

- **Source.** Issue 28, "dev-takeover can report ready while an ignored path the note left
  out is missing", opened 2026-11-21 by the owner. The owner asked the same day for it to
  be fixed in this milestone (o).
- **Plan.** `notes/component-index-plan.md`, a draft: phase 1 in section 4. It is
  unreviewed and has no plan gate.
- **Code read.** `skills/dev-handoff/scripts/handoff.py` at main `c9648dd`:
  - `_snapshot_text`, lines 694 to 722;
  - `takeover`, lines 961 to 1018;
  - the takeover rendering, about line 1062.
  Also read: `tests/test_handoff.py` (the `repo` fixture and `handed_over`),
  `skills/dev-handoff/references/handoff.md` line 182, and `docs/handoff.html` lines 70
  to 110 and 182.
- **Written with.** `start-milestone` and `handle-issue`, from dvt-milestone 0.1.3.
- **Review rounds.** `reviews/plan-r1` (Codex, 2026-11-21) read the bytes with SHA-256
  as listed in its `BRIEF.md`. Its F1 and F2 were repaired here, marked `(r1 F1)` and
  `(r1 F2)`. `reviews/plan-r2` (Codex, 2026-11-21) read the repaired bytes; its F2 was
  repaired here, marked `(r2 F2)`. `reviews/plan-r3` read those; its F1 was repaired
  here, marked `(r3 F1)`, and T10 is its test. **The bytes repaired after round 3 carry no
  review opinion**: the round budget is spent, and the phase diff review reads them.

**Reproduced on main `c9648dd`.** The reproduction ran in a scratch folder, through the
module's own `write_note` and `takeover`:

- the project has 26 ignored folders, `out00/` (largest) to `out25/` (smallest);
- the note was written and committed, and the project was cloned;
- the 25 folders the note lists were copied into the clone, and `out25/` was left out.

The reproduction printed:

    note lists 25 paths; last line: - and 1 smaller path (`handoff.py ignored`)
    absent at the destination: ['out25']
    {"head": "ok", "missing_ignored": [], "blocking": [], "ready": true}

It exited 0. The cause is in `takeover`, which builds `missing_ignored` from the bullet
lines of the snapshot only (`re.findall(r"^- \`([^\`]+)\` \(([^)]*)\)", listed, …)`).
`_snapshot_text` writes at most 25 such lines (`snap["ignored"][:25]`). A path after the
25th is never checked.

## 3. Obligations (step 0 harvest)

| # | Obligation | Source | Discharged in |
|---|---|---|---|
| O1 | `takeover` does not report ready while an ignored path the note was written with, other than a key file, is missing, wherever that path sits in the list. A missing key file is reported (r1 F1) | Issue 28, "Problem" | Design, `takeover`; T1, T4 |
| O2 | A test with more than 25 ignored paths, one of them missing after the cut-off | Issue 28, "Suggested fix" | T1 |
| O3 | A note written by 0.1.3 or older, whose list was cut, does not read as ready | Issue 28 (its first fix option needs a new note format; old notes exist on branches) | Design, "Older notes"; T3 |
| O4 | A note with 25 paths or fewer is written exactly as today | Standing rule "captures are real output": `docs/handoff.html` shows a note's snapshot (lines 70 to 110) | Design, `_snapshot_text`; T5 |
| O5 | The reference and the site say what ready now checks | Standing rule "the page that describes it" | Design, "Text" |
| O6 | The release under a new version | Standing rule "plugins are rebuilt" | Design, "Release"; G3 |
| O7 | The issue gets a reply saying where it went, posted only with the owner's approval | `handle-issue`, step 3 and step 4 | Plan section 8, "Owner actions"; the pull request says `Fixes #28` |

## 4. The standing rules, bound to this phase

| Rule | Bound here to |
|---|---|
| A script change comes with a test | `handoff.py`: `_snapshot_text`, `takeover` and the takeover rendering. T1 to T10 are in `tests/test_handoff.py`; T1, T3, T6, T7, T8, T9 and T10 fail on main (r2, r3: the earlier wording counted T1 to T6) |
| The plugins are rebuilt, and released under a new version | `release_plugins.py bump` to 0.1.4, then G3. The owner tags after the merge |
| A wording change says what prompted it | Issue 28 prompts the sentence in `references/handoff.md` and in `docs/handoff.html` |
| Shared skills stay general | Any project's note can list more than 25 ignored paths. Nothing in the fix names dev-tools |
| Both agents read the same file | `dev-takeover` and `dev-handoff` are read the same way by both tools. The change is in the script's report, which both read as JSON or text |
| Captures on the site are real output | O4: a note with 25 paths or fewer is unchanged, so the snapshot capture stays true. The takeover captures (`docs/handoff.html` lines 186 to 226) show no cut list, and their output is unchanged (T5) |
| The page that describes it is updated too | `skills/dev-handoff/references/handoff.md` line 182, and `docs/handoff.html` line 182 |
| R0.1 A shipped script stands alone | `handoff.py` gains no import |
| R0.2 The index is the project's | Does not apply: no index files |
| R0.3 The released plugin runs | G1 to G3 run pytest and the build check. No gate runs a script against this repository |

## 5. Goal

`handoff.takeover` on a checkout where an ignored path the note was written with is absent
reports it, whether the path is the 1st or the 26th:

- a key file under `missing_keys`, which does not block, as today (D2);
- any other path under `missing_ignored`, with `ready: false`.

(r1 F1: the earlier wording said every missing path makes `ready` false, which D2
contradicted.) For a note from an
older version whose list was cut, it returns `ready: false` with the number of unlisted
paths. `uv run --no-project --with pytest python -m pytest tests -q` gives 1 failure, the
GND `synth` case (plan, R5).

## 6. Design

**Reuse.** This project has no component index yet; it is built in phase 3.
`git grep -n "\[:25\]\|smaller path" skills/ tests/` finds only `_snapshot_text`.
`ignored_inventory` already gives the full list, and `snap["ignored"]` holds all of it
when the note is written. Decision: **adapt** `_snapshot_text` and `takeover`. Nothing new
is needed beside them.

**Module.** `skills/dev-handoff/scripts/handoff.py`. The estimate is about 25 changed
source lines.

- **`_snapshot_text`.** When `len(snap["ignored"]) > 25`, write one more line after the
  `- and N smaller path(s)` line and before `SNAPSHOT_END`:

  ```
  <!-- ignored-rest: [{"path": "out25/", "kind": "carry"}, …] -->
  ```

  The line holds the paths after the 25th, in order, as compact JSON (`json.dumps` with
  `separators=(",", ":")`). Each item is `{"path": <str>, "kind": "carry" | "large" | "key"}`,
  spelled as `snap["ignored"]` spells `kind`. These are the three kinds the snapshot
  already prints (its `tail` map in `_snapshot_text`). Nothing changes with 25 paths or fewer (O4).
- **`takeover`.** Build the list to check from:
  - the bullet lines. Today's pattern, ``^- `([^`]+)` \(([^)]*)\)``, skips a bullet
    whose path holds a backtick, and the writer does not escape one, so such a path is
    never checked even in a note of 25 paths or fewer. The pattern becomes
    ``^- `(.+)` \(([^)]*)\)$``, one bullet per line: the path runs to the last
    `` ` ( `` of the line, since the text in parentheses after it never holds `)` (r2 F2);
  - a line under the ignored-files heading that starts with ``- ` `` and does not match
    that pattern cannot be read. It happens when a path holds a newline, which
    `ls-files -z` allows and the writer prints as it is. Each such line adds 1 to
    `unlisted_ignored` (below), so the note is not ready until the path is checked by hand
    (r3 F1: the r2 pattern skipped such a path, and the note read as ready);
  - plus the items of an `ignored-rest` line, when there is one.
  A missing item whose `kind` is `"key"` goes to `missing_keys`, and any other to
  `missing_ignored`. This matches the bullet rule, under which a bullet whose text
  contains `key file` goes to `missing_keys`.
  - An `ignored-rest` line is **readable** only if it is valid JSON, it is a list of such
    items, and its length equals the `N` of the `- and N smaller path(s)` line (r1 F2).
    A line that fails any of these is treated as absent. The note then falls under
    "Older notes", so a damaged or short line can never make the result ready.
- **Older notes.** When the snapshot has a `- and N smaller path(s)` line and no readable
  `ignored-rest` line, set `report["unlisted_ignored"] = N`. Otherwise it is `0`, and the
  key is always present. Each bullet line that cannot be read adds 1 to it (r3 F1).
  `ready` also requires `unlisted_ignored == 0`.
- **Rendering.** When `unlisted_ignored` is above 0, the text report prints one line
  after the `missing ignored path:` lines, in their style:

  ```
    ignored paths the note did not list: N  (compare with handoff.py ignored in the old checkout, or handoff.py pull --from-checkout <old checkout>)
  ```

  The JSON report carries the key.
- **Text** (O5):
  - `references/handoff.md` line 182 reads "no ignored path the note lists is missing".
    It becomes "no ignored path the note was written with is missing: the ones it lists,
    and those after the 25th, which it keeps in one line at the end of the snapshot. A
    note from before 0.1.4 that cut its list is not ready until those are checked by
    hand".
  - `docs/handoff.html` line 182 gets the same point in one sentence.
- **Release** (O6): `python3 devtools/release_plugins.py bump` takes 0.1.3 to 0.1.4 and
  rebuilds `plugins/`.

## 7. Decisions

| # | Question | Readings, and what each costs | Proposed |
|---|---|---|---|
| D1 | How the note carries the paths after the 25th | **(A)** One comment line holding them, written only when the list is cut. The note stays readable, every path is checked, and the capture is unchanged. **(B)** List every path in the note. This is the simplest code, but a note with hundreds of ignored paths grows by hundreds of lines. **(C)** No new format: a cut list makes `takeover` not ready. Small, but a project with more than 25 ignored paths can never be ready without checking by hand | (A), with (C) as the rule for older notes |
| D2 | Whether a missing key file after the 25th blocks | Today a missing key file is reported and does not block (`references/handoff.md`: "key files are reported as not needed to continue"). Keeping that rule is consistent. Making it block would change the rule for every note | Keep: it is reported in `missing_keys`, and it does not block |

## 8. Tests

The tests are in `tests/test_handoff.py` and use the `repo` fixture and helpers there. A
new helper makes `n` ignored folders of falling size, as the reproduction does.

| Id | Case | Expected |
|---|---|---|
| T1 | 26 ignored folders; the note is written and the project cloned; the 25 listed folders are copied; `out25/` is absent | `missing_ignored == ["out25/"]` and `ready is False`. On main: `[]` and `True` |
| T2 | As T1, with `out25/` copied too | `missing_ignored == []` and `ready is True` |
| T3 | A note in the old format: its snapshot ends with `- and 1 smaller path …` and has no `ignored-rest` line (written as text) | `unlisted_ignored == 1` and `ready is False`. On main there is no key, and the result is `True` |
| T4 | 26 paths, the 26th a key file (`.env.local` matched by the key pattern), absent | `missing_keys == [".env.local"]`; `missing_ignored == []`; `ready` follows the other conditions (D2) |
| T5 | 2 ignored paths | the note's snapshot holds no `ignored-rest` line, and the snapshot text equals main's for the same input |
| T6 | As T3, through the command line: `handoff.py takeover` | the text output holds `ignored paths the note did not list: 1`, and the exit is as for any other not-ready report |
| T7 | An `ignored-rest` line holding `not json` | treated as absent: `unlisted_ignored == 1` and `ready is False` |
| T8 | The note says `- and 1 smaller path`, its `ignored-rest` line is `[]`, and the path is absent (r1 F2) | treated as absent: `unlisted_ignored == 1` and `ready is False` |
| T9 | 2 ignored folders, one named ``out`1/`` (a backtick in the name); the note is written; the project is cloned with only the other folder copied (r2 F2) | `missing_ignored` holds ``out`1/`` and `ready is False`. On main: `[]` and `True` |
| T10 | As T9, the folder named `out\n1/` (a newline in the name) (r3 F1) | `unlisted_ignored == 1` and `ready is False`. On main: no key, and `True` |

Branch walk:

- `_snapshot_text`: cut (T1) and not cut (T5).
- `takeover`'s list: bullets only (T2 and T5), bullets plus the rest (T1), an unreadable
  rest (T7), and a readable rest of the wrong length (T8).
- The bullet pattern: a plain path (T1, T2), a path holding a backtick (T9), and a
  line it cannot read (T10).
- A missing item's kind: key (T4) and other (T1).
- Older notes: cut with no rest line (T3, T6), and not cut (T2).

**Gates:**

- G1: `uv run --no-project --with pytest python -m pytest tests/test_handoff.py -q`
  exits 0.
- G2: `uv run --no-project --with pytest python -m pytest tests -q` has 1 failure, the R5
  case.
- G3: `python3 devtools/build_plugins.py --check` exits 0.

## 9. Out of scope for this phase

- The 25 itself: how many paths the note lists for a reader.
- What `pull` or `carry` copies. They read the inventory, not the note.
- `check` on the leaving side.
- Posting the reply to issue 28, which is an owner action.

## 10. Size

Estimated at write time:

- `handoff.py`: about 25 source lines;
- `tests/test_handoff.py`: about 80 test lines;
- 2 sentences of text;
- the rebuilt `plugins/` copies.

## 11. Approval instrument

This prose. The phase changes a serialized format, the note's snapshot. For that shape
`review-convergence.md` makes a corpus written first the default answer, and the burden is
on prose. The argument for prose: the format change is one line, written only when the
list is cut. Its whole grammar is the JSON item above, and T1, T3, T5 and T7 are that
corpus, written first in step 3. If the owner prefers, those four fixtures are written
before the gate, and the gate rules on them.
