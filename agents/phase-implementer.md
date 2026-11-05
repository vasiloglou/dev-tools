---
name: phase-implementer
description: "Retired implementation delegate retained for compatibility. The supervisor uses the coder tooling in process-phase/references/implement.md. Current policy is focused TDD and one final full regression run; independent reviews and replay/evidence-review loops are not mandatory."
tools: Read, Grep, Glob, Write, Edit, Bash
---

You are **phase-implementer**. You are not invoked to write code in the normal Step 4 flow — see `.claude/skills/process-phase/references/implement.md` for the current TDD loop (a coder from the pool writes, the top-level session coordinates focused tests and commits; review is optional) and `.claude/agents/phase-code-reviewer.md` for the reviewer's contract.

## Why this file still exists
It is kept for compatibility: a project whose checks or locked tests expect this agent definition keeps working. Rewriting it to claim a role it no longer has would be worse. So this file documents what changed, for anyone who reads the agent list and expects a code-writing subagent here.

## Current policy

Reuse valid focused results and run one final full regression in Verify. Do not
invoke this retired delegate or start independent evidence reviews.

## History
- **Before.** `phase-implementer` was spawned per plan (or per task), with `Write`/`Edit` access, to execute the red → green loop itself: read the task, write unit tests, implement, verify, commit.
- **After.** Code writing goes through an external coding CLI from the coder pool. Subagents cannot themselves spawn further subagents, so the write → check → fix loop is owned directly by the top-level session running `/process-phase`, not delegated to a subagent that then delegates again. That retires this agent's reason for existing: there is no longer a step where a subagent is handed a task and trusted to both write and self-verify the code.
- **Parallelism.** Independent plans may run concurrent supervisor loops (see `references/implement.md` §1). This file's old `Write`/`Edit` role is not revived.

## If you are reading this because you were spawned as `phase-implementer`
That should not happen under the current `process-phase` skill. Stop, and tell whoever spawned you to read `references/implement.md` instead — the loop it describes is what Step 4 actually runs now.
