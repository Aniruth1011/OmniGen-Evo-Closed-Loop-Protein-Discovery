---
name: generate-uncertainty-pool
description: "Create candidates expected to reduce model uncertainty. Use this skill when executing the generate uncertainty pool stage of the OmniEvo project under Databricks Omnigent."
---

# generate-uncertainty-pool

## Goal
Create candidates expected to reduce model uncertainty.

## Procedure
1. compute uncertainty proxy,
2. remove measured sequences,
3. rank by uncertainty,
4. optionally remove extreme duplicates,
5. return candidate pool.

## Caution
High uncertainty is not automatically useful. The Critic must evaluate whether the pool provided information or simply sampled poor sequences.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
