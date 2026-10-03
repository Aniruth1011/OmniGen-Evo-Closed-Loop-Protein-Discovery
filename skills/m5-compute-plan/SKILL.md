---
name: m5-compute-plan
description: "Keep the project fast and reliable on Apple M5. Use this skill when executing the m5 compute plan stage of the OmniEvo project under Databricks Omnigent."
---

# m5-compute-plan

## Goal
Keep the project fast and reliable on Apple M5.

## Rules
- avoid CUDA-only dependencies,
- use sklearn primary models,
- precompute 160k sequence encodings once,
- vectorize scoring,
- cache candidate metadata,
- parallelize seed-level runs only after deterministic single-run validation,
- prefer CPU-friendly uncertainty proxies,
- avoid deep protein model fine-tuning.

## Escalation
If local runtime becomes a bottleneck, move execution to Databricks Sandbox without changing the Omnigent agent protocol.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
