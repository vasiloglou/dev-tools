---
phase: "{{PHASE}}"
title: "{{TITLE}}"
slug: {{SLUG}}
paused_at: YYYY-MM-DD
active_step: implement
---

# Continue here — Phase {{PHASE}}: {{TITLE}}

Delete this file when the named plan completes.

## Next task
- Plan: `{{PHASE}}-MM-PLAN.md`
- Task: `{{PHASE}}-MM-T<k>` — <title>
- Tests it must turn green: 

## Done so far in this plan
- 

## Dirty files (expected)
<!-- Orient resumes only if the working tree's dirty files match this list exactly. -->
- 

## Open decisions
- 

## Resume commands
```bash
git switch phase/{{PHASE}}-{{SLUG}}
python3 .claude/skills/process-phase/scripts/phase_tool.py status --phase {{PHASE}}
.venv/bin/pytest --phase {{PHASE}} -q
```
