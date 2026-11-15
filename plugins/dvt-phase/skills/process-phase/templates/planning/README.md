# Planning

This folder is the project's plan of record. `phase_tool.py` reads and updates it:

```bash
python3 {{TOOL}} status
python3 {{TOOL}} check --all
```

| File | What it holds |
|---|---|
| `STATE.md` | Where the project is now: current phase, its status, completed phases, lessons |
| `ROADMAP.md` | The phases, with what each depends on and how it is accepted |
| `REQUIREMENTS.md` | What users need (U rows) and what the project must do about it (REQ rows) |
| `MANIFESTO.md` | The few rules the project does not bend |
| `DECISIONS.md` | Decisions that changed the plan, one row each (DEC ids) |
| `RISKS.md`, `OPEN-QUESTIONS.md` | Known risks and undecided questions |
| `GLOSSARY.md`, `MIGRATION.md` | Terms; modules being replaced |
| `planned-paths.txt` | Paths the plan will create, checked against `.gitignore` |
| `phases/NN-<slug>/` | One folder per phase, created when the phase starts |

Status fields are changed only through `phase_tool.py`, never by hand.
