---
name: analyze-agent-value
description: "Test the core hypothesis that adaptivity adds value beyond the surrogate model. Use this skill when executing the analyze agent value stage of the OmniEvo project under Databricks Omnigent."
---

# analyze-agent-value

## Goal
Test the core hypothesis that adaptivity adds value beyond the surrogate model.

## Primary contrast
```text
Adaptive planner
vs
Fixed mixture
```

## Must hold constant
- surrogate,
- features,
- initialization,
- candidate primitives,
- total budget.

## Additional analyses
- compare with and without critic,
- compare allocation changes to next-round outcomes,
- measure which strategy changes were beneficial.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
