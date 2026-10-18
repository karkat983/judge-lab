# Pilot 2 base separability check

48 preregistered local Ollama calls; no changes to the model, prompt or faithful reports.

All-case accuracy: **24/48 = 50.0% (95% CI 36.4%–63.6%)**; answered accuracy: 24/45 = 53.3% (95% CI 39.1%–67.1%); **κ = 0.0**.
Coverage: 45/48.

| Reference | ACCEPT | REJECT | ABSTAIN | ERROR |
|---|---:|---:|---:|---:|
| ACCEPT | 24 | 0 | 0 | 0 |
| REJECT | 21 | 0 | 3 | 0 |

Defective reports rejected: **0/24**; accepted despite explicit defects: **21/24**.
Minimum separability met: False. Preregistered ≥75% accuracy / κ > 0 target met: False.
ABSTAIN: 3/48 = 6.2% (95% CI 2.1%–16.8%); ERROR: 0/48 = 0.0% (95% CI 0.0%–7.4%); NOT_RUN: 0.

Proceed to both injection directions and all other probes under the frozen protocol, regardless of this checkpoint. No tuning follows this base check.

Intervals are nominal: repeated templates and paired reports are correlated.
Model manifest digest: `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`.
Raw evidence commit: `8842c4f95cee691d7ce10cddebbb581295c50980`.
Exact command: `PYTHONPATH=src .venv/bin/python scripts/run_probe_pilot_2.py base`.
Raw responses and show output: [base metadata](../../runs/probe-pilot-2/llama3.1-8b/base/metadata.json).
