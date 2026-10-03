---
name: generate-diversity-pool
description: "Explore under-sampled sequence regions. Use this skill when executing the generate diversity pool stage of the OmniEvo project under Databricks Omnigent."
---

# generate-diversity-pool

## Goal
Explore under-sampled sequence regions.

## Possible methods
- maximum Hamming distance from observed set,
- farthest-point traversal,
- underrepresented residue combinations,
- diversity in one-hot feature space.

## Rule
Freeze the method for confirmatory runs.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
