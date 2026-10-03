---
name: critic-round-review
description: "Evaluate whether the previous strategy worked and whether the next strategy should change. Use this skill when executing the critic round review stage of the OmniEvo project under Databricks Omnigent."
---

# critic-round-review

## Goal
Evaluate whether the previous strategy worked and whether the next strategy should change.

## Required checks
- best-fitness improvement,
- yield by candidate source,
- surrogate error on newly revealed points,
- uncertainty usefulness,
- redundancy,
- local-search stagnation,
- leakage,
- budget compliance,
- fairness relative to baselines,
- whether policy change is justified.

## Output
`critic_report.yaml`

## Blocking rule
Leakage failure blocks continuation.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
