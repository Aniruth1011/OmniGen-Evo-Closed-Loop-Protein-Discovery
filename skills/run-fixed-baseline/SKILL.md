---
name: run-fixed-baseline
description: "Execute one baseline with the exact same accounting rules. Use this skill when executing the run fixed baseline stage of the OmniEvo project under Databricks Omnigent."
---

# run-fixed-baseline

## Goal
Execute one baseline with the exact same accounting rules.

## Requirements
- same common initialization,
- same assay budget,
- same unavailable-candidate handling,
- same seed pairing,
- same surrogate and encoding for model-based baselines.

## Output
Identical run schema to adaptive strategy for easy comparison.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
