---
name: generate-local-pool
description: "Generate directed-evolution candidates near the current best measured variants. Use this skill when executing the generate local pool stage of the OmniEvo project under Databricks Omnigent."
---

# generate-local-pool

## Goal
Generate directed-evolution candidates near the current best measured variants.

## Procedure
1. identify current best sequence(s),
2. enumerate unseen Hamming-1 neighbors,
3. optionally include Hamming-2 only if protocol allows,
4. return a candidate pool with distance metadata,
5. never use hidden fitness for ranking.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
