---
name: statistical-review
description: "Produce defensible repeated-run statistics. Use this skill when executing the statistical review stage of the OmniEvo project under Databricks Omnigent."
---

# statistical-review

## Goal
Produce defensible repeated-run statistics.

## Procedure
1. verify paired seeds,
2. summarize mean, median, IQR/SD,
3. compute 95% confidence intervals,
4. compute paired differences,
5. perform paired bootstrap,
6. optionally run Wilcoxon signed-rank sensitivity analysis,
7. inspect outlier seeds,
8. report both wins and losses.

## Rule
Do not declare superiority from a single run or only from a p-value.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
