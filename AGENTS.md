# Judge Lab operating instructions

Read and follow [the canonical MVP instructions](JUDGE_LAB_CODEX_MVP_PACK/AGENTS.md).
The pack's relative `specs/`, `prompts/`, `templates/` and `reference/` paths resolve
within `JUDGE_LAB_CODEX_MVP_PACK/`. Do not maintain duplicate specification copies.
Explicit user instructions take precedence. Read the latest root `worklogs/` handoff.

Current authorization: implement phases 02–10 sequentially, validate each, commit
and push coherent changes to the existing remote. The user supersedes per-phase
approval pauses. Missing real labels/pilot participation/external review must be
reported as unavailable, never fabricated. Keep empirical gates explicit.
The old `src.*` safe/unsafe workflow remains separate from the installable
`judge_lab` ACCEPT/REJECT/ABSTAIN contracts. Preserve legacy code and tests.

Run `make test`, `make lint`, `make typecheck`. Tests default to offline; never
enable `live` or call provider APIs without explicit authorization.

The requested `specs/04-SECURITY-AND-PRIVACY.md` does not exist in this edition;
use [spec 06](JUDGE_LAB_CODEX_MVP_PACK/specs/06-SECURITY-BOUNDARIES.md).
