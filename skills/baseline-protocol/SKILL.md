---
name: baseline-protocol
description: "Freeze a fair baseline suite. Use this skill when executing the baseline protocol stage of the OmniEvo project under Databricks Omnigent."
---

# baseline-protocol

## Goal
Freeze a fair baseline suite.

## Required baselines
1. Random Search.
2. Budget-Matched Greedy Local Directed Evolution.
3. Fixed Exploitation.
4. Fixed Uncertainty/UCB.
5. Fixed Mixture Control.

## Primary fairness constraint
Adaptive and Fixed Mixture must share:

- initial data,
- surrogate model,
- sequence encoding,
- candidate primitives,
- assay budget,
- seed pairing.

## Output
`research/baseline_protocol.md`

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
