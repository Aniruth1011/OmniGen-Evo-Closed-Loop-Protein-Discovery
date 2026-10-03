---
name: leakage-audit
description: "Prove that unmeasured fitness did not influence selection. Use this skill when executing the leakage audit stage of the OmniEvo project under Databricks Omnigent."
---

# leakage-audit

## Goal
Prove that unmeasured fitness did not influence selection.

## Checks
- agent filesystem access,
- tool interfaces,
- logs for accidental full-dataset reads,
- candidate tables for hidden labels,
- offline evaluator isolation,
- global optimum not present in planner context,
- no post-hoc availability list exposed.

## Failure action
Mark run invalid and rerun from clean state.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
