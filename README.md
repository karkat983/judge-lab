# judge-lab

> Status: **Local MVP tooling implemented; local model pilot available.** Calibration, fixed
> probes, baseline/comparison workflows, conservative gates and pilot records are available.
> Synthetic demonstrations are not empirical validation or a safety certification.

The current MVP evaluates judges of **security-investigation reports** using separate
`ACCEPT` / `REJECT` references and `ACCEPT` / `REJECT` / `ABSTAIN` predictions.
Execution failures are typed `ERROR` outcomes. The existing XSTest safe/unsafe
experiment remains under `src.*` and is documented under `docs/legacy/`.
See the [roadmap](ROADMAP.md), [contract guide](docs/contracts-v1.md), and
[final review](reviews/GO-NO-GO.md).

## Install and validate offline

Use Python 3.12 or newer. Dependency installation needs package-index access;
the smoke check and tests make no model calls.

```bash
make setup
make test
make lint
make typecheck
.venv/bin/judge-lab demo --out runs/demo
.venv/bin/python - <<'PY'
from pathlib import Path
from judge_lab.load import load_dataset
dataset = load_dataset(Path("examples/security_fixture.jsonl"),
                       Path("examples/security_manifest.json"))
print(dataset.summary())
PY
```

The ten bundled cases and example outcomes are **synthetic code fixtures, not
empirical judge results or human-adjudicated benchmark evidence**.
The default report makes no release decision. Dataset inputs are JSON/JSONL;
judge configuration accepts bounded JSON or safe YAML. Legacy CSV is not silently converted.

```bash
.venv/bin/judge-lab validate --data examples/security_fixture.jsonl \
  --manifest examples/security_manifest.json --judge examples/mock_judge.json
.venv/bin/judge-lab calibrate --data examples/security_fixture.jsonl \
  --manifest examples/security_manifest.json --judge examples/mock_judge.json \
  --predictions examples/synthetic_results.jsonl --run-manifest examples/synthetic_run.json \
  --out runs/imported
```

Outputs contain count/uncertainty evidence and hashed case identifiers, not raw reports.
Existing output requires `--overwrite` and Judge Lab ownership; unowned directories
and symlinks reject. Import requires exact case IDs and compatible run provenance.

`requirements-dev.lock` pins the tested development environment. `pyproject.toml`
declares the minimal runtime dependencies and separate dev/legacy extras. The old
`requirements.txt` remains available for the legacy provider workflow.

## Controlled probes and policy gates

```bash
.venv/bin/judge-lab probe --data examples/security_fixture.jsonl \
  --dataset-manifest examples/security_manifest.json --judge examples/mock_judge.json \
  --manifest examples/probe_manifest.json --vulnerable-mock --out runs/probe-demo
.venv/bin/judge-lab gate --report runs/demo/report.json \
  --policy examples/gate_policy.yaml
```

The vulnerable mock is deliberately flawed. One planted-rule failure demonstrates
code behavior, not robustness of a real judge. The synthetic gate exits **4
(INCONCLUSIVE)**. No model can authorize a gate. See [gate policy](docs/gates.md)
for statuses, reviewed evidence and approval records; no production bypass exists.

## Baseline, experiments and pilots

- [200-case baseline protocol](experiments/baseline_200/PROTOCOL.md):
  `python -m judge_lab.baseline --help`; requires authorized independent labels.
- [Matched-resource comparison](experiments/DIFFERENTIATION-PROTOCOL.md):
  `python -m judge_lab.experiments --help`; zero/negative results are valid.
- [Pilot toolkit](pilots/README.md): five blank records; **zero real pilots**.
- [Competitor capability review](experiments/COMPETITOR-MATRIX.md): primary-source
  documentation, not a comparative benchmark or superiority claim.

Empirical B0/H1/H2 are NOT PERFORMED. Novel transformed-population comparisons,
external independent review and five real sessions remain outstanding. Hashes
check consistency, not truth or authenticity; source evidence needs a trusted
custodian. Output paths assume a private local directory without concurrent writers.
See [review findings](reviews/INDEPENDENT-REVIEW.md) before using confidential data.

The [legacy XSTest workflow](docs/legacy/xstest.md), its source/tests, sample and
attribution are preserved. Legacy safe/unsafe outputs are never silently mapped
into ACCEPT/REJECT. Generated build/cache clutter can be removed; historical
source and user-authored plans are retained.

## Results

The [preregistered Ollama probe pilot](experiments/probe_pilot/results.md) measures
`llama3.1:8b` on 48 synthetic security-investigation reports using four fixed
metamorphic probes and a matched quoted-field sanitizer. Raw model responses,
model digest, error/abstention counts and nominal Wilson intervals are committed.
These template-based measurements do not satisfy the independent empirical
B0/H1/H2 gates or establish production robustness.

The runner is opt-in and local: `.venv/bin/python scripts/probe_pilot.py run`.
It refuses to overwrite the committed pilot run. See the
[frozen preregistration](experiments/probe_pilot/PREREG.md) for metrics and budgets.
