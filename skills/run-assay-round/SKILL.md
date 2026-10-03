---
name: run-assay-round
description: "Execute one 24-assay round through the hidden virtual lab. Use this skill when executing the run assay round stage of the OmniEvo project under Databricks Omnigent."
---

# run-assay-round

## Goal
Execute one 24-assay round through the hidden virtual lab.

## Procedure
1. validate run and round IDs,
2. submit selected candidates,
3. handle unavailable variants,
4. refill rejected slots using planner-approved fallback rules,
5. stop when 24 new valid measurements are obtained,
6. write assay ledger,
7. return only measured values and rejection metadata.

## Output
`measurements.csv`

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
