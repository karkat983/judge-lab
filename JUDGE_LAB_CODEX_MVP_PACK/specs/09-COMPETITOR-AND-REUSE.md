# 09 — Compete with reality; reuse what already exists

## Comparison targets (research leads, NOT proof of missing capabilities)
- Braintrust evaluations and evaluator calibration/validation workflows.
- LangSmith evaluations, datasets, feedback, tracing and CI integration.
- Arize Phoenix evaluation and tracing tools.
- Patronus AI evaluators, testing and monitoring.
- Galileo and Inspect AI as relevant evaluation infrastructure.

Agent's task: verify **current** capabilities directly from official documentation or code before writing claims. Vendor features change; mark unknown, unsupported and license-gated functionality precisely. A claim such as "only Judge Lab supports X" is prohibited without direct verification.

## Common baseline alternatives
1. Straightforward 200-case labeled evaluation in Python/pandas/sklearn.
2. Existing platform configured to run the same rubric and data (when user actually has access).
3. A fixed suite of curated injection strings with expert validation.
4. Random selection of additional cases for review at equal labeling cost.

## Differentiation hypothesis, not marketing assertion
Perhaps Judge Lab can provide *validated security-domain false-accept discovery at lower total review cost* and CI-ready evidence. This must be tested; regular platforms might already support most parts.

## Reuse-first implementation
Use a minimal dependency stack and bring-your-own-provider adapter. Where a common existing library already offers correct metrics, use it if license/reproducibility works and validate numeric conventions with goldens. Don't implement a generalized evaluation platform when a converter + tested methodology is enough.

## Required competitor matrix (to populate with sources during phase 0/7)
| Product | Actual verified functionality | Source URL and checked date | Baseline fit | Gap/unknown | Cost/licensing caveat |
|---|---|---|---|---|---|
| Braintrust | UNVERIFIED IN THIS REPO | TBD | TBD | TBD | TBD |
| LangSmith | UNVERIFIED IN THIS REPO | TBD | TBD | TBD | TBD |
| Arize Phoenix | UNVERIFIED IN THIS REPO | TBD | TBD | TBD | TBD |
| Patronus | UNVERIFIED IN THIS REPO | TBD | TBD | TBD | TBD |

## Decision gate
If an existing tool achieves equal failure detection and workflow usefulness at lower engineering burden, recommend integration, complementary plugins or a tighter domain specialization rather than a redundant new platform.
