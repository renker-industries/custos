---
name: multi-session
description: >-
  Coordinate several Claude Code sessions or subagents working the same project (or
  several fleet repos) so they take distinct tasks instead of colliding. Uses a
  shared task queue plus git-worktree isolation. Use when running parallel sessions
  or fanning work out to subagents.
---

# Multi-Session Coordination

Parallel work collides unless it is coordinated. CUSTOS uses two existing
primitives together (concept section 11): a shared task queue and git-worktree
isolation. There is no magic orchestrator.

## Task-Queue

```bash
python bin/task_queue.py add --title "Fix login" --desc "..."
python bin/task_queue.py list --status open
python bin/task_queue.py claim --id T1 --session <session-id>
python bin/task_queue.py complete --id T1 --proof "pytest run #42 green"
```

- At session start, the senior-dev agent lists open tasks and claims a free one;
  it does not touch a task already `claimed` by another session.
- A task is `done` only with a `--proof` reference (test-run id / linter result) —
  never on a claim. The queue enforces this.
- Writes are lock-guarded so concurrent sessions do not corrupt the queue.

## Isolation

- Each session/subagent that writes runs in its own git worktree (`Agent` tool,
  `isolation: worktree`) so file edits never collide.
- Merges go through normal git (branch per worktree → PR/merge after the proof
  gate passes). No direct cross-worktree writes.

## Config

`monitors/monitors.json` holds the queue/isolation settings and any scheduled
monitors (e.g. the daily passive security scan, disabled by default).
