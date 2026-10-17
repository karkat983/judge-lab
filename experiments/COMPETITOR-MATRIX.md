# Capability check — official documentation checked 2026-10-17 UTC

Documentation review only. No vendor account, paid plan, model call or comparative
benchmark was used. Absence from this table is not evidence of a feature gap.

| Product | Documented functionality | Primary source | Baseline fit (inference) | Unknown / cost and licensing caveat |
|---|---|---|---|---|
| Braintrust | Datasets, code/model evaluators, immutable experiments, CI evaluation and online scoring | [Evaluate systematically](https://www.braintrust.dev/docs/evaluate) | Can host conventional dataset/scorer evaluation | Domain validity oracle and matched-budget human study not tested; plans/pricing/license not assessed |
| LangSmith | Offline curated datasets; code, LLM, summary and pairwise evaluators; online evaluation | [Evaluation types](https://docs.langchain.com/langsmith/evaluation-types) | Can run/compare reference-based evaluations | Independent label/attack protocol requires configuration; account entitlements and pricing not assessed |
| Arize Phoenix | Code and model evaluators over traces, experiments and datasets; SDK and UI approaches | [Evaluation](https://arize.com/docs/phoenix/evaluation/evals) | Evaluation infrastructure could be reused | Domain-specific efficacy, hosting cost and current license terms not assessed |
| Patronus | SDK/API evaluation, evaluator result logging and dashboard; quickstart uses API key | [Evaluation quickstart](https://docs.patronus.ai/docs/quickstart_eval) | Can run and record evaluator results | No access or paid benchmark; prices/terms and independent label validation not tested |
| Galileo | Expected-output comparison; CSV/JSONL evaluation export | [Expected answers](https://docs.galileo.ai/galileo/gen-ai-studio-products/galileo-evaluate/how-to/logging-and-comparing-against-your-expected-answers), [Export](https://docs.galileo.ai/galileo/gen-ai-studio-products/galileo-evaluate/how-to/export-your-evaluation-runs) | Potential import/export integration | Documentation version, account feature availability, costs and license need confirmation before integration |
| Inspect AI | Dataset/task/scorer components, evaluation/retry/logging CLI | [Reference](https://inspect.aisi.org.uk/reference/), [Tutorial](https://inspect.aisi.org.uk/tutorial.html) | Reusable evaluation framework | Integration effort, provider spend and applicable license terms not assessed |

A Braintrust best-practices URL was inaccessible; claims above use the accessible
canonical evaluation overview. No claim of exclusive functionality or commercial
superiority is supported. Existing platforms may meet the need with less custom
engineering. Validate the security-domain review method before building a platform;
prefer integration if it performs equivalently at lower burden.
