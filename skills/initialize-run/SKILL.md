---
name: initialize-run
description: "Create one fair paired run. Use this skill when executing the initialize run stage of the OmniEvo project under Databricks Omnigent."
---

# initialize-run

## Goal
Create one fair paired run.

## Procedure
1. Set seed.
2. Create run ID.
3. Generate common initial 24 candidates using the preregistered rule.
4. Send through virtual lab.
5. Store results once.
6. Fork the same observed initial dataset to every strategy in the pair/set.
7. Initialize per-strategy ledgers.

## Output
`runs/<strategy>/seed_<n>/round_01/*`

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
