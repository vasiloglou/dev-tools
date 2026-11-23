# Search cases

Capabilities someone new to dev-tools would ask for, in their own words, and the
component each should find. The index script ignores this file. Run each case from the
repository root:

```bash
python3 plugins/dvt-milestone/skills/components/scripts/components_index.py search --explain <query>
```

A case holds when its component is the first `component` line. When one misses, fix the
entry's `does` or `verbs`, never the query.

| Query | Expected first component |
|---|---|
| copy the skills into my project | `sync.copies` |
| move my planning folder off GSD | `migrate.from_gsd` |
| bump the plugin version and tag a release | `plugins.release` |
| regenerate the plugins folder | `plugins.build` |
| does the project already have a function for this | `components.index` |
| enforce which areas may import which | `components.rules` |
| continue this branch on another machine | `handoff.notes` |
| get an independent review of a phase diff | `review.rounds` |
| which phase is next and can it advance | `phase.state` |

Negative case: `deploy to kubernetes` gives `no component matched`, or no component line
that matches more than one query word.
