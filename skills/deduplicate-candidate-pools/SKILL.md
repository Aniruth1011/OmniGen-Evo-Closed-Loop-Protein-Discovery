---
name: deduplicate-candidate-pools
description: "Resolve overlap between exploitation, uncertainty, diversity, and local candidate pools before assays are spent. Use this skill when executing the deduplicate candidate pools stage of the OmniEvo project under Databricks Omnigent."
---

# deduplicate-candidate-pools

## Goal
Resolve overlap between exploitation, uncertainty, diversity, and local candidate pools before assays are spent.

## Procedure
1. merge selected candidates,
2. preserve source-priority and source attribution,
3. remove already measured sequences,
4. resolve duplicate nominations deterministically,
5. refill from the same source first unless planner specifies otherwise,
6. produce exactly 24 candidate proposals before virtual-lab availability rejections.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
