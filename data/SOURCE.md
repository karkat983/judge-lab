# Source of data/prompts.csv

A stratified sample of 200 prompts from **XSTest** (Röttger et al., 2024), produced by
`scripts/fetch_data.py` with seed 13 (see `config.yaml`).

- Paper: Paul Röttger, Hannah Rose Kirk, Bertie Vidgen, Giuseppe Attanasio, Federico Bianchi,
  Dirk Hovy. "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large
  Language Models." NAACL 2024.
- Data: https://github.com/paul-rottger/xstest (`xstest_prompts.csv`)
- Licence: CC BY 4.0. This sample is redistributed under the same licence.

Columns: `id` (xstest-<original id>), `text`, `human_label` (safe/unsafe, from XSTest),
`category` (XSTest `type`), `focus` (XSTest `focus`).
