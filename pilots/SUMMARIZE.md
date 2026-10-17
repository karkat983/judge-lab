# Summarizing pilot records

Run `python -m judge_lab.pilots --records <private-records.json ...> --out runs/pilots`.
Input schema is PilotRecord in src/judge_lab/pilots.py. JSON dates use YYYY-MM-DD.
Blank templates validate but do not count. Completed records require consent,
permissions, retention consent, observed timing/counts, supporting evidence hashes,
feedback and source type. Withdrawn, incomplete and synthetic records are excluded.
Duplicate pseudonyms reject the whole batch. Invalid records exit 2 without raw text.

Summary emits counts, time totals and hashes; it omits participant statements and
raw records. Five completed REAL declarations are necessary for the five-record
flag. They are insufficient to authenticate five real humans: a custodian must
verify distinct participants, consent, sessions and evidence independently. Blank
records currently produce NO_REAL_PILOT_DATA and zero completed records.

After five real sessions, write an evidence table with positive and disconfirming
observations. Choose ship a narrow local tool, integrate, pivot or stop based on
verified outcomes. Stated interest alone does not imply demand; five sessions do
not establish statistical product effectiveness. No choice is preselected here.
