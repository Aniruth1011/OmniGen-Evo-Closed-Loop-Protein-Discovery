---
name: run-repeated-benchmark
description: "Run paired adaptive and baseline experiments over many seeds. Use this skill when executing the run repeated benchmark stage of the OmniEvo project under Databricks Omnigent."
---

# run-repeated-benchmark

## Goal
Run paired adaptive and baseline experiments over many seeds.

## Procedure
1. load frozen confirmatory config,
2. loop over confirmatory seeds,
3. create common initialization per seed,
4. run all strategies,
5. store all raw results,
6. never change hyperparameters based on partial confirmatory outcomes.

## Target
30–100 paired seeds depending on time.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
