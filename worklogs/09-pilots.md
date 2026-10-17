# Phase 09 — local pilot toolkit

Added local onboarding/deletion instructions, a timed synthetic walkthrough,
voluntary consent/data-rights procedure, discovery questions and five individually
blank Markdown/JSON records. Private populated records are ignored. No people
contacted, accounts created, or employer data collected.

`judge_lab.pilots` validates completion requirements and summarizes only completed
REAL records. Synthetic tests, incomplete/withdrawn sessions cannot count toward
five. Duplicate pseudonyms reject. Summary output omits statements/identities and
warns that declarations cannot authenticate participants or observations.

Executed: 10 pilot tests passed, Ruff passed, mypy passed (17 modules), exit 0.
An initial JSON date roundtrip failed strict parsing; added explicit canonical ISO
date validation and reran successfully. CLI summary over P01–P05 exited 0 and
printed NO_REAL_PILOT_DATA; saved runs/phase09-pilots/pilot_summary.json.
Actual real participants = 0; completed real sessions = 0. Test-only REAL-shaped
objects exercise counting and were not saved as pilot evidence.

Limitations: independent custodian still needed for consent, rights, distinct
participants and evidence authentication. No demand or customer-validation claim.
Next authorized prompt: prompts/10-INDEPENDENT-REVIEW.md in the canonical pack;
final review will explicitly distinguish implementation self-review from external
independent reviewer approval.
