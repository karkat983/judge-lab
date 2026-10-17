# Local pilot toolkit — NO REAL PILOT DATA

Zero participants recruited, zero completed sessions. Five templates are blank
planning records. Do not report them as users, testimonials, demand or validation.
A human must arrange voluntary recruitment and permissions. No messages were sent.

Use Python 3.12+ and `make setup` from the repository. The pinned environment was
executed on Python 3.14 locally; CI targets 3.12. The installed CLI is offline:
only bundled deterministic mock or explicit imported predictions. No provider
adapter or telemetry is enabled. External judge prediction generation is outside
this tool and requires a separate approved data/provider arrangement.

## Ten-minute synthetic walkthrough

1. Minutes 0–2: explain scope and limitations; review consent and data boundaries.
   Use synthetic fixtures for the demonstration. Do not ask for employer logs.
2. Minutes 2–4: run `.venv/bin/judge-lab demo --out runs/pilot-demo` in a new output
   directory. Open report.html locally. The banner must say synthetic demonstration.
3. Minutes 4–6: inspect confusion counts, coverage, abstentions/errors and Wilson
   uncertainty. Ask the participant to explain the denominator they would use.
4. Minutes 6–8: run `.venv/bin/judge-lab gate --report runs/pilot-demo/report.json
   --policy examples/gate_policy.yaml` on one line. Expected exit 4, INCONCLUSIVE.
   Explain that a mock demonstration cannot authorize release.
5. Minutes 8–10: capture observed setup/task times and blockers separately from
   opinions, future intentions and stated willingness to pay. Invite correction.

For a real baseline comparison, arrange rights-cleared deidentified cases,
independent labels and a matched resource plan first; ten minutes is a demo,
not enough to claim a 200-case empirical study. Stop if participants lack rights.

Copy templates/P01.json and P01.md to an ignored private `pilots/records/`
directory. Keep real identities and consent signatures in an access-controlled
local system outside this repository; the JSON uses pseudonyms and record hashes.
Do not put private records in commits, screenshots or shared support logs.
Run `python -m judge_lab.pilots --records pilots/templates/P*.json
--out runs/pilot-summary` on one line to verify the blank starter records.
See SUMMARIZE.md before replacing paths with real records.

Deletion: agree a retention date and custodian before consent. On withdrawal,
remove private record and linked artifacts/exports from the agreed local storage,
remove the participant from aggregate source data and regenerate summaries in a
new output directory. Delete superseded summaries/backups under the same retention
policy. Do not delete source systems you do not own. Git history is not a private
record store and ordinary file deletion does not erase history or external backups.

Known limits: no participant/consent authentication, no PII detector, no provider
integration, no empirical superiority and no customer validation. Source text may
be confidential even when outputs contain only hashes; treat both as private.
