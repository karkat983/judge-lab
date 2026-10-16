# Codex prompt 09 — local pilot toolkit for five real users

## Read first
`AGENTS.md`, `specs/10-PILOT-PROTOCOL.md`, `specs/06-SECURITY-BOUNDARIES.md`, `specs/11-ACCEPTANCE-AND-PIVOT.md`.

## Mission
Make a usability and demand experiment executable, without simulating customers or pretending outreach occurred.

## Build
1. `pilots/README.md`: private/local-first onboarding and deletion guide, data-handling boundaries, provider transparency, and known limitations.
2. Five individually blank `templates/PILOT-RECORD.md` copies or generated files with pseudonymous IDs and `STATUS: NOT STARTED`.
3. `pilots/INTERVIEW-GUIDE.md`: scripted discovery questions about current spend/workflow, labels and review effort, failure decisions, missing capabilities, willingness to try/pay; distinguish responses from observations.
4. `pilots/CONSENT-AND-PERMISSIONS.md`: explicit voluntary participation, dataset rights, sanitization, no storage of real secrets/PII, withdrawal path.
5. `pilots/SUMMARIZE.md` or a local script consuming completed and validated records only; refuse to claim five pilots until five are actually complete.
6. Sample 10-minute synthetic-demo workflow with participant walkthrough, setup instructions and actionable feedback capture.

## Disallow
Don't send messages to people, open external SaaS accounts, collect real employer logs, or generate fabricated user conversations, testimonials, deal sizes or case findings. Recruitment is human-authorized.

## Exit gate
Run pilot-record schema checks with blank and synthetic test records. Mark status NOT RUN / no external users recruited until user provides data. Write `worklogs/09-pilots.md`. STOP.
