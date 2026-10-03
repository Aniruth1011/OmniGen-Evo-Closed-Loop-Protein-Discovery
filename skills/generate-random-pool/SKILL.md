---
name: generate-random-pool
description: "Create a seeded random candidate pool for random search or planner diversification. Use this skill when executing the generate random pool stage of the OmniEvo project under Databricks Omnigent."
---

# generate-random-pool

## Goal
Create a seeded random candidate pool for random search or planner diversification.

## Rule
Random selection must be reproducible and exclude measured sequences.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
