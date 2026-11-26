# Issue 50: components: an entry read and found accurate still goes stale, and nothing fails when a reread line is ignored (OPEN)

Twenty days after a project built its component index, `components_index.py review` listed 103 of its 266 components under "Descriptions older than their code". All 103 were then read beside the diff of their modules (vasiloglou/gnd-public#316). 74 were still accurate and 29 needed an edit. Most of the 74 had already been read and judged accurate when their phase closed; the index kept no trace of it. Three things in what dev-tools ships produce that, and a fourth would catch part of the 29. Line numbers are at `main` 31249da.

## 1. process-phase sends "still accurate" to the phase record, not to the entry

The `components` skill says how to settle a `reread:` line from `changed` (`skills/components/SKILL.md`, "Before a PR"): edit the entry, or "add or update its `reread:` line". `review` then dates the entry from that line.

The milestone `process-phase` skill, which is what runs the check at every phase close, says something else (`skills/milestone/process-phase/SKILL.md:298-300`):

> For each `reread:` line, read the entry beside the diff and either edit it or state in the record that it is still accurate.

"The record" is the phase record. An agent that follows this writes the sentence in the planning folder and leaves the entry alone, so `review` keeps listing it. In the project above:

```
$ grep -rlE "still accurate" .gnd-planning | wc -l
31
$ grep -c '^- reread:' dev/components/COMPONENTS.md      # before the repair
1
```

The `reread:` field only reached that project with plugins 0.1.7 (vasiloglou/dev-tools#45), so the earlier phases had no other place to write it. But the wording was not changed when the field arrived, so the list refills after any repair.

**What would help:** in `process-phase` (the milestone variant, and the phase variant if it has the same step), tell the author to add or update the entry's `reread:` line, and to name the entries in the record as well. One sentence, the same one the `components` skill uses.

## 2. `changed` and `review` disagree on what counts as an edit

`changed` prints no `reread:` line for an entry when any hand-written field differs from the base (`skills/components/scripts/components_index.py:1198-1207`):

```python
def authored(entry):
    return {k: v for k, v in entry.items() if k not in GENERATED}
...
if before.get(name) != authored(entry):
    continue  # written or edited in this change
```

`review` dates an entry only from `does`, `verbs`, `flow` and `reread` (`:1339`). So a change that touches a component's code and adds a sentence to its `notes:`, or a file to its `tests:`, is silent in `changed` and leaves the entry on `review`'s list.

Of the 103 listed entries, 14 had only such fields edited after their description was last touched (`notes` 13 times, `tests` 3, `in`, `out` and `modules` once each). Two examples where the note was updated for the new behaviour and the verbs were not: an entry whose note gained "excludes ... guarded-filter, guarded-disjunction" while no verb names either, and one whose note gained a new public function that no verb finds.

**What would help:** one rule in both places. The narrower one seems right: `changed` skips the `reread:` line only when `does`, `verbs`, `flow` or `reread` changed. An edit to `notes`, `tests` or `modules` does not say the description was read.

## 3. Nothing fails when a `reread:` line is left unanswered

`changed --strict` exits 0 with any number of `reread:` lines; only `fail:` and `warn:` set the exit (`:1217-1222`). That was the only possible design while the script had no way to tell "read and true" from "not read". Since 0.1.7 it has one: the `reread:` field counts as an edit.

The project's phase records show the check printing unanswered lines at close:

```
$ grep -rhoE "[0-9]+ to reread" .gnd-planning | sort | uniq -c | sort -rn | head -8
 139 0 to reread
  17 1 to reread
  15 3 to reread
   9 4 to reread
   8 2 to reread
   6 7 to reread
   5 19 to reread
   4 9 to reread
```

**What would help:** a way to make an unanswered `reread:` line fail: under `--strict`, or under a separate flag or setting if changing what `--strict` means is too much for projects that already gate on it. The author clears it by editing `does` or `verbs`, or by updating `reread:`. The script still does not judge the sentence; it only requires that someone signed for it. `examples/components-check.yml` and the `process-phase` gate row would then name the stricter form.

## 4. The `reread:` line could name what the entry does not mention (enhancement)

Most of the 29 real gaps were a public name or a capability the change added and no verb finds. Examples: a module gained `evaluate_filtered_temporal_guard`, `render_report`, `read_evolution_outcome_report`, `run_guarded_cases`, `score_reading_coverage`, `workspace_relative`; none appeared in its entry's `does` or `verbs`. A second module was added to a component (`synth/guarded_service.py`) and the entry had no verb for anything in it.

The script already parses every module's public names for the `modules/` pages, at the base and in the working tree.

**What would help:** when `changed` prints a `reread:` line, add the public names the change added to (or removed from) the entry's modules that appear nowhere in its `does` and `verbs`: `reread: synth.service (entry not edited): src/.../guarded_service.py; new public names not in does or verbs: run_guarded_cases`. It is a lead, not a failure: a private-by-intent helper needs no verb.

## Not a dev-tools defect

The project runs none of this in CI, although `examples/components-check.yml` exists. That is the project's to adopt.

## Reproduce

Parts 2 and 3 on any indexed project:

1. Change a line in a module that a component covers, and add a sentence to that entry's `notes:`. `changed --base <base> --strict` prints no `reread:` line and exits 0; after the commit `review` lists the entry.
2. Change the module only. `changed --base <base> --strict` prints `reread: <id> (entry not edited): ...` and exits 0.

