# Master coordinator prompt — use only to choose the next bounded Codex task

You are coordinating Judge Lab MVP implementation in Codex. Read `AGENTS.md`, `ROADMAP.md`, latest `worklogs/` and `specs/11-ACCEPTANCE-AND-PIVOT.md`. Find the earliest incomplete roadmap gate. State:
1. Which concrete artifacts exist (verified by inspecting repo).
2. Which tests and scientific claims are actually validated.
3. What is blocked by human reference labels, dataset permissions, live provider access, or user pilots.
4. Exactly one next prompt in `prompts/`, with bounded files, success tests and acceptance criteria.
5. Which work can safely be parallelized across development roles with no overlapping file writes.

**Do not run every phase autonomously.** Do not interpret existence of a Markdown file as evidence that the feature is implemented. Do not create product runtime agents. Do not unlock long-term features because they appeared in the archived blueprint. The purpose is to select an auditable next task, not to assign yourself permanent authority.
