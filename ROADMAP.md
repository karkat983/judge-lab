# Judge Lab roadmap

The [canonical MVP roadmap](JUDGE_LAB_CODEX_MVP_PACK/ROADMAP.md) defines phases 00–10.
The user authorized sequential implementation, tests, commits and pushes through
Phase 10. Engineering deliverables and empirical acceptance are separate.

| Phase | Delivered | Remaining evidence / limitation |
|---|---|---|
| 00 | Repository audit and decisions | Historical baseline in worklogs/00-repo-audit.md |
| 01 | Strict contracts, environment, hashes and fixtures | Offline only; legacy label semantics separate |
| 02 | Bounded mock/import runner and owned artifacts | Concurrent output race found in final review |
| 03 | Counts, coverage, kappa, Wilson and slices | Correlated-family intervals suppressed |
| 04 | Installed local CLI, JSON and escaped HTML | No hosted service or provider adapter |
| 05 | Frozen independent 200-family selection/evaluation | Empirical baseline NOT PERFORMED |
| 06 | Fixed local probes and independent planted-rule oracle | One narrow synthetic defect; semantic pairs require review |
| 07 | Matched-resource same-observation review comparison | Novel H2 population mapping incomplete; H1/H2 NOT PERFORMED |
| 08 | Conservative deterministic gates and offline CI example | Attestations need independent authentication |
| 09 | Pilot toolkit and five blank records | Zero real sessions |
| 10 | Self-review, independent-library numeric audit, go/no-go | External independent reviewer pending; P1 findings open |

See [final review](reviews/INDEPENDENT-REVIEW.md), [stage decision](reviews/GO-NO-GO.md)
and [handoff](worklogs/10-review.md). Overall status: **NEEDS_FIXES / INCONCLUSIVE**,
not production readiness or demonstrated market value. One bounded proposed next
task is [output ownership remediation](reviews/REMEDIATION-PROMPT.md).

The locally ignored `docs/commit-plan.md` and archived pack blueprint are historical,
not implementation queues. Working legacy code and history remain preserved.
