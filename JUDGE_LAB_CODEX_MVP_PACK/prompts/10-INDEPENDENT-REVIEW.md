# Codex prompt 10 — independent scientific, security and product review

## Read first
`AGENTS.md`; all approved ADRs; `specs/01` through `specs/11`; actual code, fixtures, tests, reports and worklogs. Adopt **reviewer** perspective, not implementation booster.

## Independent audit tasks
- **Scientific validity:** reproduce goldens independently; verify denominators, undefined kappa, Wilson 95%, class prevalence, coverage, sampling/split selection, paired-case dependence, holdout isolation and whether claims overreach data.
- **Attack validity:** test rubric/reference tampering, invalid transformations, attack-output injection, parser-error handling, adversarial budget accounting and conditional attack success denominator.
- **Security:** try malicious case strings, HTML injection, path traversal, output overwrite, digest tampering, secrets redaction and mock network access. Don't use real victims/production systems.
- **Operational behavior:** fresh-install CLI, reproducible demo, evidence digests, exit-code/gate semantics, model-version metadata, reason codes and honest unrun tests.
- **Market differentiator:** evidence (or absence) compared with simple B0 and currently documented alternatives. If vendor features inaccessible, explicitly say so.
- **Research/product boundary:** ensure no hidden runtime subagents, premature 17-domain packs or empty "assurance" scores appear.

## Format
Create `reviews/INDEPENDENT-REVIEW.md`: P0 blockers, P1 substantive defects, P2 improvements, exact file/line evidence, reproduction commands and actual outcomes. Create `reviews/GO-NO-GO.md`: stage status `READY / NEEDS_FIXES / INCONCLUSIVE`, allowed scope of claims and explicit unresolved questions. Suggest a minimal follow-up remediation prompt; do not auto-fix high-risk defects in the review task, preserving reviewer independence.

## Gate
No statement of readiness without executed tests and at least one independent sample audit. Do not say validated with customers unless actual pilots exist. Stop and hand control back to human.
