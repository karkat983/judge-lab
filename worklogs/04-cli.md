# Phase 04 — installed CLI and evidence reports

Implemented validate/calibrate/demo commands, package resources, strict bounded
JSON/YAML config, exact imported prediction workflow and private JSON plus escaped
standalone HTML reports. Reports contain hash-linked run/observation evidence,
counts, explicit denominators, nulls, intervals, slices and limitations. Raw report,
evidence and source text are omitted; optional raw result export remains omitted.
HTML escapes all data and has no CDN/script dependency. Report integrity verification
recomputes aggregate statistics, rather than trusting supplied percentage fields.

PyYAML (already pinned) is now a runtime dependency. YAML aliases, duplicate keys,
deep input and executable tags reject. Packaged synthetic resources are tested
byte-for-byte against documented examples to prevent drift.

Actual validation:

- Nine new CLI/report/config tests passed, exit 0; all current contract tests passed.
- Ruff initially found import/line-length issues, corrected; final lint exit 0.
- mypy initially required a narrow annotation at the untyped SafeLoader boundary;
  final type check exit 0, 12 source files.
- Installed `judge-lab demo --out runs/phase04-demo`: exit 0, JSON/HTML/manifest produced.
- Wheel build: exit 0. Separate wheel environment ran demo from `/private/tmp` without
  repository imports or API keys, exit 0; data resources included.
- Initial attempted installation from installed YAML metadata failed (exit 1);
  corrected by downloading/installing the pinned wheel, exit 0.

Tests cover output collisions/overwrite, imported errors, safe summaries, canary
omission, HTML escaping, exact HTML/JSON agreement, malformed config and metrics
tampering. No empirical accuracy claim. Engineering gate complete; next: 05.
