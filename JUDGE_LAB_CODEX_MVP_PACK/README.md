# Judge Lab — Codex MVP Implementation Pack

**Edition:** v2.0 / 2026-10-16  
**Status:** engineering instructions, not implemented functionality.  
**Core decision:** stop building a general-purpose Agentic AI Assurance Operating System until a narrow judge-calibration workflow proves useful.

## Product in one sentence
A **bring-your-own-judge, local-first CLI and Python library** that measures whether an evaluator of *security-incident investigation reports* makes trustworthy release decisions, using reference labels, independent checks, quantified uncertainty, and controlled attacks.

### First user / buyer hypothesis
- Daily user: AI evaluation engineer or security-engineering lead maintaining an investigation or SOC-assistant evaluation pipeline.
- Potential budget owner: Head of AI Engineering or Head of Security Engineering. **Unvalidated hypothesis**, not known customer demand.
- First job to be done: "Before changing an AI judge model or rubric, show whether it accepts incorrect security-investigation reports, whether attacker-controlled evidence changes its decisions, and whether the change merits release or manual review."

### Core falsifiable claims
- **H1 (calibration value):** targeted reliability analysis reveals *verified, decision-relevant* evaluator failures or reduces reviewing effort versus the customer's existing judge + 200 hand-labeled examples.
- **H2 (adversarial value):** controlled, valid adversarial probes discover held-out, independently verified failures that standard labeled evaluation + fixed-attack baseline misses at comparable budget.

If those hypotheses are not supported, narrow, reposition or stop. Do **not** relabel generic metrics as a moat.

## Read in this order
1. [`AGENTS.md`](AGENTS.md) — top-level Codex instructions, read on every task.
2. [`00-QUICKSTART.md`](00-QUICKSTART.md) — exact setup in Cursor/Codex.
3. [`ROADMAP.md`](ROADMAP.md) — stage gates and file sequence.
4. [`specs/01-SCOPE-AND-NONGOALS.md`](specs/01-SCOPE-AND-NONGOALS.md).
5. [`specs/02-ARCHITECTURE.md`](specs/02-ARCHITECTURE.md) and [`specs/03-DATA-CONTRACTS.md`](specs/03-DATA-CONTRACTS.md).
6. [`specs/04-METRICS-AND-STATISTICS.md`](specs/04-METRICS-AND-STATISTICS.md), [`specs/05-ADVERSARIAL-VALIDITY.md`](specs/05-ADVERSARIAL-VALIDITY.md), [`specs/06-SECURITY-BOUNDARIES.md`](specs/06-SECURITY-BOUNDARIES.md).
7. One step in `prompts/` at a time.

## What gets implemented
**Stage A — Baseline replication:** parse labeled fixtures; strict provider-independent judge interface; confusion matrix, accuracy, kappa, false-accept and uncertainty metrics; human-readable offline reports; reproduce a 200-case baseline before claiming a delta.

**Stage B — Measurable differentiation:** controlled paired probes (rubric/instruction injection, limited meaning-preserving transformations), independent validity checks, held-out tests, fair cost-matched baseline, and a deterministic release-decision policy. No generative attack agent initially.

**Stage C — Five real-user pilots:** onboarding docs, opt-in/privacy protocol, measurement templates, feedback, and a go/no-go decision. Pilot discovery and enrollment require humans; Codex must not invent them.

## What is explicitly postponed
Ten runtime agents, seventeen domain packs, trajectory reasoning as a core feature, agent-generated causal narratives, GPU fleet, hosted dashboard/SaaS, SSO/multi-tenancy, autonomous exploitation, commercial safety certification, insurance/auditing claims, and arbitrary real-world integrations.

## Product agent count: ZERO at MVP
The **product itself** initially runs deterministic orchestration and user-provided judge calls. Codex can use bounded *coding roles* (implementer, evaluator, independent reviewer), but do not confuse those development roles with product runtime agents.

## Repository integration
If this pack is placed inside an existing Judge Lab repository, **do not overwrite existing code blindly**. Begin with `prompts/00-REPO-AUDIT.md`, reconcile conflicts in an ADR, and implement only missing functionality. The archived blueprint in `reference/` is historical vision, NOT the MVP implementation contract.

## Expected outputs
A working package, reproducible fixtures and tests, truthful JSON/HTML reports, recorded experiment protocols/results, and pilot evidence. No fabricated benchmark results or pretend user interviews.
