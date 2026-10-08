# judge-lab

> Status: **in progress.** Sections marked *planned* are not built yet.

## Problem
LLMs are increasingly used to grade other models' outputs, but a grader is only useful if its verdicts track human judgement and cannot be steered by the text it is grading. This matters because safety evaluations, leaderboards and guardrails all inherit whatever bias or weakness the judge has. See Zheng et al. 2023, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena".

## Approach
*Planned.* Run an LLM judge over a labelled public set of safe and unsafe prompts (XSTest), measure agreement with the human labels (accuracy, Cohen's kappa), test position and verbosity bias, and test whether an instruction hidden in the graded text flips the verdict.

## Results
*Planned.* No numbers yet.

| Metric | Value |
|--------|-------|
| Judge vs human accuracy | — |
| Cohen's kappa | — |
| Verdict flip rate under swap | — |
| Judge-injection success rate | — |

## Run it
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_data.py     # XSTest -> stratified 200-prompt sample in data/prompts.csv
pytest
```
The judge, bias and injection experiments are *planned*.

## What I learned
*Planned.*

## Notes
Public data only (XSTest, Röttger et al. 2024, CC BY 4.0). Not affiliated with any employer. Built October 2026.

## Changelog
- Day 1: project scaffold and changelog; XSTest sampler, loader, agreement stats.
- Committed the 200-prompt sample with source, licence and data card; label review of 30 items
  (28 agree, 2 ambiguous, 0 clear disagreements; docs/label_review.md).
- LLM layer: local Ollama judge by default (qwen2.5:3b-instruct), Claude optional; cache, cost
  meter, retry with backoff, rate limiting, scripted fake LLM for tests.
- Statistics: Cohen's kappa checked against its definition, bootstrap CI (coverage-tested),
  balanced accuracy and precision/recall for the unsafe class.
