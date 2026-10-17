# Proposed next task — preserve output ownership under concurrent writers

Read AGENTS.md, reviews/INDEPENDENT-REVIEW.md P1-01 and src/judge_lab/artifacts.py.
Reproduce the disposable race. Add failing tests for concurrent target creation,
owned overwrite races, ancestor replacement, failure rollback and preservation of
unrelated files. Choose the smallest portable, explicit ownership/reservation
protocol; fail closed on unsupported cases. Do not delete stale reservations
without verified ownership. Preserve normal CLI output paths/schema. Run the full
offline suite, lint, types, fresh installed CLI and race reproduction. Record the
reviewed design and limitations in worklogs/11-output-ownership.md and obtain an
independent review of the change before claiming race-safe output handling.
Do not expand into H2 datasets, live model calls, deployment or participant outreach.
