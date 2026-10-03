---
name: final-project-gate
description: "Prevent an incomplete but visually polished project from being presented as finished. Use this skill when executing the final project gate stage of the OmniEvo project under Databricks Omnigent."
---

# final-project-gate

## Goal
Prevent an incomplete but visually polished project from being presented as finished.

## Pass conditions
- literature survey complete,
- hidden oracle audited,
- baselines fair,
- adaptive-vs-fixed ablation complete,
- repeated confirmatory runs complete,
- statistics complete,
- reproducibility audit complete,
- Omnigent orchestration visible,
- demo assets generated,
- final claim reviewed by Critic.

If any primary gate fails, state the limitation explicitly in the final presentation.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
