---
name: analyze-sample-efficiency
description: "Quantify how quickly each method discovers strong variants. Use this skill when executing the analyze sample efficiency stage of the OmniEvo project under Databricks Omnigent."
---

# analyze-sample-efficiency

## Goal
Quantify how quickly each method discovers strong variants.

## Metrics
- best fitness after 24/48/72/96 assays,
- area under best-so-far curve,
- assay count to threshold,
- top-1% and top-0.1% hit rates,
- normalized regret computed offline after runs finish.

## Outputs
- aggregate CSV,
- plot-ready tables,
- analysis memo.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
