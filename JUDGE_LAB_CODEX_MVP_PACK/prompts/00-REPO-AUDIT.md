# Codex prompt 00 — audit the repository; do not code the old roadmap

## Copy/paste instruction
You are Judge Lab's Implementation Lead. Read `AGENTS.md`, `README.md`, `ROADMAP.md`, `specs/01-SCOPE-AND-NONGOALS.md`, `specs/02-ARCHITECTURE.md`, `specs/03-DATA-CONTRACTS.md`, and `specs/11-ACCEPTANCE-AND-PIVOT.md` in full.

**Your only task now:** inspect the actual repository and prepare a migration plan from the previous expansive blueprint/guide to this focused MVP. Do not assume a `src/` directory or tests exist. Inspect `git status`, top-level source tree, pyproject/requirements, available tests and existing docs. Read relevant files before proposing changes. Preserve any working code matching the new core; catalog unused/deferred files instead of deleting them.

Produce:
1. `worklogs/00-repo-audit.md` with current code/documentation inventory, a table of `EXISTS / PARTIAL / PLANNED / DEFERRED / CONFLICTING`, existing test commands and their observed results.
2. `worklogs/DECISIONS.md` (new or appended) with ADR candidates and explicit scope conflicts between old and new instructions, including import/package strategy.
3. A minimal file-level implementation sequence mapped to prompts 01–10, with time/complexity as estimates not commitments.
4. Specific risks: privacy/data leakage, label leakage, unvalidated "assurance" claims, odd old verdict enums, missing tests.

**Allowed writes:** audit docs, decisions and nonfunctional repository metadata only. No code generation, external model calls, infrastructure access, destructive git actions or automatic deletion. If old root `AGENTS.md` conflicts, stop and state exact conflicting lines before editing it.

**Exit gate:** human can approve exactly which existing modules to reuse and which proposed changes to make. Stop after presenting actual findings.
