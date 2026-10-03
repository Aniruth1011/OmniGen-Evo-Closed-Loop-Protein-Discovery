---
name: fit-surrogate
description: "Fit a reproducible sequence-to-fitness model using observed assays only. Use this skill when executing the fit surrogate stage of the OmniEvo project under Databricks Omnigent."
---

# fit-surrogate

## Goal
Fit a reproducible sequence-to-fitness model using observed assays only.

## Primary model
`ExtraTreesRegressor` unless preregistration says otherwise.

## Primary encoding
80-dimensional one-hot encoding of 4 positions × 20 amino acids.

## Procedure
1. Load only observed assay pairs.
2. Encode sequences.
3. Fit model with fixed seed.
4. Compute diagnostics on observed data using small-data-aware cross-validation where possible.
5. Save model and diagnostics.
6. Produce predictions for theoretical unseen candidates without using hidden fitness.
7. Derive uncertainty proxy from tree-ensemble variance if used.

## Outputs
- model artifact,
- `surrogate_report.json`,
- candidate score table.

## Prohibition
Do not evaluate surrogate against the entire hidden landscape during an active run.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
