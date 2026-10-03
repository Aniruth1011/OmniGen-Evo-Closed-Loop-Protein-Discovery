---
name: omnigent-orchestration
description: "Ensure Databricks Omnigent is the actual scientific orchestration layer. Use this skill when executing the omnigent orchestration stage of the OmniEvo project under Databricks Omnigent."
---

# omnigent-orchestration

## Goal
Ensure Databricks Omnigent is the actual scientific orchestration layer.

## Procedure
1. Keep the Scientific Director as the root agent.
2. Delegate to specialist sub-agents through Omnigent.
3. Require structured handoff outputs.
4. Keep tool boundaries explicit.
5. Use Omnigent policies to constrain risky or excessive tool use where appropriate.
6. Maintain one persistent session per major research run or one clearly indexed session tree.
7. Preserve handoff traces for the demo.
8. Do not replace the agent loop with a hidden end-to-end Python optimizer.

## Success criterion
A reviewer can inspect the Omnigent session and identify:

```text
result → critic → planner → changed round plan → lab measurement
```

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
