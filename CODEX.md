# CUSTOS for Codex (functionally equivalent variant)

Concept section 14: besides Claude Code, CUSTOS should also be available for **Codex**
– not a 1:1 port of the files, but **the same gate logic** in its
own extension/configuration format.

This file records how the building blocks are mapped. The actual
Codex adapter is not yet implemented (an open roadmap point); the
detector/gate scripts themselves are deliberately written shell-independently
(stdlib Python, JSON payload on stdin, exit codes) and are therefore reusable.

## Mapping of the levels

| CUSTOS building block (Claude Code) | Codex equivalent (target picture) |
|---|---|
| `hooks/hooks.json` (hook events) | Codex's own hook/event configuration, same events (before/after tool call, session end) |
| Default agent via `settings.json: "agent"` | Codex system prompt/profile for the senior dev |
| Subagents (`agents/*.md`) | Codex roles/profiles with the same descriptions |
| Skills (`skills/*/SKILL.md`) | Codex mode prompts |
| Detectors (`detectors/*.py`, `bin/*.py`) | **reusable unchanged** – pure CLI scripts |

## Reusability of the scripts

All gate/detector scripts:

- read the tool/event payload as **JSON on stdin**,
- signal a block via **exit code 2** (+ stderr rationale),
- write findings to `custos_findings.json`.

A Codex adapter therefore only needs to map the Codex events onto the same stdin/exit-code
contract; the checking logic stays identical. This makes the proof logic
the same across platforms, only the shell differs.

## Status

- [x] Scripts shell-independent (stdin JSON / exit code / findings log).
- [ ] Codex event adapter (mapping the Codex hooks onto the script contract).
- [ ] Codex profiles for agents/modes.
